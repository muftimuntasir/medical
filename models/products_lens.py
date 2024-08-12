from odoo import api, models, fields
from datetime import date, time

class ProductLens(models.Model):
    _name = "product.lens"


    lens_code = fields.char("Code")
    name = fields.char("Name")
    purchase_price = fields.float("Purchase price")
    sell_price = fields.float("Sale Price")
    lens_type = fields.selection([( 'glass','Glass'),('plastic','Plastic')],default='plastic')
    supplier = fields.char("Supplier Name")
