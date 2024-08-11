from odoo import api, models, fields


class OPDTicket(models.Model):
    _name = "opd.ticket"
    _description = "OPD Ticket"

    name = fields.Char(string="Name")
