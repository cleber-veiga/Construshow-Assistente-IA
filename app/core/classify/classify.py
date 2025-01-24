import os
import pickle
import sys
import joblib
from tensorflow.keras.models import load_model
from app.core.data.cleaner import TextCleaner
from config import loger

def classifier(message, domain, config):
    try:
        # Carrega modelo e componentes
        loger.log('DEBUG', "Carregando modelo e componentes")
        model, tokenizer, mlb = load_components(domain)
        
        if model:
            loger.log('DEBUG', "Modelo carregado corretamente")
        else:
            loger.log('ERROR', "Falha ao carregar o modelo")
            return None, None, None, None

        if tokenizer:
            loger.log('DEBUG', "Tokenizer carregado corretamente")
        else:
            loger.log('ERROR', "Falha ao carregar o tokenizer")
            return None, None, None, None

        if mlb:
            loger.log('DEBUG', "MultiLabelBinarizer carregado corretamente")
        else:
            loger.log('ERROR', "Falha ao carregar o MultiLabelBinarizer")
            return None, None, None, None

        # Limpa o texto
        cleaner = TextCleaner(config)
        message = cleaner.clean_text(message)

        if message:
            # Processa e classifica
            loger.log('DEBUG', "Iniciando a predição")
            domain, trust = predict_domain(
                message,
                tokenizer,
                model,
                mlb,
                confidence_threshold=0.6
            )
            return message, domain, trust, mlb  # Retorna mlb também
        else:
            loger.log('ERROR', "Falha ao limpar o texto")
            return None, None, None, None

    except Exception as e:
        loger.log('ERROR', f"Erro ao classificar a mensagem: {str(e)}")
        return None, None, None, None


def load_components(domain):
    try:
        # Validação do domínio
        if not domain or not isinstance(domain, str):
            loger.log('ERROR', f"Domínio inválido: {domain}")
            return None, None, None

        # Divide o domínio e converte para o formato esperado
        domain_split = domain.split('/')
        if len(domain_split) < 3:
            loger.log('ERROR', f"Formato de domínio inválido: {domain}")
            return None, None, None

        domain_convert = f'{domain_split[0]}_{domain_split[1]}_{domain_split[2]}'
        loger.log('DEBUG', f"Domínio convertido: {domain_convert}")

        # Caminho base para os arquivos do modelo
        path_sys = _get_base_dir()
        base_path = os.path.join(path_sys, domain_split[0], domain_split[1], domain_split[2])
        loger.log('DEBUG', f"Caminho base: {base_path}")

        # Carrega o modelo
        model_path = os.path.join(base_path, f"{domain_convert}_best_model.keras")
        loger.log('DEBUG', f"Carregando modelo: {model_path}")
        if not os.path.exists(model_path):
            loger.log('ERROR', f"Arquivo do modelo não encontrado: {model_path}")
            return None, None, None
        try:
            model = load_model(model_path)
            loger.log('DEBUG', "Modelo carregado com sucesso.")
        except Exception as e:
            loger.log('ERROR', f"Erro ao carregar o modelo: {str(e)}")
            return None, None, None

        # Carrega o tokenizer
        tokenizer_path = os.path.join(base_path, f"{domain_convert}_tokenizer.pkl")
        loger.log('DEBUG', f"Carregando tokenizer: {tokenizer_path}")
        if not os.path.exists(tokenizer_path):
            loger.log('ERROR', f"Arquivo do tokenizer não encontrado: {tokenizer_path}")
            return None, None, None
        try:
            with open(tokenizer_path, 'rb') as f:
                tokenizer = pickle.load(f)
            loger.log('DEBUG', "Tokenizer carregado com sucesso.")
        except Exception as e:
            loger.log('ERROR', f"Erro ao carregar o tokenizer: {str(e)}")
            return None, None, None

        # Carrega o MultiLabelBinarizer
        mlb_path = os.path.join(base_path, f"{domain_convert}_mlb.pkl")
        loger.log('DEBUG', f"Carregando MultiLabelBinarizer: {mlb_path}")
        if not os.path.exists(mlb_path):
            loger.log('ERROR', f"Arquivo do MultiLabelBinarizer não encontrado: {mlb_path}")
            return None, None, None
        try:
            with open(mlb_path, 'rb') as f:
                mlb = pickle.load(f)
            loger.log('DEBUG', "MultiLabelBinarizer carregado com sucesso.")
        except Exception as e:
            loger.log('ERROR', f"Erro ao carregar o MultiLabelBinarizer: {str(e)}")
            return None, None, None

        return model, tokenizer, mlb

    except Exception as e:
        loger.log('ERROR', f"Erro inesperado ao carregar componentes: {str(e)}")
        return None, None, None


def _get_base_dir():
    """Determina o diretório base do script ou executável."""
    if getattr(sys, 'frozen', False):  # Executável
        base_dir = os.path.dirname(sys.executable)
        path = os.path.abspath(os.path.join(base_dir, "mod", "app", "models", "saved"))
    else:  # Script
        current_dir = os.path.dirname(os.path.abspath(__file__))
        path = os.path.abspath(os.path.join(current_dir, "../../..", "mod", "app", "models", "saved"))
    loger.log('DEBUG', f"Caminho base: {path}")
    return path


def predict_domain(text, tokenizer, model, mlb, confidence_threshold=0.6):
    try:
        sequence = tokenizer.transform([text])
        predictions = model.predict(sequence, verbose=0)[0]

        # Filtra os domínios com confiança acima do limiar
        selected_domains = [
            (domain, prob) for domain, prob in zip(mlb.classes_, predictions)
            if prob >= confidence_threshold
        ]
        
        # Se houver domínios selecionados, retorna o com maior confiança
        if selected_domains:
            selected_domains.sort(key=lambda x: x[1], reverse=True)
            return selected_domains[0][0], selected_domains[0][1]
        else:
            return None, None
    except Exception as e:
        loger.log('ERROR', f"Erro ao prever o domínio: {str(e)}")
        return None, None


def predict_intention(message):
    try:
        model_path = os.path.join(_get_base_dir(), "model_predicting_intentions.joblib")
        if not os.path.exists(model_path):
            loger.log('ERROR', f"Arquivo do modelo de intenções não encontrado: {model_path}")
            return None
        model = joblib.load(model_path)
        return model.predict([message])[0]
    except Exception as e:
        loger.log('ERROR', f"Erro ao prever a intenção: {str(e)}")
        return None