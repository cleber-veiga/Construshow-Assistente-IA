
from app.api.v1.utils.identify_relationship import ClassifyRelationship
from app.core.classify.classify import classifier, predict_intention
from app.database.processing.chat.chat import create_new_chat_detail, create_new_chat_detail_domain, search_chat_header_and_datail, search_or_open_chat
from app.database.processing.domain_distribution import create_complete_question, search_and_format_domain_data
from app.database.processing.format_data import unify_data
from app.extensions.client.response_handler import ResponseHandler
from config import loger,conf
from app.api.v1.utils.split import remove_duplicate_dicts, split_message
from app.core.data.cleaner import TextCleaner
from app.client.v1 import api_groq as gq

class ChatProcessorMessage:
    @staticmethod
    def process_chat_request_message(data):
        """Processa a requisição de chat."""
        id_chat = data['id_chat']
        message = data['message']

        loger.log('DEBUG', 'Dividindo submensagens')
        sub_messages = split_message(message)

        loger.log('DEBUG', 'Realizando classficiação das submensagens')
        classify_relationship = ChatProcessorMessage.classify_sub_messages(sub_messages)
        print(f'Depois: {classify_relationship}')

        loger.log('DEBUG', 'Calculando o score de confiança')
        trust_scores = ChatProcessorMessage.calculate_trust_scores(classify_relationship, conf.get_processing_config())
        domain_set = ChatProcessorMessage.filter_trust_scores(trust_scores)

        print(domain_set)
        loger.log('DEBUG', 'Gerando respostas')
        response = ChatProcessorMessage.generate_response(id_chat, message, domain_set)
        ChatProcessorMessage.save_response_to_database(id_chat, message, response, domain_set)

        return unify_data(search_chat_header_and_datail(id_chat, 1))

    @staticmethod
    def classify_sub_messages(sub_messages):
        """Classifica submensagens e identifica entidades."""
        cleaner = TextCleaner(conf.get_processing_config())
        process_entities = ClassifyRelationship()

        classify_relationship = []
        for idx, sub_msg in enumerate(sub_messages):
            predict_message = cleaner.clean_text(sub_msg)
            loger.log('DEBUG', f'Classificando intenção: {predict_message}')

            message_intention = predict_intention(predict_message)
            entity_main = process_entities.run_identify_entity_main(predict_message)
            entities_msg = process_entities.run_identify_entity(predict_message)
            classify_relationship.append(process_entities.run_relationship_processing(entities_msg))

            classify_relationship[idx]['shot_message'] = sub_msg
            classify_relationship[idx]['string_intention'] = 'search' if message_intention == 'BUSCAR_DADO' else 'doubt'

            print(f'Antes: {classify_relationship}')
        return remove_duplicate_dicts(classify_relationship)
    
    @staticmethod
    def calculate_trust_scores(classify_relationship, config):
        """Calcula as pontuações de confiança para as classificações."""
        trust_scores = {}
        for idx, item in enumerate(classify_relationship):
            sub_msg = item['shot_message']
            string_intention = item['string_intention']
            string_domain = item['path_rn']

            _, domains, trust, mlb = classifier(sub_msg, string_intention + string_domain, config)

            for domain in domains:
                index = list(mlb.classes_).index(domain)
                score = trust[index]

                if domain not in trust_scores or trust_scores[domain]['trust'] < score:
                    trust_scores[idx] = {'domain': domain, 'trust': score, 'short_message': sub_msg}

        return trust_scores
    
    @staticmethod
    def filter_trust_scores(trust_scores):
        """Filtra as pontuações para retornar apenas os domínios mais confiáveis."""
        domain_set = {
                idx: {
                    'domain': v['domain'],  # Inclui o domínio, se necessário
                    'trust': float(v['trust']),
                    'short_message': v['short_message']
                }
                for idx, (_, v) in enumerate(sorted(trust_scores.items(), key=lambda item: item[0]))
            }
        filtered_domain_set = {}
        for item in domain_set.values():
            domain = item['domain']
            trust = item['trust']
            
            # Se o domínio ainda não está no resultado ou o trust atual é maior, substituímos
            if domain not in filtered_domain_set or trust > filtered_domain_set[domain]['trust']:
                filtered_domain_set[domain] = item

        # Redefine domain_set para usar os valores filtrados
        domain_set = {
            idx: value for idx, value in enumerate(filtered_domain_set.values())
        }
        return domain_set
    
    @staticmethod
    def generate_response(id_chat, message, domain_set):
        """Gera a resposta baseada nos domínios processados."""
        response_handler = ResponseHandler()
        response_greeting, response_unknown, response_domain = '', '', ''

        for item in domain_set.values():
            if item['domain'] == 'greeting':
                response_greeting += response_handler.get_response(message, 'short_greeting')
            elif item['domain'] == 'unknown':
                response_unknown = response_handler.get_response(message, 'unknown')
            else:
                response_domain += search_and_format_domain_data(item['domain'], id_chat)

        if response_unknown:
            return response_greeting + ' ' + response_unknown if response_greeting else response_unknown

        if response_greeting and len(domain_set) == 1:
            return response_greeting

        complete_question = create_complete_question(message, response_domain)
        return gq.chat_with_groq(complete_question)
    
    @staticmethod
    def save_response_to_database(id_chat, message, response, domain_set):
        """Salva a interação do chat no banco de dados."""
        id_message = create_new_chat_detail(id_chat, 'USER', message)

        for item in domain_set.values():
            create_new_chat_detail_domain(id_message[0], item['domain'], item['short_message'], item['trust'])

        create_new_chat_detail(id_chat, 'SYSTEM', response)

class ChatProcessorOpen:
    @staticmethod
    def process_chat_request_open(data):
        loger.log('DEBUG',f'Inicia criação do chat')
        response = search_or_open_chat(data)

        loger.log('DEBUG',f'Inicia processo para unificar dados compartilhados e aninhar mensagens')
        response = unify_data(response)
        return response