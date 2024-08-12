from odoo import api, models, fields
from datetime import date, time


class Ward(models.Model):
    _name = "ward.managment"


    wname = fields.Char("Ward Name",required=True)
    bed = fields.Char("Bed No", required=True)
    name = fields.Char("Patient Name", required=True)
    pid = fields.Char("Patient ID", required=True)
    Date = fields.Datetime("Received Date", required=True)
    precived = fields.Char("Received By", required=True)