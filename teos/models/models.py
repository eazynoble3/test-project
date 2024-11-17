from odoo import models, fields, api
import base64
import requests
import sqlite3

from langchain.document_loaders import WebBaseLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OllamaEmbeddings
from langchain.vectorstores import Chroma
from langchain.chains import RetrievalQA
from langchain_community.llms import Ollama

print("SQLITE", sqlite3.sqlite_version)


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

    @api.model
    def send_request(self):
        for record in self:
            if record.model in ['llava', 'gemma']:
                if record.image:
                    image_base64 = base64.b64encode(base64.b64decode(record.image)).decode('utf-8')
                    data = {
                        "model": str(record.model),
                        "stream": False,
                        "messages": [
                            {
                                "role": "user",
                                "content": str(record.prompt),
                                "images": [image_base64]
                            }
                        ]
                    }
                else:
                    data = {
                        "model": str(record.model),
                        "stream": False,
                        "messages": [
                            {
                                "role": "user",
                                "content": str(record.prompt)
                            }
                        ]
                    }
            else:
                data = {
                    "model": str(record.model),
                    "stream": False,
                    "messages": [
                        {
                            "role": "user",
                            "content": str(record.prompt)
                        }
                    ]
                }

            response = requests.post('https://ollama.master1.teoshore.com:32574/api/chat', json=data)
            if response.status_code == 200:
                response_data = response.json()
                assistant_message = response_data.get('message', {})
                content = assistant_message.get('content', 'No content found')
                record.response = content
            else:
                record.response = 'Error: {}'.format(response.status_code)

    def send_request_and_refresh(self):
        self.send_request()
        self.refresh()

    def button_send_request(self):
        self.send_request()
        return True

    button_count = fields.Integer(string="Button Clicks", default=0)
    file = fields.Binary('PDF File')
    file_name = fields.Char('File Name')

    @api.model
    def ask_question(self):
        for record in self:
            if record.document_url and record.prompt:
                url = 'http://localhost:5000/process_url'
                data = {
                    'url': record.document_url,
                    'question': record.prompt
                }

                try:
                    response = requests.post(url, data=data)
                    response.raise_for_status()  # Raise error for bad responses (4xx or 5xx)

                    if response.status_code == 200:
                        response_data = response.json()
                        record.response = response_data.get('answer', 'No answer received')
                    else:
                        record.response = f"Error: Unexpected status code {response.status_code}"

                except requests.exceptions.RequestException as e:
                    record.response = f"Error: {str(e)}"

    def ask_question_button(self):
        self.ask_question()
