from odoo import api, fields, models, _
from datetime import datetime

class CashCollection(models.Model):
    _name = "cash.collection"
    _description = "Cash Collection"
    _order = 'id desc'

    name = fields.Char("Cash Collection No")
    date = fields.Datetime("Date", default=fields.Datetime.now)
    type = fields.Selection([
        ('bill', 'Bill [Diagnosis]'),
        ('bill_others', 'Bill [Others]'),
        ('opd', 'OPD'),
        ('admission', 'Admission'),
        ('optics', 'Optics')
    ], string='Type')
    total = fields.Float("Total")
    journal_id = fields.Many2one('account.move', 'Journal')
    debit_act_id = fields.Many2one('account.account', 'Debit Account', required=True)
    credit_act_id = fields.Many2one('account.account', 'Credit Account', required=True)
    cash_collection_lines = fields.One2many("cash.collection.line", "cash_collection_line_id", 'Cash Collection', required=True)
    state = fields.Selection([
        ('pending', 'Pending'),
        ('approve', 'Confirmed'),
        ('cancel', 'Cancelled')
    ], string='State', default='pending', readonly=True)

    @api.onchange('type')
    def _onchange_type(self):
        child_list = []
        total = 0

        if self.type == 'bill':
            vals_parameter = [('bill_id', '!=', False), ('diagonostic_bill', '=', True), ('already_collected', '!=', True), ('state', '!=', 'cancel')]
            if self.date:
                vals_parameter.append(('date', '=', self.date))
            mr_obj = self.env['leih.money.receipt'].search(vals_parameter)

        elif self.type == 'bill_others':
            vals_parameter = [('bill_id', '!=', False), ('diagonostic_bill', '!=', True), ('already_collected', '!=', True), ('state', '!=', 'cancel')]
            if self.date:
                vals_parameter.append(('date', '=', self.date))
            mr_obj = self.env['leih.money.receipt'].search(vals_parameter)

        elif self.type == 'admission':
            vals_parameter = [('admission_id', '!=', False), ('already_collected', '!=', True), ('state', '!=', 'cancel')]
            if self.date:
                vals_parameter.append(('date', '=', self.date))
            mr_obj = self.env['leih.money.receipt'].search(vals_parameter)

        elif self.type == 'optics':
            vals_parameter = [('optics_sale_id', '!=', False), ('already_collected', '!=', True), ('state', '!=', 'cancel')]
            if self.date:
                vals_parameter.append(('date', '=', self.date))
            mr_obj = self.env['leih.money.receipt'].search(vals_parameter)

        elif self.type == 'opd':
            vals_parameter = [('already_collected', '!=', True)]
            if self.date:
                vals_parameter.append(('date', '=', self.date))
            mr_obj = self.env['opd.ticket'].search(vals_parameter)

        for record in mr_obj:
            abc = {
                'bill_admission_opd_id': record.bill_id.name if self.type != 'opd' else record.name,
                'mr_no': record.id if self.type != 'opd' else False,
                'opd_id': record.id if self.type == 'opd' else False,
                'amount': record.amount if self.type != 'opd' else record.total
            }
            total += abc['amount']
            child_list.append((0, 0, abc))

        self.total = total
        self.cash_collection_lines = child_list

    def action_button_confirm(self):
        for cc_obj in self:
            if cc_obj.state == 'approve':
                raise models.ValidationError(_('Sorry, it is already confirmed'))
            else:
                periods = self.env['account.period'].find()
                period_id = periods and periods[0].id or False

                line_ids = [(0, 0, {
                    'name': cc_obj.name,
                    'account_id': cc_obj.debit_act_id.id,
                    'debit': cc_obj.total,
                }), (0, 0, {
                    'name': cc_obj.name,
                    'account_id': cc_obj.credit_act_id.id,
                    'credit': cc_obj.total,
                })]

                j_vals = {
                    'name': '/',
                    'journal_id': 2,  # Sales Journal
                    'date': fields.Date.today(),
                    'period_id': period_id,
                    'ref': cc_obj.name,
                    'line_ids': line_ids
                }

                jv_entry = self.env['account.move'].create(j_vals)
                jv_entry.action_post()

                cc_obj.state = 'approve'
                cc_obj.journal_id = jv_entry.id

                for line_item in cc_obj.cash_collection_lines:
                    if line_item.mr_no:
                        line_item.mr_no.already_collected = True
                    else:
                        line_item.opd_id.already_collected = True

    def action_button_cancel(self):
        self.write({'state': 'cancel'})

    @api.model
    def create(self, vals):
        record = super(CashCollection, self).create(vals)
        if record:
            record.name = 'Cash-0' + str(record.id)
        return record

class CashCollectionLine(models.Model):
    _name = "cash.collection.line"
    _description = "Cash Collection Line"

    cash_collection_line_id = fields.Many2one("cash.collection", "Cash Collection")
    mr_no = fields.Many2one('leih.money.receipt', 'MR No.')
    opd_id = fields.Many2one('opd.ticket', 'OPD No.')
    bill_admission_opd_id = fields.Char("Bill/Admission/OPD Number")
    amount = fields.Float("Amount")
