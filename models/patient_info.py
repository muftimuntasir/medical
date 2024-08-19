from odoo import api, models, fields

class patient_info(models.Model):
    _name = "patient.info"


    def name_get(self):
        result = []
        for record in self:
            name = record.name
            if record.patient_id:
                name += ' ' + str(record.patient_id)
            else:
                name += ' ---'
            result.append((record.id, name))
        return result



    def _testname(self,cr,uid,ids,field_name, arg, context=None):
        result={}
        tes_id =[]
        abc=[]
        patient_id=self.browse(cr,uid,ids,context=None)
        for items in patient_id:
            abc.append(items.id)



        bill_id=self.pool.get('bill.register').search(cr,uid,[('patient_name', '=', abc)],context=None)
        test_history = self.pool.get('bill.register').browse(cr, uid, bill_id, context=None)
        xyz=[]
        for testname in test_history:
            for datas in testname.bill_register_line_id.name:
                xyz.append(datas)
        abcd = []
        for item in xyz:
            for items in self.browse(cr,uid,ids,context=None):
            # import pdb
            # pdb.set_trace()
                abcd.append(item.name)
                result[items.id]=abcd

        return result


    @api.constrains('mobile')
    def _check_mobile(self):

        for rec in self:

            if rec.mobile and len(rec.mobile) != 11:

                raise ValidationError(_("Mobile Number Should be 11 digit"))

        return True




    mobile= fields.Char("Mobile No")
    patient_id= fields.Char("Patient Id", readonly=True)
    name=fields.Char("Name", required=True)
    age=fields.Char('Age')
    address=fields.Char('Address',required=True)
    sex= fields.Selection([('male', 'Male'), ('female', 'Female'),('others','Others')], string='Sex', default='male')
    # bills=fields.One2many('bill.register','patient_name','Bill History',required=False)
    testname=fields.Char('Char')
    state= fields.Selection(
        [('created', 'Created'), ('notcreated', 'Notcreated')],
        'Status', default='notcreated', readonly=True)


    def create(self, cr, uid, vals, context=None):

        stored_id=super(patient_info, self).create(cr, uid, vals, context=context)
        if stored_id is not None:
            name_text = 'P-0' + str(stored_id)
            cr.execute('update patient_info set patient_id=%s where id=%s', (name_text, stored_id))
            cr.execute('update patient_info set state=%s where id=%s', ('created', stored_id))
            cr.commit()

        return stored_id

    def write(self, cr, uid, ids, vals, context=None):
        change_patient= self.browse(cr, uid, ids, context)
        if "age" in vals:
            newage=vals['age']
        # query="select name from opd_ticket where patient_id=%"
        # cr.execute(query, (ids))
        # import pdb
        # pdb.set_trace()

        return super(patient_info, self).write(cr, uid, ids, vals, context=context)

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        recs = self.browse()
        # test_val=self.search([])

        if name:
            recs = self.search([('patient_id', '=', name)] + args, limit=limit)

        # import pdb
        # pdb.set_trace()
        if not recs:
            recs = self.search([('patient_id', operator, name)] + args, limit=limit)
        if not recs:
            recs = self.search([('name', operator, name)] + args, limit=limit)
        if not recs:
            recs = self.search([('mobile', operator,name)] + args, limit=limit)

        return recs.name_get()
