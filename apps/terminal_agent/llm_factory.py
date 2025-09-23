"""
Factory para criação de diferentes provedores de LLM.

Este módulo permite instanciar diferentes tipos de LLM de forma
centralizada e configurável.
"""

import logging

from .llm_interface import LLMInterface
from .ollama_client import OllamaClient
from .simple_llm import SimpleLLM

logger = logging.getLogger(__name__)


class LLMFactory:
    """Factory para criação de provedores de LLM."""

    _providers = {
        "simple": SimpleLLM,
        "ollama": OllamaClient,
    }

    @classmethod
    def create_llm(cls, provider: str = "simple", **kwargs) -> LLMInterface:
        """
        Cria uma instância do provedor LLM especificado.

        Args:
            provider: Nome do provedor ("simple", "ollama")
            **kwargs: Argumentos específicos do provedor

        Returns:
            Instância do provedor LLM

        Raises:
            ValueError: Se o provedor não for suportado

        """
        if provider not in cls._providers:
            available = ", ".join(cls._providers.keys())
            raise ValueError(f"Provedor '{provider}' não suportado. Disponíveis: {available}")

        provider_class = cls._providers[provider]

        try:
            if provider == "ollama":
                return provider_class(
                    base_url=kwargs.get("base_url", "http://localhost:11434"), model=kwargs.get("model", "llama3.1:8b")
                )
            else:
                return provider_class()
        except Exception as e:
            logger.error(f"Erro ao criar LLM {provider}: {e}")
            # Fallback para SimpleLLM
            logger.info("Usando SimpleLLM como fallback")
            return SimpleLLM()

    @classmethod
    def get_available_providers(cls) -> list[str]:
        """Retorna lista de provedores disponíveis."""
        return list(cls._providers.keys())

    @classmethod
    def register_provider(cls, name: str, provider_class: type):
        """
        Registra um novo provedor LLM.

        Args:
            name: Nome do provedor
            provider_class: Classe do provedor

        """
        cls._providers[name] = provider_class
        logger.info(f"Provedor '{name}' registrado com sucesso")

    @classmethod
    def create_auto_llm(cls, **kwargs) -> LLMInterface:
        """
        Cria automaticamente o melhor LLM disponível.

        Tenta criar Ollama primeiro, se falhar usa SimpleLLM.

        Args:
            **kwargs: Argumentos para os provedores

        Returns:
            Instância do melhor LLM disponível

        """
        # Tentar Ollama primeiro
        try:
            ollama = cls.create_llm("ollama", **kwargs)
            if ollama.is_available():
                logger.info("Usando Ollama como provedor LLM")
                return ollama
        except Exception as e:
            logger.warning(f"Ollama não disponível: {e}")

        # Fallback para SimpleLLM
        logger.info("Usando SimpleLLM como provedor LLM")
        return cls.create_llm("simple", **kwargs)
