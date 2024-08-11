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
    'depends': ['base'],
    # 'live_test_url': 'https://www.youtube.com/watch?v=yA4NLwOLZms',
    'data': [
        'security/ir.model.access.csv',
        'views/menu.xml',
        'views/opd_ticket_view.xml',
        'views/opd_ticket_view.xml',
    ],
    # 'images': ['static/description/banner.gif'],
    'application': True,
}
