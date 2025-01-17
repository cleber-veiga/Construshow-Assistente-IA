from flask_sqlalchemy import SQLAlchemy
from config import loger,conf

# Instância do SQLAlchemy
db = SQLAlchemy()

def start_the_database(app):
    try:
        loger.log('DEBUG',f'Iniciando a instância do SQLAlchemy (Database)...')
        app.config['SQLALCHEMY_DATABASE_URI'] = f"oracle+cx_oracle://{conf.get_database_credentials()['username']}:{conf.get_database_credentials()['password']}@{conf.get_database_credentials()['server']}"
        
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

        loger.log('DEBUG',f'Iniciando o banco de dados com a aplicação')
        db.init_app(app)
    except FileNotFoundError as e:
        loger.log('ERROR',f'Erro ao inicializar o banco de dados: {e}')
        raise
    except Exception as e:
        loger.log('ERROR',f'Erro inesperado ao inicializar o banco de dados: {e}')

