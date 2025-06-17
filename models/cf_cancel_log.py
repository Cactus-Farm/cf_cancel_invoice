from odoo import api, fields, models, _
from odoo.exceptions import UserError


class CFCancelLog(models.Model):
    _name = 'cf.cancel.log'
    _description = 'CF Cancel Invoice Log'
    _order = 'cf_date desc'
    _rec_name = 'cf_invoice_name'
    
    cf_invoice_name = fields.Char(string='Numero Fattura', required=True)
    cf_invoice_date = fields.Date(string='Data Fattura')
    cf_partner_name = fields.Char(string='Cliente/Fornitore')
    cf_amount = fields.Float(string='Importo')
    cf_reason = fields.Text(string='Motivo', required=True)
    cf_user_id = fields.Many2one('res.users', string='Cancellata da', required=True)
    cf_date = fields.Datetime(string='Data Cancellazione', required=True)
    cf_data = fields.Text(string='Dati Extra')
    
    def unlink(self):
        """I log non si cancellano mai"""
        raise UserError(_("I log non possono essere eliminati"))
    
    @api.model
    def create(self, vals):
        """Solo creazione, no modifica"""
        return super(CFCancelLog, self.sudo()).create(vals)