import logging
from odoo import api, fields, models, _
from datetime import datetime, timedelta

_logger = logging.getLogger(__name__)

class CFEdiInspector(models.Model):
    _name = 'cf.edi.inspector'
    _description = 'CF EDI Documents Inspector'
    
    name = fields.Char(string='Name', default='EDI Inspector')
    
    @api.model
    def inspect_edi_documents_cron(self):
        """Cron job per ispezionare documenti EDI"""
        _logger.warning("=== CF EDI INSPECTOR CRON START ===")
        
        try:
            # 1. Trova fatture validate degli ultimi 30 giorni
            date_limit = datetime.now() - timedelta(days=30)
            
            invoices = self.env['account.move'].search([
                ('state', '=', 'posted'),
                ('move_type', 'in', ['out_invoice', 'in_invoice', 'out_refund', 'in_refund']),
                ('create_date', '>=', date_limit),
            ])
            
            _logger.warning("FOUND %s POSTED INVOICES IN LAST 30 DAYS", len(invoices))
            
            # 2. Controlla solo quelle con documenti EDI
            invoices_with_edi = invoices.filtered(lambda inv: hasattr(inv, 'edi_document_ids') and inv.edi_document_ids)
            
            _logger.warning("INVOICES WITH EDI DOCUMENTS: %s", len(invoices_with_edi))
            
            # 3. Analizza ogni fattura con EDI
            for invoice in invoices_with_edi:
                self._inspect_invoice_edi(invoice)
                
            # 4. Statistiche generali
            self._log_edi_statistics()
            
        except Exception as e:
            _logger.error("EDI INSPECTOR CRON ERROR: %s", e)
        
        _logger.warning("=== CF EDI INSPECTOR CRON END ===")
    
    def _inspect_invoice_edi(self, invoice):
        """Ispeziona EDI di una singola fattura"""
        _logger.warning("=" * 50)
        _logger.warning("INVOICE: %s (ID: %s)", invoice.name, invoice.id)
        _logger.warning("  - Partner: %s", invoice.partner_id.name)
        _logger.warning("  - Amount: %s %s", invoice.amount_total, invoice.currency_id.name)
        _logger.warning("  - Date: %s", invoice.date)
        _logger.warning("  - Journal: %s", invoice.journal_id.name)
        _logger.warning("  - Company: %s", invoice.company_id.name)
        
        # Controlla modalità demo
        demo_mode = self._check_demo_mode(invoice)
        _logger.warning("  - Demo Mode: %s", demo_mode)
        
        # Analizza documenti EDI
        _logger.warning("  - EDI DOCUMENTS COUNT: %s", len(invoice.edi_document_ids))
        
        for i, doc in enumerate(invoice.edi_document_ids):
            _logger.warning("    === EDI DOCUMENT #%s ===", i+1)
            _logger.warning("      - ID: %s", doc.id)
            _logger.warning("      - Format: %s (%s)", 
                          doc.edi_format_id.code if doc.edi_format_id else 'None',
                          doc.edi_format_id.name if doc.edi_format_id else 'None')
            _logger.warning("      - State: %s", doc.state)
            _logger.warning("      - Created: %s", doc.create_date)
            _logger.warning("      - Updated: %s", doc.write_date)
            
            # Attachment info
            if doc.attachment_id:
                _logger.warning("      - Attachment: %s", doc.attachment_id.name)
                _logger.warning("      - Attachment Size: %s bytes", 
                              doc.attachment_id.file_size if hasattr(doc.attachment_id, 'file_size') else 'N/A')
                _logger.warning("      - Attachment Type: %s", doc.attachment_id.mimetype)
            else:
                _logger.warning("      - Attachment: None")
            
            # Campi aggiuntivi se esistono
            extra_fields = ['error', 'blocking_level', 'edi_content']
            for field in extra_fields:
                if hasattr(doc, field):
                    value = getattr(doc, field, None)
                    if value:
                        _logger.warning("      - %s: %s", field.title(), str(value)[:200])
        
        # Controlla campi fatturazione elettronica sulla fattura
        self._check_invoice_edi_fields(invoice)
    
    def _check_invoice_edi_fields(self, invoice):
        """Controlla campi EDI sulla fattura stessa"""
        _logger.warning("  - INVOICE EDI FIELDS:")
        
        edi_fields = [
            'l10n_it_edi_transaction',
            'l10n_it_edi_state', 
            'l10n_it_send_state',
            'l10n_it_edi_attachment_id',
            'l10n_it_edi_attachment_file'
        ]
        
        for field in edi_fields:
            if hasattr(invoice, field):
                value = getattr(invoice, field, None)
                _logger.warning("      - %s: %s", field, value)
    
    def _check_demo_mode(self, invoice):
        """Verifica modalità demo per una fattura"""
        checks = []
        
        # Parametri sistema
        demo_mode = self.env['ir.config_parameter'].sudo().get_param('l10n_it_edi.demo_mode', False)
        checks.append(f"system_demo: {demo_mode}")
        
        # Azienda
        if hasattr(invoice.company_id, 'l10n_it_edi_demo_mode'):
            company_demo = invoice.company_id.l10n_it_edi_demo_mode
            checks.append(f"company_demo: {company_demo}")
        
        # Journal
        if hasattr(invoice.journal_id, 'l10n_it_edi_demo_mode'):
            journal_demo = invoice.journal_id.l10n_it_edi_demo_mode
            checks.append(f"journal_demo: {journal_demo}")
        
        return " | ".join(checks)
    
    def _log_edi_statistics(self):
        """Log statistiche generali EDI"""
        _logger.warning("=== EDI STATISTICS ===")
        
        try:
            # Totale documenti EDI
            total_edi = self.env['account.edi.document'].search_count([])
            _logger.warning("TOTAL EDI DOCUMENTS IN SYSTEM: %s", total_edi)
            
            # Per stato
            states = ['to_send', 'sent', 'delivered', 'accepted', 'cancelled']
            for state in states:
                count = self.env['account.edi.document'].search_count([('state', '=', state)])
                _logger.warning("EDI DOCUMENTS IN STATE '%s': %s", state, count)
            
            # Per formato
            formats = self.env['account.edi.format'].search([])
            for fmt in formats:
                count = self.env['account.edi.document'].search_count([('edi_format_id', '=', fmt.id)])
                _logger.warning("EDI DOCUMENTS FOR FORMAT '%s': %s", fmt.code, count)
            
            # Documenti con errori
            error_docs = self.env['account.edi.document'].search([('error', '!=', False)])
            _logger.warning("EDI DOCUMENTS WITH ERRORS: %s", len(error_docs))
            
            for doc in error_docs[:5]:  # Solo primi 5
                _logger.warning("ERROR DOC: %s - %s", doc.move_id.name if doc.move_id else 'No Move', doc.error[:100])
            
        except Exception as e:
            _logger.warning("ERROR IN STATISTICS: %s", e)
    
    @api.model
    def manual_inspect_invoice(self, invoice_id):
        """Metodo per ispezionare manualmente una fattura specifica"""
        invoice = self.env['account.move'].browse(invoice_id)
        if invoice.exists():
            _logger.warning("=== MANUAL EDI INSPECTION FOR INVOICE %s ===", invoice.name)
            self._inspect_invoice_edi(invoice)
            return True
        return False