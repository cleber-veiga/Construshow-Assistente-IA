from app.api.v1.utils.identify_relationship import ClassifyRelationship


process_entities = ClassifyRelationship()





while True:
    input_message = input("Digite sua mensagem:")

    if input_message =="Sair":
        break
    
    entity_main = process_entities.run_identify_entity_main(input_message)
    print(entity_main)