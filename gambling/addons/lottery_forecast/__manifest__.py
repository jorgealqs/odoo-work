{
    'name': 'Lottery Forecast Project',
    'version': '1.0',
    'author': 'Jorge Alberto Quiroz Sierra',
    'depends': ['base', "web"],
    "category": "Lottery/Creations",
    "sequence": -1005,
    'data': [
        "security/ir.model.access.csv",
        'data/ir_cron_baloto.xml',  # Include your cron job XML file here
        "wizards/baloto/view_baloto_wizard.xml",
        "views/baloto/view_baloto.xml",
        "views/baloto/view_baloto_type.xml",
        "views/baloto/view_baloto_number_frequency.xml",
        "views/baloto/view_baloto_number_frequency_1_16.xml",
        "views/baloto/view_analysis_pair.xml",
        "views/action_manual/manual.xml",
        "views/baloto_analysis/baloto_analysis.xml",
        "views/menu.xml",
    ],
    'assets': {
        'web.assets_backend': [
            "lottery_forecast/static/src/css/kanban_styles.css",
            "lottery_forecast/static/src/**/*"
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
