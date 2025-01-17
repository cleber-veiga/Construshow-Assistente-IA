import datetime

def serialize_row(rows):
    # Verifica se rows é uma lista de dicionários
    if isinstance(rows, list):
        # Se for uma lista, aplica a serialização em cada item da lista
        return [serialize_row(row) for row in rows]
    
    # Se não for uma lista, processa cada dicionário individualmente
    if isinstance(rows, dict):
        row_dict = rows  # Se já for um dicionário, usa diretamente
        for key, value in row_dict.items():
            if isinstance(value, datetime):
                row_dict[key] = value.isoformat()  # Converte datetime para string no formato ISO 8601
            elif value is None:
                row_dict[key] = None  # Mantém None, que é JSON serializável
        return row_dict