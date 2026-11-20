{
    "name": "PBMS Knowledge Management",
    "category": "G2P",
    "version": "1.0.0",
    "summary": "In-app knowledge library: user manual, setup guides and workflow guides for PBMS",
    "author": "OpenG2P / Nigeria Social Protection",
    "website": "https://openg2p.org",
    "license": "LGPL-3",
    "depends": ["web", "g2p_pbms", "pbms_theme_nigeria"],
    "data": ["views/menu.xml"],
    "assets": {
        "web.assets_backend": [
            "pbms_knowledge/static/src/scss/knowledge.scss",
            "pbms_knowledge/static/src/js/guides_data.js",
            "pbms_knowledge/static/src/js/knowledge.js",
            "pbms_knowledge/static/src/xml/knowledge.xml",
        ],
    },
    "application": False,
    "installable": True,
    "auto_install": False,
}
