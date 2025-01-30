
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

    if len(df)> 0:

        prompt_text = "\n\n#DADOS PARA ANÁLISE - PRODUTOS SIMILARES AOS PRODUTOS DO CARRINHO:"
        prompt_text += "\n##CONTEXTO DOS DADOS:"
        prompt_text += "\nEsses dados retornam os produtos similares dos produtos existentes no carrinho"

        prompt_text += "\n\n##DADOS:"
        prompt_text += f"\n{df.to_markdown(index=False)}"

        prompt_text += "\n\n##EXPLICAÇÃO COLUNAS:"
        prompt_text += "\n###COLUNA: 'IDITEMORIGEM'"
        prompt_text += "\n- Descrição: Código do item do carrinho"

        prompt_text += "\n###COLUNA: 'DESCRICAOITEMORIGEM'"
        prompt_text += "\n- Descrição: Descrição do item do carrinho"

        prompt_text += "\n###COLUNA: 'QUANTIDADEITEMORIGEM'"
        prompt_text += "\n- Descrição: Quantidade do item no carrinho"

        prompt_text += "\n###COLUNA: 'VALORUNITITEMORIGEM'"
        prompt_text += "\n- Descrição: Valor unitário do item no carrinho"

        prompt_text += "\n###COLUNA: 'DESCITEMITEMORIGEM'"
        prompt_text += "\n- Descrição: Desconto total concedido ao item no carrinho"

        prompt_text += "\n###COLUNA: 'MARCAITEMORIGEM'"
        prompt_text += "\n- Descrição: Marca do item do carrinho"

        prompt_text += "\n###COLUNA: 'IDITEM'"
        prompt_text += "\n- Descrição: Código do item similar"

        prompt_text += "\n###COLUNA: 'DESCRICAO'"
        prompt_text += "\n- Descrição: Descrição do item similar"

        prompt_text += "\n###COLUNA: 'SDOATUAL'"
        prompt_text += "\n- Descrição: Saldo atual do item simular em estoque"

        prompt_text += "\n###COLUNA: 'PRECO'"
        prompt_text += "\n- Descrição: Preço atual do item similar"

        prompt_text += "\n###COLUNA: 'OFERTA'"
        prompt_text += "\n- Descrição: Preço de oferta atual do item similar"

        prompt_text += "\n###COLUNA: 'MARCA'"
        prompt_text += "\n- Descrição: Marca do item similar"
    else:
        prompt_text = "\n\n#DADOS PARA ANÁLISE - PRODUTOS SIMILARES AOS PRODUTOS DO CARRINHO:"
        prompt_text += "\n##CONTEXTO DOS DADOS:"
        prompt_text += "\nEsses dados retornam os produtos similares dos produtos existentes no carrinho"

        prompt_text += "\n\n##DADOS:"
        prompt_text += "\nNenhum dos produtos deste carrinho possui produto similar configurado"
    return prompt_text