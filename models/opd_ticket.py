from odoo import api, models, fields


class OPDTicket(models.Model):
    _name = "opd.ticket"
    _description = "OPD Ticket"

    name = fields.Char(string="Name")
    # 'patient_id': fields.char("Patient ID")

    mobile = fields.Char(string="Mobile", store=False)
    # patient_id = fields.Char(related='patient_name.patient_id', string="Patient Id", readonly=True)
    patient_id = fields.Char( string="Patient Id", readonly=True)
    patient_name = fields.Many2one('patient.info', "Patient Name")
    address = fields.Char("Address", store=False)
    age = fields.Char("Age", store=False)
    sex = fields.Char("Sex", store=False)
    already_collected = fields.Boolean("Money Collected", default=False)
    # 'date =fields.datetime("Date", readonly=True,default=lambda self: fields.datetime.now())
    date = fields.Date("Date", readonly=True, default=lambda self: fields.Datetime.now())
    ref_doctors = fields.Many2one('doctors.profile', 'Reffered by')
    opd_ticket_line_id = fields.One2many('opd.ticket.line', 'opd_ticket_id', 'Investigations', required=True)
    user_id = fields.Many2one('res.users', 'Assigned to', select=True, track_visibility='onchange')
    state = fields.Selection(
        [('confirmed', 'Confirmed'), ('cancelled', 'Cancelled')],
        'Status', default='confirmed')


    total = fields.Float(string="Total")
    with_doctor_total = fields.Float(string="with_doctor_total")



class test_information(models.Model):
    _name = 'opd.ticket.line'
    _description = "OPD ticket lines "

    name = fields.Many2one("opd.ticket.entry","Item Name", ondelete='cascade')
    opd_ticket_id = fields.Many2one('opd.ticket', "Information")
    price = fields.Integer("Price")
    department =fields.Char('Department')
    total_amount = fields.Integer("Total Amount")





class opd_ticket_config(models.Model):
    _name = "opd.ticket.entry"
    _order = 'id desc'
    _description = "Tkt Entry"

    name = fields.Char("Name")
    department = fields.Many2one("diagnosis.department","Department")
    fee = fields.Float("Fee")
    accounts_id = fields.Many2one('account.account',"Account ID",required=True)
    total_cash = fields.Float("Total Cash")

