{
    "name": "Sports",
    "version": "1.0",
    "author": "Jorge Alberto Quiroz Sierra",
    "category": "Sports/Leagues",
    "description": """
        This module allows users to manage and follow
        up on various football leagues. It includes features
        such as tracking league information, managing teams and
        players, and updating standings and statistics. Ideal for
        sports enthusiasts and organizations needing a centralized
        platform for league management.
    """,
    "sequence": -14,
    "depends": ["base", "web"],
    "data": [
        "security/ir.model.access.csv",
        "views/football/countries.xml",
        "views/actions/action_owl.xml",
        "views/actions/manual.xml",
        "views/session/session.xml",
        "views/leagues/league.xml",
        "views/team/team.xml",
        "views/standings/standing.xml",
        "views/fixture/fixture.xml",
        "views/config_football_api/football_api_configuration_wizar.xml",
        "views/menu.xml",
    ],
    'assets': {
        'web.assets_backend': [
            "follow_up_football/static/src/css/main.css",
            "follow_up_football/static/src/**/*",
        ],
        'follow_up_football.assets_api_football': [
            # bootstrap
            ('include', 'web._assets_helpers'),
            'web/static/src/scss/pre_variables.scss',
            'web/static/lib/bootstrap/scss/_variables.scss',
            ('include', 'web._assets_bootstrap_backend'),

            # required for fa icons
            'web/static/src/libs/fontawesome/css/font-awesome.css',

            # include base files from framework
            ('include', 'web._assets_core'),

            'web/static/src/core/utils/functions.js',
            'web/static/src/core/browser/browser.js',
            'web/static/src/core/registry.js',
            'web/static/src/core/assets.js',
            'follow_up_football/static/src/**/*',
        ],

    },
    'images': [
        'web/static/description/icon.png',
    ],
    "installable": True,
    "application": True,
    "auto_install": False,
    "license": "LGPL-3",
}
