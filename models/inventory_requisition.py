from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import date

class InventoryRequisition(models.Model):
    _name = "inventory.requisition"
    _description = "Inventory Requisition"
    _order = 'id desc'

    name = fields.Char("Inventory Requisition")
    reference_no = fields.Char("Reference No")
    warehouse_id = fields.Many2one('stock.warehouse', 'Warehouse Location', required=True)
    partner_id = fields.Many2one('res.partner', 'Receiver')
    challan_id = fields.Many2one('stock.picking', 'Challan NO')
    expense_journal_id = fields.Many2one('account.move', 'Expense Journal')
    department = fields.Many2one("hr.department", "Department", required=True)
    inventory_requisition_line_ids = fields.One2many('inventory.requisition.line', 'inventory_requisition_id', string="Inventory Requisition Items", required=True)
    date = fields.Date('Date', default=fields.Date.context_today)
    state = fields.Selection(
        [('pending', 'Pending'), ('confirmed', 'Confirmed'), ('cancelled', 'Cancelled')],
        'Status', default='pending', readonly=True)

    def confirm_transfer(self):
        for record in self:
            if record.state == 'confirmed':
                raise UserError(_('Sorry, it is already confirmed'))

            stock_picking_type = self.env['stock.picking.type'].search([
                ('warehouse_id', '=', record.warehouse_id.id),
                ('code', '=', 'outgoing')
            ], limit=1)

            if not stock_picking_type:
                raise UserError(_('No picking type found for the warehouse'))

            picking_vals = {
                'partner_id': record.partner_id.id,
                'date': fields.Datetime.now(),
                'origin': record.name,
                'date_done': fields.Date.today(),
                'move_type': 'direct',
                'picking_type_id': stock_picking_type.id,
            }

            move_lines = []
            for line in record.inventory_requisition_line_ids:
                if line.quantity > line.product_name.qty_available:
                    raise UserError(_('Stock is not available for product: %s') % line.product_name.display_name)

                move_line = {
                    'product_id': line.product_name.id,
                    'product_uom_qty': line.quantity,
                    'name': record.name,
                    'location_id': stock_picking_type.default_location_src_id.id,
                    'location_dest_id': stock_picking_type.default_location_dest_id.id,
                }
                move_lines.append((0, 0, move_line))

            picking_vals['move_lines'] = move_lines
            picking = self.env['stock.picking'].create(picking_vals)

            picking.action_confirm()
            picking.force_assign()
            picking.button_validate()

            # Create Expense Journal Entry
            journal_entry = self.env['account.move'].create({
                'journal_id': self.env.ref('account.sales_journal').id,
                'date': fields.Date.today(),
                'ref': record.name,
                'line_ids': self._prepare_journal_lines(picking),
            })

            journal_entry.action_post()

            record.write({
                'state': 'confirmed',
                'challan_id': picking.id,
                'expense_journal_id': journal_entry.id,
            })

        return True

    def _prepare_journal_lines(self, picking):
        lines = []
        for move in picking.move_lines:
            inv_value = sum(quant.inventory_value for quant in move.quant_ids)
            debit_line = {
                'name': picking.origin,
                'account_id': move.product_id.categ_id.property_account_expense_categ_id.id,
                'debit': inv_value,
                'credit': 0,
            }
            credit_line = {
                'name': picking.origin,
                'account_id': move.product_id.categ_id.property_stock_account_output_categ_id.id,
                'debit': 0,
                'credit': inv_value,
            }
            lines.append((0, 0, debit_line))
            lines.append((0, 0, credit_line))
        return lines

    @api.model
    def create(self, vals):
        record = super(InventoryRequisition, self).create(vals)
        record.name = 'IR-0{}'.format(record.id)
        return record


class InventoryRequisitionLine(models.Model):
    _name = "inventory.requisition.line"
    _description = "Inventory Requisition Line"

    name = fields.Char("Inventory Requisition Line Id")
    inventory_requisition_id = fields.Many2one("inventory.requisition", "Inventory Requisition ID")
    product_name = fields.Many2one('product.product', 'Product Name')
    available_qty = fields.Float("Available Qty", related='product_name.qty_available', readonly=True)
    quantity = fields.Float("Quantity")

    @api.onchange('product_name')
    def onchange_product(self):
        if self.product_name:
            self.available_qty = self.product_name.qty_available