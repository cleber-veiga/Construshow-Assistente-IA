
import locale
import pandas as pd
from app.database.entities.cart.cart import search_cart_header_by_id
from app.database.processing.chat.chat import fetch_data_from_query

locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

def proc(query,data_chat):
    data_cart = search_cart_header_by_id(data_chat['estab'],data_chat['chave'])

    query = query.replace(':ESTAB',str(data_chat['estab'])).replace(':IDPESS',str(data_cart['idpess']))

    data = fetch_data_from_query(query)

    formatted_data_markdown = formatted_data(data)

    return formatted_data_markdown

def formatted_data(data):
    df = data
    df_pessoa = df[['idpess', 'nome', 'cnpjf', 'email', 'dtcadastro']].drop_duplicates()
    df_endereco = df[['tipoend', 'endereco', 'complemento', 'numend', 'bairro', 'cidade', 'cep']].drop_duplicates()
    df_contato = df[['telefone', 'celular', 'email', 'dtcadastro']].drop_duplicates()

    prompt_text = "\n\n#DADOS PARA ANÁLISE - CADASTRO DO CLIENTE:"
    prompt_text += "\n##CONTEXTO DOS DADOS:"
    prompt_text += "\nEsses dados retornam informações a respeito do cadastro do cliente"

    prompt_text += "\n\n##DADOS:"
    prompt_text += f"\n###Informações Cadastrais:"
    prompt_text += f"\n{df_pessoa.to_markdown(index=False)}"

    prompt_text += f"\n###Informações de Contato:"
    prompt_text += f"\n{df_contato.to_markdown(index=False)}"

    prompt_text += f"\n###Informações de Endereço:"
    prompt_text += f"\n{df_endereco.to_markdown(index=False)}"
    
    return prompt_text