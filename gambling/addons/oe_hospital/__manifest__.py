# -*- coding: utf-8 -*-
{
    'name': "Hospital Management System",

    'summary':
    "Efficiently manage hospital operations, patient records, and staff.",
    'description': """
        A comprehensive hospital management system designed to streamline
        patient registration, appointment scheduling, doctor management,
        medical records, and billing. This module helps hospitals and clinics
        operate more efficiently by digitizing and automating key processes.
    """,

    'author': "Creative minds",
    'category': 'OWN APPS/Hospital',
    'website': "https://www.creativeminds.com",
    'version': '0.1',
    "sequence": -1030,

    # any module necessary for this one to work correctly
    'depends': ['base', 'mail', 'product'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'views/menu.xml',
        'views/patient_views.xml',
        'views/patient_readonly_views.xml',
        'views/patient_appointment_views.xml',
        'views/patient_appointment_line_views.xml',
        'views/patient_tag_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        # 'demo/demo.xml',
    ],
    'images': ['static/description/icon.png'],
    "installable": True,
    "application": True,
    "auto_install": False,
    "license": "LGPL-3",
}
