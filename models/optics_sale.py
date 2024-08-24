
from odoo import api, models, fields, _


class OpticsSale(models.Model):
    _name = "optics.sale"
    _description = "Optics Sales Entry"
    _order = 'id desc'

    # def _totalpayable(self):
    #     Percentance_calculation = {}
    #     sum = 0
    #     for items in self:
    #         total_list = []
    #         for amount in items.optics_sale_line_id:
    #             total_list.append(amount.total_amount)
    #         for item in total_list:
    #             sum = item + sum
    #             for record in self:
    #                 Percentance_calculation[record.id] = sum
    #     return Percentance_calculation

    def _default_payment_type(self):
         return self.env['payment.type'].search([('name', '=', 'Cash')], limit=1).id

    # 'patient_id= fields.Char("Patient ID"),
    name= fields.Char("Name")
    mobile= fields.Char(related='patient_name.mobile', string="Mobile", readonly=True)
    patient_id= fields.Char(related='patient_name.patient_id', string="Patient Id", readonly=True)
    patient_name= fields.Many2one('patient.info', "Patient Name", required=True, placeholder='Full Name')
    address= fields.Char("Address", placeholder='Address')
    age= fields.Char("Age")
    sex= fields.Char("Sex")
    right_eye_sph= fields.Char('Right Eye SPH')
    right_eye_cyl= fields.Char('Right Eye CYL')
    right_eye_axis= fields.Char('Right Eye AXIS')
    right_eye_sph_n= fields.Char('Right Eye SPH -N')
    right_eye_cyl_n= fields.Char('Right Eye CYL -N')
    right_eye_axis_n= fields.Char('Right Eye AXIS -N')
    left_eye_sph= fields.Char('Left Eye SPH')
    left_eye_cyl= fields.Char('Left Eye CYL')
    left_eye_axis= fields.Char('Left Eye AXIS')
    left_eye_sph_n= fields.Char('Left Eye SPH -N')
    left_eye_cyl_n= fields.Char('Left Eye CYL -N')
    left_eye_axis_n= fields.Char('Left Eye AXIS -N')
    delivery_date= fields.Date(string="Delivery Date")
    hard_cover= fields.Boolean("Cover", default=True)
    cell_pad= fields.Boolean("Cell Pad", default=True)
    frame_id= fields.Many2one('product.product', 'Frame')
    quantity =fields.Integer('Quantity')
    qty_available= fields.Integer(string="Stock Quantity")
    delivery_id =fields.Many2one('stock.picking', 'Delivery Challan')
    price= fields.Float(string='Price')
    optics_lens_sale_line_id= fields.One2many('optics.lens.sale.line', 'optics_sale_id', 'Lens Entry')
    optics_sale_payment_line_id= fields.One2many("optics.sale.payment.line", "optics_sale_payment_line_id",
                                                  "Bill Register Payment")
    # 'footer_connection= fields.One2many('leih.footer', 'relation', 'Parameters', required=True)
    # 'relation= fields.Many2one("leih.investigation")
    # 'total= fields.Float(_totalpayable,string="Total",type='float',store=True)
    total= fields.Float(string="Total")
    doctors_discounts= fields.Float("Discount(%)")
    after_discount= fields.Float("Discount Amount")
    other_discount= fields.Float("Other Discount")
    grand_total= fields.Float("Grand Total")
    paid= fields.Float(string="Paid", required=True)
    type= fields.Selection([('cash', 'Cash'), ('bank', 'Bank')], 'Payment Type')
    card_no= fields.Char('Card No.')
    bank_name= fields.Char('Bank Name')
    due= fields.Float("Due")
    date= fields.Datetime("Date", readonly=True, default=lambda self: fields.Datetime.now())
    state= fields.Selection(
        [('pending', 'Pending'), ('confirmed', 'Confirmed'), ('cancelled', 'Cancelled')],
        'Status', default='pending', readonly=True)
    # payment type attributes
    payment_type= fields.Many2one("payment.type", "Payment Type", default=_default_payment_type)
    service_charge= fields.Float("Service Charge")
    to_be_paid= fields.Float("To be Paid")
    account_number= fields.Char("Account Number")

    _defaults = {
        'quantity': 1
    }

    # @api.onchange("payment_type")
    # def onchnage_payment_type(self):
    #     if self.payment_type.active==True:
    #         interest=self.payment_type.service_charge
    #         if interest>0:
    #             service_charge=(self.paid*interest)/100
    #             self.service_charge=service_charge
    #             self.to_be_paid=self.paid+service_charge
    #         else:
    #             self.to_be_paid=self.paid
    #             self.service_charge=0
    #     return "X"
    #
    # def onchange_quantity(self,quantity=0,frame_id=1,):
    #     tests = {'values': {}}
    #     import pdb
    #     pdb.set_trace()
    #
    #     unit_price = frame_id.list_price
    #     total_price = unit_price * quantity
    #
    #     abc = {'price': total_price}
    #     tests['value'] = abc
    #     #
    #
    #     return tests
    #
    # @api.onchange('quantity')
    # def onchange_frame_bill_qty(self):
    #     frame_code = self.frame_id
    #     self.price = frame_code.list_price * self.quantity
    #     return 'X'

    def add_discount(self):
        return True

    def btn_pay_bill(self):
        # return True

        # inv = self.browse(self.id)
        # if inv.state == 'pending':
        #     raise models.except_models(_('Warning'), _('Please Confirm and Print the Optics Form'))
        # if inv.total == inv.paid:
        #     raise models.except_models(_('Full Paid'), _('Nothing to Pay Here. Already Full Paid'))
        # dummy, view_id = self.env.get('ir.model.data').get_object_reference('leih',
        #                                                                      'optics_sale_payment_form_view')
        #
        # total=inv.total
        view = self.env.ref('medical.optics_sale_payment_form_view')

        return {
            'name': _("Pay Invoice"),
            'view_mode': 'form',
            'view_id': view.id,
            'view_type': 'form',
            'res_model': 'optics.sale.payment',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
            'domain': '[]',
            'context': {
                'default_optics_sale_id': self.id,
                'default_amount': self.due
            }
        }
        raise models.except_models(_('Error!'), _('There is no default company for the current user!'))

    def btn_corporate_discount(self):
        return True

    def bill_confirm(self):
        return True

    #
    # # if same item exist in line
    # def bill_confirm(self):
    #     ids = [self.id]
    #     stored_obj = self.browse(cr, uid, [ids[0]], context=context)
    #     ## Bill Status Will Change
    #     stored = int(ids[0])
    #     if stored_obj.state == 'confirmed':
    #         raise models.except_models(_('Warning!'),
    #                              _('Already it is  Confirmed. You can not change.'))
    #     if stored_obj.paid != False:
    #         #### Create a challan
    #         picking_obj = self.pool.get('stock.picking')
    #         partner_obj = self.pool.get('res.partner')
    #         move_obj = self.pool.get('stock.move')
    #         for order in self.browse(context=context):
    #             picking_id = picking_obj.create(cr, uid, {
    #                 'origin': order.name,
    #                 'partner_id': False,
    #                 'date_done': stored_obj.date,
    #                 'picking_type_id': 13,  ## Hard Coded
    #                 # 'company_id': order.company_id.id,
    #                 'move_type': 'direct',
    #                 'note': "",
    #                 'invoice_state': 'none',
    #             }, context=context)
    #             self.write(cr, uid, [order.id], {'picking_id': picking_id}, context=context)
    #             location_id = 25  # Source Location from where stock will reduce
    #             destination_id = 9  ## Customer location
    #             move_list = []
    #             ## This is  for Fram3
    #             if order.frame_id:
    #                 move_list.append(move_obj.create(cr, uid, {
    #                     'name': order.name,
    #                     'product_uom': order.frame_id.uom_id.id,
    #                     'product_uos': order.frame_id.uom_id.id,
    #                     'picking_id': picking_id,
    #                     'picking_type_id': 13,
    #                     'product_id': order.frame_id.id,
    #                     'product_uos_qty': abs(order.quantity),
    #                     'product_uom_qty': abs(order.quantity),
    #                     'state': 'draft',
    #                     'location_id': location_id,
    #                     'location_dest_id': destination_id,
    #                 }, context=context))
    #             if order.hard_cover is True:
    #                 move_list.append(move_obj.create(cr, uid, {
    #                     'name': order.name,
    #                     'product_uom': 1,
    #                     'product_uos': 1,
    #                     'picking_id': picking_id,
    #                     'picking_type_id': 13,
    #                     'product_id': 187,  ## 187
    #                     'product_uos_qty': abs(1),
    #                     'product_uom_qty': abs(1),
    #                     'state': 'draft',
    #                     'location_id': location_id,
    #                     'location_dest_id': destination_id,
    #                 }, context=context))
    #             if order.cell_pad is True:
    #                 move_list.append(move_obj.create(cr, uid, {
    #                     'name': order.name,
    #                     'product_uom': 1,
    #                     'product_uos': 1,
    #                     'picking_id': picking_id,
    #                     'picking_type_id': 13,
    #                     'product_id': 188,  ## 188
    #                     'product_uos_qty': abs(1),
    #                     'product_uom_qty': abs(1),
    #                     'state': 'draft',
    #                     'location_id': location_id,
    #                     'location_dest_id': destination_id,
    #                 }, context=context))
    #             for opt_line in order.optics_lens_sale_line_id:
    #                 move_list.append(move_obj.create(cr, uid, {
    #                     'name': order.name,
    #                     'product_uom': 1,
    #                     'product_uos': 1,
    #                     'picking_id': picking_id,
    #                     'picking_type_id': 13,
    #                     'product_id': 190,  ## 190 This is  for lense product variant id
    #                     'product_uos_qty': abs(1),
    #                     'product_uom_qty': abs(1),
    #                     # 'product_uos_qty': abs(opt_line.qty),
    #                     # 'product_uom_qty': abs(opt_line.qty),
    #                     'state': 'draft',
    #                     'location_id': location_id,
    #                     'location_dest_id': destination_id,
    #                 }, context=context))
    #             if picking_id:
    #                 picking_obj.action_confirm(cr, uid, [picking_id], context=context)
    #                 picking_obj.force_assign(cr, uid, [picking_id], context=context)
    #                 picking_obj.action_done(cr, uid, [picking_id], context=context)
    #                 cr.execute("update optics_sale set delivery_id=%s where id=%s", (picking_id, ids[0]))
    #                 cr.commit()
    #         ### Ends Here
    #
    #         ###journal entry start
    #     if stored_obj:
    #         line_ids = []
    #
    #         if context is None: context = {}
    #         if context.get('period_id', False):
    #             return context.get('period_id')
    #         periods = self.pool.get('account.period').find(cr, uid, context=context)
    #         period_id = periods and periods[0] or False
    #         ar_amount = stored_obj.due
    #         payment_method=stored_obj.payment_type
    #         if payment_method.service_charge<=0:
    #             has_been_paid=stored_obj.paid
    #         else:
    #             has_been_paid=stored_obj.to_be_paid
    #         ar_acc=6099
    #         account=stored_obj.payment_type.account.id
    #         service_account=stored_obj.payment_type.service_charge_account.id
    #
    #
    #
    #         if ar_amount > 0:
    #             line_ids.append((0, 0, {
    #                 'analytic_account_id': False,
    #                 'tax_code_id': False,
    #                 'tax_amount': 0,
    #                 'name': stored_obj.name,
    #                 'currency_id': False,
    #                 'credit': 0,
    #                 'date_maturity': False,
    #                 'account_id': ar_acc,  ### Accounts Receivable ID
    #                 'debit': ar_amount,
    #                 'amount_currency': 0,
    #                 'partner_id': False,
    #             }))
    #
    #         if has_been_paid > 0:
    #             line_ids.append((0, 0, {
    #                 'analytic_account_id': False,
    #                 'tax_code_id': False,
    #                 'tax_amount': 0,
    #                 'name': stored_obj.name,
    #                 'currency_id': False,
    #                 'credit': 0,
    #                 'date_maturity': False,
    #                 'account_id': account,  ### Cash ID
    #                 'debit': has_been_paid,
    #                 'amount_currency': 0,
    #                 'partner_id': False,
    #             }))
    #
    #             if context is None:
    #                 context = {}
    #
    #         if stored_obj.total:
    #             line_ids.append((0, 0, {
    #                 'analytic_account_id': False,
    #                 'tax_code_id': False,
    #                 'tax_amount': 0,
    #                 'name': stored_obj.name,
    #                 'currency_id': False,
    #                 'account_id': 6098,  ##sepcticle income
    #                 'credit': stored_obj.total,
    #                 'date_maturity': False,
    #                 'debit': 0,
    #                 'amount_currency': 0,
    #                 'partner_id': False,
    #             }))
    #         if stored_obj.service_charge>0:
    #             line_ids.append((0, 0, {
    #                 'analytic_account_id': False,
    #                 'tax_code_id': False,
    #                 'tax_amount': 0,
    #                 'name': stored_obj.name,
    #                 'currency_id': False,
    #                 'account_id': service_account,  ##sepcticle income
    #                 'credit': stored_obj.service_charge,
    #                 'date_maturity': False,
    #                 'debit': 0,
    #                 'amount_currency': 0,
    #                 'partner_id': False,
    #             }))
    #
    #         jv_entry = self.pool.get('account.move')
    #
    #         j_vals = {'name': '/',
    #                   'journal_id': 2,  ## Sales Journal
    #                   'date': fields.Date.today(),
    #                   'period_id': period_id,
    #                   'ref': stored_obj.name,
    #                   'line_id': line_ids
    #                   }
    #
    #         saved_jv_id = jv_entry.create(cr, uid, j_vals, context=context)
    #         if saved_jv_id > 0:
    #             journal_id = saved_jv_id
    #             try:
    #                 jv_entry.button_validate(cr,uid, [saved_jv_id], context)
    #                 cr.execute("update optics_sale set state='confirmed' where id=%s", (ids))
    #                 cr.commit()
    #                 for bills_vals in stored_obj:
    #                     mr_value = {
    #                         'date': stored_obj.date,
    #                         'optics_sale_id': int(stored),
    #                         'amount': stored_obj.paid,
    #                         'type': stored_obj.type,
    #                         'p_type': 'advance',
    #                         'bill_total_amount': stored_obj.total,
    #                         'due_amount': stored_obj.due,
    #                     }
    #                 mr_obj = self.pool.get('leih.money.receipt')
    #                 mr_id = mr_obj.create(cr, uid, mr_value, context=context)
    #                 if mr_id is not None:
    #                     mr_name = 'MR#' + str(mr_id)
    #                     cr.execute('update leih_money_receipt set name=%s where id=%s', (mr_name, mr_id))
    #                     cr.commit()
    #             except:
    #                 import pdb
    #                 pdb.set_trace()
    #
    #         ###end journal entry
    #
    #
    #     else:
    #         raise models.except_models(_('Warning!'),
    #                              _('Minimum Payment is Required'))
    #     #journal for cogs
    #     stock_picking_obj = self.pool['stock.picking'].browse(cr, uid, [picking_id],context=context)[0]
    #     if len(stock_picking_obj)>0:
    #         lines_ids = []
    #
    #         for items in stock_picking_obj.move_lines:
    #             inv_value = 0
    #             for q_it in items.quant_ids:
    #                 inv_value = inv_value + abs(q_it.inventory_value)
    #                 break
    #                 # import pdb
    #                 # pdb.set_trace()
    #
    #             lines_ids.append((0, 0, {
    #                 'analytic_account_id': False,
    #                 'tax_code_id': False,
    #                 'tax_amount': 0,
    #                 'name': order.name,
    #                 'currency_id': False,
    #                 'credit': 0,
    #                 'date_maturity': False,
    #                 'account_id': items.product_id.categ_id.property_account_expense_categ.id,  ### Cash ID
    #                 'debit': abs(inv_value),
    #                 'amount_currency': 0,
    #                 'partner_id': False,
    #             }))
    #             lines_ids.append((0, 0, {
    #                 'analytic_account_id': False,
    #                 'tax_code_id': False,
    #                 'tax_amount': 0,
    #                 'name': order.name,
    #                 'currency_id': False,
    #                 'credit': abs(inv_value),
    #                 'date_maturity': False,
    #                 'account_id': items.product_id.categ_id.property_stock_account_output_categ.id,
    #                 ### Accounts Receivable ID
    #                 'debit': 0,
    #                 'amount_currency': 0,
    #                 'partner_id': False,
    #             }))
    #
    #
    #         jvv_entry = self.pool.get('account.move')
    #
    #
    #         nj_vals = {'name': '/',
    #                   'journal_id': 2,  ## Sales Journal
    #                   'date': fields.Date.today(),
    #                   'period_id': period_id,
    #                   'ref': order.name,
    #                   'line_id': lines_ids
    #
    #                   }
    #
    #         saved_jv_ids = jvv_entry.create(cr, uid, nj_vals, context=context)
    #
    #
    #     return self.pool['report'].get_action('leih.report_optics_sale', context=context)

    @api.onchange('patient_name')
    def onchange_patient(self):
        self.address = self.patient_name.address
        self.age = self.patient_name.age
        self.sex = self.patient_name.sex

    def bill_cancel(self):
        ## Bill Status Will Change
        # cr.execute("update optics_sale set state='cancelled' where id=%s", (ids))
        # cr.commit()
        return True

    def create(self, vals):
        stored = super(OpticsSale, self).create(vals)  # return ID int object
        if stored is not None:
            name_text = 'OPT- 1' + str(stored.id)
            stored.name = name_text

        return stored


    # def create(self, vals):
    #     f_prod_id = vals.get('frame_id')
    #     if f_prod_id:
    #         has_qty = False
    #         try:
    #             # f_prod_id = vals.get('frame_id')
    #             p_obj = self.pool['product.product'].browse(cr, uid, [f_prod_id], context=context)
    #             if p_obj.qty_available > 0:
    #                 has_qty = True
    #         except:
    #             pass
    #         if has_qty == False:
    #             raise models.except_models(_('Warning!'),
    #                                  _('Stock is not available'))
    #     if context is None:
    #         context = {}
    #     stored = super(OpticsSale, self).create(cr, uid, vals, context)  # return ID int object
    #     if stored is not None:
    #         name_text = 'OPT- 0' + str(stored)
    #         cr.execute('update optics_sale set name=%s where id=%s', (name_text, stored))
    #         cr.commit()
    #     return stored

    def write(self, vals):
        return super(OpticsSale, self).write(vals)

    @api.onchange('price', 'optics_lens_sale_line_id')
    def onchange_lens_bill(self):
        sum_all = 0
        if self.price or self.optics_lens_sale_line_id:
            for item in self.optics_lens_sale_line_id:
                sum_all += item.total_amount
        self.total = sum_all + self.price
        self.due = sum_all - self.paid + self.price


    @api.onchange('frame_id')
    def onchange_frame_id(self):
        self.price = self.frame_id.list_price
        self.qty_available = self.frame_id.qty_available

    # @api.onchange('paid')
    # def onchange_paid(self):
    #     self.due = self.total - self.paid
    #     if self.payment_type:
    #         if self.payment_type.name=='Visa Card':
    #             interest = self.payment_type.service_charge
    #             service_charge = (self.paid * interest) / 100
    #             self.service_charge = service_charge
    #             self.to_be_paid = self.paid + service_charge
    #     return 'x'
    #
    # @api.onchange('price')
    # def onchange_price(self):
    #     sumalltest = 0
    #     for item in self.optics_lens_sale_line_id:
    #         sumalltest = sumalltest + item.total_amount
    #     self.total = self.price + sumalltest
    #     self.due = self.price + sumalltest - self.paid
    #     return 'x'
    #
    # # @api.onchange('doctors_discounts')
    # # def onchange_doc_discount(self):
    # #     aft_discount = (self.total * (self.doctors_discounts / 100))
    # #     self.after_discount = aft_discount
    # #     self.grand_total = self.total - aft_discount - self.other_discount
    # #     self.due = self.total - aft_discount - self.other_discount - self.paid
    # #
    # #     return "X"
    # @api.onchange('other_discount')
    # def onchange_other_discount(self):
    #     self.grand_total = self.total - self.after_discount - self.other_discount
    #     self.due = self.total - self.after_discount - self.other_discount - self.paid
    #     return 'True'



class OpticsLensInformation(models.Model):
    _name = 'optics.lens.sale.line'
    _description = "Optics Lens Sale Line Entry"

    name= fields.Many2one("product.lens", "Lens Name", ondelete='cascade')
    product_id= fields.Many2one('product.product', "Lens Name")
    optics_sale_id= fields.Many2one('optics.sale', "Information")
    price= fields.Integer("Unit Price")
    qty= fields.Integer("Quantity")
    total_amount= fields.Integer("Total Amount")

    @api.onchange('price', 'qty')
    def onchange_lens_bill(self):
        if self.price or self.qty:
            self.total_amount = self.price * self.qty





# end of the process of lance
class OpticsSalePaymentLine(models.Model):
    _name = 'optics.sale.payment.line'
    _description = "Optics Sale Payment Line Entry"

    optics_sale_payment_line_id= fields.Many2one('optics.sale', 'bill register payment')
    date= fields.Datetime("Date")
    amount= fields.Float('Amount')
    type= fields.Char('Type')
    card_no= fields.Char('Card Number')
    bank_name= fields.Char('Bank Name')
    money_receipt_id= fields.Many2one('leih.money.receipt', 'Money Receipt ID')
