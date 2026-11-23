{
    "name": "PBMS Role-Based Access (Nigeria)",
    "category": "G2P",
    "version": "1.0.0",
    "summary": "ADMINISTRATION area for PBMS super administrators, simplified user access management",
    "description": """
Role-based access for the NSIPA PBMS:

* The ADMINISTRATION sidebar section (User Access Settings, Developer Apps, General Settings)
  is shown only to users with OpenG2P PBMS > Program Super Administration, which also grants
  Odoo administrator (Settings) rights so those pages open.
* A user's Access Rights tab shows only the OpenG2P PBMS and OpenG2P Documents Module roles,
  with or without debug mode.
* "New user" opens a compact pop-up (Name, Email, Administration).
* The three ADMINISTRATION pages use the PBMS look (page header, cards, settings rows).
""",
    "author": "OpenG2P / Nigeria Social Protection",
    "website": "https://openg2p.org",
    "license": "LGPL-3",
    "depends": [
        "base",
        "base_setup",
        "web",
        "g2p_pbms",
        "g2p_documents",
        "auth_totp",
        "pbms_theme_nigeria",
    ],
    "data": [
        "security/groups.xml",
        "views/res_users_views.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "pbms_rbac_nigeria/static/src/js/admin_sidebar.js",
            "pbms_rbac_nigeria/static/src/xml/admin_sidebar.xml",
            "pbms_rbac_nigeria/static/src/scss/admin_sidebar.scss",
            "pbms_rbac_nigeria/static/src/js/admin_pages.js",
            "pbms_rbac_nigeria/static/src/xml/admin_pages.xml",
            "pbms_rbac_nigeria/static/src/scss/admin_pages.scss",
            "pbms_rbac_nigeria/static/src/scss/user_access.scss",
        ],
    },
    "application": False,
    "installable": True,
    "auto_install": False,
}
