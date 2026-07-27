{
    "name": "G2P Disbursement Beneficiaries Export Addon",
    "summary": "Streaming CSV Export of Beneficiaries for Disbursement Lists",
    "version": "17.0.1.0.0",
    "category": "G2P",
    "author": "OpenG2P",
    "website": "https://openg2p.org",
    "license": "LGPL-3",
    "depends": [
        "base",
        "web",
        "g2p_pbms",
        "g2p_registry_addon"
    ],
    "data": [],
    "assets": {
        "web.assets_backend": [
            "g2p_disbursement_export_addon/static/src/js/disbursement_export_widget.js",
            "g2p_disbursement_export_addon/static/src/xml/disbursement_export_tpl.xml"
        ]
    },
    "installable": True,
    "application": False,
    "auto_install": False
}
