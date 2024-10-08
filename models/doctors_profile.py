from odoo import api, models, fields

class DoctorsProfile(models.Model):
    _name = "doctors.profile"


    name= fields.Char("Doctor Name",required=True)
    doctor_id= fields.Char("Doctor ID")
    department=fields.Char('Department')
    designation=fields.Char('Designation')
    degree=fields.Char('Degree')
    type= fields.Selection([('inhouse', 'In house'), ('consoled', 'Consoled'),('prttime','Part Time'),('outsid','Out Side')], string='Type', default='inhouse')
    status= fields.Selection([('active', 'Active'), ('inactive', 'Inactive')], string='Status', default='active')
    others= fields.Char("Others")
    bill_info=fields.One2many("bill.register",'ref_doctors',"Bill Register")
    # admission_info=fields.Many2one("leih.admission",'ref_doctors',"Admission Info")
    commission=fields.Many2one("commission","Commission")
    ipd_visit=fields.Float("IPD Visit Fee")

    commission_rate=fields.Float("Commission Rate (%) ")
    last_commission_calculation_date=fields.Date("Last Commission Calculation Date")
    # added for commission
    referral_id= fields.Many2one("doctors.profile", "Referral ID")
    broker_ids= fields.Many2many('brokers.info', 'referral_relation', 'doctor_id', 'broker_id',"Broker Name")
    is_referral= fields.Boolean("Is Referral?")


    def create(self,vals):

        record = super(DoctorsProfile, self).create(vals)
        if record is not None:
            record.doctor_id = 'D-900' + str(record.id)

        return record