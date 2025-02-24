{
    'name': 'English Learning App',
    'version': '1.0',
    'summary': 'English language learning application',
    'description':
    'Management of lessons and exercises to learn English in Odoo.',
    'author': 'Jorge Alberto Quiroz Sierra',
    'category': 'OWN APPS/English',
    'depends': ['base', "web", "mail"],
    'data': [
        'security/ir.model.access.csv',
        'views/journal_entry_views.xml',
        'views/lesson_views.xml',
        'views/work_views.xml',
        'views/menu.xml',
    ],
    'images': ['static/description/icon.png'],
    'installable': True,
    'application': True,
    "license": "LGPL-3",
}
