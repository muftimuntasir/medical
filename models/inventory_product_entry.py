from odoo import models, fields, api
from odoo.exceptions import UserError
from datetime import date, datetime

class InventoryProductEntry(models.Model):
    _name = "inventory.product.entry"
    _order = 'id desc'

    name = fields.Char("Entry No", readonly=True)
    invoice_no = fields.Char("Invoice/Bill No", required=True)
    invoice_date = fields.Date("Invoice/Bill Date", required=True)
    chalan_date = fields.Date("Chalan Date", required=True)
    chalan_no = fields.Char("Chalan No", required=True)
    reference_no = fields.Char("Reference No")
    total = fields.Float("Total Amount")
    partner_id = fields.Many2one('res.partner', 'Employee Name', required=True)
    grn_id = fields.Many2one('stock.picking', 'GRN NO')
    grn_journal_id = fields.Many2one('account.move', 'GRN Journal')
    advance_journal_id = fields.Many2one('account.move', 'Advance Journal')
    warehouse_id = fields.Many2one('stock.warehouse', 'Warehouse Location', required=True)
    inventory_product_entry_line_ids = fields.One2many('inventory.product.entry.line', 'inventory_product_entry_id', string="Inventory Requisition Items", required=True)
    date = fields.Date('Entry Date')
    state = fields.Selection(
        [('pending', 'Pending'), ('confirmed', 'Receive Product'), ('verify', 'Verified'), ('cancelled', 'Cancelled')],
        'Status', default='pending', readonly=True
    )

    @api.onchange('inventory_product_entry_line_ids')
    def onchange_product_line(self):
        self.total = sum(item.total_price for item in self.inventory_product_entry_line_ids)

    def confirm_finance(self):
        for record in self:
            if record.state == 'verify':
                raise UserError(_('Sorry, it is already verified'))

            period_id = self.env['account.period'].find().id
            move_lines = [
                (0, 0, {
                    'name': record.name,
                    'partner_id': record.partner_id.id,
                    'account_id': record.partner_id.property_account_payable_id.id,
                    'debit': record.total,
                    'credit': 0,
                }),
                (0, 0, {
                    'name': record.name,
                    'partner_id': record.partner_id.id,
                    'account_id': 120,  # Advance Cash
                    'debit': 0,
                    'credit': record.total,
                })
            ]

            journal_entry = self.env['account.move'].create({
                'journal_id': 6,  # Advance Cash Journal
                'date': fields.Date.today(),
                'ref': record.name,
                'line_ids': move_lines
            })
            journal_entry.action_post()

            record.write({'state': 'verify', 'advance_journal_id': journal_entry.id})

    def confirm_transfer(self):
        for record in self:
            if record.state == 'confirmed':
                raise UserError(_('Sorry, it is already confirmed'))

            picking_type = self.env['stock.picking.type'].search([
                ('warehouse_id', '=', record.warehouse_id.id),
                ('code', '=', 'incoming')
            ], limit=1)

            grn_vals = {
                'partner_id': record.partner_id.id,
                'date': fields.Datetime.now(),
                'origin': record.name,
                'picking_type_id': picking_type.id,
            }

            move_lines = [
                (0, 0, {
                    'product_id': item.product_name.id,
                    'product_uom_qty': item.quantity,
                    'location_id': picking_type.default_location_src_id.id,
                    'location_dest_id': picking_type.default_location_dest_id.id,
                    'price_unit': item.unit_price,
                }) for item in record.inventory_product_entry_line_ids
            ]

            grn_vals['move_lines'] = move_lines
            stock_picking = self.env['stock.picking'].create(grn_vals)
            stock_picking.action_confirm()
            stock_picking.button_validate()

            journal_entry = self.env['account.move'].create({
                'journal_id': 6,  # Advance Cash Journal
                'date': fields.Date.today(),
                'ref': record.name,
                'line_ids': [
                    (0, 0, {
                        'name': record.name,
                        'partner_id': record.partner_id.id,
                        'account_id': item.account_id.id,
                        'debit': item.total_price,
                        'credit': 0,
                    }) for item in record.inventory_product_entry_line_ids
                ] + [
                    (0, 0, {
                        'name': record.name,
                        'partner_id': record.partner_id.id,
                        'account_id': record.partner_id.property_account_payable_id.id,
                        'debit': 0,
                        'credit': record.total,
                    })
                ]
            })
            journal_entry.action_post()

            record.write({'state': 'confirmed', 'grn_id': stock_picking.id, 'grn_journal_id': journal_entry.id})

    @api.model
    def create(self, vals):
        record = super().create(vals)
        if record:
            record.name = 'IPE-0' + str(record.id)
        return record


class InventoryProductEntryLine(models.Model):
    _name = "inventory.product.entry.line"

    name = fields.Char("Inventory Requisition Line Id")
    inventory_product_entry_id = fields.Many2one("inventory.product.entry", "Inventory Entry ID")
    product_name = fields.Many2one('product.product', 'Product Name')
    account_id = fields.Many2one('account.account', string='Account', required=True, domain=[('deprecated', '=', False)])
    quantity = fields.Float("Quantity")
    unit_price = fields.Float("Unit Price")
    total_price = fields.Float("Total Price")

    @api.onchange('product_name')
    def onchange_product(self):
        if self.product_name:
            self.account_id = self.product_name.categ_id.property_stock_account_input_categ_id
            self.unit_price = self.product_name.standard_price
            self.quantity = 1
            self.total_price = self.unit_price

    @api.onchange('quantity', 'unit_price')
    def _compute_total_price(self):
        self.total_price = self.quantity * self.unit_price
