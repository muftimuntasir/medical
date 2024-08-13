from odoo import api, models, fields
from datetime import date, time

class ProductLens(models.Model):
    _name = "product.lens"


    lens_code = fields.Char("Code")
    name = fields.Char("Name")
    purchase_price = fields.Float("Purchase price")
    sell_price = fields.Float("Sale Price")
    lens_type = fields.Selection([( 'glass','Glass'),('plastic','Plastic')],default='plastic')
    supplier = fields.Char("Supplier Name")
