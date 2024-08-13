
from odoo import api, models, fields
from datetime import date, time

class ExaminePackage(models.Model):
    _name = "examine.package"

    name = fields.Char("Package name")
    price = fields.Float(string="Price")
    start_date = fields.Date(string="Start Date")
    end_date = fields.Date(string="End Date")
    active = fields.Boolean("Active")
    examine_package_line_id =fields.One2many('examine.package.line', 'examine_package_id', 'Add test', required=True)
    total = fields.Float("Total")



class ExaminePackageLine(models.Model):
    _name = 'examine.package.line'

    name = fields.Many2one("examination.entry","Test Name", required=True, ondelete='cascade')
    examine_package_id = fields.Many2one('examine.package', "Information")
    price = fields.Integer("Price")
    discount = fields.Integer("Discount")
    total_amount = fields.Integer("Total Amount")

