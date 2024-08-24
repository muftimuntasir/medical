from odoo import models, fields, api, _
from datetime import datetime
from odoo.exceptions import UserError



class OpticsSalePayment(models.Model):
    _name = 'optics.sale.payment'
    _description = "optics sale Payment"

    def _creation_of_money_receipt(self,payment_type='due_payment'):

        money_receipt_vals = {
            'date': self.date,
            'optics_sale_id': self.optics_sale_id.id,
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



    def _creation_of_optic_sale_payment_line(self):
        payment_obj = self
        optics_id = payment_obj.optics_sale_id.id
        pay_date = payment_obj.date
        pay_amount = payment_obj.amount
        pay_type = payment_obj.payment_type.name
        pay_card = payment_obj.account_number
        current_due = payment_obj.optics_sale_id.due
        money_receipt_id = payment_obj.money_receipt_id.id
        updated_amount = current_due - pay_amount
        if updated_amount < 0:
            updated_amount = 0


        service_dict = {
            'date': pay_date,
            'amount': pay_amount,
            'type': pay_type,
            'card_no': pay_card,
            'optics_sale_payment_line_id': optics_id,
            'money_receipt_id': money_receipt_id
        }



        return self.env['optics.sale.payment.line'].create(service_dict)


    def button_add_payment_action(self):

        payment_obj=self
        optics_sale_id=payment_obj.optics_sale_id.id
        pay_amount = payment_obj.amount
        mr_id = self._creation_of_money_receipt()

        updated_amount=10
        updated_paid = 11

        if mr_id:
            mr_id.name = f'MR#{mr_id.id}'

            self.money_receipt_id = mr_id.id
            self._creation_of_optic_sale_payment_line()

            j_id = self._create_journal_entry(amount=pay_amount, cr_act_id=1, dr_act_id=1, bill_no=self.optics_sale_id.name, line_label=f'MR#{mr_id.id}')
            self.env.cr.execute("UPDATE leih_money_receipt SET journal_id=%s WHERE id=%s",
                                (j_id.id, mr_id.id))

        return self.env.cr.execute("update optics_sale set due=%s,paid=%s where id=%s", (updated_amount, updated_paid, optics_sale_id))


    def _default_payment_type(self):
         return self.env['payment.type'].search([('name', '=', 'Cash')], limit=1).id


    name =fields.Char("Cash Collection ID", readonly=True)
    optics_sale_id = fields.Many2one('optics.sale', 'Optics Bill ID', readoly=True)
    date = fields.Date('Date',required=True)
    amount = fields.Float('Receive Amount', required=True)
    payment_type = fields.Many2one('payment.type','Payment Type',default=_default_payment_type)
    service_charge = fields.Float("Service Charge")
    to_be_paid = fields.Float("To be Paid")
    account_number =fields.Char('Account No.')
    money_receipt_id = fields.Many2one('leih.money.receipt', 'Money Receipt ID')


    def create(self, vals):

        stored_payment = super(OpticsSalePayment, self).create(vals)

        if stored_payment:
            name_text = 'CC-100' + str(stored_payment.id)
            stored_payment.name = name_text

        return stored_payment

    @api.onchange("payment_type")
    def onchnage_payment_type(self):
        if self.payment_type.active==True:
            interest=self.payment_type.service_charge
            if interest>0:
                service_charge=(self.amount*interest)/100
                self.service_charge=service_charge
                self.to_be_paid=self.amount+service_charge
            else:
                self.to_be_paid=self.amount
                self.service_charge=0
