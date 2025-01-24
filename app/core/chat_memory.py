from datetime import datetime, timedelta
from langchain.memory import ConversationBufferMemory
from langchain.schema import HumanMessage, AIMessage, SystemMessage
from collections import deque
from typing import ClassVar, Dict, List, Optional, Deque, Any

class ChatMemory:
    # Singleton com anotação de tipo correta
    _instance: ClassVar[Optional["ChatMemory"]] = None
    memory: ClassVar[Dict[str, Dict]]  # Anotação de tipo no nível da classe

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.memory = {}  # Inicialização sem anotação aqui
        return cls._instance

    def get_memory(self, id_chat: str) -> Dict:
        """Inicializa e retorna a memória para um chat específico."""
        if id_chat not in self.memory:
            self.memory[id_chat] = {
                "chat_memory": [],  # Lista de mensagens estruturadas
                "analysis_data": {},
                "pending_contexts": deque(),
                "last_updated": datetime.now()
            }
        return self.memory[id_chat]

    def add_interaction(
        self,
        id_chat: str,
        user_input: Optional[str] = None,
        ai_response: Optional[str] = None,
        hash: Optional[str|List] = None
    ) -> None:
        """Adiciona uma interação à memória no formato LangChain."""
        memory = self.get_memory(id_chat)
        
        # Normaliza metadados
        hash_list = [hash] if isinstance(hash, str) else hash if hash else []
        
        # Adiciona mensagens estruturadas
        if user_input:
            memory["chat_memory"].append(
                HumanMessage(
                    content=user_input,
                    additional_kwargs={
                        "hash": hash_list,
                        "timestamp": datetime.now().timestamp()
                    }
                )
            )
            
        if ai_response:
            memory["chat_memory"].append(
                AIMessage(
                    content=ai_response,
                    additional_kwargs={
                        "hash": hash_list,
                        "pending_contexts": memory["pending_contexts"].copy(),
                        "timestamp": datetime.now().timestamp()
                    }
                )
            )
            
        memory["last_updated"] = datetime.now()

    def add_analysis_data(
        self,
        id_chat: str,
        classification: str,
        data: Any,
        unique_hash: str
    ) -> None:
        """Armazena dados de análise apenas se não existir para o mesmo dia."""
        memory = self.get_memory(id_chat)
        
        # Verifica se já existe uma entrada para esta classificação
        existing_entry = memory["analysis_data"].get(classification)
        
        if existing_entry:
            # Converte timestamps para datas
            existing_date = datetime.fromtimestamp(existing_entry["timestamp"]).date()
            current_date = datetime.now().date()
            
            # Se já existe uma entrada para hoje, não atualiza
            if existing_date == current_date:
                return

        # Adiciona/atualiza somente se for novo ou de outro dia
        memory["analysis_data"][classification] = {
            "data": data,
            "hash": unique_hash,
            "timestamp": datetime.now().timestamp()
        }
        
    def get_recent_analysis(
        self,
        id_chat: str,
        classification: str,
        max_age_seconds: int = 3600
    ) -> Optional[Any]:
        """Recupera dados de análise recentes."""
        memory = self.get_memory(id_chat)
        data = memory["analysis_data"].get(classification)
        
        if data and (datetime.now().timestamp() - data["timestamp"]) <= max_age_seconds:
            return data["data"]
        return None

    def add_pending_context(
        self,
        id_chat: str,
        context: Dict,
        max_contexts: int = 5
    ) -> None:
        """Gerencia contextos pendentes em uma fila fixa."""
        memory = self.get_memory(id_chat)
        if len(memory["pending_contexts"]) >= max_contexts:
            memory["pending_contexts"].popleft()
        memory["pending_contexts"].append(context)

    def prepare_invoke_input(
        self,
        id_chat: str,
        include_analysis: bool = True,
        include_pending: bool = True
    ) -> List[HumanMessage|AIMessage|SystemMessage]:
        """Prepara o contexto completo para o invoke."""
        memory = self.get_memory(id_chat)
        messages = memory["chat_memory"].copy()

        # Adiciona dados de análise como SystemMessage
        if include_analysis:
            for classification, data in memory["analysis_data"].items():
                if (datetime.now().timestamp() - data["timestamp"]) <= 3600:
                    messages.append(
                        SystemMessage(
                            content=f"DADOS DE ANALISE[{classification}]: {data['data']}",
                            additional_kwargs={
                                "type": "analysis",
                                "hash": data["hash"]
                            }
                        )
                    )

        # Adiciona contextos pendentes
        if include_pending and memory["pending_contexts"]:
            messages.append(
                SystemMessage(
                    content=f"PENDING_CONTEXTS: {list(memory['pending_contexts'])}",
                    additional_kwargs={"type": "pending_context"}
                )
            )

        return messages

    def get_chat_history(
        self,
        id_chat: str,
        max_messages: int = 10
    ) -> List[HumanMessage|AIMessage]:
        """Recupera histórico recente formatado."""
        memory = self.get_memory(id_chat)
        return memory["chat_memory"][-max_messages:]

    def cleanup_old_data(
        self,
        id_chat: str,
        max_age_hours: int = 24
    ) -> None:
        """Limpa dados antigos."""
        memory = self.get_memory(id_chat)
        cutoff = datetime.now() - timedelta(hours=max_age_hours)
        
        if memory["last_updated"] < cutoff:
            del self.memory[id_chat]

    def print_memory(self, id_chat: str) -> None:
        """Debug: exibe o estado completo da memória."""
        memory = self.get_memory(id_chat)
        print(f"\n=== Memory State for Chat {id_chat} ===")
        
        print("\nChat History:")
        for msg in memory["chat_memory"]:
            prefix = "USER" if isinstance(msg, HumanMessage) else "IA"
            print(f"{prefix}: {msg.content}")
            
        print("\nAnalysis Data:")
        for k, v in memory["analysis_data"].items():
            print(f"- {k}: {v['data']} (age: {(datetime.now().timestamp() - v['timestamp']):.1f}s)")
            
        print("\nPending Contexts:")
        for ctx in memory["pending_contexts"]:
            print(f"- {ctx}")
    
    def save_memory_to_file(self, id_chat: str, filename: str = "memory_log.txt") -> bool:
        """
        Salva o estado completo da memória em um arquivo de texto.
        
        Args:
            id_chat: ID do chat a ser salvo
            filename: Nome do arquivo (padrão: memory_log.txt)
            
        Returns:
            bool: True se salvou com sucesso, False se ocorreu erro
        """
        try:
            memory = self.get_memory(id_chat)
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            with open(filename, 'a', encoding='utf-8') as file:
                file.write(f"\n=== Memory State for Chat {id_chat} - {timestamp} ===\n")
                
                # Histórico do Chat
                file.write("\nChat History:\n")
                for msg in memory["chat_memory"]:
                    prefix = "USER" if isinstance(msg, HumanMessage) else "IA"
                    file.write(f"{prefix}: {msg.content}\n")
                
                # Dados de Análise
                file.write("\nAnalysis Data:\n")
                for k, v in memory["analysis_data"].items():
                    age = datetime.now().timestamp() - v["timestamp"]
                    file.write(f"- {k}: {v['data']} (age: {age:.1f}s)\n")
                
                # Contextos Pendentes
                file.write("\nPending Contexts:\n")
                for ctx in memory["pending_contexts"]:
                    file.write(f"- {str(ctx)}\n")
                
                file.write("\n" + "="*50 + "\n")
            
            return True
            
        except Exception as e:
            print(f"Erro ao salvar memória: {str(e)}")
            return False
    
    def remove_first_pending_context(self, id_chat: str) -> bool:
        """Remove o primeiro contexto pendente da fila (deque)."""
        memory = self.get_memory(id_chat)
        
        if memory["pending_contexts"]:
            memory["pending_contexts"].popleft()
            return True
        return False