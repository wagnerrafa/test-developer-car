"""
Implementação base para provedores de LLM.

Este módulo contém funcionalidades comuns que podem ser reutilizadas
por diferentes implementações de LLM.

NOTA: A maioria das funcionalidades foram movidas para LLMInterface
para melhor compartilhamento entre implementações.
"""

import logging
from typing import Any

logger = logging.getLogger(__name__)


class LLMBase:
    """Classe base com funcionalidades comuns para LLMs."""

    def _format_cars_for_prompt(self, cars: list[dict[str, Any]]) -> str:
        """Formata carros de forma simples para o prompt."""
        formatted_cars = []
        for i, car in enumerate(cars, 1):
            car_info = f"{i}. {car['marca']} {car['modelo']} ({car['ano']}) - R$ {car['preco']:,.2f}"
            formatted_cars.append(car_info)
        return "\n".join(formatted_cars)
