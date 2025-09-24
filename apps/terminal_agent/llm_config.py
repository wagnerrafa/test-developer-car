"""
Configuração para provedores de LLM.

Este módulo permite configurar qual provedor LLM usar
e suas configurações específicas.
"""

import os
from typing import Any, Optional

# Configurações padrão
DEFAULT_LLM_PROVIDER = os.getenv("LLM_PROVIDER", "auto")  # auto, simple, ollama

# Configurações específicas por provedor
LLM_CONFIGS = {
    "simple": {"class": "SimpleLLM", "enabled": True, "description": "LLM simples para desenvolvimento e testes"},
    "ollama": {
        "class": "OllamaClient",
        "enabled": True,
        "description": "Cliente Ollama para modelos locais",
        "default_config": {"base_url": "http://localhost:11434", "model": "llama3.1:7b"},  # Modelo mais rápido
    },
    "ollama-fast": {
        "class": "OllamaClient",
        "enabled": True,
        "description": "Cliente Ollama com modelo 7b para máxima velocidade",
        "default_config": {"base_url": "http://localhost:11434", "model": "llama3.1:7b"},
    },
    "ollama-balanced": {
        "class": "OllamaClient",
        "enabled": True,
        "description": "Cliente Ollama com modelo 8b para balance entre velocidade e qualidade",
        "default_config": {"base_url": "http://localhost:11434", "model": "llama3.1:8b"},
    },
}


def get_llm_config(provider: Optional[str] = None) -> dict[str, Any]:
    """
    Obtém configuração para um provedor LLM.

    Args:
        provider: Nome do provedor (se None, usa o padrão)

    Returns:
        Configuração do provedor

    """
    if provider is None:
        provider = DEFAULT_LLM_PROVIDER

    if provider == "auto":
        # Para auto, retorna configuração que permite fallback
        return {
            "provider": "auto",
            "fallback_order": ["ollama", "simple"],
            "description": "Seleção automática do melhor LLM disponível",
        }

    return LLM_CONFIGS.get(provider, {})


def is_provider_enabled(provider: str) -> bool:
    """
    Verifica se um provedor está habilitado.

    Args:
        provider: Nome do provedor

    Returns:
        True se habilitado, False caso contrário

    """
    config = LLM_CONFIGS.get(provider, {})
    return config.get("enabled", False)


def get_available_providers() -> list[str]:
    """
    Retorna lista de provedores disponíveis e habilitados.

    Returns:
        Lista de nomes de provedores

    """
    return [name for name, config in LLM_CONFIGS.items() if config.get("enabled", False)]
