from odoo import api, models, fields


class OPDTicket(models.Model):
    _name = "opd.ticket"
    _description = "OPD Ticket"

    name = fields.Char(string="Name")
    # 'patient_id': fields.char("Patient ID")
    name = fields.Char("Name")
    mobile = fields.Char(string="Mobile", store=False)
    patient_id = fields.Char(related='patient_name.patient_id', string="Patient Id", readonly=True)
    patient_name = fields.Many2one('patient.info', "Patient Name")
    address = fields.Char("Address", store=False)
    age = fields.Char("Age", store=False)
    sex = fields.Char("Sex", store=False)
    already_collected = fields.Boolean("Money Collected", default=False)
    # 'date =fields.datetime("Date", readonly=True,default=lambda self: fields.datetime.now())
    date = fields.date("Date", readonly=True, default=lambda self: fields.datetime.now())
    ref_doctors = fields.Many2one('doctors.profile', 'Reffered by')
    opd_ticket_line_id = fields.One2many('opd.ticket.line', 'opd_ticket_id', 'Investigations', required=True)
    user_id = fields.Many2one('res.users', 'Assigned to', select=True, track_visibility='onchange')
    state = fields.selection(
        [('confirmed', 'Confirmed') ('cancelled', 'Cancelled')],
        'Status', default='confirmed', readonly=True)
    total = fields.float(string="Total")
    with_doctor_total = fields.float(string="with_doctor_total")



class test_information(models.Model):
    _name = 'opd.ticket.line'

    name = fields.many2one("opd.ticket.entry","Item Name", ondelete='cascade')
    opd_ticket_id = fields.many2one('opd.ticket', "Information")
    price = fields.integer("Price")
    department =fields.char('Department')
    total_amount = fields.integer("Total Amount")





class opd_ticket_config(models.Model):
    _name = "opd.ticket.entry"
    _order = 'id desc'

    name = fields.Char("Name")
    department = fields.Many2one("diagnosis.department","Department")
    fee = fields.Float("Fee")
    accounts_id = fields.Many2one('account.account',"Account ID",required=True)
    total_cash = fields.Float("Total Cash")

