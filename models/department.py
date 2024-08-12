from odoo import api, models, fields

class DiagnosticDepartment(models.Model):
    _name = "diagnosis.department"
    _description = "Department name Entry"

    name = fields.Char("Department Name")
    parent_id = fields.Many2one('diagnosis.department','Parent')
