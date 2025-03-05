# -*- coding: utf-8 -*-
{
    'name': "Social Media Connect",
    'author': "Creative Minds",
    'website': "https://www.creativeminds.com",
    # Categories can be used to filter modules in modules listing
    # for the full list
    'category': 'OWN APPS/Social',
    'version': '0.1',
    "sequence": -1010,
    # any module necessary for this one to work correctly
    'depends': ['base', "web", "mail"],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'report/social_media_post_report.xml',
        'views/views.xml',
        'views/social_media_post_views.xml',
        'views/social_media_tag_views.xml',
        'views/social_media_platform_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        # 'demo/demo.xml',
    ],
    "installable": True,
    "application": True,
    "auto_install": False,
    "license": "LGPL-3",
}
