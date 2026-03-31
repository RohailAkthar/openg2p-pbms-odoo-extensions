{
    'name': 'OpenG2P PBMS Rule Access',
    'version': '17.0.1.0.0',
    'category': 'Operations/PBMS',
    'summary': 'Granular access control for Eligibility and Entitlement Rules',
    'depends': ['g2p_pbms'],
    'data': [
        'security/groups.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
