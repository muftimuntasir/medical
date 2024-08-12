from odoo import api, fields, models, _
from odoo.exceptions import UserError


class ExaminationEntry(models.Model):
    _name = "examination.entry"

    name = fields.Char("Item Name", required=True)
    department = fields.Many2one("diagnosis.department", 'Department')
    rate = fields.Integer("Rate")
    base_rate = fields.Integer("Base Rate")
    required_time = fields.Integer("Required time (Days)")
    sample_req = fields.Boolean("Sample Required")
    individual = fields.Boolean("Individual")
    manual = fields.Boolean("Manual")
    merge = fields.Boolean("Merge")
    dependency = fields.Boolean("Dependency")
    lab_not_required = fields.Boolean("No Lab Required")
    indoor = fields.Boolean("Indoor Item")
    sample_type = fields.Many2one('sample.type', 'Sample Type')
    accounts_id = fields.Many2one('account.account', "Account ID")
    examination_entry_line_ids = fields.One2many('examination.entry.line', 'examinationentry_id', 'Parameters')
    merge_ids = fields.Many2many('examination.entry', 'examination_merge_line_rel', 'item_id', 'merge_id',
                                 string="Merge")

    @api.onchange('manual')
    def onchange_manual(self):
        return {'value': {'boolean': self.manual}}

    @api.onchange('group')
    def onchange_group(self):
        if self.group:
            group = self.env['diagnosis.group'].browse(self.group.id)
            self.department = group.department.id

    @api.model
    def create(self, vals):
        if vals.get('sample_req') and not vals.get('sample_type'):
            raise UserError(_('Sample type must be defined if sample is required.'))

        if vals.get('manual') and not vals.get('examination_entry_line_ids') and vals.get('sample_req'):
            raise UserError(_('Test name should exist if manual and sample is required.'))

        return super(ExaminationEntry, self).create(vals)


class ExaminationEntryLine(models.Model):
    _name = 'examination.entry.line'

    name = fields.Char("Name")
    examinationentry_id = fields.Many2one('examination.entry', "Test Entry")
    reference_value = fields.Char("Reference Value")
    bold = fields.Boolean('Bold')
    group_by = fields.Boolean("Group By")
    others = fields.Char("Others")


class ExaminationMergeLine(models.Model):
    _name = 'examination.merge.line'

    merge_id = fields.Many2one('examination.entry', "Test Entry")
    examinationentry_id = fields.Many2one('examination.entry', "Merged Test Entry")
