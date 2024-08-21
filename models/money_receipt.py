from odoo import models, fields, api,_
from odoo.exceptions import ValidationError
from datetime import date, time

class MoneyReceipt(models.Model):
    _name = "leih.money.receipt"

    name = fields.Char(string="MR ID")
    date = fields.Date(string="Date")
    bill_id = fields.Many2one("bill.register", string="Bill ID")
    admission_id = fields.Many2one("leih.admission", string="Admission ID")
    optics_sale_id = fields.Many2one("optics.sale", string="Optics Sale ID")
    amount = fields.Float(string="Paid Amount")
    bill_total_amount = fields.Float(string="Total Amount")
    due_amount = fields.Float(string="Due Amount")
    p_type = fields.Selection([
        ('advance', 'Advance'),
        ('due_payment', 'Due Payment')], string='Payment Method')
    already_collected = fields.Boolean(string="Collected", default=False)
    diagonostic_bill = fields.Boolean(string="Diagnostic Bill")
    type = fields.Many2one("payment.type", string="Type")
    user_id = fields.Many2one('res.users', string='Current User', default=lambda self: self.env.user)
    state = fields.Selection([
        ('confirm', 'Confirm'),
        ('cancel', 'Cancelled')], string='State', default='confirm')

    @api.model
    def create(self, vals):
        res = super(MoneyReceipt, self).create(vals)

        # Update Bill Register Paid Value
        try:
            paid_amount = 0
            if 'bill_id' in vals:
                bill_id = vals.get('bill_id')
                bill = self.env['bill.register'].browse(bill_id)
                paid_amount = bill.paid + float(vals.get('amount', 0.0))
                bill.write({'paid': paid_amount})
        except Exception as e:
            raise ValidationError(_("Error updating Bill Register: %s") % str(e))

        return res
