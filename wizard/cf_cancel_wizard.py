from odoo import api, fields, models, _
from odoo.exceptions import UserError
import json


class CFCancelWizard(models.TransientModel):
    _name = 'cf.cancel.wizard'
    _description = 'CF Cancel Invoice Wizard'
    
    invoice_id = fields.Many2one('account.move', string='Fattura', required=True)
    invoice_name = fields.Char(string='Numero Fattura', readonly=True)
    invoice_amount = fields.Monetary(string='Importo Totale', readonly=True)
    currency_id = fields.Many2one(related='invoice_id.currency_id')
    
    reason = fields.Text(
        string='Motivo Cancellazione',
        required=True,
        help="Descrivere il motivo della cancellazione"
    )
    
    confirm = fields.Boolean(
        string='Confermo di voler cancellare questa fattura',
        required=True
    )
    
    def cf_confirm_cancel(self):
        """Esegue la cancellazione"""
        self.ensure_one()
        
        if not self.confirm:
            raise UserError(_("Devi confermare per procedere"))
        
        invoice = self.invoice_id
        
        # Salva dati per log
        log_data = {
            'cf_invoice_name': invoice.name,
            'cf_invoice_date': invoice.date,
            'cf_partner_name': invoice.partner_id.name,
            'cf_amount': invoice.amount_total,
            'cf_reason': self.reason,
            'cf_user_id': self.env.user.id,
            'cf_date': fields.Datetime.now(),
            'cf_data': json.dumps({
                'partner_vat': invoice.partner_id.vat or '',
                'invoice_lines': len(invoice.invoice_line_ids),
                'journal': invoice.journal_id.name,
            })
        }
        
        # Crea log
        self.env['cf.cancel.log'].create(log_data)
        
        try:
            # Reset a bozza
            invoice.button_draft()
            
            # Rimuovi riconciliazioni
            if invoice.line_ids:
                invoice.line_ids.remove_move_reconcile()
            
            # Cancella
            invoice.unlink()
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'type': 'success',
                    'title': 'Fatto!',
                    'message': f'Fattura {log_data["cf_invoice_name"]} cancellata.',
                    'sticky': False,
                }
            }
            
        except Exception as e:
            raise UserError(f"Errore: {str(e)}")