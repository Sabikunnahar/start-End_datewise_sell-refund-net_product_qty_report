# -*- coding: utf-8 -*-
{
    'name': 'Product Report',
    'version': '1.0',
    'summary': 'Product Report module to meet supervisor requirement',
    'sequence': 1,
    'description': """
    Product Report
====================
""",
    'category': 'Report',
    'website': 'odoomates.com',
    'images': [],
    'depends': ['base','stock','sale','bahmni_sale'],
    'data': [
             'reports/report_product_delivery.xml',
             'reports/report_product_shop_wise_delivery_view.xml',
             'wizards/report_wizard_view.xml',
             ],
    'demo': [],
    'qweb': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}
