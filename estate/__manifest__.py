{
    'name': 'Estate',
    'version': '1.0',
    'category': 'Sales',
    'summary': 'Real estate management',
    'description': 'Module for managing real estate properties',
    'author': 'Your Name',
    'depends': ['base'],
    'data': [
        # Add your data files here (views, security, etc)
        'security/ir.model.access.csv',
        'views/estate.view-properties.xml',
        'views/res_users_views.xml',
        'views/kanban.xml'
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
} # type: ignore 