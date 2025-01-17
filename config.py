from app.extensions.database import ConfigManager
from app.extensions.func.config_log import LogManager

conf = ConfigManager()
loger = LogManager(conf)