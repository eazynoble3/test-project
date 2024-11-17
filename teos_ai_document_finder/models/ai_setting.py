import base64
import logging
import requests
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)

class LLMConfig(models.Model):
    _name = 'llm.config'
    _description = 'LLM Configuration'

    base_url = fields.Char(string='Base URL', required=True)
    model = fields.Char(string='Model', required=True)
    api_url = fields.Char(string='APP URL', required=True)

    _sql_constraints = [
        ('unique_config', 'unique()', 'Only one LLM Configuration record is allowed.')
    ]

    @api.model
    def create(self, vals):
        if self.search_count([]) > 0:
            raise ValidationError(_('Only one LLM Configuration record is allowed.'))
        self._post_llm_config(vals)
        return super(LLMConfig, self).create(vals)

    def write(self, vals):
        res = super(LLMConfig, self).write(vals)
        for record in self:
            self._post_llm_config({'base_url': record.base_url, 'model': record.model, 'api_url': record.api_url})
        return res

    def _get_flask_token(self):
        ai_app = self.env['ai.app'].search([], limit=1)
        if ai_app:
            ai_app.ensure_valid_token()
            return ai_app.flask_token
        else:
            raise UserError('AI App configuration not found. Please configure AI App settings.')

    def _post_llm_config(self, config):
        token = self._get_flask_token()
        url = str(config['api_url']) + '/api/set_llm_config'
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {token}'
        }
        payload = {
            'base_url': str(config['base_url']),
            'model': str(config['model'])
        }
        _logger.info(f'Sending LLM config: {payload} to {url} with headers {headers}')
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code != 200:
            try:
                error_message = response.json().get("error", "Unknown error")
            except ValueError:
                error_message = response.text  # in case the response is not JSON
            _logger.error(f'Error updating LLM config: {error_message}')
            raise UserError(f'Error updating LLM config: {error_message}')

    def test_llm_config(self):
        token = self._get_flask_token()
        url = str(self.api_url) + '/api/test_llm_config'
        headers = {'Authorization': f'Bearer {token}'}
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            result = response.json()
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'LLM Configuration Test',
                    'message': f'Success! Base URL: {result["base_url"]}, Model: {result["model"]}',
                    'type': 'success',
                    'sticky': False,
                }
            }
        else:
            try:
                error_message = response.json().get("error", "Unknown error")
            except ValueError:
                error_message = response.text  # in case the response is not JSON
            _logger.error(f'LLM configuration test failed: {error_message}')
            raise UserError(f'LLM configuration test failed: {error_message}')
