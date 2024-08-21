from odoo import models, fields, api
from odoo.exceptions import UserError

class DiagnosisSticker(models.Model):
    _name = "diagnosis.sticker"
    _order = 'id desc'

    def print_sticker(self):
        status = 'lab'
        for record in self:
            record.state = status
        self.env.cr.commit()
        return self.env.ref('leih.report_sample_report').report_action(self)

    def print_lab_report(self):
        status = 'done'
        for record in self:
            record.state = status
        self.env.cr.commit()
        return self.env.ref('leih.report_detail').report_action(self)

    def haematology_report(self):
        status = 'done'
        for record in self:
            record.state = status
        self.env.cr.commit()
        return self.env.ref('leih.report_haematology').report_action(self)

    def serology_report(self):
        status = 'done'
        for record in self:
            record.state = status
        self.env.cr.commit()
        return self.env.ref('leih.report_serology').report_action(self)

    def microbiology_report(self):
        status = 'done'
        for record in self:
            record.state = status
        self.env.cr.commit()
        return self.env.ref('leih.report_microbiology').report_action(self)

    def biochemistry_report(self):
        status = 'done'
        for record in self:
            record.state = status
        self.env.cr.commit()
        return self.env.ref('leih.report_biochemistry').report_action(self)

    def urine_report(self):
        status = 'done'
        for record in self:
            record.state = status
        self.env.cr.commit()
        return self.env.ref('leih.report_urine').report_action(self)

    def stool_report(self):
        status = 'done'
        for record in self:
            record.state = status
        self.env.cr.commit()
        return self.env.ref('leih.report_stool').report_action(self)

    def done_radiology(self):
        status = 'done'
        for record in self:
            record.state = status
        self.env.cr.commit()
        return True

    def delivered(self):
        status = 'delivered'
        for record in self:
            record.state = status
        self.env.cr.commit()
        return True

    def set_to_lab(self):
        status = 'lab'
        for record in self:
            record.state = status
        self.env.cr.commit()
        return True

    name = fields.Char('No #')
    full_name = fields.Char('Name')
    bill_register_id = fields.Many2one('bill.register', 'Bill Register')
    admission_id = fields.Many2one('leih.admission', 'Admission ID')
    general_admission_id = fields.Many2one('hospital.admission', 'Admission ID')
    department_id = fields.Char('Department')
    doctor_id = fields.Many2one('doctors.profile', 'Checked By')
    test_id = fields.Many2one('examination.entry', 'Test Name')
    sticker_line_id = fields.One2many('diagnosis.sticker.line', 'sticker_id', 'Record Sample')
    state = fields.Selection(
        [('cancel', 'Cancelled'), ('sample', 'Sample'), ('lab', 'Lab'), ('done', 'Done'), ('delivered', 'Delivered'), ('indoor', 'Indoor')],
        'Status', required=True, readonly=True, copy=False,
    )


class DiagnosisStickerLine(models.Model):
    _name = "diagnosis.sticker.line"

    test_name = fields.Char("Name")
    sticker_id = fields.Many2one('diagnosis.sticker', 'ID')
    result = fields.Char('Result')
    ref_value = fields.Char('Reference Value')
    bold = fields.Boolean('Bold')
    group_by = fields.Boolean('Group By')
    remarks = fields.Char('Remarks')
