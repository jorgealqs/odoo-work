{
    "name": "Sports",
    "version": "1.0",
    "author": "Jorge Alberto Quiroz Sierra",
    "category": "FollowUp/Leagues",
    "description": """
        This module allows users to manage and follow
        up on various football leagues. It includes features
        such as tracking league information, managing teams and
        players, and updating standings and statistics. Ideal for
        sports enthusiasts and organizations needing a centralized
        platform for league management.
    """,
    "sequence": -12,
    "depends": ["base", "web"],
    "data": [
        "security/ir.model.access.csv",
        "views/football/countries.xml",
        "views/session/session.xml",
        "views/leagues/league.xml",
        "views/team/team.xml",
        "views/standings/standing.xml",
        "views/fixture/fixture.xml",
        "views/user_manual/football_api_user_manual.xml",
        "views/config_football_api/football_api_configuration_wizar.xml",
        "views/menu.xml",
    ],
    'assets': {
        'web.assets_backend': [
            "follow_up_football/static/src/css/main.css",
        ],
    },
    "installable": True,
    "application": True,
    "auto_install": False,
    "license": "LGPL-3",
}
