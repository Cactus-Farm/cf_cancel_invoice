import logging
from odoo import api, fields, models, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

class AccountMoveCF(models.Model):
    _inherit = 'account.move'
    
    def cf_action_cancel_invoice(self):
        """Apre il wizard di cancellazione"""
        self.ensure_one()

        # Metodo 1: Controllo parametro specifico per fatturazione elettronica italiana
        demo_mode = self.env['ir.config_parameter'].sudo().get_param('l10n_it_edi.demo_mode', False)
        _logger.warning("L10N_IT_EDI DEMO_MODE: %s", demo_mode)
        
        # Metodo 2: Controllo alternativo per modalità test/demo
        test_mode = self.env['ir.config_parameter'].sudo().get_param('l10n_it_edi.test_mode', False)
        _logger.warning("L10N_IT_EDI TEST_MODE: %s", test_mode)
        
        # Metodo 3: Controllo generale modalità demo di Odoo
        is_demo_db = self.env['ir.config_parameter'].sudo().get_param('database.is_demo', False)
        _logger.warning("DATABASE IS_DEMO: %s", is_demo_db)
        
        # Metodo 4: Controllo diretto sulle impostazioni azienda
        company_demo = self.company_id.l10n_it_edi_demo_mode if hasattr(self.company_id, 'l10n_it_edi_demo_mode') else False
        _logger.warning("COMPANY DEMO MODE: %s", company_demo)
        
        # Metodo 4.1: Altri campi azienda per modalità demo
        company_test = self.company_id.l10n_it_edi_test_mode if hasattr(self.company_id, 'l10n_it_edi_test_mode') else False
        _logger.warning("COMPANY TEST MODE: %s", company_test)
        
        # Metodo 4.2: Controllo modalità fatturazione elettronica
        edi_mode = self.company_id.l10n_it_edi_mode if hasattr(self.company_id, 'l10n_it_edi_mode') else ''
        _logger.warning("COMPANY EDI MODE: %s", edi_mode)
        
        # Metodo 4.3: Controllo stato servizio
        service_mode = self.company_id.l10n_it_edi_service_mode if hasattr(self.company_id, 'l10n_it_edi_service_mode') else ''
        _logger.warning("COMPANY SERVICE MODE: %s", service_mode)
        
        # Metodo 5: Verifica URL endpoint SDI (se in demo, spesso punta a server di test)
        sdi_url = self.env['ir.config_parameter'].sudo().get_param('l10n_it_edi.sdi_url', '')
        _logger.warning("SDI URL: %s", sdi_url)
        is_test_sdi = 'test' in sdi_url.lower() or 'demo' in sdi_url.lower()
        
        # Metodo 7: Controllo campo transaction per modalità demo
        transaction_is_demo = False
        if hasattr(self, 'l10n_it_edi_transaction') and self.l10n_it_edi_transaction:
            transaction_value = str(self.l10n_it_edi_transaction).lower().strip()
            transaction_is_demo = transaction_value in ['demo', 'test']
            _logger.warning("TRANSACTION IS DEMO: %s (value: %s)", transaction_is_demo, transaction_value)
        
        # Logica combinata per determinare se siamo in modalità demo/test
        is_demo_mode = any([
            demo_mode in ['True', '1', True, 'true'],
            test_mode in ['True', '1', True, 'true'],
            is_demo_db in ['True', '1', True, 'true'],
            company_demo,
            company_test,
            edi_mode in ['demo', 'test'],
            service_mode in ['demo', 'test'],
            transaction_is_demo,  # Aggiunto questo controllo
            is_test_sdi
        ])
        
        # Metodo 6: Controllo tramite impostazioni di sistema (come nell'interfaccia)
        try:
            # Cerca nelle impostazioni di sistema
            demo_setting = self.env['ir.config_parameter'].sudo().search([
                ('key', 'like', '%demo%'),
                ('key', 'like', '%l10n_it%')
            ])
            for setting in demo_setting:
                _logger.warning("DEMO SETTING FOUND: %s = %s", setting.key, setting.value)
            
            # Controllo specifico per modalità fatturazione elettronica
            fe_settings = self.env['ir.config_parameter'].sudo().search([
                ('key', 'like', '%l10n_it_edi%')
            ])
            for setting in fe_settings:
                _logger.warning("FE SETTING: %s = %s", setting.key, setting.value)
                
        except Exception as e:
            _logger.warning("Error checking settings: %s", e)
            
        _logger.warning("FINAL DEMO MODE RESULT: %s", is_demo_mode)
        
        # Controllo permessi - solo admin contabilità
        if not self.env.user.has_group('account.group_account_manager'):
            raise UserError(_("Solo gli amministratori di contabilità possono utilizzare questa funzione."))
        
        # Controllo stato fattura
        if self.state != 'posted':
            raise UserError(_("Solo le fatture validate possono essere cancellate con questo metodo."))
        
        # Controllo SDI - solo se NON in modalità demo
        if not is_demo_mode:
            # DEBUG: Log tutti i campi EDI disponibili
            edi_fields = [field for field in self._fields.keys() if 'edi' in field.lower() or 'l10n_it' in field.lower()]
            _logger.warning("AVAILABLE EDI FIELDS: %s", edi_fields)
            
            # Log valori dei campi più comuni
            for field in ['l10n_it_edi_transaction', 'l10n_it_edi_state', 'l10n_it_send_state']:
                if hasattr(self, field):
                    value = getattr(self, field, None)
                    _logger.warning("FIELD %s = %s", field, value)
            
            # Log documenti EDI
            if hasattr(self, 'edi_document_ids'):
                _logger.warning("EDI DOCUMENTS COUNT: %s", len(self.edi_document_ids))
                for doc in self.edi_document_ids:
                    _logger.warning("EDI DOC: format=%s, state=%s", 
                                  doc.edi_format_id.code if doc.edi_format_id else 'None', 
                                  doc.state)
            
            # Controllo 1: Verifica se la fattura ha un transaction ID SDI REALE (non demo)
            if hasattr(self, 'l10n_it_edi_transaction') and self.l10n_it_edi_transaction:
                transaction_value = str(self.l10n_it_edi_transaction).lower().strip()
                # Blocca solo se NON è demo/test E ha un valore
                if transaction_value not in ['demo', 'test', ''] and transaction_value:
                    raise UserError(_("⚠️ Fattura già trasmessa allo SDI! Cancellazione non permessa."))
            
            # Controllo 2: Verifica stato EDI (campo più comune in Odoo 16)
            if hasattr(self, 'l10n_it_send_state') and self.l10n_it_send_state:
                if self.l10n_it_send_state in ['sent', 'delivered', 'accepted', 'other']:
                    raise UserError(_("⚠️ Fattura già trasmessa allo SDI! Cancellazione non permessa."))
            
            # Controllo 3: Verifica stato EDI alternativo
            if hasattr(self, 'l10n_it_edi_state') and self.l10n_it_edi_state:
                if self.l10n_it_edi_state in ['sent', 'delivered', 'accepted']:
                    raise UserError(_("⚠️ Fattura già trasmessa allo SDI! Cancellazione non permessa."))
            
            # Controllo 4: Verifica documenti EDI correlati (escludi quelli in demo)
            if hasattr(self, 'edi_document_ids'):
                edi_docs = self.edi_document_ids.filtered(lambda d: d.edi_format_id and d.edi_format_id.code == 'fattura_pa')
                for doc in edi_docs:
                    # Se il documento EDI è stato effettivamente inviato (non solo to_send in demo)
                    if doc.state in ['sent', 'delivered', 'accepted']:
                        raise UserError(_("⚠️ Fattura già trasmessa allo SDI! Cancellazione non permessa."))
                    # Per stato to_send, verifica se è realmente in coda o solo demo
                    elif doc.state in ['to_send'] and not transaction_is_demo:
                        # Controllo aggiuntivo: se non è demo E è in coda, potrebbe essere pericoloso
                        _logger.warning("INVOICE TO_SEND but not demo mode - allowing cancel")
                        # In questo caso permettiamo la cancellazione ma con warning nel log
        
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

    def _check_demo_mode_alternative(self):
        """Metodo alternativo per verificare modalità demo"""
        # Controlla se il modulo di fatturazione elettronica è in modalità test
        try:
            # Verifica se esiste il modello per le impostazioni EDI
            if self.env['ir.model'].search([('model', '=', 'l10n_it_edi.settings')]):
                settings = self.env['l10n_it_edi.settings'].search([], limit=1)
                if settings and hasattr(settings, 'demo_mode'):
                    return settings.demo_mode
        except:
            pass
        
        # Verifica tramite journal
        if self.journal_id and hasattr(self.journal_id, 'l10n_it_edi_demo_mode'):
            return self.journal_id.l10n_it_edi_demo_mode
        
        return False