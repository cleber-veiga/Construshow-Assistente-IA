import logging
from logging.handlers import RotatingFileHandler
import os

class LogManager:
    def __init__(self, conf):
        log_config = conf.get_log_config()
        self.debug_file_level = log_config['debug_file_level']
        self.debug_file = log_config['debug_file']
        self._validate_config()
        self._setup_logging()

    def _validate_config(self):
        """Valida as configurações de log."""
        if self.debug_file_level not in ['0', '1', '2']:
            raise ValueError("Nível de log inválido: debug_file_level deve ser '0', '1' ou '2'")
        if not isinstance(self.debug_file, str) or not self.debug_file.strip():
            raise ValueError("Caminho do arquivo de log inválido")

    def _ensure_log_directory(self):
        """Garante que o diretório de logs exista, criando-o se necessário."""
        log_dir = os.path.dirname(self.debug_file)
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
            print(f"Diretório de logs criado: {log_dir}")

    def _get_handler_level(self):
        """Mapeia debug_file_level para o nível correspondente."""
        if self.debug_file_level == '0':
            return logging.CRITICAL + 1  # Nenhum log será processado
        elif self.debug_file_level == '1':
            return logging.WARNING  # Exibe WARNING e níveis mais altos
        elif self.debug_file_level == '2':
            return logging.DEBUG  # Exibe todos os logs
        return logging.NOTSET

    def _setup_logging(self):
        """Configura o sistema de logs com base nas configurações."""
        self._ensure_log_directory()

        # Remove handlers existentes
        for handler in logging.getLogger().handlers[:]:
            logging.getLogger().removeHandler(handler)

        logging.getLogger().setLevel(logging.DEBUG)

        # Configura o arquivo de log com rotação
        rotating_handler = RotatingFileHandler(
            self.debug_file,
            maxBytes=10 * 1024 * 1024,
            backupCount=2
        )
        rotating_handler.setLevel(self._get_handler_level())
        rotating_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
        logging.getLogger().addHandler(rotating_handler)

        # Adiciona um handler para o console
        console_handler = logging.StreamHandler()
        console_handler.setLevel(self._get_handler_level())
        console_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        logging.getLogger().addHandler(console_handler)

    def log(self, log_type="INFO", description=""):
        """Registra mensagens de log."""
        logger = logging.getLogger()
        log_type = log_type.upper()
        if hasattr(logger, log_type.lower()):
            log_method = getattr(logger, log_type.lower())
            log_method(description)

    @staticmethod
    def get_logger(name):
        """Retorna um logger com o nome especificado."""
        logger = logging.getLogger(name)
        if not logger.handlers:
            for handler in logging.getLogger().handlers:
                logger.addHandler(handler)
            logger.setLevel(logging.getLogger().level)
        return logger
