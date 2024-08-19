from odoo import api, models, fields

class leih_admission(models.Model):
    _name = "leih.admission"
    _order = 'id desc'




    def _totalpayable(self, cr, uid, ids, field_name, arg, context=None):
        Percentance_calculation = {}
        sum = 0
        for items in self.pool.get("leih.admission").browse(cr,uid,ids,context=None):
            total_list=[]
            for amount in items.leih_admission_line_id:
                total_list.append(amount.total_amount)

            for item in total_list:
                sum=item+sum


                for record in self.browse(cr, uid, ids, context=context):
                    Percentance_calculation[record.id] = sum
                    # import pdb
                    # pdb.set_trace()
        return Percentance_calculation
    def _default_payment_type(self):
         return self.env['payment.type'].search([('name', '=', 'Cash')], limit=1).id



    name=fields.Char("Name")
    mobile= fields.Char(string="Mobile",store=False)
    patient_id= fields.Char(related='patient_name.patient_id',string="Patient Id")
    patient_name= fields.Many2one('patient.info', "Patient Name")
    address= fields.Char("Address",store=False)
    age= fields.Char("Age",store=False)
    sex=fields.Char("Sex",store=False)
    ref_doctors= fields.Many2one('doctors.profile','Reffered by')
    operation_date= fields.Date("Operation Date")
    release_note= fields.Text("Release Note")
    package_name= fields.Many2one("examine.package", string="Package")
    leih_admission_line_id= fields.One2many('leih.admission.line', 'leih_admission_id', 'Investigations')
    guarantor_line_id=fields.One2many("patient.guarantor","admission_id","Guarantor Name")
    bill_register_admission_line_id= fields.One2many("bill.register.admission.line","admission_line_id","Bill Register")
    admission_payment_line_id= fields.One2many("admission.payment.line","admission_payment_line_id","Admission Payment")
    admission_journal_relation_id= fields.One2many("bill.journal.relation", "admission_journal_relation_id", "Journal")
    emergency=fields.Boolean("Emergency Department")
    total_without_discount= fields.Float(string="Total without discount")
    total= fields.Float(string="Total")
    doctors_discounts= fields.Float("Discount(%)")
    after_discount= fields.Float("Discount Amount")
    other_discount= fields.Float("Other Discount")
    grand_total= fields.Float("Grand Total")
    advance=fields.Float("Advance")
    paid= fields.Float("Paid")
    due= fields.Float("Due")
    type= fields.Selection([('cash', 'Cash'), ('bank', 'Bank')], 'Payment Type')
    card_no= fields.Char('Card No.')
    bank_name= fields.Char('Bank Name')
    date= fields.Datetime("Date", readonly=True, default=lambda self: fields.datetime.now())
    ser_id= fields.Many2one('res.users', 'Assigned to', select=True, track_visibility='onchange')
    state= fields.Selection(
        [('pending', 'Pending'),('activated', 'Admitted'), ('released', 'Released'), ('cancelled', 'Cancelled')],
        'Status',default='pending', readonly=True,
    )
    emergency_covert_time=fields.Datetime("Admission Convert time")
    old_journal=fields.Boolean("Old Journal")
    payment_type= fields.Many2one("payment.type", "Payment Type", default=_default_payment_type)
    service_charge= fields.Float("Service Charge")
    to_be_paid= fields.Float("To be Paid")
    account_number= fields.Char("Account Number")
    father_name=fields.Char("Father's Name")
    mother_name=fields.Char("Mother's Name")
    religion=fields.Selection([('islam', 'Islam'), ('hindu', 'Hinduism'),('buddhism','Buddhism'),('christianity','Christianity')], 'Religion')
    blood_group= fields.Char('Blood Group')
    reffered_to_hospital= fields.Many2one('brokers.info', 'Referred to this hospital by')
    occupation=fields.Char('Occupation')
    business_address=fields.Char('Business Address')
    admitting_doctor=fields.Many2one('doctors.profile','Admitting Doctor')
    bed=fields.Char('Bed')
    received_by=fields.Char('Received/Registered By')
    clinic_diagnosis=fields.Char('Clinical Diagnosis')
    discount_remarks=fields.Char('Discount Remarks')



    _defaults = {
        'user_id': lambda obj, cr, uid, context: uid,
    }
    @api.onchange("payment_type")
    def onchnage_payment_type(self):
        if self.payment_type.active==True:
            interest=self.payment_type.service_charge
            if interest>0:
                service_charge=(self.paid*interest)/100
                self.service_charge=service_charge
                self.to_be_paid=self.paid+service_charge
            else:
                self.to_be_paid=self.paid
                self.service_charge=0
        return "X"

    @api.multi
    def amount_to_text(self, amount, currency='Bdt'):
        text = amount_to_text(amount, currency)
        new_text = text.replace("euro", "Taka")
        # initializing sub string
        sub_str = "Taka"
        final_text = new_text[:new_text.index(sub_str) + len(sub_str)]


        # final_text = new_text.replace("Cent", "Paisa")
        return final_text


    @api.multi
    def advance_paid(self,name):
        mr = self.env['leih.money.receipt'].search([('admission_id', '=', name)])
        advance = 0
        paid = 0
        if len(mr)>2:
            for i in range(len(mr)-1):
                advance=advance+mr[i].amount
            paid=mr[len(mr)-1].amount
        # mr_ids=self.pool.get('leih.money.receipt').search([('bill_id', '=', name)], context=context)

            lists={
                'advance':advance,
                'paid':paid
            }
        elif len(mr)==2:
            advance = advance + mr[0].amount
            paid = paid + mr[1].amount
            lists={
                'advance':advance,
                'paid':paid
            }
        elif len(mr)==1:
            advance = advance + mr[0].amount
            lists={
                'advance':advance,
                'paid':0
            }
        elif len(mr)==0:
            advance = advance
            lists={
                'advance':advance,
                'paid':0
            }

        # final_text = new_text.replace("Cent", "Paisa")
        return lists



    # def print_bill_register(self, cr, uid, ids, context=None):
    #     '''
    #     This function prints the sales order and mark it as sent, so that we can see more easily the next step of the workflow
    #     '''
    #     assert len(ids) == 1, 'This option should only be used for a single id at a time'
    #
    #     return self.pool['report'].get_action(cr, uid, ids, 'sale.report_saleorder', context=context)

    def onchange_patient(self,cr,uid,ids,name,context=None):
        tests={}
        dep_object = self.pool.get('patient.info').browse(cr, uid, name, context=None)
        abc={'mobile':dep_object.mobile,'address':dep_object.address,'age':dep_object.age,'sex':dep_object.sex}
        tests['value']=abc
        return tests

    # def _package_fields(self, cr, uid, context=None):
    #     return list(PACKAGE_FIELDS)

    # def onchange_mobile(self,cr,uid,ids,mobile,context=None):
    #     tests={'values':{}}
    #     patient_id=self.pool.get('patient.info').search(cr,uid,[('mobile', '=', mobile)],context=None)
    #     dep_object=self.pool.get('patient.info').browse(cr,uid,patient_id,context)
    #     abc = {'patient': dep_object.name, 'address': dep_object.address, 'age': dep_object.age, 'sex': dep_object.sex}
    #     tests['value']=abc
    #     return tests

        #
        # import pdb
        # pdb.set_trace()

    def onchange_package(self,cr,uid,ids,package_name,vals,context=None):
        values={}
        if not package_name:
            return {}
        total_amount = 0.0
        abc={'leih_admission_line_id':[]}
        package_object=self.pool.get('examine.package').browse(cr,uid,package_name,context=None)
        abc['other_discount'] = package_object.total_without_discount -package_object.total

        for item in package_object.examine_package_line_id:
            items=item.name.id

            total_amount = total_amount + item.total_amount



            abc['leih_admission_line_id'].append([0, False, {'name':item.name.id,'total_amount':item.total_amount,'price':item.price,'flat_discount':item.discount}])
        values['value']=abc

        return values


    def change_status(self, cr, uid, ids, context=None):
        stored_obj = self.browse(cr, uid, [ids[0]], context=context)
        journal_object = self.pool.get("bill.journal.relation")
        ## Bill Status Will Change

        if stored_obj.state == 'activated':
            raise osv.except_osv(_('Warning!'),
                                 _('Already this Bill is Confirmed.'))

        stored = int(ids[0])


        ### check and merged with Lab report

        get_all_tested_ids = []

        for items in stored_obj.leih_admission_line_id:
            get_all_tested_ids.append(items.name.id)

        ### Ends here merged Section

        already_merged = []
        custom_name = ''

        for items in stored_obj.leih_admission_line_id:
            custom_name = ''
            state = 'sample'
            ### Create LAB/SAMPLE From Here
            if items.name.sample_req == False or items.name.sample_req == None:
                state = 'lab'
            if items.name.indoor==True:
                state='indoor'

            if items.name.manual != True or items.name.lab_not_required != True:

                custom_name = custom_name + ' ' + str(items.name.name)

                if items.name.id not in already_merged:

                    child_list = []
                    value = {
                        'admission_id': int(stored),
                        'test_id': int(items.name.id),
                        'department_id': items.name.department.name,
                        'state': state
                    }

                    for test_item in items.name.examination_entry_line:
                        tmp_dict = {}
                        tmp_dict['test_name'] = test_item.name
                        tmp_dict['ref_value'] = test_item.reference_value
                        tmp_dict['bold'] = test_item.bold
                        tmp_dict['group_by'] = test_item.group_by
                        child_list.append([0, False, tmp_dict])

                    if items.name.merge == True:

                        for entry in items.name.merge_ids:
                            test_id = entry.examinationentry_id.id

                            if test_id in get_all_tested_ids:
                                custom_name = custom_name + ', ' + str(entry.examinationentry_id.name)
                                already_merged.append(test_id)
                                for m_test_line in entry.examinationentry_id.examination_entry_line:
                                    tmp_dict = {}
                                    tmp_dict['test_name'] = m_test_line.name
                                    tmp_dict['ref_value'] = m_test_line.reference_value
                                    tmp_dict['bold'] = m_test_line.bold
                                    tmp_dict['group_by'] = m_test_line.group_by
                                    child_list.append([0, False, tmp_dict])

                    value['sticker_line_id'] = child_list

                    value['full_name'] = custom_name

                    sample_obj = self.pool.get('diagnosis.sticker')
                    sample_id = sample_obj.create(cr, uid, value, context=context)

                ### Ends Here LAB/SAMPLE From Here

                if sample_id is not None:
                    sample_text = 'Lab-0' + str(sample_id)
                    cr.execute('update diagnosis_sticker set name=%s where id=%s', (sample_text, sample_id))
                    cr.commit()

        has_been_paid = 0
            ### Journal ENtry will be here
        if stored_obj:
            line_ids = []

            if context is None: context = {}
            if context.get('period_id', False):
                return context.get('period_id')
            periods = self.pool.get('account.period').find(cr, uid, context=context)
            period_id = periods and periods[0] or False
            # if mehtod is cash
            if stored_obj.payment_type.name == 'Cash':
                has_been_paid = stored_obj.paid
                ar_amount = stored_obj.due
                account_id = 6
            elif stored_obj.payment_type.name == 'Visa Card':
                has_been_paid = stored_obj.to_be_paid
                ar_amount = stored_obj.due
                account_id = stored_obj.payment_type.account.id

            if ar_amount > 0:
                line_ids.append((0, 0, {
                    'analytic_account_id': False,
                    'tax_code_id': False,
                    'tax_amount': 0,
                    'name': stored_obj.name,
                    'currency_id': False,
                    'credit': 0,
                    'date_maturity': False,
                    'account_id': 195,  ### Accounts Receivable ID
                    'debit': ar_amount,
                    'amount_currency': 0,
                    'partner_id': False,
                }))

            if has_been_paid > 0:
                line_ids.append((0, 0, {
                    'analytic_account_id': False,
                    'tax_code_id': False,
                    'tax_amount': 0,
                    'name': stored_obj.name,
                    'currency_id': False,
                    'credit': 0,
                    'date_maturity': False,
                    'account_id': account_id,  ### Cash ID
                    'debit': has_been_paid,
                    'amount_currency': 0,
                    'partner_id': False,
                }))

            for cc_obj in stored_obj.leih_admission_line_id:
                ledger_id = 611
                try:
                    ledger_id = cc_obj.name.accounts_id.id
                except:
                    ledger_id = 611  ## Diagnostic Income Head , If we don't assign any Ledger

                if context is None:
                    context = {}

                line_ids.append((0, 0, {
                    'analytic_account_id': False,
                    'tax_code_id': False,
                    'tax_amount': 0,
                    'name': cc_obj.name.name,
                    'currency_id': False,
                    'account_id': cc_obj.name.accounts_id.id,
                    'credit': cc_obj.total_amount,
                    'date_maturity': False,
                    'debit': 0,
                    'amount_currency': 0,
                    'partner_id': False,
                }))
            if stored_obj.service_charge > 0:
                line_ids.append((0, 0, {
                    'analytic_account_id': False,
                    'tax_code_id': False,
                    'tax_amount': 0,
                    'name': stored_obj.payment_type.name,
                    'currency_id': False,
                    'credit': stored_obj.service_charge,
                    'date_maturity': False,
                    'account_id': stored_obj.payment_type.service_charge_account.id,  ### Cash ID
                    'debit': 0,
                    'amount_currency': 0,
                    'partner_id': False,
                }))

            jv_entry = self.pool.get('account.move')

            j_vals = {'name': '/',
                      'journal_id': 2,  ## Sales Journal
                      'date': stored_obj.date,
                      'period_id': period_id,
                      'ref': stored_obj.name,
                      'line_id': line_ids

                      }
            # import pdb
            # pdb.set_trace()

            saved_jv_id = jv_entry.create(cr, uid, j_vals, context=context)
            if saved_jv_id > 0:
                journal_id = saved_jv_id
                try:
                    jv_entry.button_validate(cr, uid, [saved_jv_id], context)
                    cr.execute("update leih_admission set state='activated' where id=%s", (ids))
                    cr.commit()
                    journal_dict = {'journal_id': journal_id, 'admission_journal_relation_id': stored_obj.id}
                    journal_object.create(cr, uid, vals=journal_dict, context=context)
                    if stored_obj.paid != False:
                        ad_vals = {
                            'date': stored_obj.date,
                            'admission_id': stored_obj.id,
                            'amount': stored_obj.paid,
                            'type': stored_obj.type,
                            'p_type': 'advance',
                            'bill_total_amount': stored_obj.total,
                            'due_amount': stored_obj.due,
                        }
                        has_been_paid = stored_obj.paid
                        mr_obj = self.pool.get('leih.money.receipt')
                        mr_id = mr_obj.create(cr, uid, ad_vals, context=context)
                        if mr_id is not None:
                            mr_name = 'MR#' + str(mr_id)
                            cr.execute('update leih_money_receipt set name=%s where id=%s', (mr_name, mr_id))
                            cr.commit()
                            admission_payment_obj = self.pool.get('admission.payment.line')
                            service_dict = {'date': stored_obj.date, 'amount': stored_obj.paid,
                                            'type': stored_obj.payment_type.name,
                                            'admission_payment_line_id': stored_obj.id,
                                            'money_receipt_id': mr_id}
                            bill_payment_id = admission_payment_obj.create(cr, uid, vals=service_dict, context=context)
                except:
                    import pdb
                    pdb.set_trace()
            ###close here

        return self.pool['report'].get_action(cr, uid, ids, 'leih.report_admission', context=context)


    def admission_cancel(self, cr, uid, ids, context=None):

        #unlink journal items
        cr.execute("select  id as jounral_id from account_move where ref = (select name from leih_admission where id=%s limit 1)",(ids))
        joural_ids = cr.fetchall()
        context = context

        itm = [itm[0] for itm in joural_ids]
        if len(itm) > 0:
            uid = 1
            moves = self.pool.get('account.move').browse(cr, uid, itm, context=context)
            moves.button_cancel()  ## Cancelling
            moves.unlink()  ### Deleting Journal
        ## Bill Status Will Change

        cr.execute("update leih_admission set state='cancelled' where id=%s", (ids))
        cr.commit()
        ## Lab WIll be Deleted

        # cr.execute("update diagnosis_sticker set state='cancel' where bill_register_id=%s", (ids))
        # cr.commit()

        #for updates on cash collection
        cr.execute("update leih_money_receipt set state='cancel' where admission_id=%s", (ids))
        cr.commit()
        return True



    def add_new_test(self, cr, uid, ids, context=None):
        if not ids: return []

        dummy, view_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'leih', 'add_bill_view')
        #
        inv = self.browse(cr, uid, ids[0], context=context)
        # import pdb
        # pdb.set_trace()
        return {
            'name':_("Pay Invoice"),
            'view_mode': 'form',
            'view_id': view_id,
            'view_type': 'form',
            'res_model': 'add.bill',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
            'domain': '[]',
            'context': {
                'leih_admission_id': ids[0]

                # 'default_partner_id': self.pool.get('res.partner')._find_accounting_partner(inv.partner_id).id,
                # 'default_amount': inv.type in ('out_refund', 'in_refund') and -inv.residual or inv.residual,
                # 'default_reference': inv.name,
                # 'close_after_process': True,
                # 'invoice_type': inv.type,
                # 'invoice_id': inv.id,
                # 'default_type': inv.type in ('out_invoice','out_refund') and 'receipt' or 'payment',
                # 'type': inv.type in ('out_invoice','out_refund') and 'receipt' or 'payment'
            }
        }
        raise osv.except_osv(_('Error!'), _('There is no default company for the current user!'))

    def btn_final_settlement(self, cr, uid, ids, context=None):
        if not ids: return []

        dummy, view_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'leih', 'admission_release_view')
        #
        inv = self.browse(cr, uid, ids[0], context=context)
        total=inv.total
        # import pdb
        # pdb.set_trace()
        return {
            'name':_("Pay Invoice"),
            'view_mode': 'form',
            'view_id': view_id,
            'view_type': 'form',
            'res_model': 'admission.release',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
            'domain': '[]',
            'context': {
                'default_total':total,
                'default_admission_id': ids[0]

            }
        }
        raise osv.except_osv(_('Error!'), _('There is no default company for the current user!'))


    def btn_pay(self, cr, uid, ids, context=None):
        if not ids: return []

        inv = self.browse(cr, uid, ids[0], context=context)
        if inv.state == 'pending' or inv.state=='cancelled':
            raise osv.except_osv(_('Warning'), _('Please Confirm and Print the Bill'))
        if inv.total <= inv.paid:
            raise osv.except_osv(_('Full Paid'), _('Nothing to Pay Here. Already Full Paid'))

        dummy, view_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'leih', 'admission_payment_form_view')
        #

        # total=inv.total
        # import pdb
        # pdb.set_trace()
        return {
            'name':_("Pay Invoice"),
            'view_mode': 'form',
            'view_id': view_id,
            'view_type': 'form',
            'res_model': 'admission.payment',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
            'domain': '[]',
            'context': {
                'default_admission_id': ids[0],
                'default_amount': inv.due
            }
        }
        raise osv.except_osv(_('Error!'), _('There is no default company for the current user!'))


    def add_discount(self,cr,uid,ids,context=None):
        # import pdb
        # pdb.set_trace()
        if not ids: return []

        dummy, view_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'leih', 'discount_view')
        #
        inv = self.browse(cr, uid, ids[0], context=context)
        # import pdb
        # pdb.set_trace()
        return {
            'name': _("Pay Invoice"),
            'view_mode': 'form',
            'view_id': view_id,
            'view_type': 'form',
            'res_model': 'discount',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
            'domain': '[]',
            'context': {
                'pi_id':ids[0]
                # 'default_price': 500,
                # # 'default_name':context.get('name', False),
                # 'default_total_amount': 200,
                # 'default_partner_id': self.pool.get('res.partner')._find_accounting_partner(inv.partner_id).id,
                # 'default_amount': inv.type in ('out_refund', 'in_refund') and -inv.residual or inv.residual,
                # 'default_reference': inv.name,
                # 'close_after_process': True,
                # 'invoice_type': inv.type,
                # 'invoice_id': inv.id,
                # 'default_type': inv.type in ('out_invoice','out_refund') and 'receipt' or 'payment',
                # 'type': inv.type in ('out_invoice','out_refund') and 'receipt' or 'payment'
            }
        }
        raise osv.except_osv(_('Error!'), _('There is no default company for the current user!'))


    def create(self, cr, uid, vals, context=None):
        if vals.get("due"):
            if vals.get("due")<0:
                raise osv.except_osv(_('Warning!'),
                                     _("Check paid and grand total!"))

        if context is None:
            context = {}
        # import pdb
        # pdb.set_trace()
        stored = super(leih_admission, self).create(cr, uid, vals, context)  # return ID int object

        if vals.get("emergency")==False:


            if stored is not None:
                name_text = 'A-0' + str(stored)
                cr.execute('update leih_admission set name=%s where id=%s', (name_text, stored))
                cr.commit()
        else:
            if stored is not None:
                name_text = 'E-0' + str(stored)
                cr.execute('update leih_admission set name=%s where id=%s', (name_text, stored))
                cr.commit()


        return stored

    def write(self, cr, uid, ids,vals,context=None):
        if vals.get("due"):
            if vals.get("due")<0:
                raise osv.except_osv(_('Warning!'),
                                     _("Check paid and grand total!"))

        if vals.get('leih_admission_line_id') or uid == 1:
            cr.execute("select id as journal_ids from account_move where ref = (select name from leih_admission where id=%s limit 1)",(ids))
            journal_ids = cr.fetchall()
            context=context


            itm = [itm[0] for itm in journal_ids]

            if len(itm)>0:

                uid=1
                moves =self.pool.get('account.move').browse(cr, uid, itm, context=context)
                xx=moves.button_cancel() ## Cancelling
                bill_journal_id=[]
                # cr.execute("delete from bill_journal_relation where id in (select id from bill_journal_relation where journal_id in %s)",(tuple(itm)))
                user_q="select id from bill_journal_relation where journal_id in %s"
                # cr.execute("select id from bill_journal_relation where journal_id in %s",(tuple(itm)))
                cr.execute(user_q, (tuple(itm),))
                journal_id = cr.fetchall()
                for item in journal_id:
                    bill_journal_id.append(item[0])

                if len(bill_journal_id)>0:
                    query="delete from bill_journal_relation where id in %s"
                    cr.execute(query,(tuple(bill_journal_id),))

                moves.unlink()
                updated=super(leih_admission, self).write(cr, uid, ids, vals, context=context)
                stored_obj = self.browse(cr, uid, [ids[0]], context=context)
                journal_object = self.pool.get("bill.journal.relation")
                has_been_paid = stored_obj.paid
                if stored_obj:
                    line_ids = []

                    if context is None: context = {}
                    if context.get('period_id', False):
                        return context.get('period_id')
                    periods = self.pool.get('account.period').find(cr, uid, context=context)
                    period_id = periods and periods[0] or False
                    ar_amount = stored_obj.due

                    if ar_amount > 0:
                        line_ids.append((0, 0, {
                            'analytic_account_id': False,
                            'tax_code_id': False,
                            'tax_amount': 0,
                            'name': stored_obj.name,
                            'currency_id': False,
                            'credit': 0,
                            'date_maturity': False,
                            'account_id': 195, ### Accounts Receivable ID
                            'debit': ar_amount,
                            'amount_currency': 0,
                            'partner_id': False,
                        }))

                    if has_been_paid > 0:
                        line_ids.append((0, 0, {
                            'analytic_account_id': False,
                            'tax_code_id': False,
                            'tax_amount': 0,
                            'name': stored_obj.name,
                            'currency_id': False,
                            'credit': 0,
                            'date_maturity': False,
                            'account_id': 6,  ### Cash ID
                            'debit': has_been_paid,
                            'amount_currency': 0,
                            'partner_id': False,
                        }))

                    for cc_obj in stored_obj.leih_admission_line_id:
                        ledger_id=611
                        try:
                            ledger_id = cc_obj.name.accounts_id.id
                        except:
                            ledger_id= 611 ## Diagnostic Income Head , If we don't assign any Ledger



                        if context is None:
                            context = {}

                        line_ids.append((0, 0, {
                            'analytic_account_id': False,
                            'tax_code_id': False,
                            'tax_amount': 0,
                            'name': cc_obj.name.name,
                            'currency_id': False,
                            'account_id': cc_obj.name.accounts_id.id,
                            'credit': cc_obj.total_amount,
                            'date_maturity': False,
                            'debit': 0,
                            'amount_currency': 0,
                            'partner_id': False,
                        }))




                    jv_entry = self.pool.get('account.move')

                    j_vals = {'name': '/',
                              'journal_id': 2,  ## Sales Journal
                              'date': stored_obj.date,
                              'period_id': period_id,
                              'ref': stored_obj.name,
                              'line_id': line_ids

                              }

                    saved_jv_id = jv_entry.create(cr, uid, j_vals, context=context)
                    if saved_jv_id > 0:
                        journal_id = saved_jv_id
                        try:
                            jv_entry.button_validate(cr,uid, [saved_jv_id], context)
                            journal_dict={'journal_id':journal_id,'admission_journal_relation_id':stored_obj.id}
                            journal_object.create(cr,uid,vals=journal_dict,context=context)
                        except:
                            import pdb
                            pdb.set_trace()
                            # pass
                    return updated
                    ### Ends the journal Entry Here
            else:
                updated = super(leih_admission, self).write(cr, uid, ids, vals, context=context)
                # raise osv.except_osv(_('Warning!'),
                #                      _("You cannot Edit the bill"))
                return updated



    @api.onchange('leih_admission_line_id')
    def onchange_admission_line(self):
        sumalltest=0
        total_without_discount = 0
        for item in self.leih_admission_line_id:
            sumalltest=sumalltest+item.total_amount
            total_without_discount = total_without_discount + item.price

        self.total=sumalltest
        after_dis = (sumalltest* (self.doctors_discounts/100))
        self.after_discount = 0

        self.grand_total = sumalltest
        self.due = sumalltest - self.paid
        self.total_without_discount = total_without_discount

        return "X"

    @api.onchange('paid')
    def onchange_paid(self):
        self.due = self.grand_total - self.paid
        if self.payment_type:
            if self.payment_type.name=='Visa Card':
                interest = self.payment_type.service_charge
                service_charge = (self.paid * interest) / 100
                self.service_charge = service_charge
                self.to_be_paid = self.paid + service_charge
        return 'x'

    @api.onchange('doctors_discounts')
    def onchange_doc_discount(self):
        discount = self.doctors_discounts


        for item in self.leih_admission_line_id:
            item.discount_percent=round((item.price*discount)/100)
            item.discount=discount
            item.total_discount = item.flat_discount + item.discount_percent
            item.total_amount = item.price - item.total_discount

        return "X"

    @api.onchange('other_discount')
    def onchange_other_discount(self):
        other_discount = self.other_discount
        total = self.total_without_discount
        gd = total - other_discount
        line_total = 0
        if total > 0:
            discount_distribution = other_discount / total
            for item in self.leih_admission_line_id:
                item.flat_discount = 0
                item.flat_discount = round(item.price * discount_distribution)
                item.total_discount = item.flat_discount + item.discount_percent
                item.total_amount = item.price - item.total_discount
                line_total = line_total + item.total_amount
            if line_total < gd:
                item.total_amount = item.total_amount + (gd - line_total)
                item.flat_discount = item.flat_discount - (gd - line_total)
                item.total_discount = item.flat_discount + item.discount_percent
            if gd < line_total:
                item.total_amount = item.total_amount - (line_total - gd)
                item.flat_discount = item.flat_discount + (line_total - gd)
        return 'Nothing'


