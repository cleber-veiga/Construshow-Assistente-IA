
class BACKUPChatMessageCoreResource(Resource):
    def post(self):
        """Realiza validação da estrutura do JSON recebido"""
        loger.log('DEBUG',f'Iniciando validação do JSON')
        validation_error = RequestValidator.validate_json_request()
        if validation_error:
            loger.log('ERROR',f'request JSON POST inválido! /api/v1/chat/message/')
            return validation_error
        
        try:
            data = request.get_json()

            """Realiza validação dos campos obrigatórios"""
            required_fields = [
                {'name': 'id_chat', 'type': int},
                {'name': 'message', 'type': str}
            ]

            loger.log('DEBUG',f'Inicia validação dos campos obrigatórios')
            field_validation_error = RequestValidator.validate_required_fields(data, required_fields)
            if field_validation_error:
                loger.log('ERROR',f'Existem campos obrigatórios não informados {field_validation_error}')
                return field_validation_error
            
            cleaner = TextCleaner(conf.get_processing_config())
            process_entities = ClassifyRelationship()

            id_chat = data['id_chat']
            message = data['message']
            classify_relationship = []

            loger.log('DEBUG',f'Faz a divisão das sub menssagens')
            sub_messages = split_message(message)
            for idx, sub_msg in enumerate(sub_messages):

                predict_message = cleaner.clean_text(sub_msg)
                
                loger.log('DEBUG',f'Classificação de intenção, sub menssagem: {predict_message}')
                message_intention = predict_intention(predict_message)
                loger.log('DEBUG',f'Classificação de intenção realizada, resultado: {message_intention}')

                entity_main = process_entities.run_identify_entity_main(predict_message)
                loger.log('DEBUG',f'Analisado entidade principal da pergunta: {entity_main}')

                entities_msg = process_entities.run_identify_entity(predict_message)
                loger.log('DEBUG',f'Analisado entidades existentes na pergunta: {entities_msg}')

                classify_relationship.append(process_entities.run_relationship_processing(entities_msg))
                loger.log('DEBUG',f'Analisado relacionamento das entidades: {classify_relationship}')

                string_intention = 'search' if message_intention == 'BUSCAR_DADO' else 'doubt'
                classify_relationship[idx]['shot_message'] = sub_msg
                classify_relationship[idx]['string_intention'] = string_intention

            classify_relationship = remove_duplicate_dicts(classify_relationship)
                
            trust_scores = {}
            for item in classify_relationship:
                for chave, valor in item.items():
                    if chave == 'shot_message':
                        sub_msg = valor
                    if chave == 'path_rn':
                        string_domain = valor
                    if chave == 'string_intention':
                        string_intention = valor
                sub_msg, domains, trust, mlb = classifier(sub_msg,string_intention + string_domain,conf.get_processing_config())

                for domain in domains:
                    index = list(mlb.classes_).index(domain)  # Localiza o índice da categoria no MultiLabelBinarizer
                    score = trust[index]  # Associa a confiança correta
                    
                    # Atualiza ou adiciona a maior confiança para a categoria
                    if domain not in trust_scores or trust_scores[domain]['trust'] < score:
                        trust_scores[idx] = {'domain': domain, 'trust': score, 'short_message': sub_msg}

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

            response_greeting = ''
            response_unknown = ''
            response_domain = ''

            id_message = create_new_chat_detail(id_chat, 'USER', message)
            
            response_handler = ResponseHandler()
            for _, item in domain_set.items():
                create_new_chat_detail_domain(id_message[0], item['domain'], item['short_message'], item['trust'])
                
                if item['domain'] == 'greeting':
                    if len(domain_set) > 1:
                        response_greeting += response_handler.get_response(message, 'short_greeting')
                    else:
                        response_greeting += response_handler.get_response(message, item['domain'])
                elif item['domain'] == 'unknown':
                    response_unknown = response_handler.get_response(message, item['domain'])
                else:
                    response_domain += search_and_format_domain_data(item['domain'], id_chat)
            
            complete_question = create_complete_question(message, response_domain)
            
            if response_unknown:
                if not response_greeting:
                    response = response_unknown
                else:
                    response = response_greeting + ' ' + response_unknown
            elif response_greeting and len(domain_set) == 1:
                response = response_greeting
            else:
                response = gq.chat_with_groq(complete_question)
            
            # Insere perguntas e respostas no banco de dados
            id_message = create_new_chat_detail(id_chat, 'SYSTEM', response)
            response = unify_data(search_chat_header_and_datail(id_chat,1))
            
            response = make_response(jsonify(response))
            response.status_code = 200
            return response
        except Exception as e:
            loger.log('ERROR',f"Erro ao processar a requisição: {str(e)}")
            return {
                "error": f"Erro ao processar a requisição: {str(e)}"
            }, 500

