import pandas as pd
from app.database.entities.cart.cart import search_cart_header_by_id
from app.database.processing.chat.chat import fetch_data_from_query


def proc(query,data_chat):
    data_cart = search_cart_header_by_id(data_chat['estab'],data_chat['chave'])

    query = query.replace(':ESTAB',str(data_chat['estab'])).replace(':IDPESS',str(data_cart['idpess']))

    data = fetch_data_from_query(query)

    formatted_data_markdown = formatted_data(data)

    return formatted_data_markdown

def formatted_data(data):
    df = data

    prompt_text = "\n\n#DADOS PARA ANÁLISE - LIMITE DE CRÉDITO:"
    prompt_text += "\n"
    prompt_text += "##CONTEXTO DOS DADOS:"
    prompt_text += "\n"
    prompt_text += "Esses dados retornam informações importantes sobre o limite de crédito do cliente na venda"
    prompt_text += "\n\n"

    prompt_text += "##DADOS:"
    prompt_text += "\n"

    prompt_text += f"- Código do Cliente: {df.loc[0, 'idpess']} / {df.loc[0, 'nome']}"
    prompt_text += "\n"
    prompt_text += f"- Nome do Cliente: {df.loc[0, 'nome']}"
    prompt_text += "\n"

    if pd.isna(df.loc[0, 'dtproxreaval']) or (isinstance(df.loc[0, 'dtproxreaval'], str) and df.loc[0, 'dtproxreaval'].strip() == ""):
        prompt_text += "- Próxima Reavaliação: sem data informada"
    else:
        prompt_text += "- Data da próxima reavaliação: " + pd.to_datetime(df.loc[0, 'dtproxreaval']).strftime('%d/%m/%Y')
    prompt_text += "\n"

    prompt_text += f"- Limite de Compra Total: {df.loc[0, 'limite']}"
    prompt_text += "\n"
    prompt_text += f"- Limite Mensal: {df.loc[0, 'limitemensal']}"
    prompt_text += "\n"
    prompt_text += f"- Limite para Cheques: {df.loc[0, 'limitecheqrec']}"
    prompt_text += "\n"
    prompt_text += f"- Limite da Conta Pessoal: {df.loc[0, 'limitecp']}"
    prompt_text += "\n"
    prompt_text += f"- Saldo total devedor: {df.loc[0, 'saldototalpend']}"
    prompt_text += "\n"
    prompt_text += f"- Limite de Crédito disponível: {df.loc[0, 'limitedisponivel']}"

    return prompt_text
