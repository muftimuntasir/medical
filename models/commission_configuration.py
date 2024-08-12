from odoo import models, fields, api, _


class CommissionConfiguration(models.Model):
    _name = "commission.configuration"
    _description = "Commission Configuration"

    name = fields.Char("Name")
    doctor_id = fields.Many2one('doctors.profile', 'Doctor/SR Name')
    broker_id = fields.Many2one('brokers.info', 'Broker Name')
    start_date = fields.Date('MOU Start Date')
    end_date = fields.Date('MOU End Date')
    overall_commission_rate = fields.Float('Overall Commission Rate (%)')
    overall_default_discount = fields.Float('Overall Discount Rate (%)')
    max_default_discount = fields.Float('Max Discount Rate (%)')
    deduct_from_discount = fields.Boolean("Deduct Excess Discount From Commission")
    add_few_departments = fields.Boolean("Add by Department")
    calculation_base_price = fields.Boolean("Calculation on Base Price")
    department_ids = fields.Many2one('diagnosis.department', 'Department List')

    commission_configuration_line_ids = fields.One2many("commission.configuration.line", 'commission_configuration_id',
                                                        "Commission Lines")
    state = fields.Selection(
        [('pending', 'Pending'), ('done', 'Confirmed'), ('cancelled', 'Cancelled')],
        'Status', default='pending', readonly=True)

    @api.model
    def create(self, vals):
        record = super(CommissionConfiguration, self).create(vals)
        record.name = 'CA-0' + str(record.id)
        return record

    @api.onchange('overall_commission_rate')
    def add_tests_ids_in_line_with_rate(self):
        if self.overall_commission_rate:
            comm_rate = round((self.overall_commission_rate / 100), 2)
            line_data = []
            if self.commission_configuration_line_ids:
                for item in self.commission_configuration_line_ids:
                    est_comm = round((comm_rate * item.test_price), 2)
                    line_data.append({
                        'department_id': item.department_id.id,
                        'test_id': item.test_id.id,
                        'applicable': item.applicable,
                        'fixed_amount': item.fixed_amount,
                        'variance_amount': comm_rate,
                        'test_price': item.test_price,
                        'est_commission_amount': est_comm,
                        'max_commission_amount': item.max_commission_amount
                    })
            self.commission_configuration_line_ids = line_data

    @api.onchange('department_ids')
    def add_tests_ids_in_line(self):
        comm_rate = round((self.overall_commission_rate / 100), 2) if self.overall_commission_rate else 0
        if self.department_ids:
            department_id = self.department_ids.id
            query = "SELECT id, name, department, rate FROM examination_entry WHERE department=%s"
            self._cr.execute(query, [department_id])
            all_data = self._cr.dictfetchall()
            configure_line = []
            already_exist_item = [item.test_id.id for item in
                                  self.commission_configuration_line_ids] if self.commission_configuration_line_ids else []

            for item in self.commission_configuration_line_ids:
                est_comm = round((comm_rate * item.test_price), 2)
                configure_line.append({
                    'department_id': item.department_id.id,
                    'test_id': item.test_id.id,
                    'applicable': item.applicable,
                    'fixed_amount': item.fixed_amount,
                    'variance_amount': comm_rate,
                    'test_price': item.test_price,
                    'est_commission_amount': est_comm,
                    'max_commission_amount': item.max_commission_amount
                })

            for item in all_data:
                est_amnt = round((comm_rate * item.get('rate')), 2)
                if item.get('id') not in already_exist_item:
                    configure_line.append({
                        'department_id': item.get('department'),
                        'test_id': item.get('id'),
                        'applicable': True,
                        'fixed_amount': 0,
                        'variance_amount': 0,
                        'test_price': item.get('rate'),
                        'est_commission_amount': est_amnt,
                        'max_commission_amount': 0
                    })
            self.commission_configuration_line_ids = configure_line

    @api.onchange('calculation_base_price')
    def base_price_applicable_in_line(self):
        if self.calculation_base_price:
            if self.department_ids and self.commission_configuration_line_ids:
                for item in self.commission_configuration_line_ids:
                    if self.department_ids.id == item.department_id.id:
                        item.base_price_applicable = True
        else:
            if self.department_ids and self.commission_configuration_line_ids:
                for item in self.commission_configuration_line_ids:
                    if self.department_ids.id == item.department_id.id:
                        item.base_price_applicable = False

    def confirm_configuration(self):
        for config in self:
            if config.state == 'done':
                raise UserError(_('Already Confirmed!'))

            existing_config = self.search([('doctor_id', '=', config.doctor_id.id), ('state', '=', 'done')])
            if existing_config:
                raise UserError(_("There is a commission configuration associated with the doctor"))

            config.write({'state': 'done'})

    def cancel_configuration(self):
        for config in self:
            if config.state == 'done':
                raise UserError(_('Already Confirmed!'))

            config.write({'state': 'cancelled'})


class CommissionConfigurationLine(models.Model):
    _name = "commission.configuration.line"
    _description = "Commission Configuration Line"

    commission_configuration_id = fields.Many2one('commission.configuration', 'Commission Configuration ID')
    department_id = fields.Many2one('diagnosis.department', 'Department')
    test_id = fields.Many2one('examination.entry', 'Test Name')
    base_price_applicable = fields.Boolean('Base Price Applicable')
    applicable = fields.Boolean('Applicable')
    fixed_amount = fields.Float('Fixed Amount')
    variance_amount = fields.Float('Amount (%)')
    test_price = fields.Float('Test Fee')
    est_commission_amount = fields.Float('Commission Amount')
    max_commission_amount = fields.Float('Max Commission Amount')


class DoctorsProfile(models.Model):
    _inherit = "doctors.profile"

    cc_id = fields.Many2one('commission.configuration', 'Commission Rule')
