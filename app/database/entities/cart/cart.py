from app.database import db
from sqlalchemy.sql import text
from sqlalchemy.exc import SQLAlchemyError
from app.database.entities.cart.examine.examine_cart import proc as examine_cart_proc

def search_cart_header_by_id(estab,id_carrinho):
    query = text("""
        SELECT *
        FROM CARRINHO 
        WHERE ESTAB = :estab
          AND IDCARRINHO = :id_carrinho 
        ORDER BY IDCARRINHO DESC
        FETCH FIRST 1 ROW ONLY
    """)

    try:

        result = db.session.execute(
            query, 
            {'estab': estab, 'id_carrinho': id_carrinho}
        ).fetchone()

        if result:
            result_data = dict(result._mapping)
            return result_data
        else:
            return {"message": "Nenhum dado encontrado para o id_carrinho fornecido."}
    except Exception as e:
        return {"error": str(e)}

def search_cart_item_by_id(estab,id_carrinho):
    query = text("""
        SELECT 
            ESTAB,IDCARRINHO, SEQITEM,IDITEM
        FROM CARRINHOITEM 
        WHERE ESTAB = :estab
        AND IDCARRINHO = :id_carrinho 
        ORDER BY IDCARRINHO, SEQITEM DESC
    """)

    try:

        result = db.session.execute(
            query, 
            {'estab': estab, 'id_carrinho': id_carrinho}
        ).fetchall()

        if result:
            result_data = dict(result._mapping)
            return result_data
        else:
            return {"message": "Nenhum dado encontrado para o id_carrinho fornecido."}
    except Exception as e:
        return {"error": str(e)}
    
def distribute(query,domain, data_chat):
    if domain == 'examine_cart':
        formatted_data_markdown = examine_cart_proc(query,data_chat)
    return formatted_data_markdown