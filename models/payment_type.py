
from odoo import api, models, fields
from datetime import date, time

class PaymentType(models.Model):
    _name = "payment.type"



    name = fields.char("Name",required=True)
    account = fields.many2one('account.account', string='Account',required=True)
    service_charge_account = fields.many2one('account.account', string='Service Charge Account')
    service_charge = fields.float("Service Charge", required=True)
    service_charge_flat = fields.char("Service Charge(Flat)")
    active =fields.boolean("Active")
