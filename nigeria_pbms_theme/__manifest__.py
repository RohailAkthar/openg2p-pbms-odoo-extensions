{
    "name": "Nigeria PBMS: Theme Overrides",
    "category": "G2P",
    "version": "17.0.1.0.0",
    "sequence": 2,
    "author": "OpenG2P Nigeria",
    "website": "https://openg2p.org",
    "license": "LGPL-3",
    "depends": ["pbms_theme_extension", "g2p_pbms"],
    "data": [
        "views/web_templates.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "nigeria_pbms_theme/static/src/js/g2p_window_title.js",
            "nigeria_pbms_theme/static/src/css/style.css",
        ],
        "web.assets_frontend": [
            "nigeria_pbms_theme/static/src/scss/g2p_login_page.scss",
        ],
    },
    "installable": True,
    "auto_install": False,
}
