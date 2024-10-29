{
    'name': 'English Learning App',
    'version': '1.0',
    'summary': 'English language learning application',
    'description':
    'Management of lessons and exercises to learn English in Odoo.',
    'author': 'Jorge Alberto Quiroz Sierra',
    'category': 'Education/English',
    'depends': ['base', "web"],
    'data': [
        'security/ir.model.access.csv',
        'views/lesson_views.xml',
        'views/work_views.xml',
        'views/menu.xml',
    ],
    'images': ['static/description/icon.png'],
    'installable': True,
    'application': True,
}
