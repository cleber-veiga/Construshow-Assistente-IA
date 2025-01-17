from typing import Tuple, Dict, Any, List, Optional

class RequestValidator:
    @staticmethod
    def validate_json(data: Optional[Dict[str, Any]]) -> Tuple[Optional[Dict[str, Any]], int]:
        """
        Valida se o JSON é válido e não está vazio.
        
        Args:
            data: Dicionário com os dados do JSON.
        
        Returns:
            Tuple[Optional[Dict[str, Any]], int]: Dados JSON e código de status.
        """
        if data is None:
            return {"error": "O corpo da requisição deve ser um JSON válido."}, 400
            
        if not data:
            return {"error": "O corpo da requisição não pode estar vazio."}, 400
            
        return data, 200
    
    @staticmethod
    def validate_required_fields(data: dict, required_fields: List[Dict[str, Any]]) -> Tuple[Optional[Dict[str, Any]], int]:
        """
        Valida se todos os campos obrigatórios estão presentes e são do tipo correto.
        
        Args:
            data: Dicionário com os dados da requisição.
            required_fields: Lista de dicionários com nome e tipo dos campos obrigatórios.
        
        Returns:
            Tuple[Optional[Dict[str, Any]], int]: Dados validados e código de status.
        """
        missing_fields = []
        type_errors = []
        
        for field in required_fields:
            field_name = field['name']
            field_type = field['type']
            
            # Verifica se o campo existe
            if field_name not in data:
                missing_fields.append(field_name)
                continue
            
            # Verifica o tipo do campo
            if not isinstance(data[field_name], field_type):
                type_errors.append(f"O campo '{field_name}' deve ser do tipo {field_type.__name__}.")
        
        if missing_fields:
            return {"error": f"Campos obrigatórios ausentes: {', '.join(missing_fields)}"}, 400
            
        if type_errors:
            return {"error": "Erro de validação de tipos", "details": type_errors}, 400
            
        return data, 200
    
    @staticmethod
    def validate_request(data: Optional[Dict[str, Any]], required_fields: List[Dict[str, Any]]) -> Tuple[Optional[Dict[str, Any]], int]:
        """
        Valida o JSON e os campos obrigatórios.
        
        Args:
            data: Dicionário com os dados do JSON.
            required_fields: Lista de dicionários com nome e tipo dos campos obrigatórios.
        
        Returns:
            Tuple[Optional[Dict[str, Any]], int]: Dados validados e código de status.
        """
        # Valida o JSON
        json_validation_result, status_code = RequestValidator.validate_json(data)
        if status_code != 200:
            return json_validation_result, status_code
        
        # Valida os campos obrigatórios
        return RequestValidator.validate_required_fields(json_validation_result, required_fields)