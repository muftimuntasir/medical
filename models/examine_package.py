
from odoo import api, models, fields
from datetime import date, time

class ExaminePackage(models.Model):
    _name = "examine.package"




    name =fields.char("Package name"),
    price = fields.float(string="Price"),
    start_date = fields.date(string="Start Date"),
    end_date = fields.date(string="End Date"),
    active = fields.boolean("Active"),
    examine_package_line_id =fields.one2many('examine.package.line', 'examine_package_id', 'Add test', required=True),
    total = fields.float("Total")



class ExaminePackageLine(models.Model):
    _name = 'examine.package.line'

    name = fields.many2one("examination.entry","Test Name", required=True, ondelete='cascade'),
    examine_package_id = fields.many2one('examine.package', "Information"),
    # 'currency_id = fields.related('pricelist_id', 'currency_id', type="many2one", relation="res.currency",
    #                               string="Currency", readonly=True, required=True),
    # 'price_subtotal = fields.function(_amount_line, string='Subtotal', digits_compute=dp.get_precision('Account')),
    price = fields.integer("Price"),
    discount = fields.integer("Discount"),
    total_amount = fields.integer("Total Amount")

