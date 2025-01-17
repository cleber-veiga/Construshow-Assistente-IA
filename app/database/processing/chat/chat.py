import cx_Oracle
import pandas as pd
from app.database import db
from sqlalchemy.sql import text
from sqlalchemy.exc import SQLAlchemyError
from app.extensions.client.response_handler import ResponseHandler

def search_or_open_chat(data):
    result = search_chat_header(data)
    id_chat = 0 
    
    if result:
        id_chat = result.idchat
        # Primeiro verifica o status do chat
        if result.status == 'closed':
            update_chat_status(id_chat, 'open')
    else:
        result = create_new_chat(data)

        if result == 0:
            return {"error": 'Erro na criação do chat'}
        
        # Busca uma mensagem inicial
        response_handler = ResponseHandler()
        resposta_greeting = response_handler.get_response("Olá", "greeting")
        
        create_new_chat_detail(result['id_chat'], 'SYSTEM', resposta_greeting)
        
        id_chat = result['id_chat'][0]

    chat_messages = search_chat_header_and_datail(id_chat,20)
    return chat_messages

def update_chat_status(id_chat,status):
    query = text("""
        UPDATE CHATCAB
        SET STATUS = :status
        WHERE IDCHAT = :id_chat
    """)

    try:
        db.session.execute(query, {'status': status, 'id_chat': id_chat})
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()

def create_new_chat(data):
    # Criando o parâmetro de saída para o ID
    id_chat = db.session.connection().connection.cursor().var(cx_Oracle.NUMBER)
    
    query = text("""
        INSERT INTO CHATCAB(IDUSER, STATUS, PROCESS, ESTAB, CHAVE) 
        VALUES(:id_user, 'open', :process, :estab, :chave)
        RETURNING IDCHAT INTO :id_chat
    """)
    
    try:
        result = db.session.execute(query, {
            'id_user': data['id_user'],
            'process': data['process'],
            'estab': data['estab'],
            'chave': data['chave'],
            'id_chat': id_chat
        })
        db.session.commit()
        
        # Retorna o ID gerado
        return {
            'id_chat': id_chat.getvalue(),
            'id_user': data['id_user'],
            'process': data['process'],
            'estab': data['estab'],
            'chave': data['chave'],
            'status': 'open'
        }
        
    except SQLAlchemyError as e:
        db.session.rollback()
        raise Exception(f"Erro ao inserir no CHATCAB: {str(e)}")

def create_new_chat_detail(id_chat, sender, message):
    # Certifique-se de que `id_chat` é um valor único
    if isinstance(id_chat, list) and len(id_chat) == 1:
        id_chat = id_chat[0]
    
    try:
        # Criação de variável de saída (IDMESSAGE)
        id_message = db.session.connection().connection.cursor().var(cx_Oracle.NUMBER)
        
        # Query com retorno do IDMESSAGE gerado
        query = text("""
            INSERT INTO CHATDET (IDCHAT, SENDER, MESSAGE) 
            VALUES (:id_chat, :sender, :message)
            RETURNING IDMESSAGE INTO :id_message
        """)

        # Executa a query passando os parâmetros e a variável de saída
        db.session.execute(query, {
            'id_chat': id_chat,
            'sender': sender,
            'message': message,
            'id_message': id_message
        })

        # Commit na transação para confirmar a inserção
        db.session.commit()

        # Retorna o valor do IDMESSAGE criado
        return id_message.getvalue()

    except SQLAlchemyError as e:
        # Log de erro e rollback da transação
        db.session.rollback()
        print({"error": str(e)})
        return {"error": str(e)}

def create_new_chat_detail_domain(id_message,domain,short_message,trust):
    query = text("""
        INSERT INTO CHATDOMAIN (IDMESSAGE, DOMAIN, SHORTMESSAGE, TRUST) 
        VALUES (:id_message, :domain, :short_message, :trust)
    """)

    try:
        # Executa a query com os parâmetros fornecidos
        db.session.execute(query, {
            'id_message': id_message,
            'domain': domain,
            'short_message': short_message,  # Corrigido o nome do parâmetro
            'trust': trust,
        })

        # Confirma a transação
        db.session.commit()

        # Retorno de sucesso
        return {"success": True, "message": "Registro inserido com sucesso."}

    except SQLAlchemyError as e:
        # Faz o rollback em caso de erro
        db.session.rollback()

        # Loga e retorna o erro
        error_message = str(e.__dict__.get("orig", e))
        print({"error": error_message})
        return {"success": False, "error": error_message}

