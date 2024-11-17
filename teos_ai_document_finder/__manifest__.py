# -*- coding: utf-8 -*-
{
    'name': "TEOS AI",
    'summary': "AI Development Ollama Models",

    'author': "Ezekiel Victor",
    'category': 'Customizations',
    "version": "17.0.1.3.0",
    'depends': ['base', 'web'],
    'images': ['static/description/icon.png'],
    'installable': True,
    'auto_install': False,
    'application': True,
    'assets': {
        'web.assets_backend': [
            'teos_ai_document_finder/static/description/icon.png',
            'teos_ai_document_finder/static/src/ai_helper/chatgpt_prompt_dialog.js',
            'teos_ai_document_finder/static/src/ai_helper/ai_helper_menu.js',
            'teos_ai_document_finder/static/src/ai_helper/ai_help_menu.xml',
            ('include', 'web_editor.backend_assets_wysiwyg'),
        ],
        'web_editor.assets_wysiwyg':
            ['teos_ai_document_finder/static/src/ai_helper/ai_prompt_dialogue.xml'],
        'web._assets_core': [
            'teos_ai_document_finder/static/src/ai_helper/user_service.js',
        ],
    },
    # always loaded
    'data': [
        'security/base_groups.xml',
        'security/ir.model.access.csv',
        'views/res_user.xml',
        'views/test_login_wizard.xml',
        'views/menu.xml',
        'views/app_view.xml',
        'views/ai_setting.xml',
    ],
}

