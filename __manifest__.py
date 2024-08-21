# -*- coding: utf-8 -*-

{
    'name': 'Medical Management System',
    'version': '17.0.0.1',
    'category': 'Medical',
    'description': 'Medical Management System',
    'summary': 'Medical Management System',
    'sequence': '1',
    'author': 'Mufti Muntasir & Kazi & Rocky',
    'license': 'LGPL-3',
    'company': 'Aurora IT Ltd',
    # 'maintainer': 'Odoo Mates',
    # 'support': 'odoomates@gmail.com',
    # 'website': 'https://www.youtube.com/watch?v=yA4NLwOLZms',
    'depends': ['base','om_account_accountant'],
    # 'live_test_url': 'https://www.youtube.com/watch?v=yA4NLwOLZms',
    'data': [
        'security/ir.model.access.csv',
        'views/menu.xml',
        'views/opd_ticket_view.xml',
        'views/opd_ticket_entry_view.xml',
        'views/department_view.xml',
        'views/diagonosisgroup_view.xml',
        'views/examinationentry_view.xml',
        'views/sample_type_view.xml',
        'views/exmine_package_view.xml',
        'views/blood_donar.xml',
        'views/blood_receiver.xml',
        'views/patients_view.xml',
        'views/products_lens_view.xml',
        'views/optics_sale_view.xml',
        'views/advance_cash_view.xml',
        'views/bill_register_view.xml',
        'views/broker_info_view.xml',
        'views/doctors_view.xml',
        'views/commission_view.xml',
        'views/commission_calculation_view.xml',
        'views/commission_configuration_view.xml',
        'views/commission_payment_view.xml',
        'views/sticker_view.xml',
        'views/payment_type_view.xml',
        'views/leih_admission_view.xml',
        'views/leih_admission_activated_view.xml',
        'views/leih_admission_cancelled_view.xml',
        'views/inventory_product_entry_view.xml',
        'views/inventory_product_entry_verified_view.xml',
        'views/inventory_product_entry_confirmed_view.xml',
        'views/inventory_requisition_view.xml',
        'views/money_receipt_view.xml',
        'views/bill_register_payment_view.xml',
        'views/admission_payment_view.xml',
        

        'report/action_report_menu.xml',
        'report/report_bill_register.xml',
        'report/report_opd_ticket.xml',
        'report/report_leih_admission.xml',

    ],
    # 'images': ['static/description/banner.gif'],
    'application': True,
}
