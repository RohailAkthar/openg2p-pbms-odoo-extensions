{
    'name': 'PBMS Profile Custom',
    'version': '1.0',
    'category': 'G2P',
    'summary': 'Customizes the user profile display in the top bar.',
    'author': 'G2P',
    'depends': ['base', 'web', 'mail'],
    'data': [
        'views/res_users_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'g2p_pbms_profile_custom/static/src/xml/user_menu.xml',
            'g2p_pbms_profile_custom/static/src/css/user_menu.css',
            'g2p_pbms_profile_custom/static/src/js/ui_cleanup.js',
            'g2p_pbms_profile_custom/static/src/js/remove_import_menu.js',
        ],
    },
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
