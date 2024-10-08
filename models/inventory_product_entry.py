from odoo import models, fields, api,_
from odoo.exceptions import UserError
from datetime import date, datetime

class InventoryProductEntry(models.Model):
    _name = "inventory.product.entry"
    _order = 'id desc'

    name = fields.Char("Entry No", readonly=True)
    invoice_no = fields.Char("Invoice/Bill No")
    invoice_date = fields.Date("Invoice/Bill Date")
    chalan_date = fields.Date("Chalan Date")
    chalan_no = fields.Char("Chalan No")
    reference_no = fields.Char("Reference No")
    total = fields.Float("Total Amount")
    partner_id = fields.Many2one('res.partner', 'Employee Name', required=True)
    grn_journal_id = fields.Many2one('account.move', 'GRN Journal')
    advance_journal_id = fields.Many2one('account.move', 'Advance Journal')
    warehouse_id = fields.Many2one('stock.warehouse', 'Warehouse Location', required=True)
    inventory_product_entry_line_ids = fields.One2many('inventory.product.entry.line', 'inventory_product_entry_id', string="Inventory Requisition Items", required=True)
    date = fields.Date('Entry Date')
    picking_id=fields.Many2one("stock.picking", string="Picking ID")
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
        """Transfers products from stock to the customer."""
        for entry in self:
            # Check if the state is still 'pending'
            if entry.state != 'pending':
                raise UserError(_('Only pending entries can be confirmed.'))

            # Prepare stock picking values for the transfer
            picking_vals = {
                'partner_id': entry.partner_id.id,
                'location_id': entry.partner_id.property_stock_supplier.id,  # Source location (stock)
                'location_dest_id': entry.warehouse_id.lot_stock_id.id,  # Destination location (customer)
                'picking_type_id': self.env.ref('stock.picking_type_in').id,  # Receipt type
                'origin': entry.name,
                'move_ids': [],
            }

            move_ids = []
            for line in entry.inventory_product_entry_line_ids:
                move_line_vals = {
                    'name': line.product_name.name,
                    'product_id': line.product_name.id,
                    'product_uom_qty': line.quantity,
                    'product_uom': line.product_name.uom_id.id,
                    'location_id': entry.partner_id.property_stock_customer.id,
                    'location_dest_id': entry.warehouse_id.lot_stock_id.id,
                }
                move_ids.append((0, 0, move_line_vals))

            picking_vals['move_ids'] = move_ids

            # Create the stock picking record
            picking = self.env['stock.picking'].create(picking_vals)

            # Confirm and transfer the stock
            picking.action_confirm()
            picking.action_assign()
            picking.button_validate()
            self.picking_id=picking

            # Update the entry state to 'confirmed'
            entry.state = 'confirmed'



            # journal_entry = self.env['account.move'].create({
            #     'journal_id': 6,  # Advance Cash Journal
            #     'date': fields.Date.today(),
            #     'ref': record.name,
            #     'line_ids': [
            #         (0, 0, {
            #             'name': record.name,
            #             'partner_id': record.partner_id.id,
            #             'account_id': item.account_id.id,
            #             'debit': item.total_price,
            #             'credit': 0,
            #         }) for item in record.inventory_product_entry_line_ids
            #     ] + [
            #         (0, 0, {
            #             'name': record.name,
            #             'partner_id': record.partner_id.id,
            #             'account_id': record.partner_id.property_account_payable_id.id,
            #             'debit': 0,
            #             'credit': record.total,
            #         })
            #     ]
            # })
            # journal_entry.action_post()
            #
            # record.write({'state': 'confirmed', 'grn_id': stock_picking.id, 'grn_journal_id': journal_entry.id})

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
