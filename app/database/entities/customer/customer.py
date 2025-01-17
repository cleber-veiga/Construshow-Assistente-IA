from app.database.entities.customer.processing.search_customer_buy_history import proc as search_customer_buy_history_proc


def distribute(query,domain, data_chat):
    if domain == 'search_customer_buy_history':
        formatted_data_markdown = search_customer_buy_history_proc(query,data_chat)
    return formatted_data_markdown