class test_information(models.Model):
    _name = 'leih.admission.line'



    def _amount_all(self, cr, uid, ids, field_name, arg, context=None):
        cur_obj = self.pool.get('leih.admission')
        res = {}
        for record in self.browse(cr, uid, ids, context=context):
            rate=record.price
            discount=record.discount
            interst_amount=int(discount)*int(rate)/100
            total_amount=int(rate)-interst_amount
            res[record.id]=total_amount
            # import pdb
            # pdb.set_trace()
        return res


    name= fields.Many2one("examination.entry","Item Name",ondelete='cascade')
    leih_admission_id= fields.Many2one('leih.admission', "Information")
    department= fields.Char("Department")
    price= fields.Float("Price")
    discount= fields.Float("Discount")
    flat_discount= fields.Integer("Flat Discount")
    total_discount= fields.Integer("Total Discount")
    discount_percent= fields.Integer("Discount Percent")
    total_amount= fields.Float("Total Amount")



    def onchange_test(self,cr,uid,ids,name,context=None):
        tests = {'values': {}}
        dep_object = self.pool.get('examination.entry').browse(cr, uid, name, context=None)
        abc = {'department':dep_object.department.name,'price': dep_object.rate,'total_amount':dep_object.rate}
        tests['value'] = abc
        # import pdb
        # pdb.set_trace()
        return tests

    def onchange_discount(self,cr,uid,ids,name,discount,context=None):
        tests = {'values': {}}
        dep_object = self.pool.get('examination.entry').browse(cr, uid, name, context=None)
        abc = {'total_amount':round(dep_object.rate-(dep_object.rate* discount/100))}
        tests['value'] = abc
        # import pdb
        # pdb.set_trace()
        return tests
class admission_bill_register(models.Model):
    _name = 'bill.register.admission.line'


    admission_line_id= fields.Many2one('leih.admission', 'admission')
    bill_id=fields.Many2one("bill.register","Bill ID")
    total=fields.Float('Total')


    def onchange_bill_id(self,cr,uid,ids,bill_id,context=None):
        lists={'values':{}}
        dep_object = self.pool.get('bill.register').browse(cr, uid, bill_id, context=None)
        bill_info={'total':dep_object.total}
        lists['value']=bill_info
        return lists

class admission_payment_line(models.Model):
    _name = 'admission.payment.line'


    admission_payment_line_id= fields.Many2one('leih.admission', 'admission payment')
    date=fields.Datetime("Date")
    amount=fields.Float('amount')
    type=fields.Char('Type')
    card_no=fields.Char('Card Number')
    bank_name=fields.Char('Bank Name')
    money_receipt_id= fields.Many2one('leih.money.receipt', 'Money Receipt ID')

