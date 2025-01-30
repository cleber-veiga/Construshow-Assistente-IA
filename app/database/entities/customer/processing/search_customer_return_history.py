
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
    print(df.shape[0])
    print(df.columns)
    df_agrupado = df.groupby([
        'estab', 'razaosoc', 'emissao', 'entradasaida', 'especie', 'idnota', 'numdoc', 'serie',
        'situacao', 'tipooper'
    ])['total'].sum().reset_index()
    print(df_agrupado.head())
    print(df_agrupado.shape[0])

    total_dev = df_agrupado['total'].sum()
    qtde_total_dev = df_agrupado.shape[0]
    maior_dev = df_agrupado.loc[df_agrupado['total'].idxmax()]
    menor_dev = df_agrupado.loc[df_agrupado['total'].idxmin()]

    prompt_text = "\n\n#DADOS PARA ANÁLISE - HISTÓRICO DE DEVOLUÇÕES DO CLIENTE:"
    prompt_text += "\n##CONTEXTO DOS DADOS:"
    prompt_text += "\nEsses dados retornam informações a respeito do histórico de devoluções do cliente"

    prompt_text += "\n\n##DADOS:"
    prompt_text += f"\n###Valor total de devoluções últimos 12 meses: R${total_dev:.2f}"
    prompt_text += f"\n###Quantidade total de devoluções últimos 12 meses: {qtde_total_dev}"

    df_agrupado['emissao'] = pd.to_datetime(df_agrupado['emissao'], errors='coerce')
    devolucoes_mensais = df_agrupado.groupby(df['emissao'].dt.to_period('M')).size()
    devolucoes_mensais.index = devolucoes_mensais.index.strftime('%m/%Y')
    devolucoes_mensais = devolucoes_mensais.to_frame().T
    devolucoes_mensais.columns.name = None
    prompt_text += f"\n###Frequência das devoluções (Quantidade):\n {devolucoes_mensais.to_markdown(index=False)}"

    prompt_text += f"\n###Top 5 Principais motivos de devolução do cliente:"
    df_motivos = df['motivodev'].value_counts(normalize=True) * 100
    percentual_motivos = df_motivos.drop_duplicates()
    prompt_text += f"\n {percentual_motivos.to_markdown()}"

    prompt_text += f"\n###Top 10 Principais itens devolvidos pelo cliente:"
    itens_devolvidos = df.groupby(['iditem', 'descricao']).size().sort_values(ascending=False).head(10)
    prompt_text += f"\n {itens_devolvidos.to_markdown()}"

    for col in ['departamento', 'secao', 'grupo', 'subgrupo']:
        top_values = df[col].value_counts(normalize=True).head(5) * 100
        prompt_text += f"\n###Principais {col}s devolvidos pelo cliente:\n {top_values.to_markdown()}"

    prompt_text += f"\n###Maior devolução últimos 12 meses:\n {maior_dev.to_markdown()}"
    prompt_text += f"\n###Menor devolução últimos 12 meses:\n {menor_dev.to_markdown()}"

    prompt_text += f"\n###Últimas 10 devoluções:\n {df_agrupado.sort_values('emissao', ascending=False).head(10).to_markdown()}"
    
    return prompt_text