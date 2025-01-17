import re

from flask import json

def split_message(message):
    # Expressão regular para dividir o texto após pontuações ou palavras específicas
    splitters = r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?|\!|\,|\;)\s+|(?<=\btambém\b)\s+|(?<=\be\b)\s+|(?<=\bou\b)\s+'
    sub_messages = re.split(splitters, message)
    
    # Filtrar sub-mensagens irrelevantes (como "e", "ou", "também" isolados)
    final_messages = [msg.strip() for msg in sub_messages if msg.strip() and msg.strip() not in ['e', 'ou', 'também']]
    
    return final_messages

def remove_duplicate_dicts(list_of_dicts):
    """
    Remove dicionários duplicados de uma lista, mantendo a estrutura original.
    
    Args:
        list_of_dicts: Lista de dicionários que pode conter duplicatas.
    
    Returns:
        Lista de dicionários únicos, mantendo a estrutura original.
    """
    seen = set()  # Conjunto para armazenar dicionários serializados
    unique_dicts = []  # Lista para armazenar dicionários únicos
    
    for d in list_of_dicts:
        # Serializa o dicionário em uma string
        serialized = json.dumps(d, sort_keys=True)
        
        # Se o dicionário ainda não foi visto, adiciona à lista de únicos
        if serialized not in seen:
            seen.add(serialized)
            unique_dicts.append(d)
    
    return unique_dicts