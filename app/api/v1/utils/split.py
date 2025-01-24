import hashlib
import re
import uuid
from flask import json

def split_message(message, ignore_list=None):
    if ignore_list is None:
        ignore_list = [
            'bom dia',
            'boa tarde',
            'boa noite',
            'tudo bem?',
            'tudo bom?',
            'oi',
            'olá',
            'opa',
            'Boa tarde. Tudo bem?'
        ]  # Lista padrão de frases para ignorar

    # Primeiro, verifique se a mensagem contém alguma frase da lista de ignorados
    for phrase in ignore_list:
        if phrase.lower() in message.lower():
            # Substitua a frase ignorada por um marcador único temporário
            marker = f"@@@{phrase}@@@"
            message = message.replace(phrase, marker)

    # Expressão regular para dividir o texto após pontuações ou palavras específicas
    splitters = r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?|\!|\,|\;)\s+|(?<=\btambém\b)\s+|(?<=\be\b)\s+|(?<=\bou\b)\s+'
    sub_messages = re.split(splitters, message)
    
    # Filtrar sub-mensagens irrelevantes (como "e", "ou", "também" isolados)
    final_messages = []
    for msg in sub_messages:
        msg = msg.strip()
        if not msg:
            continue  # Ignorar strings vazias

        # Se a mensagem contiver um marcador, restaure a frase original
        if "@@@" in msg:
            msg = msg.replace("@@@", "")  # Remove os marcadores temporários
            final_messages.append(msg)
        else:
            final_messages.append(msg)

    return final_messages

def remove_duplicate_dicts(list_of_dicts):
    """
    Remove dicionários duplicados de uma lista, mantendo a estrutura original,
    mas ignorando explicitamente a chave 'shot_message' ao verificar a unicidade.

    Args:
        list_of_dicts: Lista de dicionários que pode conter duplicatas.

    Returns:
        Lista de dicionários únicos, mantendo a estrutura original.
    """
    seen = set()  # Conjunto para armazenar dicionários serializados
    unique_dicts = []  # Lista para armazenar dicionários únicos
    ignore_key = 'shot_message'  # Chave a ser ignorada explicitamente
    
    for d in list_of_dicts:
        # Cria uma cópia do dicionário para não modificar o original
        temp_dict = d.copy()
        
        # Remove a chave que deve ser ignorada, se existir
        if ignore_key in temp_dict:
            del temp_dict[ignore_key]
        
        # Serializa o dicionário em uma string
        serialized = json.dumps(temp_dict, sort_keys=True)
        
        # Se o dicionário ainda não foi visto, adiciona à lista de únicos
        if serialized not in seen:
            seen.add(serialized)
            unique_dicts.append(d)
    
    return unique_dicts

def generate_unique_hash():
    # Gera um UUID único
    unique_id = uuid.uuid4().hex
    
    # Cria um hash SHA-256 a partir do UUID
    hash_object = hashlib.sha256(unique_id.encode())
    hash_hex = hash_object.hexdigest()
    
    return hash_hex