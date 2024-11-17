# -*- coding: utf-8 -*-
{
    'name': "TEOS AI",
    'summary': "AI Development Ollama Models",

    'author': "Ezekiel Victor",
    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Customizations',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base'],
    'images': ['static/description/icon.png'],
    'installable': True,
    'application': True,
    'assets': {
        'web.assets_backend': [
            'teos/static/description/icon.png',
        ],
    },

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
    ],
}

