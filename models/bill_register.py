from odoo import api, fields, models
from datetime import date, time, timedelta, datetime
from odoo.exceptions import UserError
from odoo import _

class BillRegister(models.Model):
    _name = "bill.register"
    _order = 'id desc'

    def _totalpayable(self, cr, uid, ids, field_name, arg, context=None):
        Percentance_calculation = {}
        sum = 0
        for items in self.pool.get("bill.register").browse(cr, uid, ids, context=None):
            total_list = []
            for amount in items.bill_register_line_id:
                total_list.append(amount.total_amount)

            for item in total_list:
                sum = item + sum

                for record in self.browse(cr, uid, ids, context=context):
                    Percentance_calculation[record.id] = sum

        return Percentance_calculation

    def _delivery_dates(self, cr, uid, ids, field_name, arg, context=None):
        delivery_date = {}
        test_delivery_date = []
        max_day = 0
        for items in self.pool.get("bill.register").browse(cr, uid, ids, context=None):
            total_list = []
            for amount in items.bill_register_line_id:
                for test in amount.name:
                    test_delivery_date.append(test.required_time)

        if len(test_delivery_date):
            max_day = max(test_delivery_date)

        for record in self.browse(cr, uid, ids, context=context):
            delivery_date[record.id] = date.today() + timedelta(days=max_day)

        return delivery_date

    def _default_payment_type(self):
        return self.env['payment.type'].search([('name', '=', 'Cash')], limit=1).id



        # 'patient_id': fields.Char("Patient ID"),
    name= fields.Char("Name")
    mobile= fields.Char(string="Mobile")
    patient_id= fields.Char(related='patient_name.patient_id', string="Patient Id", readonly=True)
    patient_name= fields.Many2one('patient.info', "Patient Name", required=True)
    address= fields.Char("Address")
    age= fields.Char("Age")
    sex= fields.Char("Sex")
    diagonostic_bill= fields.Boolean("Diagnostic Bill")
    ref_doctors= fields.Many2one('doctors.profile', 'Referred by')
    referral= fields.Many2one('brokers.info', 'Referral')
    bill_register_line_id= fields.One2many('bill.register.line', 'bill_register_id', 'Item Entry', required=True)
    bill_register_payment_line_id= fields.One2many("bill.register.payment.line", "bill_register_payment_line_id",
                                                     "Bill Register Payment")
    bill_journal_relation_id= fields.One2many("bill.journal.relation", "bill_journal_relation_id", "Journal")
    total_without_discount= fields.Float(string="Total without discount")
    total= fields.Float(string="Total")
    doctors_discounts= fields.Float("Doctor Discount(%)")
    after_discount= fields.Float("Discount Amount")
    other_discount= fields.Float("Other Discount")
    grand_total= fields.Float("Grand Total")
    paid= fields.Float(string="Paid", required=True)
    type= fields.Selection([('cash', 'Cash'), ('bank', 'Bank')], 'Payment Type')
    card_no= fields.Char('Card No.')
    bank_name= fields.Char('Bank Name')
    due= fields.Float("Due")
    date= fields.Datetime("Date", readonly=True, default=lambda self: fields.Datetime.now())
    user_id= fields.Many2one('res.users', 'Assigned to', select=True, track_visibility='onchange')
    state= fields.Selection(
        [('pending', 'Pending'), ('confirmed', 'Confirmed'), ('cancelled', 'Cancelled')],
        'Status', default='pending')
    old_journal= fields.Boolean("Old Journal")
    # new attributes for payment type
    payment_type= fields.Many2one("payment.type", "Payment Type", default=_default_payment_type)
    service_charge= fields.Float("Service Charge")
    to_be_paid= fields.Float("To be Paid")
    account_number= fields.Char("Account Number")
    discount_remarks= fields.Char("Discount Remarks")

  

    @api.onchange("payment_type")
    def onchnage_payment_type(self):
        if self.payment_type.active == True:
            interest = self.payment_type.service_charge
            if interest > 0:
                service_charge = (self.paid * interest) / 100
                self.service_charge = service_charge
                self.to_be_paid = self.paid + service_charge
            else:
                self.to_be_paid = self.paid
                self.service_charge = 0




    def advance_paid(self, name):
        bill_obj = self.env['bill.register'].search([('name', '=', name)])
        if bill_obj.state != 'confirmed':
            raise UserError (_('Already this Bill is Confirmed.'))
        elif bill_obj.state == 'confirmed':
            mr = self.env['leih.money.receipt'].search([('bill_id', '=', name)])
            advance = 0
            paid = 0
            if len(mr) > 2:
                for i in range(len(mr) - 1):
                    advance = advance + mr[i].amount
                paid = mr[len(mr) - 1].amount
                # mr_ids=self.pool.get('leih.money.receipt').search([('bill_id', '=', name)], context=context)

                lists = {
                    'advance': advance,
                    'paid': paid
                }
            elif len(mr) == 2:
                advance = advance + mr[0].amount
                paid = paid + mr[1].amount
                lists = {
                    'advance': advance,
                    'paid': paid
                }
            elif len(mr) == 1:
                advance = advance + mr[0].amount
                lists = {
                    'advance': advance,
                    'paid': 0
                }
            elif len(mr) < 1:
                lists = {
                    'advance': 0,
                    'paid': 0
                }

        # final_text = new_text.replace("Cent", "Paisa")
        return lists

    # if same item exist in line
    #
    # @api.constrains('bill_register_line_id')
    # def _check_exist_item_in_line(self):
    #     for item in self:
    #         exist_item_list = []
    #         for line in item.bill_register_line_id:
    #             if line.name.id in exist_item_list:
    #                 raise ValidationError(_('Item should be one per line.'))
    #             exist_item_list.append(line.name.id)


    def _crerate_journal(self):
        return True

    def _create_labs_data(self):
        return True

    def bill_confirm(self):

        stored_obj = self
        journal_object = self.pool.get("bill.journal.relation")

        diagonostic_bill = stored_obj.diagonostic_bill
        ## Bill Status Will Change

        # if stored_obj.state == 'confirmed':
        #     raise UserError(_('Already this Bill is Confirmed.'))

        # this section is used to minimum payment for bill 35%
        grand_total = stored_obj.grand_total
        paid_amount = stored_obj.paid
        if grand_total != 0:
            percent_amount = (paid_amount * 100) / grand_total
        if grand_total == 0:
            percent_amount = 0



        if percent_amount >= 0 or grand_total == 0:
            self.state = "confirmed"

            #### Create Journal From Here

            #### Ends Here

            # report_action = self.env.ref('medical.action_report_leih_bill_register')
            # return report_action.report_action(self)
            return True

            # return self.pool['report'].get_action(cr, uid, ids, 'leih.report_bill_register', context=context)
        else:
            raise UserError('PLease Pay minimum amount.')


    @api.onchange('patient_name')
    def onchange_patient(self):
        dep_object = self.patient_name
        self.mobile=dep_object.mobile
        self.address= dep_object.address
        self.age= dep_object.age
        self.sex= dep_object.sex

    # def add_new_test(self, cr, uid, ids, context=None):
    #     if not ids: return []
    #
    #     dummy, view_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'leih', 'add_bill_view')
    #     #
    #     inv = self.browse(cr, uid, ids[0], context=context)
    #     # import pdb
    #     # pdb.set_trace()
    #     return {
    #         'name': _("Pay Invoice"),
    #         'view_mode': 'form',
    #         'view_id': view_id,
    #         'view_type': 'form',
    #         'res_model': 'add.bill',
    #         'type': 'ir.actions.act_window',
    #         'nodestroy': True,
    #         'target': 'new',
    #         'domain': '[]',
    #         'context': {
    #             'bill_id': ids[0],
    #             'default_price': 500,
    #             # 'default_name':context.get('name', False),
    #             'default_total_amount': 200,
    #         }
    #     }
    #     raise UserError(_('Error!'), _('There is no default company for the current user!'))

    def button_dummy(self, cr, uid, ids, context=None):

        return True

    def bill_cancel(self, cr, uid, ids, context=None):

        ##### Cancel Journal And Unlink/ Delete all journals

        cr.execute(
            "select id as jounral_id from account_move where ref = (select name from bill_register where id=%s limit 1)",
            (ids))
        joural_ids = cr.fetchall()
        context = context

        itm = [itm[0] for itm in joural_ids]
        if len(itm) > 0:
            uid = 1
            moves = self.pool.get('account.move').browse(cr, uid, itm, context=context)
            moves.button_cancel()  ## Cancelling

            bill_journal_id = []
            # cr.execute("delete from bill_journal_relation where id in (select id from bill_journal_relation where journal_id in %s)",(tuple(itm)))
            user_q = "select id from bill_journal_relation where journal_id in %s"
            # cr.execute("select id from bill_journal_relation where journal_id in %s",(tuple(itm)))
            cr.execute(user_q, (tuple(itm),))
            journal_id = cr.fetchall()
            for item in journal_id:
                bill_journal_id.append(item[0])

            query = "delete from bill_journal_relation where id in %s"
            cr.execute(query, (tuple(bill_journal_id),))

            moves.unlink()  ### Deleting Journal

        #### Ends Here

        ## Bill Status Will Change

        cr.execute("update bill_register set state='cancelled' where id=%s", (ids))
        cr.commit()
        ## Lab WIll be Deleted

        cr.execute("update diagnosis_sticker set state='cancel' where bill_register_id=%s", (ids))
        cr.commit()

        # for updates on cash collection
        cr.execute("update leih_money_receipt set state='cancel' where bill_id=%s", (ids))
        cr.commit()

        return True


    def btn_pay_bill(self):
        self.ensure_one()  # Ensure that only one record is being processed
        inv = self

        if inv.state == 'pending':
            raise UserError(_('Please Confirm and Print the Bill'))

        if inv.total <= inv.paid:
            raise UserError(_('Nothing to Pay Here. Already Full Paid'))

        # Get the view ID
        view_id = self.env.ref('medical.bill_register_payment_form_view').id

        return {
            'name': _("Pay Invoice"),
            'view_mode': 'form',
            'view_id': view_id,
            'res_model': 'bill.register.payment',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': {
                'default_bill_id': inv.id,
                'default_amount': inv.due
            }
        }
    def add_discount(self, cr, uid, ids, context=None):
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
                'pi_id': ids[0]
            }
        }
        raise UserError(_('Error!'), _('There is no default company for the current user!'))

    @api.model
    def create(self, vals):
        # Check if 'due' is present and validate it
        if vals.get("due"):
            if vals.get("due") < 0:
                raise UserError(_('Warning! Check paid and grand total!'))

        # List of diagnostic departments
        child_ids = ["MRI", 'X-Ray', 'Radiology & Imaging', 'Pathology', 'Bio-Chemistry', 'Haematology', 'Serology',
                     'Micro-Biology', 'CT Scan', 'USG', 'Diagnostic', 'X-Ray', 'Echocardiogram', 'Hormone',
                     'Immunology']

        # Get departments from bill register lines
        get_all_depts = []
        if vals.get('bill_register_line_id'):
            for items in vals.get('bill_register_line_id'):
                if isinstance(items, (list, tuple)) and len(items) == 3 and items[2].get('department'):
                    department = items[2].get('department')
                    if department not in get_all_depts:
                        get_all_depts.append(department)

        # Check if there are mixed departments
        mixed_up = False
        vals['diagonostic_bill'] = True

        intersection_result = list(set(child_ids) & set(get_all_depts))
        if intersection_result and len(intersection_result) == len(get_all_depts):
            vals['diagonostic_bill'] = True
        elif intersection_result and len(intersection_result) != len(get_all_depts):
            mixed_up = True

        if mixed_up:
            raise UserError(_('Attention'), _('This investigation has diagnosis and other departments mixed up'))

        # Create the bill register record
        record = super(BillRegister, self).create(vals)

        # Update the name field after creation
        if record:
            name_text = 'Bill-0' + str(record.id)
            self.env.cr.execute('UPDATE bill_register SET name=%s WHERE id=%s', (name_text, record.id))

        return record

    def write(self, vals):
        # Check if 'due' is present and validate it
        if vals.get("due") and vals.get("due") < 0:
            raise UserError(_('Warning! Check paid and grand total!'))

        updated = False

        # Check if 'bill_register_line_id' is present or if the user is an admin
        if vals.get('bill_register_line_id') or self.env.uid == 1:
            # Fetch journal entries linked to this bill register
            self.env.cr.execute("""
                SELECT id AS journal_ids 
                FROM account_move 
                WHERE ref = (SELECT name FROM bill_register WHERE id=%s LIMIT 1)
            """, (self.id,))
            journal_ids = [row[0] for row in self.env.cr.fetchall()]

            updated = super(BillRegister, self).write(vals)

            if journal_ids:
                # Cancel linked journal entries and delete related records
                moves = self.env['account.move'].browse(journal_ids)
                moves.button_cancel()

                # Delete entries from bill_journal_relation
                self.env.cr.execute("""
                    DELETE FROM bill_journal_relation 
                    WHERE journal_id IN %s
                """, (tuple(journal_ids),))

                # Delete the journal entries
                moves.unlink()

                # Recreate the journal entries
                stored_obj = self.browse(self.id)
                if stored_obj:
                    line_ids = []
                    period_id = self.env['account.period'].find().id

                    if stored_obj.due > 0:
                        line_ids.append((0, 0, {
                            'name': stored_obj.name,
                            'account_id': 195,  # Accounts Receivable ID
                            'debit': stored_obj.due,
                        }))

                    if stored_obj.paid > 0:
                        line_ids.append((0, 0, {
                            'name': stored_obj.name,
                            'account_id': 6,  # Cash ID
                            'debit': stored_obj.paid,
                        }))

                    for cc_obj in stored_obj.bill_register_line_id:
                        account_id = cc_obj.name.accounts_id.id if cc_obj.name.accounts_id else 611
                        line_ids.append((0, 0, {
                            'name': cc_obj.name.name,
                            'account_id': account_id,
                            'credit': cc_obj.total_amount,
                        }))

                    journal_entry = self.env['account.move'].create({
                        'journal_id': 2,  # Sales Journal
                        'date': stored_obj.date,
                        'ref': stored_obj.name,
                        'line_ids': line_ids
                    })
                    journal_entry.action_post()

                    # Update bill register state and link the journal entry
                    stored_obj.write({'state': 'confirmed'})
                    self.env['bill.journal.relation'].create({
                        'journal_id': journal_entry.id,
                        'bill_journal_relation_id': stored_obj.id,
                    })

        if not updated:
            updated = super(BillRegister, self).write(vals)

        return updated

    @api.onchange('bill_register_line_id')
    def onchange_test_bill(self):
        sumalltest = 0
        total_without_discount = 0

        # Loop through the related line items to calculate sums
        for item in self.bill_register_line_id:
            sumalltest += item.total_amount
            total_without_discount += item.price

        # Update the fields with calculated values
        self.total = sumalltest

        if self.doctors_discounts:
            after_dis = sumalltest * (self.doctors_discounts / 100)
        else:
            after_dis = 0

        self.after_discount = after_dis

        self.grand_total = sumalltest
        self.due = sumalltest - self.paid
        self.total_without_discount = total_without_discount

    @api.onchange('paid')
    def onchange_paid(self):
        self.due = self.grand_total - self.paid
        if self.payment_type:
            if self.payment_type.name == 'Visa Card':
                interest = self.payment_type.service_charge
                service_charge = (self.paid * interest) / 100
                self.service_charge = service_charge
                self.to_be_paid = self.paid + service_charge

    @api.onchange('doctors_discounts')
    def onchange_doc_discount(self):
        discount = self.doctors_discounts

        for item in self.bill_register_line_id:
            item.discount_percent = round((item.price * discount) / 100)
            item.discount = discount
            item.total_discount = item.flat_discount + item.discount_percent
            item.total_amount = item.price - item.total_discount

    @api.onchange('other_discount')
    def onchange_other_discount(self):
        other_discount = self.other_discount
        total = self.total_without_discount
        if total > 0:
            discount_distribution = other_discount / total
            for item in self.bill_register_line_id:
                item.flat_discount = 0
                item.flat_discount = round(item.price * discount_distribution)
                item.total_discount = item.flat_discount + item.discount_percent
                item.total_amount = item.price - item.total_discount


