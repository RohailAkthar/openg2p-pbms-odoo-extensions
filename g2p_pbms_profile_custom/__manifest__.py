{
    'name': 'PBMS Profile Custom',
    'version': '1.0',
    'category': 'G2P',
    'summary': 'Customizes the user profile display in the top bar.',
    'author': 'G2P',
    'depends': ['web'],
    'data': [],
    'assets': {
        'web.assets_backend': [
            'g2p_pbms_profile_custom/static/src/xml/user_menu.xml',
            'g2p_pbms_profile_custom/static/src/css/user_menu.css',
        ],
    },
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
