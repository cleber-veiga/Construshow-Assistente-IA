import pandas as pd
import locale
from app.database.processing.chat.chat import fetch_data_from_query

locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

def proc(query,data_chat):
    query = query.replace(':ESTAB',str(data_chat['estab'])).replace(':IDCARRINHO',str(data_chat['chave']))

    data = fetch_data_from_query(query)

    formatted_data_markdown = formatted_data(data)

    return formatted_data_markdown

def formatted_data(data: pd.DataFrame):
    df = data

    prompt_text = "\n\n#DADOS PARA EXAMINAR - CARRINHO DE VENDA:"
    prompt_text += "\n##CONTEXTO DOS DADOS:"
    prompt_text += "\nEsses dados são informações dos produtos da venda"


    prompt_text += "\n\n##DADOS:"
    prompt_text += f"\n{df.to_markdown(index=False)}"

    prompt_text += "\n\n##REGRAS DE ANALISE:"
    prompt_text += "\n1. Preço Ideal → Valor que atraia o cliente sem comprometer a lucratividade."
    prompt_text += "\n2. Margem Mínima Garantida → Assegurar que qualquer desconto ou ajuste no preço não comprometa a rentabilidade"
    prompt_text += "\n3. Desconto Máximo Permitido → Oferecer o menor preço possível para garantir a venda sem comprometer o lucro"
    
    return prompt_text
