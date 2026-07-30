{
    "name": "PBMS Beneficiary List Disbursement Verification Workflow",
    "version": "17.0.1.0.0",
    "summary": "OpenG2P Beneficiary list linear hierarchy disbursement verification workflow",
    "description": "OpenG2P Beneficiary list linear hierarchy disbursement verification workflow",
    "category": "G2P",
    "license": "LGPL-3",
    "depends": ["g2p_pbms"],
    "data": [
        "security/ir.model.access.csv",
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
