
from app.database.processing.chat.chat import search_chat_header_by_id, search_querys_chat
from app.database.entities.customer.customer import distribute as customer
from app.database.entities.product.product import distribute as product

def search_and_format_domain_data(domain,id_chat):
    
    query = search_querys_chat('SEL_MCP_IA_' + domain,'like')
    
    data_chat = search_chat_header_by_id(id_chat)
    
    data_return = allocate_domain(query,domain, data_chat)

    return data_return


def allocate_domain(query,domain, data_chat):
    if domain.startswith('search_customer'):
        data_return = customer(query,domain, data_chat)
    
    if domain.startswith('search_product'):
        data_return = product(query,domain, data_chat)

    return data_return

def create_complete_question(message,domain):
    
    prompt_text = "#PERGUNTA DO USUÁRIO:"
    prompt_text += "\n"
    prompt_text += f'"{message}"'

    prompt_text += domain

    prompt_text += set_rules()

    return prompt_text

def set_rules():
    prompt_text = "#REGRAS:"
    prompt_text += "\n"
    prompt_text += "1. Responda em linguagem natural."
    prompt_text += "\n"
    prompt_text += "2. Seja direto e objetivo sem enrolar muito na resposta."
    prompt_text += "\n"
    prompt_text += "3. Responda como se tivesse acesso direto aos dados, sem informar que os dados foram recebidos"
    prompt_text += "\n"
    prompt_text += "4. Qualquer análise solicitada deve ser em cima dos dados recebidos, caso não tenha retorne informando a impossibilidade de responder"
    prompt_text += "\n"
    prompt_text += "5. Mantenha as respostas no contexto da pergunta e o conjunto de dados, caso seja fora de contexto informe ao usuário solicitando uma pergunta mais específica"
    prompt_text += "\n"
    prompt_text += "6. Responda somente em português - Brasil"
    prompt_text += "\n"
    prompt_text += "7. Nunca retorne mensagens do tipo - a mensagen ao usuário é: -  responda diretamente"
    

    return prompt_text