class TestInformation(models.Model):
    _name = 'bill.register.line'

    def _amount_all(self, cr, uid, ids, field_name, arg, context=None):
        cur_obj = self.pool.get('bill.register')
        res = {}
        for record in self.browse(cr, uid, ids, context=context):
            rate = record.price
            discount = record.discount
            interst_amount = int(discount) * int(rate) / 100
            total_amount = int(rate) - interst_amount
            res[record.id] = total_amount
            # import pdb
            # pdb.set_trace()
        return res


    examination_id= fields.Many2one("examination.entry", "Item Name", ondelete='cascade')

    bill_register_id= fields.Many2one('bill.register', "Information")
    department= fields.Char("Department")
    name= fields.Char("Name")
    product_qty= fields.Float('Quantity')
    delivery_date= fields.Date("Delivery Date")
    date= fields.Datetime("Date", readonly=True, default=lambda self: fields.Datetime.now())
    price= fields.Integer("Price")
    discount= fields.Integer("Discount (%)")
    flat_discount= fields.Integer("Flat Discount")
    total_discount= fields.Integer("Total Discount")
    discount_percent= fields.Integer("Discount Percent")
    total_amount= fields.Integer("Total Amount")
    assign_doctors= fields.Many2one('doctors.profile', 'Doctor')
    commission_paid= fields.Boolean("Commission Paid")


    @api.onchange('examination_id')
    def onchange_test(self):
        if not self.examination_id:
            return

        # Fetch the related examination.entry record
        dep_object = self.examination_id

        # Calculate the delivery date based on the required time
        delivery_required_days = dep_object.required_time
        delivery_date = date.today() + timedelta(days=delivery_required_days)

        # Update the current record's fields based on the fetched data
        self.department = dep_object.department.name
        self.product_qty = 1
        self.price = dep_object.rate
        self.total_amount = dep_object.rate
        self.bill_register_id.paid = dep_object.rate
        self.delivery_date = delivery_date

    @api.onchange('product_qty')
    def onchange_qty(self):
        self.total_amount = self.price * self.product_qty

    @api.onchange('discount')
    def onchange_discount(self):

        dis_amount = round(self.price - (self.price * self.discount / 100))
        self.total_amount= dis_amount
        self.total_discount= dis_amount

    def create(self, vals):
        # Create the record using the new API
        record = super(TestInformation, self).create(vals)

        return record


class AdmissionPaymentLine(models.Model):
    _name = 'bill.register.payment.line'

    bill_register_payment_line_id= fields.Many2one('bill.register', 'bill register payment')
    date= fields.Date("Date")
    amount= fields.Float('Amount')
    type= fields.Char("Type")
    card_no= fields.Char('Card Number')
    bank_name= fields.Char('Bank Name')
    money_receipt_id= fields.Many2one('leih.money.receipt', 'Money Receipt ID')



class BillJournalRelation(models.Model):
    _name = 'bill.journal.relation'

    bill_journal_relation_id= fields.Many2one('bill.register', 'bill register payment')
    admission_journal_relation_id= fields.Many2one('leih.admission', 'Admission Journal')
    general_admission_journal_relation_id= fields.Many2one('hospital.admission', 'General Admission Journal')
    journal_id= fields.Integer("Journal Id")


