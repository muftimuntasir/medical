from odoo import api, models, fields,_
# from odoo.addons.base.models.res_currency import amount_to_text
from odoo.exceptions import UserError

class LeihAdmission(models.Model):
    _name = "leih.admission"
    _order = 'id desc'

    def _default_payment_type(self):
         return self.env['payment.type'].search([('name', '=', 'Cash')], limit=1).id



    name=fields.Char("Name")
    mobile= fields.Char(string="Mobile")
    patient_id= fields.Char(related='patient_name.patient_id',string="Patient Id")
    patient_name= fields.Many2one('patient.info', "Patient Name")
    address= fields.Char("Address")
    age= fields.Char("Age")
    sex=fields.Char("Sex")
    ref_doctors= fields.Many2one('doctors.profile','Reffered by')
    operation_date= fields.Date("Operation Date")
    release_note= fields.Text("Release Note")
    package_name= fields.Many2one("examine.package", string="Package")
    leih_admission_line_id= fields.One2many('leih.admission.line', 'leih_admission_id', 'Investigations')
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
        if self.payment_type and self.payment_type.active:
            interest = self.payment_type.service_charge
            if interest > 0:
                service_charge = (self.paid * interest) / 100
                self.service_charge = service_charge
                self.to_be_paid = self.paid + service_charge
            else:
                self.to_be_paid = self.paid
                self.service_charge = 0

    # def amount_to_text(self, amount, currency='Bdt'):
    #     text = self.env['ir.qweb.field.monetary'].amount_to_text(amount, currency)
    #     new_text = text.replace("euro", "Taka")
    #     sub_str = "Taka"
    #     final_text = new_text[:new_text.index(sub_str) + len(sub_str)]
    #     return final_text

    def advance_paid(self, name):
        mr = self.env['leih.money.receipt'].search([('admission_id', '=', name)])
        advance = sum(mr[:-1].mapped('amount'))
        paid = mr[-1].amount if len(mr) > 1 else 0
        return {'advance': advance, 'paid': paid}

    @api.onchange("patient_name")
    def onchange_patient(self):
        if self.patient_name:
            self.update({
                'mobile': self.patient_name.mobile,
                'address': self.patient_name.address,
                'age': self.patient_name.age,
                'sex': self.patient_name.sex,
            })

    @api.onchange('package_name')
    def onchange_package(self):
        if self.package_name:
            total_amount = 0.0
            leih_admission_lines = []
            for item in self.package_name.examine_package_line_id:
                total_amount += item.total_amount
                leih_admission_lines.append((0, 0, {
                    'name': item.name.id,
                    'total_amount': item.total_amount,
                    'price': item.price,
                    'flat_discount': item.discount,
                }))
            self.update({
                'leih_admission_line_id': leih_admission_lines,
                'other_discount': self.package_name.total_without_discount - self.package_name.total,
            })

    def change_status(self):
        journal_obj = self.env['bill.journal.relation']
        if self.state == 'activated':
            raise UserError(_('Already this Bill is Confirmed.'))

        if self.paid > self.grand_total:
            raise UserError(_('You paid more than the TOTAL AMOUNT'))

        self.write({'state': 'activated'})
        # Update money receipt
        if self.paid:
            vals ={'account_number': False,
             'amount': self.paid,
             'date': self.date,
             'payment_type': 1,
             'admission_id': self.id,
             'service_charge': 0,
             'to_be_paid': self.due}

            admission_payment_id = self.env['admission.payment'].create(vals)

            mr_id = admission_payment_id._creation_of_money_receipt()
            if mr_id:
                mr_id.name = f'MR#{mr_id.id}'

                admission_payment_id.money_receipt_id = mr_id.id
                admission_payment_id._creation_of_admission_payment_line()

                j_id = admission_payment_id._create_journal_entry(amount=self.paid, cr_act_id=1, dr_act_id=1,
                                                  bill_no=self.name, line_label=f'MR#{mr_id.id}')
                self.env.cr.execute("UPDATE leih_money_receipt SET journal_id=%s WHERE id=%s",
                                    (j_id.id, mr_id.id))


        # return self.env.ref('medical.action_report_leih_admission').report_action(self)
        return True

    def admission_cancel(self):
        # Unlink journal entries
        move_ids = self.env['account.move'].search([('ref', '=', self.name)])
        if move_ids:
            move_ids.button_cancel()
            move_ids.unlink()

        # Update admission status
        self.write({'state': 'cancelled'})

        # Update money receipts
        self.env['leih.money.receipt'].search([('admission_id', '=', self.id)]).write({'state': 'cancelled'})
        #for updates on cash collection
        self.env['leih.money.receipt'].search([('admission_id', '=', self.id)]).write({'state': 'cancel'})
        return True


    @api.model
    def create(self, vals):
        # Check if the due amount is negative
        if vals.get("due") and vals.get("due") < 0:
            raise UserError(_('Check paid and grand total!'))

        # Create the record using super
        admission = super(LeihAdmission, self).create(vals)

        # Generate the name field based on whether it's an emergency
        if not vals.get("emergency", False):
            name_text = 'A-0' + str(admission.id)
        else:
            name_text = 'E-0' + str(admission.id)

        # Update the record with the new name
        admission.name = name_text

        return admission

    @api.model
    def write(self, vals):
        if vals.get("due") and vals.get("due") < 0:
            raise UserError(_("Check paid and grand total!"))



        return super(LeihAdmission, self).write(vals)

    def btn_pay(self):
        self.ensure_one()

        if self.state in ['pending', 'cancelled']:
            raise UserError(_('Please Confirm and Print the Bill'))

        if self.total <= self.paid:
            raise UserError(_('Nothing to Pay Here. Already Fully Paid'))

        view = self.env.ref('medical.admission_payment_form_view')

        return {
            'name': _("Pay Invoice"),
            'view_mode': 'form',
            'view_id': view.id,
            'view_type': 'form',
            'res_model': 'admission.payment',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': {
                           'default_admission_id': self.id,
                           'default_amount': self.due
                       }}

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


    @api.onchange('paid')
    def onchange_paid(self):
        self.due = self.grand_total - self.paid
        if self.payment_type:
            if self.payment_type.name=='Visa Card':
                interest = self.payment_type.service_charge
                service_charge = (self.paid * interest) / 100
                self.service_charge = service_charge
                self.to_be_paid = self.paid + service_charge

    @api.onchange('doctors_discounts')
    def onchange_doc_discount(self):
        discount = self.doctors_discounts


        for item in self.leih_admission_line_id:
            item.discount_percent=round((item.price*discount)/100)
            item.discount=discount
            item.total_discount = item.flat_discount + item.discount_percent
            item.total_amount = item.price - item.total_discount

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


    examination_id= fields.Many2one("examination.entry","Item Name",ondelete='cascade')
    leih_admission_id= fields.Many2one('leih.admission', "Information")
    department= fields.Char("Department")
    price= fields.Float("Price")
    discount= fields.Float("Discount")
    flat_discount= fields.Integer("Flat Discount")
    total_discount= fields.Integer("Total Discount")
    discount_percent= fields.Integer("Discount Percent")
    total_amount= fields.Float("Total Amount")

    @api.onchange('examination_id')
    def onchange_test(self):
        if self.examination_id:
            self.department = self.examination_id.department.name
            self.price = self.examination_id.rate
            self.total_amount = self.examination_id.rate

    @api.onchange('discount')
    def onchange_discount(self):
        if self.examination_id and self.discount:
            self.total_amount = round(self.examination_id.rate - (self.examination_id.rate * self.discount / 100))
class admission_bill_register(models.Model):
    _name = 'bill.register.admission.line'


    admission_line_id= fields.Many2one('leih.admission', 'admission')
    bill_id=fields.Many2one("bill.register","Bill ID")
    total=fields.Float('Total')

    @api.onchange('bill_id')
    def onchange_bill_id(self):
        if self.bill_id:
            self.total = self.bill_id.total

class admission_payment_line(models.Model):
    _name = 'admission.payment.line'


    admission_payment_line_id= fields.Many2one('leih.admission', 'admission payment')
    date=fields.Datetime("Date")
    amount=fields.Float('amount')
    type=fields.Char('Type')
    card_no=fields.Char('Card Number')
    bank_name=fields.Char('Bank Name')
    money_receipt_id= fields.Many2one('leih.money.receipt', 'Money Receipt ID')

