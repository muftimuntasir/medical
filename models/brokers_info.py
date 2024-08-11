from odoo import api, models, fields

class brokers_info(models.Model):
    _name = "brokers.info"
    _rec_name = 'broker_name'



    broker_id= fields.Char(string="Broker ID", readonly=True)
    broker_name= fields.Char("Broker Name", required=True)
    status= fields.Selection([('active', 'Active') ('inactive', 'Inactive')], string='Status', default='active')
    commission_rate= fields.Float("Commission Rate (%) ")
    last_commission_calculation_date= fields.Date("Last Commission Calculation Date")
    bill_info= fields.One2many("bill.register", 'referral', "Bill Register")
    doctor_ids= fields.Many2many('doctors.profile', 'referral_relation', 'broker_id', 'doctor_id', "Broker Name")


    def create(self, cr, uid, vals, context=None):
        if context is None: context = {}
        record = super(brokers_info, self).create(cr, uid, vals, context)
        if record is not None:
            name_text = 'BR-1001' + str(record)
            cr.execute('update brokers_info set broker_id=%s where id=%s', (name_text, record))
            cr.commit()
        return record
