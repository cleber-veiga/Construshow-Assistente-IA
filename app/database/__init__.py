from flask_sqlalchemy import SQLAlchemy
from config import loger, conf
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import text  # Importe o método text

# Instância do SQLAlchemy
db = SQLAlchemy()

def start_the_database(app):
    try:
        loger.log('DEBUG', 'Iniciando a instância do SQLAlchemy (Database)...')
        
        # Configura a URI do banco de dados
        app.config['SQLALCHEMY_DATABASE_URI'] = (
            f"oracle+cx_oracle://{conf.get_database_credentials()['username']}:"
            f"{conf.get_database_credentials()['password']}@"
            f"{conf.get_database_credentials()['server']}"
        )
        
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

        loger.log('DEBUG', 'Iniciando o banco de dados com a aplicação')
        db.init_app(app)

        # Verifica a conexão com o banco de dados
        with app.app_context():
            loger.log('DEBUG', 'Verificando a conexão com o banco de dados...')
            connection = db.engine.connect()
            
            # Use text() para criar uma expressão executável
            query = text('SELECT 1 FROM DUAL')
            result = connection.execute(query)  # Execute a consulta
            
            loger.log('DEBUG', f'Conexão com o banco de dados verificada com sucesso: {result.fetchone()}')
            connection.close()

    except FileNotFoundError as e:
        loger.log('ERROR', f'Erro ao inicializar o banco de dados: {e}')
        raise
    except SQLAlchemyError as e:
        loger.log('ERROR', f'Erro ao conectar ao banco de dados: {e}')
        raise
    except Exception as e:
        loger.log('ERROR', f'Erro inesperado ao inicializar o banco de dados: {e}')
        raise