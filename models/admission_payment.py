from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime
from odoo.exceptions import UserError


class AdmissionPayment(models.Model):
    _name = 'admission.payment'
    _description = "Admission Payment"

    name = fields.Char("Cash Collection ID", readonly=True)
    admission_id = fields.Many2one('leih.admission', 'Admission ID', readonly=True)
    date = fields.Date('Date', default=fields.Date.context_today)
    amount = fields.Float('Receive Amount', required=True)
    payment_type = fields.Many2one('payment.type', 'Payment Type', default=lambda self: self._default_payment_type())
    service_charge = fields.Float("Service Charge")
    to_be_paid = fields.Float("To be Paid")
    account_number = fields.Char('Account No.')
    money_receipt_id = fields.Many2one('leih.money.receipt', 'Money Receipt ID')

    @api.model
    def _default_payment_type(self):
        return self.env['payment.type'].search([('name', '=', 'Cash')], limit=1).id

    def _creation_of_admission_payment_line(self):
        payment_obj = self
        admission_id = payment_obj.admission_id.id
        leih_admission_id = payment_obj.admission_id.name
        pay_date = payment_obj.date
        pay_amount = payment_obj.amount
        pay_type = payment_obj.payment_type.name
        pay_card = payment_obj.account_number
        current_due = payment_obj.admission_id.due
        current_paid = payment_obj.admission_id.paid
        money_receipt_id = payment_obj.money_receipt_id.id
        updated_amount = current_due - pay_amount
        if updated_amount < 0:
            updated_amount = 0

        service_dict = {
            'date': pay_date,
            'amount': pay_amount,
            'type': pay_type,
            'card_no': pay_card,
            'admission_payment_line_id': admission_id,
            'money_receipt_id': money_receipt_id
        }


        return self.env['admission.payment.line'].create(service_dict)


    def _creation_of_money_receipt(self,payment_type='due_payment'):

        money_receipt_vals = {
            'date': self.date,
            'admission_id': self.admission_id.id,
            'amount': self.amount,
            'type': self.payment_type.id,
            'p_type': payment_type,
            'diagonostic_bill': False
        }

        return self.env['leih.money.receipt'].create(money_receipt_vals)

    def _create_journal_entry(self,amount=0.0,cr_act_id=1,dr_act_id=1,bill_no="Admission",line_label="MR"):
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
        current_due = payment_obj.admission_id.due
        current_paid = payment_obj.admission_id.paid
        updated_amount = current_due - pay_amount
        updated_paid = current_paid + pay_amount
        mr_id = self._creation_of_money_receipt()

        if mr_id:
            mr_id.name = f'MR#{mr_id.id}'

            self.money_receipt_id = mr_id.id
            self._creation_of_admission_payment_line()

            j_id = self._create_journal_entry(amount=pay_amount, cr_act_id=1, dr_act_id=1, bill_no=self.admission_id.name, line_label=f'MR#{mr_id.id}')
            self.env.cr.execute("UPDATE leih_money_receipt SET journal_id=%s WHERE id=%s",
                                (j_id.id, mr_id.id))

        return self.env.cr.execute("update leih_admission set due=%s, paid=%s where id=%s",
                            (updated_amount, updated_paid, payment_obj.admission_id.id))


    @api.model
    def create(self, vals):
        if vals.get('amount') > vals.get('to_be_paid'):
            raise UserError(_('You paid more than the TOTAL AMOUNT'))

        stored = super(AdmissionPayment, self).create(vals)  # return ID object

        if stored:
            name_text = 'CC-100' + str(stored.id)
            stored.name = name_text
        return stored

    @api.onchange("payment_type")
    def onchange_payment_type(self):
        if self.payment_type and self.payment_type.active:
            interest = self.payment_type.service_charge
            if interest > 0:
                self.service_charge = (self.amount * interest) / 100
                self.to_be_paid = self.amount + self.service_charge
            else:
                self.to_be_paid = self.amount
                self.service_charge = 0
        else:
            self.to_be_paid = self.amount
            self.service_charge = 0


