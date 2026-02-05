{
    'name': 'G2P Entitlement Verification Rule Definition',
    'version': '17.0.1.0.0',
    'category': 'G2P',
    'summary': 'G2P Entitlement Verification Rule Definition',
    'description': """
        G2P Entitlement Verification Rule Definition
    """,
    'author': 'OpenG2P',
    'website': 'https://openg2p.org',
    'depends': ['g2p_pbms'],
    'data': [
        'security/ir.model.access.csv',
        'views/g2p_entitlement_verification_rule_definition_view.xml',
        'views/g2p_bgtask_summary_wizard_view.xml',
        'views/g2p_program_definition_view.xml',
    ],

    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
