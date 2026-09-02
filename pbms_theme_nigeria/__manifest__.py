{
    "name": "PBMS Nigeria Branding Theme",
    "category": "G2P/Theme",
    "version": "1.0.0",
    "sequence": 1,
    "summary": "Official Federal Republic of Nigeria Branding and Theme for PBMS",
    "author": "OpenG2P / Nigeria Social Protection",
    "website": "https://openg2p.org",
    "license": "LGPL-3",
    "depends": [
        "base",
        "web",
        "pbms_theme_extension",
    ],
    "data": [
        "views/webclient_templates.xml",
        "templates/login_templates.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "pbms_theme_nigeria/static/src/js/nigeria_window_title.js",
            "pbms_theme_nigeria/static/src/css/nigeria_navbar.css",
        ],
        "web.assets_frontend": [
            "pbms_theme_nigeria/static/src/scss/nigeria_login.scss",
        ],
    },
    "post_init_hook": "post_init_hook",
    "application": False,
    "installable": True,
    "auto_install": False,
}
