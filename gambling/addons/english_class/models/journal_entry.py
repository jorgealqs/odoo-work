import requests
import logging
# import os
from odoo import models, fields, api

_logger = logging.getLogger(__name__)


class EnglishJournalEntry(models.Model):
    _name = 'english.journal.entry'
    _description = 'English Journal Entry'
    _inherit = ['mail.thread', 'mail.activity.mixin']  # Habilita el tracking
    _order = 'date desc'
    _rec_name = 'title'

    title = fields.Char(string="Title", required=True, tracking=True)
    content = fields.Html(string="Content", required=True)
    date = fields.Date(string="Date", default=fields.Date.context_today)
    word_count = fields.Integer(
        string="Word Count",
        compute="_compute_word_count",
        store=True,
        tracking=True
    )
    suggestions = fields.Html(
        string="Suggestions",
        readonly=True,
        help="Suggestions for improving your writing"
    )

    @api.depends('content')
    def _compute_word_count(self):
        for record in self:
            record.word_count = (
                len(record.content.split()) if record.content else 0
            )

    def _get_ai_suggestions(self, text):
        """Llama a la API local de Ollama para obtener sugerencias."""
        url = "http://host.docker.internal:11434/api/chat"
        # Ollama expone su API en este puerto
        text = f"Correct the following text: {text}"
        payload = {
            "model": "deepseek-r1:1.5b",
            "messages": [{"role": "user", "content": text}],
            "temperature": 0.2,   # Bajo para mayor precisión y coherencia
            "top_p": 0.8,         # Limita la aleatoriedad, mantiene fluidez
            "max_tokens": 200,    # Limita la longitud de la respuesta
            "stream": False
        }

        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()
            # Lanza una excepción si el estado no es 200
            result = response.json()
            _logger.info(f"\n\n\n {text} --> {result} \n\n\n")
            return result.get("message", {}).get("content", "No suggestions.")
        except requests.RequestException as e:
            _logger.error(f"Error fetching AI suggestions: {e}")
            return "Error: Unable to connect to Ollama."

    def action_get_suggestions(self):
        """Genera sugerencias usando la API de Hugging Face"""
        for record in self:
            if record.content:
                record.suggestions = self._get_ai_suggestions(record.content)
            else:
                record.suggestions = (
                    "Please write something to get suggestions."
                )


class EnglishJournalProgress(models.Model):
    _name = 'english.journal.progress'
    _description = 'English Journal Progress'

    date = fields.Date(string="Date", default=fields.Date.context_today)
    total_words = fields.Integer(string="Total Words Written")
    entry_count = fields.Integer(string="Entries Written")
