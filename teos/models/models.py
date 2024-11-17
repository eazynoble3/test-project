from odoo import models, fields, api
import base64


class ApiRequest(models.Model):
    _name = 'api.request'
    _description = 'API Request'

    model = fields.Selection([
        ('llama3.1', 'Llama3.1'),
        ('llama3.2', 'Llama3.2'),
        ('llama3', 'Llama3'),
        ('codegemma', 'Code Gemma'),
        ('mistral', 'Mistral')
    ], required=True)
    prompt = fields.Char(string="Prompt", required=True)
    image = fields.Binary(string="Image")
    response = fields.Text(string="Response")
    document_url = fields.Char(string="Document URL")
