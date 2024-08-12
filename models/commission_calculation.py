from odoo import models, fields, api, _

class CommissionCalculation(models.Model):
    _name = "commission.calculation"
    _description = "Commission Calculation"

    name = fields.Char("Name")
    doctor_id = fields.Many2one('doctors.profile', 'Doctor/Broker Name')
    start_date = fields.Date('Calculation Start Date')
    end_date = fields.Date('Calculation End Date')
    total_commission_amount = fields.Float('Total Commission Amount', compute='_compute_total_commission_amount', store=True)
    given_discount_amount = fields.Float('Total Discount Amount', compute='_compute_given_discount_amount', store=True)
    total_payable_amount = fields.Float('Total Payable Amount', compute='_compute_total_payable_amount', store=True)
    no_of_total_patient = fields.Float('Total Patients', compute='_compute_no_of_total_patient', store=True)
    no_of_total_bill = fields.Float('Total Bill', compute='_compute_no_of_total_bill', store=True)
    no_of_total_bill_amount = fields.Float('Total Bill Amount', compute='_compute_no_of_total_bill_amount', store=True)
    no_of_total_test = fields.Float('Total Test', compute='_compute_no_of_total_test', store=True)

    commission_calculation_line_ids = fields.One2many("commission.calculation.line", 'commission_calculation_id', "Commission Lines")
    status = fields.Selection(
        [('pending', 'Pending'), ('done', 'Confirmed'), ('cancelled', 'Cancelled'), ('close', 'Closed')],
        'Status', default='pending', readonly=True)
    state = fields.Selection(
        [('pending', 'Unpaid'), ('partially_paid', 'Partially Paid'), ('paid', 'Paid')],
        'State', default='pending', readonly=True)

    @api.depends('commission_calculation_line_ids')
    def _compute_total_commission_amount(self):
        for record in self:
            record.total_commission_amount = sum(line.payble_amount for line in record.commission_calculation_line_ids)

    @api.depends('commission_calculation_line_ids')
    def _compute_given_discount_amount(self):
        for record in self:
            record.given_discount_amount = sum(line.discount_amount for line in record.commission_calculation_line_ids)

    @api.depends('commission_calculation_line_ids')
    def _compute_total_payable_amount(self):
        for record in self:
            record.total_payable_amount = sum(line.payble_amount for line in record.commission_calculation_line_ids) - record.given_discount_amount

    @api.depends('commission_calculation_line_ids')
    def _compute_no_of_total_patient(self):
        for record in self:
            record.no_of_total_patient = len(set(line.test_id.patient_id.id for line in record.commission_calculation_line_ids if line.test_id.patient_id))

    @api.depends('commission_calculation_line_ids')
    def _compute_no_of_total_bill(self):
        for record in self:
            record.no_of_total_bill = len(record.commission_calculation_line_ids)

    @api.depends('commission_calculation_line_ids')
    def _compute_no_of_total_bill_amount(self):
        for record in self:
            record.no_of_total_bill_amount = sum(line.test_amount for line in record.commission_calculation_line_ids)

    @api.depends('commission_calculation_line_ids')
    def _compute_no_of_total_test(self):
        for record in self:
            record.no_of_total_test = len(record.commission_calculation_line_ids)


class CommissionCalculationLine(models.Model):
    _name = "commission.calculation.line"
    _description = "Commission Calculation Line"

    commission_calculation_id = fields.Many2one('commission.calculation', 'Commission Calculation ID')
    department_id = fields.Many2one('diagnosis.department', 'Department')
    test_id = fields.Many2one('examination.entry', 'Test Name')
    discount_amount = fields.Float('Discount Amount')
    test_amount = fields.Float('Test Amount')
    mou_payable_commission_var = fields.Float('MOU Payable Commission (%)')
    mou_payable_commission = fields.Float('MOU Payable Commission Fixed')
    payble_amount = fields.Float('Payable Amount')
    after_discount_amount = fields.Float('After Discount Amount')
    mou_max_cap = fields.Float('MOU Max Cap Amount')
