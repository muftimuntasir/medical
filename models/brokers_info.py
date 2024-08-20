from odoo import api, models, fields

class BrokersInfo(models.Model):
    _name = "brokers.info"
    _rec_name = 'broker_name'



    broker_id= fields.Char(string="Broker ID")
    broker_name= fields.Char("Broker Name", required=True)
    status= fields.Selection([('active', 'Active'),('inactive', 'Inactive')], string='Status', default='active')
    commission_rate= fields.Float("Commission Rate (%) ")
    last_commission_calculation_date= fields.Date("Last Commission Calculation Date")
    bill_info= fields.One2many("bill.register", 'referral', "Bill Register")
    # doctor_ids= fields.Many2many('doctors.profile', 'referral_relation', 'broker_id', 'doctor_id', "Broker Name")


    def create(self, vals):
        record = super(BrokersInfo, self).create(vals)
        record.broker_id = 'BR-1001' + str(record.id)
        return record
