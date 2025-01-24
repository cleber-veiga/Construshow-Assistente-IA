from datetime import datetime, timedelta
from langchain.memory import ConversationBufferMemory
from collections import deque

class ChatMemory:
    _instance = None  # Instância única (Singleton)

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.memory = {}  # Dicionário para armazenar memórias por id_chat
        return cls._instance

    def get_memory(self, id_chat):
        """
        Retorna a memória do chat específico. Se não existir, cria uma nova.
        :param id_chat: ID do chat.
        :return: Instância de ConversationBufferMemory.
        """
        if id_chat not in self.memory:
            self.memory[id_chat] = {
                "conversation_memory": ConversationBufferMemory(
                    human_prefix="USER",
                    ai_prefix="IA",
                    input_key="input",
                    output_key="output"
                ),
                "analysis_data": {},  # Dados de análise por classificação
                "pending_contexts": deque() # Fila de contextos não resolvidos
            }
        return self.memory[id_chat]

    def add_interaction(self, id_chat, user_input=None, ai_response=None, hash=None, domain=None):
        """
        Adiciona uma interação USER-IA à memória do chat.
        Pode adicionar apenas a mensagem do usuário, apenas a resposta da IA, ou ambas.
        :param id_chat: ID do chat.
        :param user_input: Input do usuário (opcional).
        :param ai_response: Resposta da IA (opcional).
        :param hash: Identificador hash para a análise (pode ser único ou uma lista, opcional).
        :param domain: Domínio da interação (pode ser único ou uma lista, opcional).
        """
        if user_input is None and ai_response is None:
            raise ValueError("Pelo menos um dos parâmetros (user_input ou ai_response) deve ser fornecido.")

        memory = self.get_memory(id_chat)

        # Garante que hash e category sejam listas
        hash_list = hash if isinstance(hash, list) else [hash] if hash is not None else []
        category_list = domain if isinstance(domain, list) else [domain] if domain is not None else []

        # Prepara os dicionários de input e output
        input_dict = {
            "input": user_input if user_input is not None else "",
            "additional_kwargs": {
                "hash": hash_list,
                "category": category_list
            }
        }
        output_dict = {
            "output": ai_response if ai_response is not None else "",
            "additional_kwargs": {
                "hash": hash_list,
                "category": category_list
            }
        }

        # Adiciona a interação à memória
        memory["conversation_memory"].save_context(input_dict, output_dict)
        
    def add_analysis_data(self, id_chat, classification, data,unique_hash):
        """
        Adiciona dados de análise à memória do chat.
        :param id_chat: ID do chat.
        :param classification: Classificação dos dados (ex: "search_customer_buy_history").
        :param data: Dados a serem armazenados.
        """
        memory = self.get_memory(id_chat)
        memory["analysis_data"][classification] = {
            "data_relationship_hash": unique_hash,
            "data": data,
            "timestamp": datetime.now().timestamp()  # Armazena o timestamp atual
        }

    def get_recent_analysis_data(self, id_chat, classification, max_age_seconds=3600):
        """
        Retorna os dados de análise se existirem e forem recentes.
        :param id_chat: ID do chat.
        :param classification: Classificação dos dados.
        :param max_age_seconds: Idade máxima permitida dos dados (em segundos).
        :return: Dados se forem recentes, caso contrário None.
        """
        memory = self.get_memory(id_chat)
        if classification not in memory["analysis_data"]:
            return None

        data_entry = memory["analysis_data"][classification]
        data_age = datetime.now().timestamp() - data_entry["timestamp"]

        if data_age <= max_age_seconds:
            return data_entry["data"]
        else:
            return None

    def get_chat_history(self, id_chat):
        """
        Retorna o histórico de conversas de um chat específico.
        :param id_chat: ID do chat.
        :return: Lista de interações.
        """
        memory = self.get_memory(id_chat)
        return memory["conversation_memory"].chat_memory.messages

    def get_chat_memory(self, id_chat):
        """
        Retorna toda a memória de um chat específico.
        :param id_chat: ID do chat.
        :return: Dicionário com interações e dados de análise.
        """
        memory = self.get_memory(id_chat)
        return {
            "conversation_history": self.get_chat_history(id_chat),
            "analysis_data": memory["analysis_data"]
        }
    
    def print_memory(self, id_chat):
        """
        Imprime o conteúdo da memória para um id_chat específico.
        :param id_chat: ID do chat.
        """
        if id_chat not in self.memory:
            print(f"Nenhuma memória encontrada para o chat {id_chat}.")
            return

        memory = self.get_memory(id_chat)
        chat_history = memory["conversation_memory"].chat_memory.messages

        print(f"Memória do chat {id_chat}:")
        for message in chat_history:
            if message.type == "human":
                print(f"USER: {message.content}")
            elif message.type == "ai":
                print(f"IA: {message.content}")

    def add_pending_context(self, id_chat, context):
        """
        Adiciona um contexto à fila de pendências do chat.
        :param id_chat: ID do chat.
        :param context: Dicionário com informações do contexto (ex: {"tipo": "historico", "pergunta": "..."}).
        """
        memory = self.get_memory(id_chat)
        memory["pending_contexts"].append(context)