
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

    prompt_text = "\n\n#DADOS PARA ANÁLISE - HISTÓRICO DE PAGAMENTOS:"
    prompt_text += "\n##CONTEXTO DOS DADOS:"
    prompt_text += "\nEsses dados retornam informações a respeito do histórico de pagamentos do cliente"


    prompt_text += "\n\n##DADOS:"
    prompt_text += f"\n{df.to_markdown(index=False)}"

    prompt_text += "\n\n##EXPLICAÇÃO COLUNAS:"

    prompt_text += "\n###COLUNA: 'ATRASOMEDIO'"
    prompt_text += "\n- Descrição: Atraso médio para pagamento do cliente"
    prompt_text += "\n- Lógica: Indica quanto tempo, em média, os pagamentos foram atrasados ou adiantados, ajustado pelo peso do valor de cada boleto. "
    prompt_text += "Se o valor final for positivo, os pagamentos têm tendência a atrasar. "
    prompt_text += "Se for negativo, os pagamentos geralmente são feitos antes do vencimento. "
    prompt_text += "Um valor próximo de zero indica que os pagamentos são feitos pontualmente em média."

    prompt_text += "\n###COLUNA: 'PRAZOMEDIO'"
    prompt_text += "\n- Descrição: Prazo médio para recebimento do cliente"
    prompt_text += f"\n-Lógica: Representa o prazo médio (em dias) entre a emissão e o vencimento dos boletos, ponderado pelo valor de cada boleto. "
    prompt_text += "Um prazo médio maior indica que os boletos têm vencimentos mais longos em relação às datas de emissão. "
    prompt_text += "Um prazo médio menor sugere que os vencimentos estão mais próximos das datas de emissão."

    prompt_text += "\n###COLUNA: 'VLRDUP'"
    prompt_text += "\n- Descrição: Total de Duplicatas em Aberto"
    prompt_text += f"\n-Lógica: Representa o total de duplicatas que o cliente tem que ainda não foram pagas"

    prompt_text += "\n###COLUNA: 'DESCDUP'"
    prompt_text += "\n- Descrição: Total de Desconto das duplicatas em aberto"
    prompt_text += f"\n-Lógica: Representa o total de desconto concedido nas duplictas em aberto"

    prompt_text += "\n###COLUNA: 'SDODUPA'"
    prompt_text += "\n- Descrição: Saldo pendente das duplicatas em aberto atrasadas"
    prompt_text += f"\n-Lógica: Representa o total de saldo pendente a receber do cliente que está em atraso"

    prompt_text += "\n###COLUNA: 'SALDODUPREC'"
    prompt_text += "\n- Descrição: Saldo pendente das duplicatas em aberto"
    prompt_text += f"\n-Lógica: Representa o total de saldo pendente a receber do cliente incluindo duplicatas ainda no prazo e as em atraso"

    prompt_text += "\n###COLUNA: 'SALDODUPPAG'"
    prompt_text += "\n- Descrição: Saldo a pagar da empresa para o cliente"
    prompt_text += f"\n-Lógica: Representa o total de crédito que o cliente tem na empresa para uso, isso vem de créditos de devoluções e adiantamentos"
    
    prompt_text += "\n###COLUNA: 'SALDOCHEQREC'"
    prompt_text += "\n- Descrição: Saldo dos cheques a receber do cliente"
    prompt_text += f"\n-Lógica: Representa o total de cheques a receber do cliente, ou seja, aqueles que ainda estão em aberto"
    
    prompt_text += "\n###COLUNA: 'SALDOCHEQDEV'"
    prompt_text += "\n- Descrição: Saldo dos cheques devolvidos"
    prompt_text += f"\n-Lógica: Representa o saldo de cheques recebidos do cliente que estão com a situação devolvido"

    prompt_text += "\n###COLUNA: 'SALDOCHEQCOMP'"
    prompt_text += "\n- Descrição: Saldo de cheques a compensar"
    prompt_text += f"\n-Lógica: Representa o valor que existe de cheques deste cliente em compensação, ou seja, que foram depositados no banco mas ainda não recebidos"

    prompt_text += "\n###COLUNA: 'SALDOCHEQEMI'"
    prompt_text += "\n- Descrição: Saldo de cheques emitidos da empresa"
    prompt_text += f"\n-Lógica: Saldo de cheques emitidos pela empresa para pagar o cliente mas que ainda não foram compensados pelo mesmo"

    prompt_text += "\n###COLUNA: 'SALDOCHEQBLOQ'"
    prompt_text += "\n- Descrição: Saldo de cheques bloqueados do cliente"
    prompt_text += f"\n-Lógica: Saldo de cheques com situação bloqueado do cliente"

    return prompt_text