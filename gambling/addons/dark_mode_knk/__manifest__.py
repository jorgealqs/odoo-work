# -*- coding: utf-8 -*-

{
    'name': 'Dark mode',
    'version': '17.0.1.1',
    'summary': 'Dark Mode is an extension that helps you quickly turn the screen (browser) to dark in Odoo. This dark mode backend theme gives you a fully modified view with a full-screen display. It is a perfect choice for your Odoo Backend and an attractive theme for Odoo. | apps night mode | dark mode| night mode | enable dark mode | odoo night mode |',
    'description': """
       Dark Mode is an extension that helps you quickly turn the screen (browser) to dark in Odoo. This dark mode backend theme gives you a fully modified view with a full-screen display. It is a perfect choice for your Odoo Backend and an attractive theme for Odoo.
    """,
    'category': 'Website',
    'author': 'Kanak Infosystems LLP.',
    'license': 'OPL-1',
    'depends': ['base'],
    'assets': {
        'web.assets_backend': [
            'dark_mode_knk/static/src/js/dark_mode_button.js',
            'dark_mode_knk/static/src/scss/night_mode.scss',
            'dark_mode_knk/static/src/xml/dark_mode_button.xml',
        ],
    },
    'images': ['static/description/banner.gif'],
    'installable': True
}