def search_chat_header_by_id(id_chat):
    query = text("""
        SELECT *
        FROM CHATCAB 
        WHERE IDCHAT = :id_chat 
        ORDER BY IDCHAT DESC
        FETCH FIRST 1 ROW ONLY
    """)

    try:
        # Executa a query e retorna uma única linha
        result = db.session.execute(query, {'id_chat': id_chat}).fetchone()

        # Verifique se o resultado não é None (não vazio)
        if result:
            # Convertendo a linha diretamente para um dicionário
            result_data = dict(result._mapping)
            return result_data
        else:
            return {"message": "Nenhum dado encontrado para o id_chat fornecido."}
    except SQLAlchemyError as e:
        return {"error": str(e)}

def search_chat_header(data):
    query = text("""
        SELECT *
        FROM CHATCAB 
        WHERE ESTAB = :estab 
          AND CHAVE = :chave
          AND PROCESS = :process
          AND IDUSER = :id_user
        ORDER BY IDCHAT DESC
        FETCH FIRST 1 ROW ONLY
    """)

    try:
        result = db.session.execute(query, {
            'estab': data['estab'], 
            'chave': data['chave'],
            'process': data['process'],
            'id_user': data['id_user'],
        }).fetchone()

        return result
    except SQLAlchemyError as e:
        return {"error": str(e)}
    
def search_chat_header_and_datail(id_chat,num_reg):
    query = text("""
        SELECT
            CB.IDCHAT,
            CB.IDUSER,
            CB.STATUS,
            CB.CREATEDAT,
            CB.PROCESS,
            CB.ESTAB,
            CB.CHAVE,
            CD.IDMESSAGE,
            CD.SENDER,
            CD.MESSAGE,
            CD.TIMESTAMP
        FROM CHATCAB CB
        LEFT JOIN CHATDET CD ON CD.IDCHAT = CB.IDCHAT
        WHERE CB.IDCHAT = :id_chat
        ORDER BY CD.IDMESSAGE DESC
        FETCH FIRST :num_reg ROWS ONLY
    """)

    try:
        result = db.session.execute(query, {'id_chat': id_chat,'num_reg': num_reg}).fetchall()
        
        # Converte cada linha para um dicionário
        chat_data = [dict(row._mapping) for row in result]
        
        return chat_data
    except SQLAlchemyError as e:
        return {"error": str(e)}
    
def search_querys_chat(nome, format):
    nome = nome.upper()

    if format == 'like':
        query = text("""
            SELECT SQL
            FROM VSCONSULTACHAT
            WHERE NOME LIKE :nome
        """)
        param = {'nome': f'%{nome}%'}  # Adiciona os curingas de LIKE
    elif format == 'equal':
        query = text("""
            SELECT SQL
            FROM VSCONSULTACHAT
            WHERE NOME = :nome
        """)
        param = {'nome': nome}
    else:
        raise ValueError("Formato inválido. Use 'like' ou 'equal'.")

    try:
        # Executa a consulta e retorna o primeiro resultado da coluna SQL
        result = db.session.execute(query, param).fetchone()
        db.session.commit()

        # Retorna o valor da coluna SQL ou None se não houver resultado
        return result[0] if result else None
    except SQLAlchemyError as e:
        db.session.rollback()
        print(f"Erro ao executar consulta: {e}")
        return None
    
def fetch_data_from_query(query) -> pd.DataFrame:
    try:
        query = text(query)
        result = db.session.execute(query)
        
        if not result:
            return pd.DataFrame({"error": ["Nenhum resultado encontrado"]})
        
        # Obtém as colunas dinamicamente
        columns = result.keys()
        
        # Converte o resultado para um DataFrame
        df = pd.DataFrame(result.fetchall(), columns=columns)
        return df
        
    except Exception as e:
        db.session.rollback()
        return pd.DataFrame({"error": [str(e)]})

    finally:
        db.session.close()

    