{
    "name": "Sports Metrics JQ",
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
    "sequence": -1001,
    "depends": ["base", "web"],
    "data": [
        "security/ir.model.access.csv",
        "views/menu.xml",
        "data/data_session.xml",
        "data/data_country.xml",
        "views/countries/country.xml",
        "views/leagues/league.xml",
        "views/teams/team.xml",
        "views/standings/standing.xml",
        "views/rounds/round.xml",
        "views/matches/match.xml",
        "views/owl_action/match.xml",
    ],
    'assets': {
        'web.assets_backend': [
            "sport_metrics_jq/static/src/css/main.css",
            "sport_metrics_jq/static/src/**/*",
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