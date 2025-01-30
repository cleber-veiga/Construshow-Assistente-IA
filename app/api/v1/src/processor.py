from app.api.v1.utils.identify_relationship import ClassifyRelationship
from app.client.v1.llm_providers import LLMFactory
from app.core.chat_memory import ChatMemory
from app.core.classify.classify import classifier, predict_intention
from app.database.processing.chat.chat import create_new_chat_detail, create_new_chat_detail_domain, search_chat_header_and_datail, search_or_open_chat
from app.database.processing.domain_distribution import create_complete_question, search_and_format_domain_data
from app.database.processing.format_data import unify_data
from config import loger,conf
from app.api.v1.utils.split import remove_duplicate_dicts, split_message,generate_unique_hash
from app.core.data.cleaner import TextCleaner
from app.client.v1 import api_groq as gq
from langchain.schema import HumanMessage, AIMessage
from langchain_core.runnables import RunnablePassthrough

class ChatProcessorMessage:
    def __init__(self):
        self.memory = ChatMemory()
        self.llm_factory = LLMFactory()
        self.process_entities = ClassifyRelationship()
        self.cleaner = TextCleaner(conf.get_processing_config())

    def process_chat_request_message(self,data):
        """Processa a requisição de chat"""
        id_chat = data['id_chat']
        message = data['message']

        """Identifica a entidade principal da pergunta"""
        loger.log('DEBUG',"Identifica a entidade principal da pergunta")
        entity_main = self.process_entities.run_identify_entity_main(message)

        """Realiza a divisão em submenssagens"""
        loger.log('DEBUG',"Realiza a divisão em submenssagens")
        sub_messages = split_message(message)

        """Identifica as entidades de cada submenssagem e realiza a análise dos seus relacionamentos"""
        loger.log('DEBUG',"Identifica as entidades de cada submenssagem e realiza a análise dos seus relacionamentos")
        unique_hash_mensage,contextual_messages = self.contextual_message_analyzer(id_chat,message,entity_main,sub_messages)

        loger.log('DEBUG',f"Classifica o domínio das mensagens -> contextual_messages: {contextual_messages}, conf: {conf.get_processing_config()}")
        contextual_messages = self.sort_message_domains(contextual_messages, conf.get_processing_config())

        loger.log('DEBUG',"Inicia a geração da resposta")
        response = self.generate_response_langchain(id_chat, message, contextual_messages,unique_hash_mensage)
        
        loger.log('DEBUG',"Salva a mensagem da IA no banco de dados")
        self.save_response_to_database(id_chat, message, response, contextual_messages)

        return unify_data(search_chat_header_and_datail(id_chat, 1))

    def contextual_message_analyzer(self,id_chat,message,entity_main,sub_messages):

        contextual_messages = []
        unique_hash_mensage = generate_unique_hash()
        
        for idx, sub_msg in enumerate(sub_messages):
            memory_temp = self.memory.get_memory(id_chat)
            memory_pending = memory_temp["pending_contexts"]
            
                    
                
            unique_hash_sub_message = generate_unique_hash()
            message_intention = predict_intention(sub_msg)
            message = self.cleaner.clean_text(sub_msg)
            entities_ignore = ['greeting','unknown']
            
            entities_msg = self.process_entities.run_identify_entity(message) if message_intention not in entities_ignore else []
            
            if memory_pending:
                for pending_context in memory_pending:
                    message_intention = pending_context['original_intention']
                    entities_msg = self.update_entities_with_pending_context(entities_msg, pending_context)
                self.memory.remove_first_pending_context(id_chat)

            contextual_messages.append(self.process_entities.run_relationship_processing(entities_msg,message_intention,entities_ignore))
            contextual_messages[idx]['short_message'] = sub_msg
            contextual_messages[idx]['string_intention'] = message_intention
            contextual_messages[idx]['sub_message_hash'] = unique_hash_sub_message

            if contextual_messages[idx]['success'] == False:
                context_pending = {
                    'original_intention': message_intention,
                    'original_entites': entities_msg,
                    'missing_entities': contextual_messages[idx]['missing'],
                    'sub_mensage': sub_msg,
                    'sub_message_hash': unique_hash_sub_message,
                }
                self.memory.add_pending_context(id_chat,context_pending)
        return unique_hash_mensage,remove_duplicate_dicts(contextual_messages)
    
    def update_entities_with_pending_context(self,entities_msg, pending_context):
        matching_entities = [
            entity for entity in entities_msg if entity in pending_context["missing_entities"]
        ]
        if matching_entities:
            updated_entities = matching_entities.copy()
            updated_entities.extend(pending_context["original_entites"])
            return updated_entities
        return entities_msg

    def analyzes_pending_context(self,sub_messages):
        pass


    def sort_message_domains(self,contextual_messages, config):
        loger.log('DEBUG',"Inicia o For")
        for idx, item in enumerate(contextual_messages):
            if item['success'] == True:
                if item['string_intention'] != 'greeting' and item['path_rn'] != '/':
                    loger.log('DEBUG',"Inicia a classificação")
                    _, domain, trust, mlb = classifier(item['short_message'], str(item['string_intention']) + str(item['path_rn']), config)
                    
                    contextual_messages[idx]['domain'] = domain
                    contextual_messages[idx]['trust'] = trust
                else:
                    loger.log('DEBUG',"É greeting")
                    contextual_messages[idx]['domain'] = 'greeting'
                    contextual_messages[idx]['trust'] = 0
            else:
                loger.log('DEBUG',"É Falso")
                contextual_messages[idx]['domain'] = None
                contextual_messages[idx]['trust'] = None

        return contextual_messages
    
    def generate_response_langchain(self, id_chat, message, contextual_messages, unique_hash_mensage):
        # Processamento de mensagens contextuais
        for idx, item in enumerate(contextual_messages):
            if item['success']:
                if item['domain'] != 'greeting' and item['entitie'] != '/':
                    response_data = search_and_format_domain_data(item['domain'], id_chat)
                    self.memory.add_analysis_data(id_chat, item['domain'], response_data, item['sub_message_hash'])
            else:
                response_data = self.generate_followup_message(
                    entity=item.get('entitie', 'entidade desconhecida'),
                    message=item['short_message'],
                    entities=item.get('missing', [])
                )
                self.memory.add_analysis_data(id_chat, item['domain'], response_data, item['sub_message_hash'])

        # Adiciona a interação do usuário na memória
        self.memory.add_interaction(
            id_chat=id_chat,
            user_input=message,
            hash=unique_hash_mensage
        )

        # Prepara o contexto para o LLM
        try:
            input_messages = self.memory.prepare_invoke_input(id_chat, include_pending=False)
            
            # Ajuste: Garantir que as mensagens estão no formato correto para o LLM
            llm = self.llm_factory.get_llm()
            
            # Construir a cadeia sem RunnablePassthrough desnecessário
            chain = llm | {
                "response": lambda msg: msg.content,
                "pending_actions": lambda msg: msg.additional_kwargs.get("pending_requests", [])
            }

            # Invocar o LLM com as mensagens diretamente
            response = chain.invoke(input_messages)
            response_ia = response.get("response", "")

        except Exception as e:
            response_ia = f"Erro ao gerar resposta via LLM: {str(e)}"
            loger.error(f"Erro no LLM: {e}", exc_info=True)

        # Adiciona a resposta da IA na memória
        self.memory.add_interaction(
            id_chat=id_chat,
            ai_response=response_ia,
            hash=unique_hash_mensage
        )
        #self.memory.save_memory_to_file(id_chat)
        return response_ia if response_ia else "Desculpe, não consegui gerar uma resposta no momento."
    
    def save_response_to_database(self,id_chat, message, response, classify):
        """Salva a interação do chat no banco de dados."""
        id_message = create_new_chat_detail(id_chat, 'USER', message)

        for idx, item in enumerate(classify):
            create_new_chat_detail_domain(id_message[0], item['domain'], item['short_message'], item['trust'])

        create_new_chat_detail(id_chat, 'IA', response)

    def generate_followup_message(self,entity: str, message: str, entities: list) -> str:
        """
        Gera uma mensagem para solicitar mais informações sobre o contexto de uma pergunta.

        Args:
            entity (str): Entidade principal mencionada na pergunta.
            message (str): Mensagem ou pergunta do usuário.
            entities (list): Lista de entidades relacionadas para refinar o contexto.

        Returns:
            str: Mensagem para solicitar mais informações ao LLM.
        """
        # Formatando a lista de entidades para ser exibida na mensagem
        entities_list = ', '.join(entities)

        # Mensagem gerada
        followup_message = (
            f"Em relação à pergunta: '{message}', o usuário está solicitando informações sobre '{entity}'. "
            f"No entanto, solicite mais informações ao usuário para confirmar se ele está se referindo a uma das seguintes opções: {entities_list}."
            f"Esta é uma mensagem de controle do sistema então responda como se você estivesse solicitando essas informações"
        )

        return followup_message

