from odoo import api, models, fields
from datetime import date, time

class Sample(models.Model):
    _name = "diagnosis.sticker"
    _order = 'id desc'


    def print_sticker(self,cr,uid,ids,context=None):
        statue='lab'


        for id in ids:
            report_obj = self.browse(cr, uid, id, context=context)
            # if report_obj.state == 'lab' or report_obj.state == 'done':
            #     raise osv.except_osv(_('Warning!'),
            #                          _('Already it is sample collected.'))
            cr.execute('update diagnosis_sticker set state=%s where id=%s', (statue, id))
            cr.commit()
        return self.pool['report'].get_action(cr, uid, ids, 'leih.report_sample_report', context=context)
        # return True

    def print_lab_report(self,cr,uid,ids,context=None):
        status='done'

        for id in ids:
            report_obj = self.browse(cr, uid, id, context=context)
            # if report_obj.state == 'done':
            #     raise osv.except_osv(_('Warning!'),
            #                          _('Already it is Completed.'))
            cr.execute('update diagnosis_sticker set state=%s where id=%s', (status, id))
            cr.commit()
        return self.pool['report'].get_action(cr, uid, ids, 'leih.report_detail', context=context)
    def haematology_report(self,cr,uid,ids,context=None):
        status = 'done'
        for id in ids:
            report_obj = self.browse(cr, uid, id, context=context)
            # if report_obj.state == 'done':
            #     raise osv.except_osv(_('Warning!'),
            #                          _('Already it is Completed.'))
            cr.execute('update diagnosis_sticker set state=%s where id=%s', (status, id))
            cr.commit()
        return self.pool['report'].get_action(cr, uid, ids, 'leih.report_haematology', context=context)

    #call the report for serology

    def serology_report(self,cr,uid,ids,context=None):
        status = 'done'
        for id in ids:
            report_obj = self.browse(cr, uid, id, context=context)
            # if report_obj.state == 'done':
            #     raise osv.except_osv(_('Warning!'),
            #                          _('Already it is Completed.'))
            cr.execute('update diagnosis_sticker set state=%s where id=%s', (status, id))
            cr.commit()
        return self.pool['report'].get_action(cr, uid, ids, 'leih.report_serology', context=context)

    def microbiology_report(self,cr,uid,ids,context=None):
        status = 'done'
        for id in ids:
            report_obj = self.browse(cr, uid, id, context=context)
            # if report_obj.state == 'done':
            #     raise osv.except_osv(_('Warning!'),
            #                          _('Already it is Completed.'))
            cr.execute('update diagnosis_sticker set state=%s where id=%s', (status, id))
            cr.commit()
        return self.pool['report'].get_action(cr, uid, ids, 'leih.report_microbiology', context=context)

    def biochemistry_report(self,cr,uid,ids,context=None):
        status = 'done'
        for id in ids:
            report_obj = self.browse(cr, uid, id, context=context)
            # if report_obj.state == 'done':
            #     raise osv.except_osv(_('Warning!'),
            #                          _('Already it is Completed.'))
            cr.execute('update diagnosis_sticker set state=%s where id=%s', (status, id))
            cr.commit()
        return self.pool['report'].get_action(cr, uid, ids, 'leih.report_biochemistry', context=context)

    def urine_report(self,cr,uid,ids,context=None):
        status = 'done'
        for id in ids:
            report_obj = self.browse(cr, uid, id, context=context)
            # if report_obj.state == 'done':
            #     raise osv.except_osv(_('Warning!'),
            #                          _('Already it is Completed.'))
            cr.execute('update diagnosis_sticker set state=%s where id=%s', (status, id))
            cr.commit()
        return self.pool['report'].get_action(cr, uid, ids, 'leih.report_urine', context=context)

    def stool_report(self,cr,uid,ids,context=None):
        status = 'done'
        for id in ids:
            report_obj = self.browse(cr, uid, id, context=context)
            # if report_obj.state == 'done':
            #     raise osv.except_osv(_('Warning!'),
            #                          _('Already it is Completed.'))
            cr.execute('update diagnosis_sticker set state=%s where id=%s', (status, id))
            cr.commit()
        return self.pool['report'].get_action(cr, uid, ids, 'leih.report_stool', context=context)


    def done_radiology(self,cr,uid,ids,context=None):
        status = 'done'
        for id in ids:
            report_obj = self.browse(cr, uid, id, context=context)
            # if report_obj.state == 'done':
            #     raise osv.except_osv(_('Warning!'),
            #                          _('Already it is Completed.'))
            cr.execute('update diagnosis_sticker set state=%s where id=%s', (status, id))
            cr.commit()
        return True

    def delivered(self,cr,uid,ids,context=None):
        status = 'delivered'
        for id in ids:
            report_obj = self.browse(cr, uid, id, context=context)
            # if report_obj.state == 'done':
            #     raise osv.except_osv(_('Warning!'),
            #                          _('Already it is Completed.'))
            cr.execute('update diagnosis_sticker set state=%s where id=%s', (status, id))
            cr.commit()
        return True

    def set_to_lab(self,cr,uid,ids,context=None):
        status = 'lab'

        for id in ids:
            # report_obj = self.browse(cr, uid, id, context=context)
            # if report_obj.state == 'done':
            #     raise osv.except_osv(_('Warning!'),
            #                          _('Already it is Completed.'))
            cr.execute('update diagnosis_sticker set state=%s where id=%s', (status, id))
            cr.commit()
        return True






    name = fields.Char('No #')
    full_name = fields.Char('Name')
    bill_register_id =fields.Many2one('bill.register','Bill register')
    admission_id =fields.Many2one('leih.admission','Admission ID')
    general_admission_id =fields.Many2one('hospital.admission','Admission ID')
    department_id =fields.Char('Department')
    doctor_id =fields.Many2one('doctors.profile','Checked By')
    test_id =fields.Many2one('examination.entry','Test Name')
    sticker_line_id =fields.One2many('diagnosis.sticker.line','sticker_id','Record Sample')
    state = fields.Selection(
        [('cancel', 'Cancelled'), ('sample', 'Sample'), ('lab', 'Lab'),('done', 'Done'),('delivered','Delivered'),('indoor','Indoor')],
        'Status', required=True, readonly=True, copy=False,
        )



class TestSample(models.Model):
    _name = "diagnosis.sticker.line"


    test_name = fields.Char("Name")
    sticker_id =fields.Many2one('diagnosis.sticker','ID')
    result = fields.Char('Result')
    ref_value = fields.Char('Reference Value')
    bold =fields.Boolean('Bold')
    group_by =fields.Boolean('Group By')
    remarks = fields.Char('Remarks')
