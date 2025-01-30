
from app.database.processing.chat.chat import search_chat_header_by_id, search_querys_chat
from app.database.entities.customer.customer import distribute as customer
from app.database.entities.product.product import distribute as product
from app.database.entities.cart.cart import distribute as cart

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
    
    if domain.startswith('examine_cart'):
        data_return = cart(query,domain, data_chat)

    return data_return