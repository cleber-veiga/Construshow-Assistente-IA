import pandas as pd
import locale
from app.database.entities.cart.cart import search_cart_header_by_id
from app.database.processing.chat.chat import fetch_data_from_query

locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

def proc(query,data_chat):
    data_cart = search_cart_header_by_id(data_chat['estab'],data_chat['chave'])

    query = query.replace(':ESTAB',str(data_chat['estab'])).replace(':IDPESS',str(data_cart['idpess']))

    data = fetch_data_from_query(query)

    formatted_data_markdown = formatted_data(data)

    return formatted_data_markdown

def formatted_data(data: pd.DataFrame):
    df = data
    
    df_agrupado = df.groupby([
        'estab', 'razaosoc', 'emissao', 'entradasaida', 'especie', 'idnota', 'numdoc', 'serie',
        'situacao', 'motivodev', 'pagamento', 'tipooper'
    ])['total'].sum().reset_index()

    total_compra = df_agrupado['total'].sum()
    qtde_total_compra = df_agrupado.shape[0]
    maior_compra = df_agrupado.loc[df_agrupado['total'].idxmax()]
    menor_compra = df_agrupado.loc[df_agrupado['total'].idxmin()]

    prompt_text = "\n\n#DADOS PARA ANÁLISE - HISTÓRICO DE COMPRAS DO CLIENTE:"
    prompt_text += "\n##CONTEXTO DOS DADOS:"
    prompt_text += "\nEsses dados retornam informações a respeito do histórico de compras do cliente"

    prompt_text += "\n\n##DADOS:"
    prompt_text += f"\n###Valor total de compras últimos 12 meses: R${total_compra:.2f}"
    prompt_text += f"\n###Quantidade total de compras últimos 12 meses: {qtde_total_compra}"

    df_agrupado['emissao'] = pd.to_datetime(df_agrupado['emissao'], errors='coerce')
    compras_mensais = df_agrupado.groupby(df['emissao'].dt.to_period('M')).size()
    compras_mensais.index = compras_mensais.index.strftime('%m/%Y')
    compras_mensais = compras_mensais.to_frame().T
    compras_mensais.columns.name = None
    prompt_text += f"\n###Frequência das compras (Quantidade):\n {compras_mensais.to_markdown(index=False)}"


    prompt_text += f"\n###Top 10 Principais itens comprados pelo cliente:"
    itens_comprados = df.groupby(['iditem', 'descricao']).size().sort_values(ascending=False).head(10)
    prompt_text += f"\n {itens_comprados.to_markdown()}"

    for col in ['departamento', 'secao', 'grupo', 'subgrupo']:
        top_values = df[col].value_counts(normalize=True).head(5) * 100
        prompt_text += f"\n###Principais {col}s comprados pelo cliente:\n {top_values.to_markdown()}"

    prompt_text += f"\n###Maior compra últimos 12 meses:\n {maior_compra.to_markdown()}"
    prompt_text += f"\n###Menor compra últimos 12 meses:\n {menor_compra.to_markdown()}"

    traducao_dias = {
        'Monday': 'Segunda-feira',
        'Tuesday': 'Terça-feira', 
        'Wednesday': 'Quarta-feira',
        'Thursday': 'Quinta-feira',
        'Friday': 'Sexta-feira',
        'Saturday': 'Sábado',
        'Sunday': 'Domingo'
    }
    
    #Dia da semana que mais compra
    df_dia = df_agrupado['emissao'].dt.day_name().map(traducao_dias)
    cont_dia = df_dia.value_counts()
    dia_mais_compra = cont_dia.index[0]
    prompt_text += f"\n###Dia da semana que o cliente mais compra:\n {dia_mais_compra}"

    prompt_text += f"\n###Últimas 10 compras:\n {df_agrupado.sort_values('emissao', ascending=False).head(10).to_markdown()}"
    
    return prompt_text
