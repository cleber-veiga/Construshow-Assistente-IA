import spacy
from app.extensions.database import ConfigManager
from app.extensions.func.config_log import LogManager

conf = ConfigManager()
loger = LogManager(conf)
nlp = spacy.load('mod/app/models/pt_core_news_md-3.8.0')