
import locale
import pandas as pd
from app.database.entities.cart.cart import search_cart_item_by_id
from app.database.processing.chat.chat import fetch_data_from_query

locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

def proc(query,data_chat):
    query = query.replace(':ESTAB',str(data_chat['estab'])).replace(':IDCARRINHO',str(data_chat['chave']))

    data = fetch_data_from_query(query)

    formatted_data_markdown = formatted_data(data)

    return formatted_data_markdown

def formatted_data(data):
    df = data

    prompt_text = "\n\n#DADOS PARA ANÁLISE - PRODUTOS AGREGADOS/COMPLEMENTARES:"
    prompt_text += "\n##CONTEXTO DOS DADOS:"
    prompt_text += "\nEsses dados retornam os produtos agregados aos produtos existentes no carrinho"

    prompt_text += "\n\n##DADOS:"
    prompt_text += f"\n{df.to_markdown(index=False)}"

    prompt_text += "\n\n##EXPLICAÇÃO COLUNAS:"
    prompt_text += "\n###COLUNA: 'ITEMCARRINHO'"
    prompt_text += "\n- Descrição: Item que está no carrinho"

    prompt_text += "\n###COLUNA: 'ITEMAGREGADO'"
    prompt_text += "\n- Descrição: Item agregado relacionado ao carrinho"

    prompt_text += "\n###COLUNA: 'SDOATUAL'"
    prompt_text += "\n- Descrição: Saldo do estoque atual do item agregado"

    prompt_text += "\n###COLUNA: 'PRECO'"
    prompt_text += "\n- Descrição: Preço atual do item agregado"

    prompt_text += "\n###COLUNA: 'OFERTA'"
    prompt_text += "\n- Descrição: Preço de oferta atual do item agregado"
    return prompt_text