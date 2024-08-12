from odoo import api, models, fields
from datetime import datetime




class OpticsSalePayment(models.Model):
    _name = 'optics.sale.payment'
    _description = "optics sale Payment"


    def button_add_payment_action(self,cr,uid,ids,context=None):

        payment_obj=self.browse(cr,uid,ids,context=None)
        optics_sale_id=payment_obj.optics_sale_id.id
        optics_sale_name=payment_obj.optics_sale_id.name
        eve_mee_obj = self.pool.get('optics.sale.payment.line')
        pay_date=payment_obj.date
        pay_amount = payment_obj.amount
        pay_type = payment_obj.payment_type.name
        pay_card=payment_obj.account_number
        current_due =payment_obj.optics_sale_id.due
        current_paid =payment_obj.optics_sale_id.paid
        money_receipt_id =payment_obj.money_receipt_id.id


        updated_amount = current_due-pay_amount
        updated_paid = current_paid+pay_amount
        if updated_amount <0:
            updated_amount=0
        service_dict = {'date': pay_date, 'amount': pay_amount, 'type': pay_type, 'card_no': pay_card,
                        'optics_sale_payment_line_id': optics_sale_id, 'money_receipt_id': money_receipt_id}

        service_id = eve_mee_obj.create(cr, uid, vals=service_dict, context=context)

        cr.execute("update optics_sale set due=%s,paid=%s where id=%s", (updated_amount, updated_paid, optics_sale_id))
        cr.commit()

            ###journal_entry
        line_ids = []

        if context is None: context = {}
        if context.get('period_id', False):
            return context.get('period_id')
        periods = self.pool.get('account.period').find(cr, uid, context=context)
        period_id = periods and periods[0] or False
        payment_method = payment_obj.payment_type
        if payment_method.service_charge <= 0:
            has_been_paid = payment_obj.amount
            ar_amount=payment_obj.amount
        else:
            has_been_paid = payment_obj.to_be_paid
            ar_amount=payment_obj.amount
        ar_acc = 6099
        account = payment_obj.payment_type.account.id
        service_account = payment_obj.payment_type.service_charge_account.id

        if current_paid > 0:

            line_ids.append((0, 0, {
                'analytic_account_id': False,
                'tax_code_id': False,
                'tax_amount': 0,
                'name': optics_sale_name,
                'currency_id': False,
                'credit': 0,
                'date_maturity': False,
                'account_id': account,  ### Cash ID
                'debit': has_been_paid,
                'amount_currency': 0,
                'partner_id': False,
            }))
            if context is None:
                context = {}

            line_ids.append((0, 0, {
                'analytic_account_id': False,
                'tax_code_id': False,
                'tax_amount': 0,
                'name': optics_sale_name,
                'currency_id': False,
                'credit': ar_amount,
                'date_maturity': False,
                'account_id': ar_acc,  ### Accounts Receivable ID optics
                'debit': 0,
                'amount_currency': 0,
                'partner_id': False,
            }))
        if payment_obj.service_charge > 0:
            line_ids.append((0, 0, {
                'analytic_account_id': False,
                'tax_code_id': False,
                'tax_amount': 0,
                'name': optics_sale_name,
                'currency_id': False,
                'credit': payment_obj.service_charge,
                'date_maturity': False,
                'account_id': service_account,  ### Accounts Receivable ID optics
                'debit': 0,
                'amount_currency': 0,
                'partner_id': False,
            }))


        jv_entry = self.pool.get('account.move')

        j_vals = {'name': '/',
                  'journal_id': 2,  ## Sales Journal
                  'date': fields.date.today(),
                  'period_id': period_id,
                  'ref': optics_sale_name,
                  'line_id': line_ids

                  }

        # import pdb
        # pdb.set_trace()
        saved_jv_id = jv_entry.create(cr, uid, j_vals, context=context)
        if saved_jv_id > 0:
            journal_id = saved_jv_id
            try:
                jv_entry.button_validate(cr, uid, [saved_jv_id], context)
            except:
                import pdb
                pdb.set_trace()


        return service_id

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


    def create(self,cr,uid,vals,context):
        storedpayment = super(OpticsSalePayment, self).create(cr, uid, vals, context)  # return ID int object

        if storedpayment is not None:
            name_text = 'CC-100' + str(storedpayment)
            cr.execute('update optics_sale_payment set name=%s where id=%s', (name_text, storedpayment))
            cr.commit()
        value={}
        value['date']=vals['date']
        value['optics_sale_id']=vals['optics_sale_id']
        value['amount']=vals['amount']
        value['type']=vals['payment_type']
        value['p_type']='due_payment'
        # value['user_id']=vals['user_id']

        mr_object=self.pool.get("leih.money.receipt")
        mr_id=mr_object.create(cr, uid, value, context=context)

        stored_obj = self.pool.get("optics.sale").browse(cr, uid, vals['optics_sale_id'], context=None)

        ## Bill Status Will Change

        # if stored_obj.state == 'confirmed':
        #     raise osv.except_osv(_('Warning!'),
        #                          _('Already this Bill is Confirmed.'))
        grand_total = stored_obj.grand_total
        if grand_total != 0:
            cr.execute("update optics_sale set state='confirmed' where id=%s", ([vals['optics_sale_id']]))
            cr.commit()

            stored = int(vals['optics_sale_id'])

            ### check and merged with Lab report





        if mr_id is not None:
            mr_name='MR#' +str(mr_id)
            cr.execute('update leih_money_receipt set name=%s where id=%s',(mr_name,mr_id))
            cr.execute('update optics_sale_payment set money_receipt_id=%s where id=%s',(mr_id,storedpayment))
            cr.commit()
        return storedpayment

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
        return "X"