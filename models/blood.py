from odoo import models, fields, api, _
from datetime import date, time

class BloodDonor(models.Model):
    _name = "blood.donor"

    name = fields.Char('Name')
    donor_name = fields.Char('Donor Name', required=True)
    mobile_no = fields.Char('Mobile No', required=True)
    date = fields.Date('Received Date', required=True)
    receive_date = fields.Date('Received Date')
    description = fields.Text('Description')
    group = fields.Char('Blood Group')
    cost = fields.Float('Cost')
    active = fields.Boolean('Expired')
    donated = fields.Boolean('Donated')


class BloodReceiver(models.Model):
    _name = "blood.receiver"

    name = fields.Char('Name')
    buyer_name = fields.Char('Buyer Name', required=True)
    receive_date = fields.Date('Date', required=True)
    mobile_no = fields.Char('Mobile No', required=True)
    patient_id = fields.Many2one('patient.info', "Patient Name")
    description = fields.Text('Description')
    blood_group = fields.Char('Blood Group')
    price = fields.Float('Price')
    paid_amount = fields.Float('Paid Amount')
    unpaid_amount = fields.Float('Unpaid Amount')

    @api.model
    def create(self, vals):
        # Add any custom logic here

        stored = super(BloodReceiver, self).create(vals)  # This creates the record and returns the recordset

        return stored