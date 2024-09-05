{
    'name': 'Lottery Forecast Project',
    'version': '1.0',
    'author': 'Jorge Alberto Quiroz Sierra',
    'depends': ['base', "web"],
    "category": "Lottery/Creations",
    "sequence": -11,
    'data': [
        "security/ir.model.access.csv",
        "wizards/baloto/view_baloto_wizard.xml",
        "views/baloto/view_baloto.xml",
        "views/baloto/view_baloto_type.xml",
        "views/menu.xml",
    ],
    'assets': {
        'web.assets_backend': [
            "lottery_forecast/static/src/css/kanban_styles.css",
        ],
    },
    'installable': True,
    'application': True,
    'auto_install': False,
    "license": "LGPL-3",
    'description': """
        This module provides functionality for managing lottery
        results, including Baloto and other lotteries.
        It also includes features for predicting future lottery results.
    """,
}
