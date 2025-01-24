from flask import jsonify, request,make_response
from flask_restful import Resource
from app.api.v1.src.processor import ChatProcessorMessage, ChatProcessorOpen
from config import loger
from app.api.v1.utils.request_validators import *

class ChatOpenResource(Resource):
    def get(self):
        return jsonify({'message':"Chat Aberto"})
    
    def post(self):
        try:
            """Valida e processa a requisição JSON para chat."""
            data = request.get_json(force=True)
            validation_result, status_code = RequestValidator.validate_request(
                data,
                [
                    {'name': 'estab', 'type': int},
                    {'name': 'chave', 'type': int},
                    {'name': 'process', 'type': str},
                    {'name': 'id_user', 'type': str}
                ]
            )

            response = ChatProcessorOpen()
            loger.log('DEBUG',f"Inicio do processamento da equisição de abertura")
            response = response.process_chat_request_open(data)
            response = make_response(jsonify(response))
            response.status_code = 200
            return response
        except Exception as e:
            loger.log('ERROR',f"Erro ao processar a requisição: {str(e)}")
            return {
                "error": f"Erro ao processar a requisição: {str(e)}"
            }, 500

class ChatMessageCoreResource(Resource):
    def post(self):
        try:
            """Valida e processa a requisição JSON para chat."""
            data = request.get_json(force=True)
            validation_result, status_code = RequestValidator.validate_request(
                data,
                [
                    {'name': 'id_chat', 'type': int},
                    {'name': 'message', 'type': str}
                ]
            )

            response = ChatProcessorMessage()
            loger.log('DEBUG',f"Inicio do processamento da equisição da mensagem")
            response = response.process_chat_request_message(data)
            response = make_response(jsonify(response))
            loger.log('DEBUG',f"Requisição finalizada")
            response.status_code = 200
            return response
        except Exception as e:
            loger.log('ERROR',f"Erro ao processar a requisição: {str(e)}")
            return {
                "error": f"Erro ao processar a requisição: {str(e)}"
            }, 500