from datetime import datetime
from typing import List, Dict
from collections import OrderedDict

def unify_data(chat_data: List[Dict]) -> Dict:
    """
    Função para unificar dados compartilhados e aninhar mensagens no campo context_message.
    Converte objetos datetime em strings ISO 8601.
    
    :param chat_data: Lista de dicionários contendo os dados do chat.
    :return: Dicionário unificado.
    """
    if not chat_data:
        return {}

    # Seleciona os campos fixos do primeiro elemento
    fixed_fields = {
        'id_chat': chat_data[0]['idchat'],
        'id_user': chat_data[0]['iduser'],
        'status': chat_data[0]['status'],
        'created_at': chat_data[0]['createdat'].isoformat() if isinstance(chat_data[0]['createdat'], datetime) else chat_data[0]['createdat'],
        'process': chat_data[0]['process'],
        'estab': chat_data[0]['estab'],
        'chave': chat_data[0]['chave'],
    }

    # Aninha as mensagens
    context_messages = []
    for item in chat_data:
        message_data = {
            'id_message': item['idmessage'],
            'sender': item['sender'],
            'message': item['message'],
            'timestamp': item['timestamp'].isoformat() if isinstance(item['timestamp'], datetime) else item['timestamp']
        }
        context_messages.append(message_data)

    # Garante que context_message fique por último
    unified_data = OrderedDict(fixed_fields)
    unified_data['context_message'] = context_messages

    return unified_data
