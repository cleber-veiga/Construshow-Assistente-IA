from app.database.entities.product.processing.search_product_similar import proc as search_product_similar_proc
from app.database.entities.product.processing.search_product_aggregate import proc as search_product_aggregate_proc
from app.database.entities.product.processing.search_product_recurrence import proc as search_product_recurrence_proc


def distribute(query,domain, data_chat):
    if domain == 'search_product_similar':
        formatted_data_markdown = search_product_similar_proc(query,data_chat)
    
    if domain == 'search_product_aggregate':
        formatted_data_markdown = search_product_aggregate_proc(query,data_chat)

    if domain == 'search_product_recurrence':
        formatted_data_markdown = search_product_recurrence_proc(query,data_chat)
    return formatted_data_markdown


