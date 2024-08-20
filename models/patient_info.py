from odoo import api, models, fields

class PatientInfo(models.Model):
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

    @api.model
    def create(self, vals):
        # Call the original create method
        record = super(PatientInfo, self).create(vals)

        # Update patient_id and state after record creation
        if record:
            name_text = f'P-0{record.id}'
            record.write({
                'patient_id': name_text,
                'state': 'created',
            })

        return record

    def write(self, vals):
        # Retrieve the record(s) to be updated
        records = self.browse(self.ids)

        if 'age' in vals:
            new_age = vals['age']
            # Handle age update logic if needed

        # Update the records using the super method
        return super(PatientInfo, self).write(vals)

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        recs = self.browse()
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
