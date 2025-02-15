import pickle
from typing import Dict
import unicodedata
import re

class TextCleaner:
    def __init__(self, config: Dict):
        self.config = config

    def clean_text(self, text: str) -> str:
        if self.config['lowercase']:
            text = text.lower()
        
        if self.config['remove_accents_and_special_characters']:
            text = self._remove_accents_and_special_characters(text)

        if self.config['remove_punctuation']:
            text = self._remove_punctuation(text)

        return self._normalize_words(text)

    def _remove_accents_and_special_characters(self, text: str) -> str:
        """ Remove todos os acentos e caracteres especiais"""
        return unicodedata.normalize('NFKD', text).encode('ASCII', 'ignore').decode('ASCII')

    def _remove_punctuation(self, text: str) -> str:
        return re.sub(r'[^\w\s]', '', text)
    
    def _normalize_words(self, text: str) -> str:
        
        with open("mod/app/models/saved/word_replacements.pkl", 'rb') as f:
            word_replacements = pickle.load(f)
        
        words = text.split()
        return ' '.join(word_replacements.get(word, word) for word in words)