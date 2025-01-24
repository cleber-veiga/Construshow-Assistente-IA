from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
from config import conf

class LLMFactory:
    """Fábrica para criação de instâncias de modelos LLM com base na configuração."""

    def __init__(self):
        self.config = conf.get_llm_config()

    def get_llm(self):
        """Retorna uma instância de LLM com base nas configurações do cliente."""
        llm_provider = self.config['llm_provider'].lower()

        if llm_provider == "groq":
            return self._create_groq_llm()
        elif llm_provider == "gpt":
            return self._create_gpt_llm()
        else:
            raise ValueError(f"Provedor de LLM desconhecido: {llm_provider}")

    def _create_groq_llm(self):
        """Cria e retorna uma instância do modelo Groq."""
        api_key = self.config['llm_api_key']
        model = self.config['llm_model']
        temperature = 0.7

        if not api_key:
            raise ValueError("API Key para Groq não foi fornecida na configuração.")
        
        if not model:
            raise ValueError("Modelo para Groq não foi fornecido na configuração.")

        return ChatGroq(
            model=model,
            api_key=api_key,
            temperature=temperature,
            max_tokens=4000,
        )

    def _create_gpt_llm(self):
        """Cria e retorna uma instância do modelo OpenAI GPT."""
        api_key = self.config.get("gpt_api_key")
        model = self.config.get("gpt_model", "text-davinci-003")

        if not api_key:
            raise ValueError("API Key para GPT não foi fornecida na configuração.")

        return ChatOpenAI(api_key=api_key, model=model)