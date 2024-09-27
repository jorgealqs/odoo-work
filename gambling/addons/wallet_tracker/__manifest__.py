{
    'name': 'Wallet Tracker',
    'version': '1.0',
    'author': 'Jorge Alberto Quiroz Sierra',
    'depends': ['base', 'account', 'web', 'mail'],
    "category": "Wallet/Tracker",
    "sequence": -150,
    'data': [
        'security/ir.model.access.csv',
        'data/data.xml',
        'views/menu.xml',
        'views/bet/bet_view.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'description': """
        This module tracks betting investments and profits.
    """
}
