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
        "views/football/countries_wizard.xml",
        "views/football/countries.xml",
        "views/session/session_wizard.xml",
        "views/session/session.xml",
        "views/leagues/league.xml",
        "views/leagues/league_wizard.xml",
        "views/team/team.xml",
        "views/team/team_wizard.xml",
        "views/standings/standing.xml",
        "views/standings/standing_wizard.xml",
        "views/football_api/football_api_wizard.xml",
        "views/menu.xml",
    ],
    "installable": True,
    "application": True,
    "auto_install": False,
    "license": "LGPL-3",
}
