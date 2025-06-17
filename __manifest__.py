{
    'name': 'CF Cancel Invoice Clean',
    'version': '16.0.1.0.0',
    'category': 'Accounting',
    'summary': 'Cancella fatture validate - Cactus Farm',
    'author': 'Cactus Farm',
    'license': 'LGPL-3',
    'depends': ['base','sale','account'],  
    'data': [
        'security/ir.model.access.csv',
        'data/cf_edi_cron.xml',  # NUOVO
        'wizard/cf_cancel_wizard.xml',
        'views/cf_account_move_views.xml',
        'views/cf_cancel_log_views.xml',
        'views/cf_edi_inspector_views.xml',  # NUOVO
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}