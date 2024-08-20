from odoo import api, models, fields


class OPDTicket(models.Model):
    _name = "opd.ticket"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "OPD Ticket"

    name = fields.Char(string="OPD Number")
    mobile = fields.Char(string="Mobile")
    patient_id = fields.Char( string="Patient Id")
    patient_name = fields.Many2one('patient.info', string="Patient Name")
    address = fields.Char(string="Address")
    age = fields.Char(string="Age")
    sex = fields.Char(string="Sex")
    already_collected = fields.Boolean(string="Money Collected", default=False)
    # 'date =fields.datetime("Date", readonly=True,default=lambda self: fields.datetime.now())
    date = fields.Date(string="Date", readonly=True, default=lambda self: fields.Datetime.now())
    ref_doctors = fields.Many2one('doctors.profile', string='Referred by')
    opd_ticket_line_id = fields.One2many('opd.ticket.line', 'opd_ticket_id', string='Investigations', required=True)
    user_id = fields.Many2one('res.users', string='Assigned to', select=True,)
    state = fields.Selection(
        [('confirmed', 'Confirmed'), ('cancelled', 'Cancelled')],
        string='Status', default='confirmed')

    total = fields.Float(string="Total")
    with_doctor_total = fields.Float(string="With Doctor Total")

    def _totalpayable(self, cr, uid, ids, field_name, arg, context=None):
        Percentance_calculation = {}
        sum = 0
        for items in self.env["opd.ticket"].browse(cr, uid, ids, context=None):
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
            moves = self.env['account.move'].browse(cr, uid, itm, context=context)
            moves.button_cancel()  ## Cancelling
            moves.unlink()  ### Deleting Journal

        #### Ends Here

        ## Bill Status Will Change

        cr.execute("update opd_ticket set state='cancelled' where id=%s", (ids))
        cr.commit()
        return "C"

    @api.onchange('patient_name')
    def onchange_patient(self):
        self.mobile = self.patient_name.mobile
        self.address = self.patient_name.address
        self.age = self.patient_name.age
        self.sex = self.patient_name.sex
        self.patient_id = self.patient_name.patient_id

    def create(self, vals):
        record = super(OPDTicket, self).create(vals)  # return ID int object
        if record:
            name_text = f'OPD-1{record.id}'
            record.write({
                'name': name_text,

            })
        return record


    @api.onchange('opd_ticket_line_id')
    def onchange_total(self):
        total = 0
        with_doctor_total = 0
        for item in self.opd_ticket_line_id:
            total = total + item.total_amount
            with_doctor_total = with_doctor_total + item.name.total_cash
        self.total = total
        self.with_doctor_total = with_doctor_total

    def write(self, vals):
        return super(OPDTicket, self).write(vals)


class OPDTicketLine(models.Model):
    _name = 'opd.ticket.line'
    _description = "OPD ticket lines "

    name = fields.Many2one("opd.ticket.entry",string="Item Name", ondelete='cascade')
    opd_ticket_id = fields.Many2one('opd.ticket', string="Information")
    price = fields.Integer(string="Price")
    department =fields.Char(string='Department')
    total_amount = fields.Integer(string="Total Amount")

    @api.onchange('name')
    def onchange_item(self):
        self.price = self.name.fee
        self.department = self.name.department.name
        self.total_amount = self.name.fee


class OPDTicketEntry(models.Model):
    _name = "opd.ticket.entry"
    _order = 'id desc'
    _description = "Tkt Entry"

    name = fields.Char(string="Name")
    department = fields.Many2one("diagnosis.department", string="Department")
    fee = fields.Float(string="Fee")
    accounts_id = fields.Many2one('account.account', string="Account ID",required=True)
    total_cash = fields.Float(string="Total Cash")

