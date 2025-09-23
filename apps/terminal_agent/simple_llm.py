"""
Implementação simples de LLM sem dependência externa.

Este módulo fornece uma implementação rápida de LLM que não depende
de serviços externos, ideal para desenvolvimento e testes.
"""

import logging
from typing import Any, Optional

from .llm_base import LLMBase
from .llm_interface import LLMInterface

logger = logging.getLogger(__name__)


class SimpleLLM(LLMInterface, LLMBase):
    """Implementação simples de LLM para desenvolvimento e testes."""

    def __init__(self):
        """Inicializa o LLM simples."""
        pass

    def is_available(self) -> bool:
        """Sempre disponível."""
        return True

    def generate_response(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        stream: bool = False,
    ) -> str:
        """Gera resposta simples baseada no prompt."""
        # Resposta simples baseada no contexto
        if "preferências" in prompt.lower() or "preferences" in prompt.lower():
            return self._generate_preferences_response(prompt)
        elif "filtros" in prompt.lower() or "filters" in prompt.lower():
            return self._generate_filters_response(prompt)
        elif "formatar" in prompt.lower() or "format" in prompt.lower():
            return self._generate_format_response(prompt)
        else:
            return "Resposta simples gerada."

    def extract_car_preferences(self, user_input: str) -> dict[str, Any]:
        """Extrai preferências de forma simples usando implementação compartilhada."""
        # Usar implementação compartilhada da interface
        return super().extract_car_preferences(user_input)

    def generate_car_search_filters(self, preferences: dict[str, Any]) -> dict[str, Any]:
        """Gera filtros de forma simples usando implementação compartilhada."""
        # Usar implementação compartilhada da interface
        return super().generate_car_search_filters(preferences)

    def format_car_results(self, cars: list[dict[str, Any]], user_preferences: dict[str, Any]) -> str:
        """Formata resultados de forma simples usando implementação compartilhada."""
        # Usar implementação compartilhada da interface
        return super().format_car_results(cars, user_preferences)

    def generate_next_question(self, preferences: dict[str, Any], missing_info: list[str]) -> str:
        """Gera próxima pergunta simples usando implementação compartilhada."""
        # Usar implementação compartilhada da interface
        return super().generate_next_question(preferences, missing_info)

    def _generate_preferences_response(self, prompt: str) -> str:
        """Gera resposta para extração de preferências."""
        return """```json
{
  "marca": "Audi",
  "modelo": null,
  "faixa_preco": null,
  "ano": null,
  "combustivel": null,
  "transmissao": null,
  "cor": null,
  "portas": null,
  "quilometragem": null,
  "uso": null
}
```"""

    def _generate_filters_response(self, prompt: str) -> str:
        """Gera resposta para geração de filtros."""
        return """```json
{
  "brand_name": "Audi",
  "price_min": null,
  "price_max": null,
  "year_manufacture_min": null,
  "year_manufacture_max": null,
  "fuel_type": null,
  "transmission": null,
  "color_name": null,
  "doors_min": null,
  "doors_max": null,
  "mileage_min": null,
  "mileage_max": null
}
```"""

    def _generate_format_response(self, prompt: str) -> str:
        """Gera resposta para formatação."""
        return "Aqui estão os carros encontrados para você!"