class ChatProcessorOpen:
    def __init__(self):
        self.memory = ChatMemory() 
    
    def feed_memory_with_history(self,chat_history):
        """
        Alimenta a memória com o histórico de chat.
        Ignora mensagens em branco.
        """
        id_chat = chat_history['id_chat']
        context_messages = chat_history['context_message']

        # Inverte a ordem das mensagens (da mais antiga para a mais recente)
        context_messages_reversed = list(reversed(context_messages))

        # Itera sobre as mensagens do histórico (agora na ordem correta)
        i = 0
        while i < len(context_messages_reversed):
            message = context_messages_reversed[i]
            sender = message['sender']
            content = message['message']

            # Ignora mensagens em branco
            if content.strip() == "":
                i += 1
                continue

            if sender == 'USER':
                # Verifica se há uma resposta da IA correspondente
                if i + 1 < len(context_messages_reversed) and context_messages_reversed[i + 1]['sender'] == 'IA':
                    # Adiciona a mensagem do usuário e a resposta da IA juntas
                    self.memory.add_interaction(
                        id_chat,
                        user_input=content,
                        ai_response=context_messages_reversed[i + 1]['message']
                    )
                    i += 2  # Avança duas posições (USER e IA)
                else:
                    # Adiciona apenas a mensagem do usuário
                    self.memory.add_interaction(id_chat, user_input=content)
                    i += 1  # Avança uma posição
            elif sender == 'IA':
                # Adiciona apenas a resposta da IA
                self.memory.add_interaction(id_chat, ai_response=content)
                i += 1  # Avança uma posição

    def process_chat_request_open(self,data):
        loger.log('DEBUG',f'Inicia criação do chat')
        response = search_or_open_chat(data)
        
        loger.log('DEBUG',f'Inicia processo para unificar dados compartilhados e aninhar mensagens')
        response = unify_data(response)
        id_chat = response['id_chat']
        
        if response['context_message']:
            self.feed_memory_with_history(response)
        #self.memory.save_memory_to_file(id_chat)
        return response
    