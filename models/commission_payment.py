from odoo import models, fields, api, _
from datetime import date

class CommissionPayment(models.Model):
    _name = "commission.payment"
    _description = "Commission Payment"

    name = fields.Char("CP No.")
    doctor_id = fields.Many2one('doctors.profile', 'Name')
    date = fields.Date('Payment Date')
    cc_id = fields.Many2one('commission.configuration', 'Commission')
    debit_id = fields.Many2one('account.account', 'Debit Account')
    credit_id = fields.Many2one('account.account', 'Credit Account')
    paid_amount = fields.Float('Paid Amount')
    due_amount = fields.Float('Due Amount')
    period_id = fields.Many2one('account.period', 'Period')
    journal_id = fields.Many2one('account.move', 'Journal')
    note = fields.Text("Note")
    state = fields.Selection(
        [('pending', 'Pending'), ('done', 'Confirmed'), ('cancelled', 'Cancelled')],
        'Status', default='pending', readonly=True
    )

    @api.model
    def create(self, vals):
        record = super(CommissionPayment, self).create(vals)
        return record

    def button_add_payment_action(self):
        self.ensure_one()
        doc_name = self.doctor_id.name
        ref = self.cc_id.name

        # Create Journal Entry
        move_vals = {
            'name': '/',
            'period_id': self.period_id.id,
            'journal_id': 5,
            'ref': ref,
            'date': date.today(),
            'line_ids': [
                (0, 0, {
                    'name': doc_name,
                    'debit': self.paid_amount,
                    'account_id': self.debit_id.id,
                }),
                (0, 0, {
                    'name': doc_name,
                    'credit': self.paid_amount,
                    'account_id': self.credit_id.id,
                })
            ]
        }
        move = self.env['account.move'].create(move_vals)
        move.action_post()  # Validate the journal entry

        self.journal_id = move.id

        # Update Balance of Commission
        self.cc_id.write({
            'state': 'paid',
            'paid_amount': self.paid_amount,
        })

        # Update Commission Calculation Date
        end_date = self.cc_id.end_date
        doc_id = self.cc_id.doctor_id.id
        self.env['doctors.profile'].browse(doc_id).write({
            'last_commission_calculation_date': end_date
        })

        return self.id
