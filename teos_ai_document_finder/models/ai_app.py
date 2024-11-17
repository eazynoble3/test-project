import base64
import logging
from datetime import datetime, timedelta
import requests
from odoo import models, fields, api
from odoo.exceptions import UserError

class AIApp(models.Model):
    _name = 'ai.app'
    _description = 'AI App'

    question = fields.Char(string='Question')
    response = fields.Html(string='Response', readonly=True)
    flask_token = fields.Char(string='Flask Token', readonly=True)
    token_expiry = fields.Datetime(string='Token Expiry')

    def _get_api_url(self):
        llm_config = self.env['llm.config'].search([], limit=1)
        if not llm_config:
            raise UserError('LLM Configuration not found. Please configure LLM settings.')
        return str(llm_config.api_url)

    def action_renew_token(self):
        self.ensure_valid_token()
        self.response = 'Token renewed manually'

    def action_login_flask(self):
        url = self._get_api_url() + '/api/login'
        payload = {
            'username': str(self.env.user.ai_username),
            'password': str(self.env.user.ai_password)
        }
        headers = {'Content-Type': 'application/json'}
        try:
            response = requests.post(url, json=payload, headers=headers)
            logging.info(f"Login Response Status: {response.status_code}, Content: {response.content}")
            if response.status_code == 200:
                response_data = response.json()
                self.flask_token = response_data.get('access_token')
                self.token_expiry = datetime.fromisoformat(response_data.get('expiry'))  # Store the expiry time
                self.response = 'Login successful'
                logging.info("Flask token updated successfully")
            else:
                self.response = f'Failed to login: {response.text}'
                logging.error(f"Failed to login to Flask app: {response.text}")
        except requests.RequestException as e:
            self.response = f'Error: {str(e)}'
            logging.error(f"Login Request Exception: {str(e)}", exc_info=True)  # Log the error

    def _is_token_expired(self, token_expiry):
        if not token_expiry:
            return True
        return datetime.utcnow() > token_expiry - timedelta(minutes=5)

    def ensure_valid_token(self):
        if not self.flask_token or self._is_token_expired(self.token_expiry):
            self.action_login_flask()

    @api.model
    def scheduled_token_renewal(self):
        ai_app = self.search([], limit=1)
        if ai_app:
            ai_app.ensure_valid_token()

    def _submit_question(self):
        self.ensure_valid_token()

        url = self._get_api_url() + '/api/query'
        payload = {
            'query': str(self.question),
        }
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.flask_token}'
        }

        try:
            response = requests.post(url, json=payload, headers=headers)
            logging.info(f"Response Status: {response.status_code}, Content: {response.content}")
            if response.status_code == 200:
                try:
                    json_response = response.json()
                    answer = json_response.get('answer')
                    pdf_name = json_response.get('pdf_name')
                    preview_link = f"{self._get_api_url()}/preview/{pdf_name}"
                    self.response = (f'<p><strong>Answer:</strong> {answer}</p>'
                                     f'<p><strong>PDF Name:</strong> {pdf_name}</p>'
                                     f'<p><a href="{preview_link}" target="_blank">Preview Document</a></p>')
                except ValueError:
                    self.response = 'Failed to parse JSON response'
                    logging.error("Failed to parse JSON response", exc_info=True)  # Log the error
            else:
                if response.status_code == 401 or response.status_code == 422:
                    logging.warning("Token expired or invalid. Re-authenticating.")
                    self.ensure_valid_token()  # Re-authenticate and get a new token
                    response = requests.post(url, json=payload, headers=headers)  # Retry with new token
                    if response.status_code == 200:
                        json_response = response.json()
                        answer = json_response.get('answer')
                        pdf_name = json_response.get('pdf_name')
                        preview_link = json_response.get('preview_link')
                        self.response = f'Answer: {answer}\nPDF Name: {pdf_name}\nPreview Link: {preview_link}'
                    else:
                        self.response = f'Failed to get answer: {response.text}'
                        logging.error(f"Failed to get answer after re-authentication: {response.text}", exc_info=True)
                elif response.status_code == 504 or 500:
                    self.response = 'Request timed out. Please try again.'
                    logging.error(f"Failed to get answer: {response.text}", exc_info=True)
                else:
                    self.response = f'Failed to get answer: {response.text}'
                    logging.error(f"Failed to get answer: {response.text}", exc_info=True)
        except requests.RequestException as e:
            self.response = f'Error: {str(e)}'
            logging.error(f"Request Exception: {str(e)}", exc_info=True)  # Log the error

    def action_submit_question(self, *args, **kwargs):
        for record in self:
            record._submit_question()


class AttachmentUpload(models.Model):
    _inherit = 'ir.attachment'

    def _get_api_url(self):
        llm_config = self.env['llm.config'].search([], limit=1)
        if not llm_config:
            raise UserError('LLM Configuration not found. Please configure LLM settings.')
        return str(llm_config.api_url)

    def create(self, vals):
        res = super(AttachmentUpload, self).create(vals)
        ai_app = self.env['ai.app'].search([], limit=1)
        if not ai_app:
            ai_app = self.env['ai.app'].create({})

        ai_app.ensure_valid_token()

        # Upload the file to the Flask app
        url = self._get_api_url() + '/api/upload'
        headers = {
            'Authorization': f'Bearer {ai_app.flask_token}'
        }

        file_data = base64.b64decode(res.datas)
        files = {
            'file': (res.name, file_data, res.mimetype)
        }

        try:
            response = requests.post(url, headers=headers, files=files)
            logging.info(f"Upload Response Status: {response.status_code}, Content: {response.content}")
            if response.status_code != 200:
                logging.error(f"Failed to upload file to Flask app: {response.text}")
        except requests.RequestException as e:
            logging.error(f"Upload Request Exception: {str(e)}", exc_info=True)  # Log the error

        return res
