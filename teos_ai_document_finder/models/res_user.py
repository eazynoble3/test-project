from odoo import models, fields, api, exceptions
import requests


class ResUsers(models.Model):
    _inherit = 'res.users'

    ai_username = fields.Char(string='AI Username')
    ai_password = fields.Char(string='AI Password')

    def action_login_user(self):
        self.ensure_one()  # Ensure this method is called on a single record
        url = 'http://localhost:5001//api/login'  # Adjust the URL as needed
        payload = {
            'username': self.ai_username,
            'password': self.ai_password,
        }
        headers = {'Content-Type': 'application/json'}
        try:
            response = requests.post(url, json=payload, headers=headers)
            if response.status_code == 200:
                message = 'Login successful.'
            elif response.status_code == 401:
                message = 'Invalid username or password.'
            else:
                message = f'Failed to login: {response.json().get("error")}'
        except requests.RequestException as e:
            message = f'Error: {str(e)}'

        # Open a wizard to display the result
        return {
            'name': 'Login Result',
            'type': 'ir.actions.act_window',
            'res_model': 'registration.result.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_message': message},
        }

    def action_register_user(self):
        self.ensure_one()  # Ensure this method is called on a single record
        url = 'http://localhost:5001/api/register'  # Adjust the URL as needed
        payload = {
            'username': self.ai_username,
            'password': self.ai_password,
        }
        headers = {'Content-Type': 'application/json'}
        try:
            response = requests.post(url, json=payload, headers=headers)
            if response.status_code == 200:
                message = 'User registered successfully.'
            elif response.status_code == 409:
                message = 'User already exists.'
            else:
                message = f'Failed to register user: {response.json().get("error")}'
        except requests.RequestException as e:
            message = f'Error: {str(e)}'

        # Open a wizard to display the result
        return {
            'name': 'Registration Result',
            'type': 'ir.actions.act_window',
            'res_model': 'registration.result.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_message': message},
        }

class RegistrationResultWizard(models.TransientModel):
    _name = 'registration.result.wizard'
    _description = 'Registration Result Wizard'

    message = fields.Text(string='Message')
