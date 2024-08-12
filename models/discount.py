from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import date

class Discount(models.Model):
    _name = "discount"
    _order = 'id desc'

    name = fields.Char("Discount Number", readonly=True, default=lambda self: _('New'))
    date = fields.Datetime("Date", readonly=True, default=fields.Datetime.now)
    admission_id = fields.Many2one("leih.admission", "Admission ID")
    bill_no = fields.Many2one('bill.register', 'Bill No')
    patient_name = fields.Char("Patient Name", required=True)
    mobile = fields.Char("Mobile Number", required=True)
    total_discount = fields.Float('Total Discount', compute='_compute_total_discount', store=True)
    amount = fields.Integer("Amount")
    state = fields.Selection([
        ('pending', 'Pending'),
        ('approve', 'Approved'),
        ('cancel', 'Cancelled')],
        'State', default='pending', readonly=True)
    discount_line_ids = fields.One2many("discount.line", 'discount_id', 'Discount Line', required=True)

    @api.depends('discount_line_ids')
    def _compute_total_discount(self):
        for record in self:
            total_fixed = sum(line.fixed_amount for line in record.discount_line_ids)
            total_percent = sum(line.percent_amount for line in record.discount_line_ids)
            percent_discounted_amount = (record.amount * total_percent) / 100
            record.total_discount = total_fixed + percent_discounted_amount

    def approve_discount(self):
        for discount in self:
            if discount.state == 'approve':
                raise UserError(_('Discount is already approved!'))

            bill_id = discount.bill_no.id
            admission_id = discount.admission_id.id
            total_discount = discount.total_discount

            if bill_id:
                bill = self.env['bill.register'].browse(bill_id)
                if bill.state != 'confirmed':
                    raise UserError(_('The bill is not in confirmed state yet!'))

                if bill.due < total_discount:
                    raise UserError(_('Not permitted to apply a discount greater than the due amount!'))

                bill.write({
                    'other_discount': total_discount,
                    'grand_total': bill.grand_total - total_discount,
                    'due': bill.due - total_discount
                })

            elif admission_id:
                admission = self.env['leih.admission'].browse(admission_id)
                if admission.due < total_discount:
                    raise UserError(_('Not permitted to apply a discount greater than the due amount!'))

                admission.write({
                    'other_discount': total_discount,
                    'grand_total': admission.grand_total - total_discount,
                    'due': admission.due - total_discount
                })

            # Create journal entry for approved discount
            period_id = self.env['account.period'].find()[0] if self.env['account.period'].find() else False

            line_ids = [
                (0, 0, {
                    'name': discount.name,
                    'account_id': discount.discount_line_ids[0].accounts.id,  # Cash ID
                    'debit': total_discount,
                    'credit': 0,
                }),
                (0, 0, {
                    'name': discount.name,
                    'account_id': 195,  # Accounts Receivable ID
                    'debit': 0,
                    'credit': total_discount,
                })
            ]

            journal_entry = self.env['account.move'].create({
                'name': '/',
                'journal_id': 6,  # Cash Journal
                'date': fields.Date.today(),
                'period_id': period_id,
                'ref': discount.bill_no.name if discount.bill_no else discount.admission_id.name,
                'line_ids': line_ids
            })

            journal_entry.action_post()

            discount.write({'state': 'approve'})

        return True

    def cancel_discount(self):
        self.write({'state': 'cancel'})
        return True

    @api.onchange('bill_no')
    def onchange_bill(self):
        if self.bill_no:
            bill = self.bill_no
            self.patient_name = bill.patient_name.name
            self.mobile = bill.patient_name.mobile
            self.amount = bill.due

    @api.onchange('admission_id')
    def onchange_admission(self):
        if self.admission_id:
            admission = self.admission_id
            self.patient_name = admission.patient_name.name
            self.mobile = admission.patient_name.mobile
            self.amount = admission.grand_total

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('discount') or _('New')
        return super(Discount, self).create(vals)

class DiscountLine(models.Model):
    _name = "discount.line"

    category = fields.Many2one('discount.category', 'Discount Category')
    ref = fields.Char("Reference")
    accounts = fields.Many2one("account.account", "Account Name")
    fixed_amount = fields.Integer("Amount (fixed)")
    percent_amount = fields.Integer("Amount (%)")
    discount_id = fields.Many2one("discount", "Discount ID")

    @api.onchange('category')
    def onchange_category(self):
        if self.category:
            self.accounts = self.category.account_id.id or self.env.ref('account.account_expense').id
