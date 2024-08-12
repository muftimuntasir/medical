from odoo import models, fields, api, _

class Commission(models.Model):
    _name = "commission"
    _description = "Commission Calculation"

    name = fields.Char("Commission Calculation", readonly=True, default=lambda self: _('New'))
    ref_doctors = fields.Many2one('doctors.profile', 'Doctor/Broker Name')
    commission_configuration_id = fields.Many2one('commission.configuration', 'Commission Rule')
    commission_rate = fields.Float('Commission Rate')
    cal_st_date = fields.Datetime("Calculation Start Date", required=True)
    cal_end_date = fields.Datetime("Calculation End Date", required=True)
    total_amount = fields.Float('Total Commission Amount', readonly=True, compute='_compute_total_amount', store=True)
    given_discount_amount = fields.Float('Total Discount', readonly=True, compute='_compute_given_discount_amount', store=True)
    total_payable_amount = fields.Float('Total Payable Amount', readonly=True, compute='_compute_total_payable_amount', store=True)
    total_patient = fields.Float('Total Patients', readonly=True, compute='_compute_total_patient', store=True)
    total_bill = fields.Float('Total Billing Amount', readonly=True, compute='_compute_total_bill', store=True)
    total_tests = fields.Float('Total Tests in All Billing', readonly=True, compute='_compute_total_tests', store=True)
    paid_amount = fields.Float('Paid Amount', readonly=True)
    commission_line_ids = fields.One2many('commission.line', 'commission_id', "Commission Lines")
    state = fields.Selection([('pending', 'Pending'), ('done', 'Confirmed'), ('paid', 'Paid & Close'), ('cancelled', 'Cancelled')], 'Status', default='pending', readonly=True)

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('commission') or _('New')
        return super(Commission, self).create(vals)

    def btn_pay_bill(self):
        self.ensure_one()
        view_id = self.env.ref('leih.commission_payment_form_view').id
        return {
            'name': _("Payment"),
            'view_mode': 'form',
            'view_id': view_id,
            'view_type': 'form',
            'res_model': 'commission.payment',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
            'context': {
                'default_cc_id': self.id,
                'default_doctor_id': self.ref_doctors.id,
                'default_paid_amount': self.total_payable_amount,
            }
        }

    def confirm_commission(self):
        self.write({'state': 'done'})

    def cancel_commission(self):
        self.write({'state': 'cancelled'})

    @api.onchange('ref_doctors', 'cal_st_date', 'cal_end_date')
    def customer_on_select(self):
        if not self.ref_doctors:
            return

        if not self.cal_st_date or not self.cal_end_date:
            raise ValidationError(_('Please select Start and End Date of Calculation'))

        st_date = self.cal_st_date
        end_date = self.cal_end_date
        commissioner_id = self.ref_doctors.id

        commission_rate = self.env['doctors.profile'].browse(commissioner_id).commission_rate or 0.0
        commission_rate = round(commission_rate / 100, 2)

        doctor_ids = [commissioner_id] + self.env['doctors.profile'].search([('referral_id', '=', commissioner_id), ('status', '=', 'active')]).ids

        commission_configuration = self.env['commission.configuration'].search([('doctor_id', '=', commissioner_id)])

        comm_configuration_data = self.env['commission.configuration.line'].search([
            ('commission_configuration_id', 'in', commission_configuration.ids),
            ('applicable', '=', True)
        ])

        configured_test_ids = comm_configuration_data.mapped('test_id')

        last_commission = self.search([('ref_doctors', '=', commissioner_id), ('state', '=', 'done')], order='cal_end_date desc', limit=1)
        last_confirmed_date = last_commission.cal_end_date if last_commission else st_date

        bill_lines = self.env['bill.register.line'].search([
            ('bill_register_id.ref_doctors', 'in', doctor_ids),
            ('name', 'in', configured_test_ids),
            ('bill_register.date', '>=', last_confirmed_date),
            ('bill_register.date', '<=', end_date),
            ('bill_register.state', '=', 'confirmed'),
            ('commission_paid', '=', False)
        ])

        order_payment_lines = []
        total_amount = 0
        total_billing_amount = 0
        total_test_count = 0

        for bill_item in bill_lines:
            for config in comm_configuration_data:
                if config.test_id == bill_item.name:
                    total_test_count += 1
                    billed_amount = bill_item.total_amount
                    max_cap_amount = config.max_commission_amount
                    fixed_amount = config.fixed_amount
                    variance_amount = config.variance_amount

                    cal_pay_amount = max_cap_amount if max_cap_amount > 0 and (variance_amount * billed_amount) > max_cap_amount else (variance_amount * billed_amount)

                    if fixed_amount > 0:
                        cal_pay_amount = fixed_amount

                    order_payment_lines.append({
                        'department_id': config.department_id.id,
                        'name': bill_item.name.id,
                        'discount_amount': bill_item.discount_percent,
                        'test_amount': billed_amount,
                        'mou_payable_comm_var': variance_amount,
                        'mou_payable_comm_fixed': fixed_amount,
                        'mou_payable_comm_max_cap': max_cap_amount,
                        'payable_amount': cal_pay_amount,
                    })
                    total_billing_amount += billed_amount
                    total_amount += cal_pay_amount
                    break

        self.commission_line_ids = [(0, 0, line) for line in order_payment_lines]
        self.total_amount = total_amount
        self.commission_rate = commission_rate
        self.total_bill = total_billing_amount
        self.total_tests = total_test_count

    @api.depends('commission_line_ids.payable_amount')
    def _compute_total_amount(self):
        for record in self:
            record.total_amount = sum(line.payable_amount for line in record.commission_line_ids)

    @api.depends('commission_line_ids.discount_amount')
    def _compute_given_discount_amount(self):
        for record in self:
            record.given_discount_amount = sum(line.discount_amount for line in record.commission_line_ids)

    @api.depends('commission_line_ids.test_amount')
    def _compute_total_bill(self):
        for record in self:
            record.total_bill = sum(line.test_amount for line in record.commission_line_ids)

    @api.depends('commission_line_ids')
    def _compute_total_tests(self):
        for record in self:
            record.total_tests = len(record.commission_line_ids)

    @api.depends('total_amount', 'given_discount_amount')
    def _compute_total_payable_amount(self):
        for record in self:
            record.total_payable_amount = record.total_amount - record.given_discount_amount


class CommissionLine(models.Model):
    _name = "commission.line"
    _description = "Commission Line"

    commission_id = fields.Many2one('commission', 'Commission')
    department_id = fields.Many2one("diagnosis.department", "Department")
    name = fields.Many2one("examination.entry", "Test Name")
    discount_amount = fields.Float('Discount Amount')
    test_amount = fields.Float('Test Amount')
    mou_payable_comm_var = fields.Float('MOU Payable Commission Amount (%)')
    mou_payable_comm_fixed = fields.Float('MOU Payable Commission Fixed')
    mou_payable_comm_max_cap = fields.Float('MOU Max CAP Amount')
    after_discount = fields.Float('After Discount Amount')
    payable_amount = fields.Float('Payable Amount')

    @api.onchange('commission_rate')
    def commission_rate_change(self):
        if self.commission_rate:
            self.payable_amount = round((self.test_amount * (self.commission_rate / 100)), 2)
        else:
            self.payable_amount = 0
