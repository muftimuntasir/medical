from odoo import api, models, fields

class advance_cash(models.Model):
    _name = "advance.cash"



    date= fields.Date('Date')
    name= fields.Char("Cash No.")
    purpose=fields.Char("Purpose",required=True)
    amount=fields.Float("Amount",required=True)
    journal_id=fields.Many2one('account.move', 'Journal ')
    credit_accounts=fields.Many2one("account.account", "Cash/Bank Account")
    debit_accounts=fields.Many2one("account.account", "Advance Account")
    partner_id=fields.Many2one('res.partner','Partner Name',required=True)
    state= fields.Selection(
        [('pending', 'Pending'), ('confirmed', 'Confirmed'), ('cancelled', 'Cancelled')],
        'Status', default='pending', readonly=True)




    def confirm_transfer(self, cr, uid, ids, context=None):

        ## start create journal from here
        cc_ids = ids
        for id in cc_ids:
            ids = [id]
            cc_obj = self.browse(cr, uid, ids, context=context)
            if cc_obj.state == 'confirmed':
                raise osv.except_osv(_('Already Confirmed'), _('Sorry, it is already confirmed'))
            else:
                ## start create journal from here

                if context is None: context = {}
                if context.get('period_id', False):
                    return context.get('period_id')
                periods = self.pool.get('account.period').find(cr, uid, context=context)
                period_id = periods and periods[0] or False

                if context is None:
                    context = {}

                line_ids = []
                cc_obj = self.browse(cr, uid, ids, context=context)

                line_ids.append((0, 0, {
                    'name': cc_obj.purpose,
                    'partner_id': cc_obj.partner_id.id,
                    'account_id': cc_obj.debit_accounts.id,
                    'debit': cc_obj.amount,
                }))

                line_ids.append((0, 0, {
                    'name': cc_obj.purpose,
                    'partner_id': cc_obj.partner_id.id,
                    'account_id': cc_obj.credit_accounts.id,
                    'credit': cc_obj.amount,
                }))

                j_vals = {'name': '/',
                          'journal_id': 10,  ## Advance Cash Journal
                          'date': fields.Date.today(),
                          'period_id': period_id,
                          'ref': cc_obj.name,
                          'line_id': line_ids

                          }

                jv_entry = self.pool.get('account.move')

                saved_jv_id = jv_entry.create(cr, uid, j_vals, context=context)
                if saved_jv_id > 0:
                    journal_id = saved_jv_id
                jv_entry.button_validate(cr, uid, [saved_jv_id], context)

                ## Ends here

                confirm_cash_collection_query = "UPDATE advance_cash SET state='confirmed',journal_id={0} WHERE id={1}".format(
                    saved_jv_id, id)
                cr.execute(confirm_cash_collection_query)
                cr.commit()

        return True

