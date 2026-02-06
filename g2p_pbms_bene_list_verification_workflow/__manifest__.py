{
    "name": "PBMS Beneficiary List Verification Workflow",
    "version": "3.0.0",
    "summary": "OpenG2P Beneficiary list linear hierarchy verification Workflow",
    "description": "OpenG2P Beneficiary list linear hierarchy verification Workflow",
    "category": "G2P",
    "license": "LGPL-3",
    "depends": ["g2p_pbms"],
    "data": [
        "security/ir.model.access.csv",
        "views/verification/entitlement_verification_rule_definition_view.xml",
        "views/verification/disbursement_verification_rule_definition_view.xml",
        "views/program/program_definition_view.xml",
        "views/beneficiary_list/bgtask_summary_wizard_view.xml",
    ],
    "assets": {
        "web.assets_backend": [],
    },
    "installable": True,
    "application": False,
    "auto_install": False,
}
