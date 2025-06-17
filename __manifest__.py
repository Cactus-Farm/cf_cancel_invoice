{
    'name': 'CF Cancel Invoice',
    'version': '16.0.1.0.0',
    'category': 'Accounting',
    'summary': 'Cancella fatture validate - Cactus Farm',
    'description': """
        CF Cancel Invoice
        =================
        
        Modulo Cactus Farm per cancellare fatture validate in casi eccezionali.
        
        ⚠️ Solo per amministratori contabilità
        ⚠️ Usare con estrema cautela
    """,
    'author': 'Cactus Farm',
    'license': 'LGPL-3',
    'depends': [
        'account',
        'l10n_it_edi',
    ],
    'data': [
        'security/ir.model.access.csv',
        'wizard/cf_cancel_wizard.xml',
        'views/cf_account_move_views.xml',
        'views/cf_cancel_log_views.xml',
    ],
    'installable': True,
    'application': False,
}