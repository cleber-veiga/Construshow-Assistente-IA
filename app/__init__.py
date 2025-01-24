from flask import Flask, request
from flask_restful import Api
from app.core.chat_memory import ChatMemory
from app.database import start_the_database
from config import loger, conf
from app.api.v1.routes import routes as routes_v1

app = Flask(__name__)
app.chat_memory = ChatMemory()
environment = conf.get_env_config()['environment']

def create_the_application()-> Flask:
    
    if environment == '0':
        @app.before_request
        def log_request_info():
            sensitive_headers = ['Authorization', 'Cookie']
            headers = {k: v for k, v in request.headers.items() if k not in sensitive_headers}

            loger.log('DEBUG', f'Requisição recebida: {request.method} {request.url}')
            loger.log('DEBUG', f'Headers: {headers}')
            if request.method in ['POST', 'PUT']:
                loger.log('DEBUG', f'Body: {request.get_data(as_text=True)}')

        @app.after_request
        def log_response_info(response):
            loger.log('DEBUG', f'Resposta enviada: {response.status} {response.status_code}')
            return response
    
    """Inicializa conexão com banco de dados"""
    start_the_database(app)

    """Definições dos prefixos da aplicação"""
    api_v1 = Api(app, prefix="/api/v1")

    """Configuras as rotas da aplicação"""
    routes_v1.created_routes(api_v1)

    return app