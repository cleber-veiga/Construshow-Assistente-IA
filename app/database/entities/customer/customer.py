from app.database.entities.customer.processing.search_customer_buy_history import proc as search_customer_buy_history_proc
from app.database.entities.customer.processing.search_customer_credit_limit import proc as search_customer_credit_limit_proc
from app.database.entities.customer.processing.search_customer_return_history import proc as search_customer_return_history_proc
from app.database.entities.customer.processing.search_customer import proc as search_customer_proc
from app.database.entities.customer.processing.search_customer_payment_history import proc as search_customer_payment_history_proc


def distribute(query,domain, data_chat):
    if domain == 'search_customer_buy_history':
        formatted_data_markdown = search_customer_buy_history_proc(query,data_chat)
    
    if domain == 'search_customer_credit_limit':
        formatted_data_markdown = search_customer_credit_limit_proc(query,data_chat)

    if domain == 'search_customer_return_history':
        formatted_data_markdown = search_customer_return_history_proc(query,data_chat)

    if domain == 'search_customer_payment_history':
        formatted_data_markdown = search_customer_payment_history_proc(query,data_chat)

    if domain == 'search_customer':
        formatted_data_markdown = search_customer_proc(query,data_chat)
    return formatted_data_markdown


