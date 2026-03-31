{
    'name': 'PBMS Session Non-Persistent',
    'version': '1.0',
    'category': 'Security',
    'summary': 'Ensures sessions are non-persistent (logged out on browser/tab close) and 5m inactivity timeout.',
    'author': 'OpenG2P',
    'depends': ['base', 'web'],
    'data': [],
    'assets': {
        'web.assets_backend': [
            'g2p_session_non_persistent/static/src/js/session_tab_logout.js',
        ],
    },
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
