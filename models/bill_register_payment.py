from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import datetime

class BillRegisterPayment(models.Model):
    _name = 'bill.register.payment'
    _description = "Bill Register Payment"

    name = fields.Char(string="Cash Collection ID", readonly=True)
    bill_id = fields.Many2one('bill.register', string='Bill ID', readonly=True)
    date = fields.Date(string='Date', default=fields.Date.context_today)
    amount = fields.Float(string='Receive Amount', required=True)
    payment_type = fields.Many2one('payment.type', string='Payment Type', default=lambda self: self._default_payment_type())
    service_charge = fields.Float(string="Service Charge")
    to_be_paid = fields.Float(string="To be Paid")
    account_number = fields.Char(string='Account No.')
    money_receipt_id = fields.Many2one('leih.money.receipt', string='Money Receipt ID')

    @api.model
    def _default_payment_type(self):
        return self.env['payment.type'].search([('name', '=', 'Cash')], limit=1).id

    def _creation_of_bill_register_payment_line(self):


        service_dict = {
            'date': self.date,
            'amount': self.amount,
            'type': self.payment_type.name,
            'card_no': self.account_number,
            'bill_register_payment_line_id': self.bill_id.id,
            'money_receipt_id': self.money_receipt_id.id
        }
        return self.env['bill.register.payment.line'].create(service_dict)

    def _create_journal_entry(self,amount=0.0,cr_act_id=1,dr_act_id=1,bill_no="BILL",line_label="MR"):
        bill_no = bill_no + f'/' + line_label
        jv_vals = {
            'ref': bill_no,
            'journal_id':2,
            'date':'2024-08-22',
            'line_ids': [

                (0, 0, {
                    'name': line_label,
                    'account_id': dr_act_id,
                    'debit': amount,
                }),
                (0, 0, {
                    'name': line_label,
                    'account_id': cr_act_id,
                    'credit': amount,
                })
            ]

        }

        return self.env['account.move'].create(jv_vals)

    def button_add_payment_action(self):
        payment_obj = self
        pay_amount = payment_obj.amount
        current_due = payment_obj.bill_id.due
        current_paid = payment_obj.bill_id.paid
        updated_amount = max(current_due - pay_amount, 0)
        updated_paid = current_paid + pay_amount
        self._creation_of_bill_register_payment_line()


        return self.env.cr.execute("UPDATE bill_register SET due=%s, paid=%s WHERE id=%s", (updated_amount, updated_paid, payment_obj.bill_id.id))



    def _creation_of_money_receipt(self,vals=None, bill_id=None,diagonostic_bill=False):

        money_receipt_vals = {
            'date': vals['date'],
            'bill_id': bill_id,
            'amount': vals['amount'],
            'type': vals['payment_type'],
            'p_type': 'due_payment',
            'diagonostic_bill': diagonostic_bill
        }

        return self.env['leih.money.receipt'].create(money_receipt_vals)

    @api.model
    def create(self, vals):
        stored_payment = super(BillRegisterPayment, self).create(vals)

        if stored_payment:
            stored_payment.name = f'CC-200{stored_payment.id}'

            d_res = stored_payment.bill_id.diagonostic_bill
            mr_id = self._creation_of_money_receipt(vals=vals,bill_id=stored_payment.bill_id.id,diagonostic_bill=d_res)
            if mr_id:
                mr_id.name = f'MR#{mr_id.id}'

                journal_id = self._create_journal_entry(amount=vals['amount'], cr_act_id=1, dr_act_id=1,
                                           bill_no=stored_payment.bill_id.name, line_label=f'MR#{mr_id.id}')

                stored_payment.money_receipt_id = mr_id.id
                self.env.cr.execute("UPDATE leih_money_receipt SET journal_id=%s WHERE id=%s",
                                    (journal_id.id, mr_id.id))

        return stored_payment

    @api.onchange('payment_type')
    def onchange_payment_type(self):
        if self.payment_type and self.payment_type.active:
            interest = self.payment_type.service_charge
            if interest > 0:
                self.service_charge = (self.amount * interest) / 100
                self.to_be_paid = self.amount + self.service_charge
            else:
                self.to_be_paid = self.amount
                self.service_charge = 0
