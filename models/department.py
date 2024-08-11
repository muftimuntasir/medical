from odoo import api, models, fields

class diagnostic_department(models.Model):
    _name = "diagnostic.department"



    name= fields.Char("Department Name",required=True)
    parent=fields.Many2one('diagnosis.department','parent')
