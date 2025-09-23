"""
Cliente Ollama para integração com agente virtual de carros.

Este módulo fornece uma interface Python para comunicação com o Ollama
via API REST, permitindo que o agente virtual use modelos de linguagem
locais para processamento de linguagem natural.
"""

import json
import logging
from typing import Any, Optional

import requests

from .llm_base import LLMBase
from .llm_interface import LLMInterface

logger = logging.getLogger(__name__)


class OllamaClient(LLMInterface, LLMBase):
    """Cliente para comunicação com Ollama via API REST."""

    def __init__(self, base_url: str = "http://localhost:11434", model: str = "llama3.1:8b"):
        """
        Inicializa o cliente Ollama.

        Args:
            base_url: URL base do servidor Ollama
            model: Nome do modelo a ser usado

        """
        self.base_url = base_url
        self.model = model
        self.session = requests.Session()

        # Configurações de performance para a sessão
        self.session.headers.update({"Connection": "keep-alive", "Keep-Alive": "timeout=30, max=100"})

        # Adapter com pool de conexões otimizado
        from requests.adapters import HTTPAdapter
        from urllib3.util.retry import Retry

        retry_strategy = Retry(
            total=3,
            backoff_factor=0.1,
            status_forcelist=[429, 500, 502, 503, 504],
        )

        adapter = HTTPAdapter(max_retries=retry_strategy, pool_connections=10, pool_maxsize=20, pool_block=False)

        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

    def is_available(self) -> bool:
        """
        Verifica se o servidor Ollama está disponível.

        Returns:
            True se disponível, False caso contrário

        """
        try:
            response = self.session.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except Exception as e:
            logger.warning(f"Ollama não disponível: {e}")
            return False

    def get_available_models(self) -> list[dict[str, Any]]:
        """
        Obtém lista de modelos disponíveis.

        Returns:
            Lista de modelos disponíveis

        """
        try:
            response = self.session.get(f"{self.base_url}/api/tags")
            response.raise_for_status()
            data = response.json()
            return data.get("models", [])
        except Exception as e:
            logger.error(f"Erro ao obter modelos: {e}")
            return []

    def generate_response(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        stream: bool = True,  # Mudança: streaming por padrão para melhor UX
    ) -> str:
        """
        Gera resposta usando o modelo Ollama.

        Args:
            prompt: Prompt para o modelo
            system_prompt: Prompt do sistema (opcional)
            temperature: Temperatura para geração (0.0 a 1.0)
            max_tokens: Número máximo de tokens
            stream: Se deve usar streaming (recomendado para melhor performance)

        Returns:
            Resposta gerada pelo modelo

        """
        try:
            # Construir prompt completo
            full_prompt = prompt
            if system_prompt:
                full_prompt = f"System: {system_prompt}\n\nUser: {prompt}"

            payload = {
                "model": self.model,
                "prompt": full_prompt,
                "stream": stream,
                "options": {
                    "temperature": temperature,
                    "num_predict": max_tokens,
                    "top_p": 0.9,  # Otimização: reduz diversidade desnecessária
                    "top_k": 40,  # Otimização: limita vocabulário
                    "repeat_penalty": 1.1,  # Evita repetições
                    "stop": ["User:", "System:"],  # Removido \n\n para permitir quebras de linha
                },
            }

            response = self.session.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=60,  # Timeout otimizado
                stream=stream,
            )
            response.raise_for_status()

            if stream:
                return self._handle_streaming_response(response)
            else:
                data = response.json()
                return data.get("response", "")

        except requests.exceptions.Timeout as e:
            logger.error(f"Timeout ao gerar resposta (60s): {e}")
            return "⏰ A resposta está demorando muito. Tente novamente ou simplifique sua busca."
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Erro de conexão com Ollama: {e}")
            return "🔌 Erro de conexão com o servidor Ollama. Verifique se está rodando."
        except Exception as e:
            logger.error(f"Erro ao gerar resposta: {e}")
            return f"❌ Erro ao processar solicitação: {str(e)[:100]}..."

    def _handle_streaming_response(self, response) -> str:
        """Processa resposta em streaming."""
        full_response = ""
        for line in response.iter_lines():
            if line:
                try:
                    data = json.loads(line.decode("utf-8"))
                    if "response" in data:
                        full_response += data["response"]
                    if data.get("done", False):
                        break
                except json.JSONDecodeError:
                    continue
        return full_response

    def extract_car_preferences(self, user_input: str) -> dict[str, Any]:
        """
        Extrair preferências de carro da entrada do usuário.

        Usa implementação compartilhada da interface.

        Args:
            user_input: Entrada do usuário

        Returns:
            Dicionário com preferências extraídas

        """
        return super().extract_car_preferences(user_input)

    def generate_car_search_filters(self, preferences: dict[str, Any]) -> dict[str, Any]:
        """
        Modificar preferências em filtros de busca MCP.

        Usa implementação compartilhada da interface.

        Args:
            preferences: Preferências extraídas do usuário

        Returns:
            Filtros para busca MCP

        """
        return super().generate_car_search_filters(preferences)

    def format_car_results(self, cars: list[dict[str, Any]], user_preferences: dict[str, Any]) -> str:
        """
        Formatar resultados de carros de forma amigável usando LLM otimizada.

        Usa implementação compartilhada da interface.

        Args:
            cars: Lista de carros encontrados
            user_preferences: Preferências do usuário

        Returns:
            Resposta formatada

        """
        return super().format_car_results(cars, user_preferences)

    def generate_next_question(self, current_preferences: dict[str, Any], missing_info: list[str]) -> str:
        """
        Gerar próxima pergunta baseada no contexto usando LLM otimizada.

        Usa implementação compartilhada da interface.

        Args:
            current_preferences: Preferências já coletadas
            missing_info: Informações que ainda faltam

        Returns:
            Próxima pergunta sugerida

        """
        return super().generate_next_question(current_preferences, missing_info)


# Instância global do cliente
ollama_client = OllamaClient()