class ChatMessageResource(Resource):
    def get(self):
        return jsonify({'message':"Chat Recebido"})
    
    def post(self):
        """Realiza validação da estrutura do JSON recebido"""
        loger.log('DEBUG',f'Iniciando validação do JSON')
        validation_error = RequestValidator.validate_json_request()
        if validation_error:
            loger.log('ERROR',f'request JSON POST inválido! /api/v1/chat/open/')
            return validation_error
        
        try:
            data = request.get_json()

            """Realiza validação dos campos obrigatórios"""
            required_fields = [
                {'name': 'id_chat', 'type': int},
                {'name': 'message', 'type': str}
            ]

            loger.log('DEBUG',f'Inicia validação dos campos obrigatórios')
            field_validation_error = RequestValidator.validate_required_fields(data, required_fields)
            if field_validation_error:
                loger.log('ERROR',f'Existem campos obrigatórios não informados {field_validation_error}')
                return field_validation_error
            
            id_chat = data['id_chat']
            message = data['message']
            validation_entities = []

            loger.log('DEBUG',f'Faz a divisão das sub menssagens')
            sub_messages = split_message(message)
            for idx, sub_msg in enumerate(sub_messages):
                
                loger.log('DEBUG',f'Classificação de intenção, sub menssagem: {sub_msg}')
                result = classifier_intention(sub_msg,conf.get_processing_config())
                loger.log('DEBUG',f'Classificação de intenção realizada, resultado: {result}')

                loger.log('DEBUG',f'Inicializa a classificação de relacionamentos')
                classify_relation = ClassifyRelationship(result['entities'])
                response_identify= classify_relation.run_relationship_processing()
                loger.log('DEBUG',f'Resultado dos relacionamentos analisados: {response_identify}')

                string_intention = 'search' if result['intention'] == 'BUSCAR_DADO' else 'doubt'
                validation_entities.append(response_identify)
                validation_entities[idx]['shot_message'] = sub_msg
                validation_entities[idx]['string_intention'] = string_intention

            validation_entities = remove_duplicate_dicts(validation_entities)
            
            trust_scores = {}
            for item in validation_entities:
                for chave, valor in item.items():
                    if chave == 'shot_message':
                        sub_msg = valor
                    if chave == 'path_rn':
                        string_domain = valor
                    if chave == 'string_intention':
                        string_intention = valor
                sub_msg, domains, trust, mlb = classifier(sub_msg,string_intention + string_domain,conf.get_processing_config())

                for domain in domains:
                    index = list(mlb.classes_).index(domain)  # Localiza o índice da categoria no MultiLabelBinarizer
                    score = trust[index]  # Associa a confiança correta
                    
                    # Atualiza ou adiciona a maior confiança para a categoria
                    if domain not in trust_scores or trust_scores[domain]['trust'] < score:
                        trust_scores[idx] = {'domain': domain, 'trust': score, 'short_message': sub_msg}

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

            response_greeting = ''
            response_unknown = ''
            response_domain = ''

            id_message = create_new_chat_detail(id_chat, 'USER', message)
            
            response_handler = ResponseHandler()
            for _, item in domain_set.items():
                create_new_chat_detail_domain(id_message[0], item['domain'], item['short_message'], item['trust'])
                
                if item['domain'] == 'greeting':
                    if len(domain_set) > 1:
                        response_greeting += response_handler.get_response(message, 'short_greeting')
                    else:
                        response_greeting += response_handler.get_response(message, item['domain'])
                elif item['domain'] == 'unknown':
                    response_unknown = response_handler.get_response(message, item['domain'])
                else:
                    response_domain += search_and_format_domain_data(item['domain'], id_chat)
            
            complete_question = create_complete_question(message, response_domain)
            
            if response_unknown:
                if not response_greeting:
                    response = response_unknown
                else:
                    response = response_greeting + ' ' + response_unknown
            elif response_greeting and len(domain_set) == 1:
                response = response_greeting
            else:
                response = gq.chat_with_groq(complete_question)
            
            # Insere perguntas e respostas no banco de dados
            id_message = create_new_chat_detail(id_chat, 'SYSTEM', response)
            response = unify_data(search_chat_header_and_datail(id_chat,1))
            
            response = make_response(jsonify(response))
            response.status_code = 200
            return response
        
        except Exception as e:
            loger.log('ERROR',f"Erro ao processar a requisição: {str(e)}")
            return {
                "error": f"Erro ao processar a requisição: {str(e)}"
            }, 500