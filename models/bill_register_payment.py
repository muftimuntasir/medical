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

    def _creation_of_money_receipt(self):

        payment_obj = self
        bill_id = payment_obj.bill_id.id
        bill_register_id = payment_obj.bill_id.name
        pay_date = payment_obj.date
        pay_amount = payment_obj.amount
        pay_type = payment_obj.payment_type.name
        pay_card = payment_obj.account_number
        current_due = payment_obj.bill_id.due
        current_paid = payment_obj.bill_id.paid
        money_receipt_id = payment_obj.money_receipt_id.id

        updated_amount = max(current_due - pay_amount, 0)
        updated_paid = current_paid + pay_amount

        service_dict = {
            'date': pay_date,
            'amount': pay_amount,
            'type': pay_type,
            'card_no': pay_card,
            'bill_register_payment_line_id': bill_id,
            'money_receipt_id': money_receipt_id
        }
        return self.env['bill.register.payment.line'].create(service_dict)

    def _create_journal_entry(self):
        payment_obj =self
        bill_register_id = payment_obj.bill_id.name
        current_paid = payment_obj.bill_id.paid
        pay_amount = payment_obj.amount
        journal_object = self.env["bill.journal.relation"]
        line_ids = []

        periods = self.env['account.period'].find()
        period_id = periods and periods[0].id or False

        if current_paid > 0 and payment_obj.payment_type.name == 'Cash':
            line_ids.append((0, 0, {
                'analytic_account_id': False,
                'name': bill_register_id,
                'account_id': 6,  # Cash ID
                'debit': pay_amount,
                'credit': 0,
            }))
            line_ids.append((0, 0, {
                'analytic_account_id': False,
                'name': bill_register_id,
                'account_id': 195,  # Accounts Receivable ID
                'debit': 0,
                'credit': pay_amount,
            }))
        elif current_paid > 0 and payment_obj.payment_type.name == 'Visa Card':
            other_method_pay = payment_obj.to_be_paid
            service_charge = payment_obj.service_charge

            line_ids.append((0, 0, {
                'analytic_account_id': False,
                'name': bill_register_id,
                'account_id': payment_obj.payment_type.account.id,  # Card ID
                'debit': other_method_pay,
                'credit': 0,
            }))
            line_ids.append((0, 0, {
                'analytic_account_id': False,
                'name': bill_register_id,
                'account_id': 195,  # Accounts Receivable ID
                'debit': 0,
                'credit': pay_amount,
            }))
            if service_charge > 0:
                line_ids.append((0, 0, {
                    'analytic_account_id': False,
                    'name': bill_register_id,
                    'account_id': payment_obj.payment_type.service_charge_account.id,
                    'debit': 0,
                    'credit': service_charge,
                }))

        move_vals = {
            'journal_id': 2,  # Cash Journal
            'date': fields.Date.today(),
            'ref': bill_register_id,
            'line_ids': line_ids,
        }

        move = self.env['account.move'].create(move_vals)
        if move:
            move.action_post()
            journal_object.create({'journal_id': move.id, 'bill_journal_relation_id': bill_register_id})

        return True

    def button_add_payment_action(self):
        payment_obj = self
        pay_amount = payment_obj.amount
        current_due = payment_obj.bill_id.due
        current_paid = payment_obj.bill_id.paid
        updated_amount = max(current_due - pay_amount, 0)
        updated_paid = current_paid + pay_amount
        self._creation_of_money_receipt()

        return self.env.cr.execute("UPDATE bill_register SET due=%s, paid=%s WHERE id=%s", (updated_amount, updated_paid, payment_obj.bill_id.id))


    @api.model
    def create(self, vals):
        stored_payment = super(BillRegisterPayment, self).create(vals)

        import pdb
        pdb.set_trace()

        if stored_payment:
            name_text = f'CC-200{stored_payment.id}'
            stored_payment.name = name_text

            money_receipt_vals = {
                'date': vals['date'],
                'bill_id': stored_payment.bill_id.id,
                'amount': vals['amount'],
                'type': vals['payment_type'],
                'p_type': 'due_payment',
                'diagonostic_bill': stored_payment.bill_id.diagonostic_bill
            }
            mr_id = self.env['leih.money.receipt'].create(money_receipt_vals)
            if mr_id:
                mr_id.name = f'MR#{mr_id.id}'
                stored_payment.money_receipt_id = mr_id.id

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
