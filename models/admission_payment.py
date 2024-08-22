from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime


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

    def _creation_of_money_receipt(self):
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

    def _create_journal_entry(self):
        payment_obj = self
        admission_id = payment_obj.admission_id.id
        pay_amount = payment_obj.amount
        current_paid = payment_obj.admission_id.paid
        journal_object = self.env['bill.journal.relation']
        line_ids = []

        periods = self.env['account.period'].find()
        period_id = periods and periods[0].id or False

        if current_paid > 0 and payment_obj.payment_type.name == 'Cash':
            line_ids.append((0, 0, {
                'name': admission_id,
                'account_id': 6,  # Cash ID
                'debit': pay_amount,
            }))
            line_ids.append((0, 0, {
                'name': admission_id,
                'account_id': 195,  # Accounts Receivable ID
                'credit': pay_amount,
            }))

        if current_paid > 0 and payment_obj.payment_type.name == 'Visa Card':
            other_method_pay = payment_obj.to_be_paid
            service_charge = payment_obj.service_charge
            line_ids.append((0, 0, {
                'name': admission_id,
                'account_id': payment_obj.payment_type.account.id,
                'debit': other_method_pay,
            }))
            line_ids.append((0, 0, {
                'name': admission_id,
                'account_id': 195,  # Accounts Receivable ID
                'credit': pay_amount,
            }))
            if service_charge > 0:
                line_ids.append((0, 0, {
                    'name': admission_id,
                    'account_id': payment_obj.payment_type.service_charge_account.id,
                    'credit': service_charge,
                }))

        jv_entry = self.env['account.move']

        move_vals = {
            'journal_id': 2,  # Sales Journal
            'date': fields.Date.today(),
            'ref': admission_id,
            'line_ids': line_ids,
        }

        move = jv_entry.create(move_vals)
        if move:
            move.action_post()
            journal_object.create({
                'journal_id': move.id,
                'admission_journal_relation_id': admission_id
            })
        return True


    def button_add_payment_action(self):
        payment_obj = self
        pay_amount = payment_obj.amount
        current_due = payment_obj.admission_id.due
        current_paid = payment_obj.admission_id.paid
        updated_amount = current_due - pay_amount
        updated_paid = current_paid + pay_amount
        self._creation_of_money_receipt()


        return self.env.cr.execute("update leih_admission set due=%s, paid=%s where id=%s",
                            (updated_amount, updated_paid, payment_obj.admission_id.id))


    @api.model
    def create(self, vals):
        stored = super(AdmissionPayment, self).create(vals)  # return ID object

        if stored:
            name_text = 'CC-100' + str(stored.id)
            stored.name = name_text

            # Create a new money receipt
            value = {
                'date': vals.get('date'),
                'admission_id': vals.get('admission_id'),
                'amount': vals.get('amount'),
                'type': vals.get('payment_type'),
                'p_type': 'due_payment',
            }

            mr_object = self.env['leih.money.receipt']
            mr_id = mr_object.create(value)
            if mr_id:
                mr_id.name = 'MR#' + str(mr_id.id)
                stored.money_receipt_id = mr_id.id
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


