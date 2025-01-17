import os
import sys
import configparser

class ConfigManager:
    def __init__(self):
        self.config_file = self._get_config_file()
        self.app_path = self._get_base_dir()
        
        """Configurações gerais"""
        self.connection_file = None
        self.connection_name = None
        self.url_base = "http://+:2710/ia"
        self.debug_file_level = "DEBUG"
        self.debug_file = None
        self.environment = None
        
        """Configurações de conexão com o banco de dados Oracle"""
        self.db_server = None
        self.db_username = None
        self.db_password = None
        
        """Configurações do servidor IA"""
        self.server_host = None
        self.server_port = None
        self.server_base = None

        """Configurações do processo"""
        self.lowercase = None
        self.remove_accents_and_special_characters = None
        self.remove_punctuation = None

        self._load_configuration()
        if self.connection_file and self.connection_name:
            self._load_connection_file()
        self._load_server_configuration()

    def _get_base_dir(self):
        """Determina o diretório base do script ou executável."""
        if getattr(sys, 'frozen', False):  # Executável
            return os.path.dirname(sys.executable)
        else:  # Script
            current_dir = os.path.dirname(os.path.abspath(__file__))
            return os.path.abspath(os.path.join(current_dir, "../../..", "config"))

    def _get_config_file(self):
        """Obtém o caminho completo para o arquivo de configuração."""
        base_dir = self._get_base_dir()
        config_file = os.path.join(base_dir, 'ViasoftServerConstruShowIA.conf')

        if os.path.exists(config_file):
            return config_file
        else:
            raise FileNotFoundError(f"Arquivo de configuração não encontrado em: {config_file}")

    def _replace_app_path(self, value):
        """Substitui {AppPath} pelo caminho do executável ou script."""
        if "{AppPath}" in value:
            return value.replace("{AppPath}", self.app_path)
        return value

    def _load_configuration(self):
        """Carrega as configurações do arquivo principal."""
        try:
            config = configparser.ConfigParser()
            config.read(self.config_file)
        

            if config.has_option('Conexoes', 'ArquivoConexoes'):
                self.connection_file = self._replace_app_path(
                    config.get('Conexoes', 'ArquivoConexoes')
                )

            if config.has_option('Conexoes', 'NomeConexoes'):
                self.connection_name = config.get('Conexoes', 'NomeConexoes')

            if config.has_option('Portas', 'UrlBase'):
                self.url_base = config.get('Portas', 'UrlBase')

            if config.has_option('Debug', 'DebugFileLevel'):
                self.debug_file_level = config.get('Debug', 'DebugFileLevel')
            
            if config.has_option('Debug', 'DebugFile'):
                self.debug_file = self._replace_app_path(
                    config.get('Debug', 'DebugFile')
                )
            
            if config.has_option('Ambiente', 'Ambiente'):
                self.environment = config.get('Ambiente', 'Ambiente')
            else:
                self.environment = 1

            if config.has_option('Processing', 'Lowercase'):
                self.lowercase = self._replace_app_path(
                    config.get('Processing', 'Lowercase')
                )
            else:
                 self.lowercase = True

            if config.has_option('Processing', 'RemoveAccents'):
                self.remove_accents_and_special_characters = self._replace_app_path(
                    config.get('Processing', 'RemoveAccents')
                )
            else:
                 self.remove_accents_and_special_characters = True

            if config.has_option('Processing', 'RemovePunctuation'):
                self.remove_punctuation = self._replace_app_path(
                    config.get('Processing', 'RemovePunctuation')
                )
            else:
                 self.remove_punctuation = True
            
        except configparser.Error as e:
            raise RuntimeError(f"Erro ao carregar o arquivo de configuração: {e}")


    def _load_connection_file(self):
        """Carrega as informações do arquivo de conexões usando o nome especificado."""
        try:
            if not os.path.exists(self.connection_file):
                raise FileNotFoundError(f"Arquivo de conexões não encontrado: {self.connection_file}")

            config = configparser.ConfigParser(allow_no_value=True)
            config.read(self.connection_file)

            if self.connection_name and self.connection_name in config:
                self.db_server = config.get(self.connection_name, 'Server', fallback=None)
                self.db_username = config.get(self.connection_name, 'Username', fallback=None)
                self.db_password = config.get(self.connection_name, 'Password', fallback=None)

                # Ajusta o formato do Server, se necessário
                if self.db_server and ':' in self.db_server and self.db_server.count(':') == 2:
                    parts = self.db_server.split(':')
                    if len(parts) == 3:
                        self.db_server = f"{parts[0]}:{parts[1]}/{parts[2]}"

            else:
                raise ValueError(
                    f"Seção '{self.connection_name}' não encontrada no arquivo de conexões: {self.connection_file}"
                )
        except configparser.Error as e:
            raise RuntimeError(f"Erro ao carregar o arquivo de conexões: {e}")

    def _load_server_configuration(self):
        """Carrega as informações do servidor IA."""
        try:
            if getattr(sys, 'frozen', False):  # Executável
                client_dir = os.path.join(self.app_path, "..", "..", "Client")
            else:  # Script
                current_dir = os.path.dirname(os.path.abspath(__file__))
                client_dir = os.path.abspath(os.path.join(current_dir, "../../..", "config"))

            server_file = os.path.join(client_dir, "viasoft.MCP.server")

            if not os.path.exists(server_file):
                raise FileNotFoundError(f"Arquivo do servidor não encontrado: {server_file}")

            config = configparser.ConfigParser(allow_no_value=True)
            config.read(server_file)

            if self.connection_name and self.connection_name in config:
                self.server_host = config.get(self.connection_name, 'IAServerIP', fallback=None)
                self.server_port = config.get(self.connection_name, 'IAServerPort', fallback=None)
                self.server_base = config.get(self.connection_name, 'IAUrlBase', fallback=None)
            else:
                raise ValueError(
                    f"Seção '{self.connection_name}' não encontrada no arquivo do servidor: {server_file}"
                )
        except configparser.Error as e:
            raise RuntimeError(f"Erro ao carregar o arquivo do servidor: {e}")

    def __str__(self):
        """Representação de string para depuração."""
        return (
            f"ConfigManager(\n"
            f"  Config File: {self.config_file}\n"
            f"  Connection File: {self.connection_file}\n"
            f"  Connection Name: {self.connection_name}\n"
            f"  URL Base: {self.url_base}\n"
            f"  Debug File Level: {self.debug_file_level}\n"
            f"  Debug File: {self.debug_file}\n"
            f"  DB Server: {self.db_server}\n"
            f"  DB Username: {self.db_username}\n"
            f"  DB Password: {self.db_password}\n"
            f"  Server Host: {self.server_host}\n"
            f"  Server Port: {self.server_port}\n"
            f"  Server Base: {self.server_base}\n"
            f")"
        )
    
    def get_database_credentials(self):
        """Retorna as credenciais do banco de dados."""
        if not self.db_server or not self.db_username or not self.db_password:
            raise ValueError("As credenciais do banco de dados não foram carregadas corretamente.")
        return {
            "server": self.db_server,
            "username": self.db_username,
            "password": self.db_password
        }

    def get_server_config(self):
        """Retorna as configurações do servidor."""
        if not self.server_host or not self.server_port or not self.server_base:
            raise ValueError("As configurações do servidor IA não foram carregadas corretamente.")
        return {
            "server_host": self.server_host,
            "server_port": self.server_port,
            "server_base": self.server_base
        }

    def get_log_config(self):
        """Retorna as configurações de log."""
        if not self.debug_file or not self.debug_file_level:
            raise ValueError("As configurações de log não foram carregadas corretamente.")
        return {
            "debug_file_level": self.debug_file_level,
            "debug_file": self.debug_file
        }
    
    def get_env_config(self):
        """Retorna as configurações de Ambiente."""
        if not self.environment:
            raise ValueError("As configurações de Ambiente não foram carregadas corretamente.")
        return {
            "environment": self.environment
        }
    
    def get_processing_config(self):
        """Retorna as configurações de Ambiente."""
        if not self.lowercase or not self.remove_accents_and_special_characters or not self.remove_punctuation:
            raise ValueError("As configurações de Ambiente não foram carregadas corretamente.")
        return {
            "lowercase": self.lowercase,
            "remove_accents_and_special_characters": self.remove_accents_and_special_characters,
            "remove_punctuation": self.remove_punctuation
        }