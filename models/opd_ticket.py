from odoo import api, models, fields


class OPDTicket(models.Model):
    _name = "opd.ticket"
    _description = "OPD Ticket"

    name = fields.Char(string="Name")
    # 'patient_id': fields.char("Patient ID")

    mobile = fields.Char(string="Mobile", store=False)
    # patient_id = fields.Char(related='patient_name.patient_id', string="Patient Id", readonly=True)
    patient_id = fields.Char( string="Patient Id", readonly=True)
    patient_name = fields.Many2one('patient.info', "Patient Name")
    address = fields.Char("Address", store=False)
    age = fields.Char("Age", store=False)
    sex = fields.Char("Sex", store=False)
    already_collected = fields.Boolean("Money Collected", default=False)
    # 'date =fields.datetime("Date", readonly=True,default=lambda self: fields.datetime.now())
    date = fields.Date("Date", readonly=True, default=lambda self: fields.Datetime.now())
    ref_doctors = fields.Many2one('doctors.profile', 'Reffered by')
    opd_ticket_line_id = fields.One2many('opd.ticket.line', 'opd_ticket_id', 'Investigations', required=True)
    user_id = fields.Many2one('res.users', 'Assigned to', select=True,)
    state = fields.Selection(
        [('confirmed', 'Confirmed'), ('cancelled', 'Cancelled')],
        'Status', default='confirmed')


    total = fields.Float(string="Total")
    with_doctor_total = fields.Float(string="with_doctor_total")

    def _totalpayable(self, cr, uid, ids, field_name, arg, context=None):
        Percentance_calculation = {}
        sum = 0
        for items in self.pool.get("opd.ticket").browse(cr, uid, ids, context=None):
            total_list = []
            for amount in items.opd_ticket_line_id:
                total_list.append(amount.total_amount)

            for item in total_list:
                sum = item + sum
                for record in self.browse(cr, uid, ids, context=context):
                    Percentance_calculation[record.id] = sum
                    # import pdb
                    # pdb.set_trace()
        return Percentance_calculation

    def opd_cancel(self, cr, uid, ids, context=None):
        cr.execute(
            "select id as jounral_id from account_move where ref = (select name from opd_ticket where id=%s limit 1)",
            (ids))
        joural_ids = cr.fetchall()
        context = context

        itm = [itm[0] for itm in joural_ids]
        if len(itm) > 0:
            uid = 1
            moves = self.pool.get('account.move').browse(cr, uid, itm, context=context)
            moves.button_cancel()  ## Cancelling
            moves.unlink()  ### Deleting Journal

        #### Ends Here

        ## Bill Status Will Change

        cr.execute("update opd_ticket set state='cancelled' where id=%s", (ids))
        cr.commit()
        return "C"

    # def onchange_total(self, cr, uid, ids, name, context=None):
    #     tests = {'values': {}}
    #     dep_object = self.pool.get('leih.tests').browse(cr, uid, name, context=None)
    #     abc = {'total': dep_object.rate}
    #     tests['value'] = abc
    #     # import pdb
    #     # pdb.set_trace()
    #     return tests
    #
    # def onchange_patient(self, cr, uid, ids, name, context=None):
    #     tests = {}
    #     dep_object = self.pool.get('patient.info').browse(cr, uid, name, context=None)
    #     abc = {'mobile': dep_object.mobile, 'address': dep_object.address, 'age': dep_object.age, 'sex': dep_object.sex}
    #     tests['value'] = abc
    #     return tests

    def create(self, cr, uid, vals, context=None):
        if context is None:
            context = {}

        stored = super(OPDTicket, self).create(cr, uid, vals, context)  # return ID int object

        if stored is not None:

            name_text = 'OPD-0' + str(stored)
            cr.execute('update opd_ticket set name=%s where id=%s', (name_text, stored))
            cr.commit()
            stored_obj = self.browse(cr, uid, stored, context=context)

            ###OPD JOurnal Start Here
            if stored_obj:

                line_ids = []

                if context is None: context = {}
                if context.get('period_id', False):
                    return context.get('period_id')
                periods = self.pool.get('account.period').find(cr, uid, context=context)
                period_id = periods and periods[0] or False
                has_been_paid = stored_obj.total

                line_ids.append((0, 0, {
                    'analytic_account_id': False,
                    'tax_code_id': False,
                    'tax_amount': 0,
                    'name': stored_obj.name,
                    'currency_id': False,
                    'credit': 0,
                    'date_maturity': False,
                    'account_id': 6,  ### Cash ID
                    'debit': has_been_paid,
                    'amount_currency': 0,
                    'partner_id': False,
                }))

                for cc_obj in stored_obj.opd_ticket_line_id:
                    # import pdb
                    # pdb.set_trace()
                    total = 0

                    if cc_obj.name.name:
                        # ledger_id = 611
                        # try:
                        #     ledger_id = cc_obj.name.accounts_id.id
                        # except:
                        #     ledger_id = 611  ## Diagnostic Income Head , If we don't assign any Ledger

                        if context is None:
                            context = {}

                        line_ids.append((0, 0, {
                            'analytic_account_id': False,
                            'tax_code_id': False,
                            'tax_amount': 0,
                            'name': cc_obj.name.name,
                            'currency_id': False,
                            'account_id': cc_obj.name.accounts_id.id,
                            'credit': cc_obj.total_amount,
                            'date_maturity': False,
                            'debit': 0,
                            'amount_currency': 0,
                            'partner_id': False,
                        }))
                    # import pdb
                    # pdb.set_trace()

                jv_entry = self.pool.get('account.move')

                j_vals = {'name': '/',
                          'journal_id': 2,  ## Sales Journal
                          'date': stored_obj.date,
                          'period_id': period_id,
                          'ref': stored_obj.name,
                          'line_id': line_ids

                          }

                # import pdb
                # pdb.set_trace()

                saved_jv_id = jv_entry.create(cr, uid, j_vals, context=context)
                if saved_jv_id > 0:
                    journal_id = saved_jv_id
                    try:

                        jv_entry.button_validate(cr, uid, [saved_jv_id], context)
                    except:
                        cr.execute("delete from opd_ticket where id=%s", ([stored]))
                        cr.commit()
                        raise Exception("Check the item, missmatched total!")
            ###ENd of Journal
            return stored

    @api.onchange('opd_ticket_line_id')
    def onchange_total(self):
        total = 0
        with_doctor_total = 0
        for item in self.opd_ticket_line_id:
            total = total + item.total_amount
            with_doctor_total = with_doctor_total + item.name.total_cash
        self.total = total
        self.with_doctor_total = with_doctor_total

    def write(self, cr, uid, ids, vals, context=None):
        if vals.get('opd_ticket_line_id') or uid == 1:
            cr.execute(
                "select id as journal_ids from account_move where ref = (select name from opd_ticket where id=%s limit 1)",
                (ids))
            journal_ids = cr.fetchall()
            context = context
            updated = super(OPDTicket, self).write(cr, uid, ids, vals, context=context)
            itm = [itm[0] for itm in journal_ids]
            if len(itm) > 0:
                uid = 1
                moves = self.pool.get('account.move').browse(cr, uid, itm, context=context)
                xx = moves.button_cancel()  ## Cancelling
                moves.unlink()

                stored_obj = self.browse(cr, uid, [ids[0]], context=context)
                if stored_obj:

                    line_ids = []

                    if context is None: context = {}
                    if context.get('period_id', False):
                        return context.get('period_id')
                    periods = self.pool.get('account.period').find(cr, uid, context=context)
                    period_id = periods and periods[0] or False
                    has_been_paid = stored_obj.total

                    line_ids.append((0, 0, {
                        'analytic_account_id': False,
                        'tax_code_id': False,
                        'tax_amount': 0,
                        'name': stored_obj.name,
                        'currency_id': False,
                        'credit': 0,
                        'date_maturity': False,
                        'account_id': 6,  ### Cash ID
                        'debit': has_been_paid,
                        'amount_currency': 0,
                        'partner_id': False,
                    }))

                    for cc_obj in stored_obj.opd_ticket_line_id:
                        # import pdb
                        # pdb.set_trace()
                        total = 0

                        if cc_obj.name.name:
                            # ledger_id = 611
                            # try:
                            #     ledger_id = cc_obj.name.accounts_id.id
                            # except:
                            #     ledger_id = 611  ## Diagnostic Income Head , If we don't assign any Ledger

                            if context is None:
                                context = {}

                            line_ids.append((0, 0, {
                                'analytic_account_id': False,
                                'tax_code_id': False,
                                'tax_amount': 0,
                                'name': cc_obj.name.name,
                                'currency_id': False,
                                'account_id': cc_obj.name.accounts_id.id,
                                'credit': cc_obj.total_amount,
                                'date_maturity': False,
                                'debit': 0,
                                'amount_currency': 0,
                                'partner_id': False,
                            }))
                        # import pdb
                        # pdb.set_trace()

                    jv_entry = self.pool.get('account.move')

                    j_vals = {'name': '/',
                              'journal_id': 2,  ## Sales Journal
                              'date': stored_obj.date,
                              'period_id': period_id,
                              'ref': stored_obj.name,
                              'line_id': line_ids

                              }

                    # import pdb
                    # pdb.set_trace()

                    saved_jv_id = jv_entry.create(cr, uid, j_vals, context=context)
                    if saved_jv_id > 0:
                        journal_id = saved_jv_id
                        try:

                            jv_entry.button_validate(cr, uid, [saved_jv_id], context)
                        except:
                            import pdb
                            pdb.set_trace()
                    return updated
                    ### Ends the journal Entry Here
            else:
                updated = super(OPDTicket, self).write(cr, uid, ids, vals, context=context)
                # raise osv.except_osv(_('Warning!'),
                #                      _("You cannot Edit the bill"))
                return updated


class test_information(models.Model):
    _name = 'opd.ticket.line'
    _description = "OPD ticket lines "

    name = fields.Many2one("opd.ticket.entry","Item Name", ondelete='cascade')
    opd_ticket_id = fields.Many2one('opd.ticket', "Information")
    price = fields.Integer("Price")
    department =fields.Char('Department')
    total_amount = fields.Integer("Total Amount")

    # def onchange_item(self, cr, uid, ids, name, context=None):
    #     tests = {'values': {}}
    #     dep_object = self.pool.get('opd.ticket.entry').browse(cr, uid, name, context=None)
    #     abc = {'price': dep_object.fee, 'department': dep_object.department.name, 'total_amount': dep_object.fee}
    #     tests['value'] = abc
    #     # import pdb
    #     # pdb.set_trace()
    #     return tests





class opd_ticket_config(models.Model):
    _name = "opd.ticket.entry"
    _order = 'id desc'
    _description = "Tkt Entry"

    name = fields.Char("Name")
    department = fields.Many2one("diagnosis.department","Department")
    fee = fields.Float("Fee")
    accounts_id = fields.Many2one('account.account',"Account ID",required=True)
    total_cash = fields.Float("Total Cash")

