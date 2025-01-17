import pickle
import spacy

class ClassifyRelationship:

    def __init__(self):
        self.entities = None
        self.df = self._loads_entity_relationship()
        self.data = self.transform_df_to_dictionary()
        self.translation_df = self._loads_entity_translation()
        self.nlp = self._load_nlp()
    
    def _loads_entity_relationship(self):
        with open("mod/app/models/saved/entity_relationship.pkl", "rb") as f:
            df = pickle.load(f)
        return df
    
    def _load_nlp(self):
        return spacy.load('mod/app/models/pt_core_news_md-3.8.0')
    
    def _loads_entity_translation(self):
        with open("mod/app/models/saved/entity_translation.pkl", "rb") as f:
            df = pickle.load(f)
        return df
    def transform_df_to_dictionary(self):
        df_filtered = self.df[['entity', 'weight', 'parent']]
        result_dict = {}

        for _, row in df_filtered.iterrows():
            entity = row['entity']
            weight = row['weight']
            parent = row['parent']

            # Se a entidade ainda não estiver no dicionário, adicioná-la
            if entity not in result_dict:
                result_dict[entity] = {
                    'weight': weight,
                    'parents': []
                }
            if parent:
                result_dict[entity]['parents'].append(parent)

        # Remover duplicatas nas listas de dependências
        for entity in result_dict:
            result_dict[entity]['parents'] = list(set(result_dict[entity]['parents']))

        return result_dict

    def generate_path_to_RN(self):
        """Gera o caminho para a RN com base nas entidades identificadas."""
        filtered_entities = [entity for entity in self.entities if self.data[entity]["weight"] != 2]
        ordered_entities = sorted(filtered_entities, key=lambda e: self.data[e]["weight"])
        
        translated_entities = [
            self.translation_df.loc[self.translation_df["translation"] == entity, "entity"].values[0]
            for entity in ordered_entities
        ]

        return "/" + "/".join(translated_entities)
    
    def validate_relationship(self):
        for entity in self.entities:
            dependencies = self.data[entity]['parents']
            # Ignora dependências alternativas se pelo menos uma está presente
            if any(dep in self.entities for dep in dependencies):
                continue
            missing = [dep for dep in dependencies if dep not in self.entities]
            if missing:
                return False, missing, entity
        return True, [], ""

    def run_relationship_processing(self,entities):
        self.entities = entities
        valid, missing, main_entity = self.validate_relationship()

        if valid:
            path = self.generate_path_to_RN()
            result = {
                "success": True,
                "path_rn": path,
                "entitie": "",
                "missing": []
            }
        else:
            result = {
                "success": False,
                "path_rn": "",
                "entitie": main_entity,
                "missing": missing
            }

        return result
    
    def run_identify_entity(self,message):
        entities_list = self.df['entity'].drop_duplicates().tolist()
        doc = self.nlp(message)
        identify = []

        for token in doc:
            if token.lemma_.lower() in entities_list:
                identify.append(token.lemma_.lower())
        identify = list(set(identify))

        return identify
    
    def run_identify_entity_main(self,message):
        entities_list = self.df['entity'].drop_duplicates().tolist()
        doc = self.nlp(message)
    
        entities_present = [entity for entity in entities_list if entity in message.lower()]
        
        if len(entities_present) == 1:
            return entities_present[0]
        
        main_verb = None
        for token in doc:
            if token.pos_ == "VERB" and token.dep_ == "ROOT":
                main_verb = token
                break
        
        # Se encontrar o verbo principal, procura a entidade mais próxima
        if main_verb:
            for token in main_verb.children:
                if token.lemma_.lower() in entities_present:
                    return token.lemma_.lower()
        
        # Se não encontrar, retorna a primeira entidade presente
        return entities_present[0] if entities_present else None