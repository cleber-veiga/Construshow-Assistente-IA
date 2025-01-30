
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

    prompt_text = "\n\n#DADOS PARA ANÁLISE - PRODUTOS RECORRENTES/COMPRADOS JUNTOS:"
    prompt_text += "\n##CONTEXTO DOS DADOS:"
    prompt_text += "\nEsses dados retornam os produtos mais recorrentes com os produtos que estão no carrinho. Ou seja, que mais venderam juntos"

    prompt_text += "\n\n##DADOS:"
    prompt_text += f"\n{df.to_markdown(index=False)}"

    prompt_text += "\n\n##EXPLICAÇÃO COLUNAS:"
    prompt_text += "\n###COLUNA: 'ITEMCARRINHO'"
    prompt_text += "\n- Descrição: Item que está no carrinho"

    prompt_text += "\n###COLUNA: 'PRODUTORECORRENTE'"
    prompt_text += "\n- Descrição: Item recorrente relacionado ao produto do carrinho"

    prompt_text += "\n###COLUNA: 'MARCA'"
    prompt_text += "\n- Descrição: Marca do produto recorrente"

    prompt_text += "\n###COLUNA: 'PERC'"
    prompt_text += "\n- Descrição: Percentual em que o PRODUTORECORRENTE apareceu junto com o ITEMCARRINHO em outras vendas"

    prompt_text += "\n###COLUNA: 'ORDEM'"
    prompt_text += "\n- Descrição: Ordenação da lista com base no percentual"

    prompt_text += "\n###COLUNA: 'SALDO'"
    prompt_text += "\n- Descrição: Saldo atual do produto recorrente"

    prompt_text += "\n###COLUNA: 'UNIDADE'"
    prompt_text += "\n- Descrição: Unidade do produto recorrente"

    prompt_text += "\n###COLUNA: 'PRECONORMAL'"
    prompt_text += "\n- Descrição: Preço atual do produto recorrente"

    prompt_text += "\n###COLUNA: 'PRECOPROMO'"
    prompt_text += "\n- Descrição: Preço de promoção atual do produto recorrente"
    return prompt_text