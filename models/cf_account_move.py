import logging
from odoo import api, fields, models, _
from odoo.exceptions import UserError


_logger = logging.getLogger(__name__)


class AccountMoveCF(models.Model):
    _inherit = 'account.move'
    
    def cf_action_cancel_invoice(self):
        """Apre il wizard di cancellazione"""
        self.ensure_one()

        demo_mode = self.env['ir.config_parameter'].sudo().get_param('edi.demo_mode')
        _logger.warning("DEMO_MODE PARAM VALUE: %s", demo_mode)
        
        # Controllo permessi - solo admin contabilità
        if not self.env.user.has_group('account.group_account_manager'):
            raise UserError(_("Solo gli amministratori di contabilità possono utilizzare questa funzione."))
        
        # Controllo stato fattura
        if self.state != 'posted':
            raise UserError(_("Solo le fatture validate possono essere cancellate con questo metodo."))
        
        # Controllo SDI
        if demo_mode not in ['True', '1', True]:
            if self.l10n_it_edi_transaction and self.l10n_it_edi_transaction.strip():
                raise UserError(_("⚠️ Fattura già trasmessa allo SDI! Cancellazione non permessa."))
        
        # Controllo pagamenti
        if self.payment_state in ('paid', 'partial'):
            raise UserError(_("⚠️ Fattura con pagamenti! Rimuovere prima i pagamenti."))
        
        return {
            'name': _('CF Cancel Invoice'),
            'type': 'ir.actions.act_window',
            'res_model': 'cf.cancel.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_invoice_id': self.id,
                'default_invoice_name': self.name,
                'default_invoice_amount': self.amount_total,
            }
        }