"""
Interface abstrata para provedores de LLM.

Este módulo define a interface padrão que todos os provedores de LLM devem implementar,
permitindo fácil troca entre diferentes modelos e serviços.
"""

import json
import logging
import re
from abc import ABC, abstractmethod
from typing import Any, Optional

logger = logging.getLogger(__name__)


class LLMPrompts:
    """Constantes com prompts padronizados para todos os LLMs."""

    # Prompt para extração de preferências
    EXTRACT_PREFERENCES_SYSTEM = """
    Você é um assistente especializado em extrair preferências de carros de conversas naturais.

    Extraia as seguintes informações do input do usuário:
    - marca: marca do carro (ex: Audi, BMW, Toyota)
    - modelo: modelo específico (ex: A4, X5, Corolla)
    - faixa_preco: faixa de preço (economico, medio, luxo)
    - ano: preferência de ano. Se o usuário fornecer um ano específico (ex: 2016), retorne um NÚMERO inteiro (ex: 2016). A saída deve ser sempre um NÚMERO inteiro, qunado solicitado um ano.
    - combustivel: tipo de combustível (gasolina, etanol, flex, diesel, eletrico, hibrido)
    - transmissao: tipo de transmissão (manual, automatico, cvt, semi_automatico, dual_clutch)
    - cor: cor preferida
    - portas: número de portas (2, 4, 5)
    - quilometragem: quilometragem máxima aceita
    - uso: tipo de uso (cidade, estrada, trabalho, lazer)

    IMPORTANTE: Se o usuário está refinando uma busca anterior (quando há contexto de resultados anteriores):
    - Mantenha as preferências da busca anterior que não foram alteradas
    - Adicione/modifique apenas as novas preferências mencionadas
    - Se o usuário mencionar uma característica específica (ex: "cor Perolado"), use isso para filtrar os resultados anteriores

    Responda APENAS com um JSON válido contendo as preferências extraídas.
    Use null para informações não mencionadas.
    """

    # Prompt para geração de filtros
    GENERATE_FILTERS_SYSTEM = """
    Você é um especialista em converter preferências de carros em filtros de busca para Django ORM.

    REGRAS IMPORTANTES DE SAÍDA (obrigatórias):
    - Responda APENAS com um JSON VÁLIDO (sem explicações).
    - Use campos FLAT (planos), SEM operadores como $eq, $gte, $lte, $in.
    - Mapeie ranges para chaves com sufixo _min/_max (ex.: price_min, price_max).
    - Use exatamente estas chaves quando aplicável:
      - brand_name (marca do carro em texto)
      - car_name (nome do carro em texto)
      - color_name, engine_name, car_model_name
      - fuel_type (gasoline, ethanol, flex, diesel, electric, hybrid)
      - transmission (manual, automatic, cvt, semi_automatic, dual_clutch)
      - price_min, price_max
      - year_manufacture_min, year_manufacture_max (se o usuário disser um ano específico ex.: 2016, use os dois com o MESMO valor 2016)
      - year_model_min, year_model_max (pode repetir o mesmo valor do ano específico quando aplicável)
      - mileage_min, mileage_max
      - doors_min, doors_max
    - Não inclua campos com valor null/None.

    Exemplos de saída CORRETA:
    {"brand_name": "Audi"}
    {"brand_name": "Audi", "price_max": 120000, "year_manufacture_min": 2018}
    """

    # Prompt para formatação de resultados
    FORMAT_RESULTS_SYSTEM = """
    Você é um assistente virtual especializado em apresentar resultados de busca de carros.

    INSTRUÇÕES OBRIGATÓRIAS:
    - Apresente TODOS os carros encontrados em formato de lista numerada
    - Para cada carro, inclua: marca, modelo, ano, preço, quilometragem, cor, combustível, transmissão
    - Use emojis apropriados (🚗, 💰, ⛽, etc.)
    - Seja detalhado e informativo
    - Formate o preço em reais (R$)
    - Sugira próximos passos ou perguntas
    - Mínimo de 200 caracteres por resposta
    - Use formatação clara com quebras de linha
    """

    # Prompt para geração de perguntas
    GENERATE_QUESTION_SYSTEM = """
    Você é um assistente de vendas de carros experiente.

    Gere uma pergunta natural e amigável para esclarecer as preferências do cliente.
    Seja conversacional e útil, não robótico.
    Foque em uma informação por vez para não sobrecarregar.
    """

    # Templates de perguntas por tipo de informação
    QUESTION_TEMPLATES = {
        "marca": "Qual marca de carro você prefere? (ex: Audi, BMW, Toyota, Honda...)",
        "faixa_preco": "Qual sua faixa de preço preferida? (econômico, médio, luxo)",
        "ano": "Prefere carros mais novos ou usados?",
        "combustivel": "Qual tipo de combustível prefere? (gasolina, etanol, flex, híbrido...)",
        "transmissao": "Prefere câmbio manual ou automático?",
        "cor": "Tem alguma cor preferida?",
        "portas": "Quantas portas prefere? (2, 4 ou 5 portas)",
        "quilometragem": "Qual a quilometragem máxima que aceita?",
        "uso": "Para que tipo de uso? (cidade, estrada, trabalho, lazer)",
    }

    # Configurações de geração
    GENERATION_CONFIGS = {
        "extract_preferences": {"temperature": 0.1, "max_tokens": 200},
        "generate_filters": {"temperature": 0.1, "max_tokens": 200},
        "format_results": {"temperature": 0.5, "max_tokens": 1500},  # Aumentado para respostas detalhadas
        "generate_question": {"temperature": 0.7, "max_tokens": 150},
    }


class LLMInterface(ABC):
    """Interface abstrata para provedores de LLM."""

    # Métodos utilitários compartilhados
    def _extract_json_from_response(self, response: str) -> Optional[str]:
        """Extrai JSON de uma resposta de texto de forma robusta."""
        # Procurar por blocos de código JSON
        json_pattern = r"```(?:json)?\s*(\{.*?\})\s*```"
        match = re.search(json_pattern, response, re.DOTALL)
        if match:
            return match.group(1)

        # Procurar por JSON simples
        json_start = response.find("{")
        json_end = response.rfind("}") + 1

        if json_start != -1 and json_end > json_start:
            return response[json_start:json_end]

        return None

    def _simplify_cars_for_formatting(self, cars: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Simplifica estrutura dos carros para formatação."""
        simplified_cars = []
        for car in cars:
            try:
                simplified_car = {
                    "marca": car.get("car_name", {}).get("brand", {}).get("name", "N/A"),
                    "modelo": car.get("car_name", {}).get("name", "N/A"),
                    "ano": car.get("year_manufacture", "N/A"),
                    "cor": car.get("color", {}).get("name", "N/A"),
                    "preco": car.get("price", 0),
                    "quilometragem": car.get("mileage", 0),
                    "combustivel": car.get("fuel_type", "N/A"),
                    "transmissao": car.get("transmission", "N/A"),
                }
                simplified_cars.append(simplified_car)
            except Exception as e:
                logger.warning(f"Erro ao simplificar carro: {e}")
                continue

        return simplified_cars

    def _format_cars_simple(self, cars: list[dict[str, Any]]) -> str:
        """Formatação simples como fallback."""
        if not cars:
            return "😔 Não encontrei carros que atendam aos seus critérios. Que tal ajustarmos a busca?"

        result_text = f"🚗 Encontrei {len(cars)} carro(s) que atendem aos seus critérios:\n\n"

        for i, car in enumerate(cars, 1):
            try:
                # Usar dados simplificados se disponíveis
                if "marca" in car:
                    brand_name = car.get("marca", "N/A")
                    car_name = car.get("modelo", "N/A")
                    year = car.get("ano", "N/A")
                    price = car.get("preco", 0)
                    color = car.get("cor", "N/A")
                    fuel = car.get("combustivel", "N/A")
                    transmission = car.get("transmissao", "N/A")
                    mileage = car.get("quilometragem", 0)
                else:
                    # Usar dados originais
                    brand_name = car.get("car_name", {}).get("brand", {}).get("name", "N/A")
                    car_name = car.get("car_name", {}).get("name", "N/A")
                    year = car.get("year_manufacture", "N/A")
                    price = car.get("price", 0)
                    color = car.get("color", {}).get("name", "N/A")
                    fuel = car.get("fuel_type", "N/A")
                    transmission = car.get("transmission", "N/A")
                    mileage = car.get("mileage", 0)

                result_text += f"{i}. **{brand_name} {car_name} ({year})**\n"
                result_text += f"   💰 Preço: R$ {price:,.2f}\n"
                result_text += f"   🎨 Cor: {color}\n"
                result_text += f"   ⛽ Combustível: {fuel}\n"
                result_text += f"   🔧 Transmissão: {transmission}\n"
                if mileage > 0:
                    result_text += f"   🛣️ Quilometragem: {mileage:,} km\n"
                result_text += "\n"
            except Exception as e:
                logger.warning(f"Erro ao formatar carro {i}: {e}")
                continue

        result_text += "💡 Gostaria de saber mais detalhes sobre algum carro específico?"
        return result_text

    def _format_cars_fast(self, cars: list[dict[str, Any]], user_preferences: dict[str, Any]) -> str:
        """
        Formatação rápida de carros sem usar LLM.

        Args:
            cars: Lista de carros encontrados
            user_preferences: Preferências do usuário

        Returns:
            Resultados formatados rapidamente

        """
        if not cars:
            return "😔 Não encontrei carros que atendam aos seus critérios. Que tal ajustarmos a busca?"

        # Cabeçalho personalizado baseado nas preferências
        header = self._generate_personalized_header(user_preferences, len(cars))

        result_text = f"{header}\n\n"

        # Formatar cada carro
        for i, car in enumerate(cars, 1):
            try:
                car_info = self._format_single_car(car, i)
                result_text += car_info + "\n"
            except Exception as e:
                logger.warning(f"Erro ao formatar carro {i}: {e}")
                continue

        # Rodapé com sugestões
        footer = self._generate_suggestions_footer(user_preferences)
        result_text += f"\n{footer}"

        return result_text

    def _generate_personalized_header(self, preferences: dict[str, Any], car_count: int) -> str:
        """Gera cabeçalho personalizado baseado nas preferências."""
        brand = preferences.get("marca", "")
        year_range = ""
        price_range = ""

        if preferences.get("ano"):
            year_range = f" do ano {preferences['ano']}"

        if preferences.get("faixa_preco"):
            price_range = f" na faixa {preferences['faixa_preco']}"

        if brand:
            return f"🚗 Encontrei {car_count} carro(s) {brand}{year_range}{price_range} que atendem aos seus critérios:"
        else:
            return f"🚗 Encontrei {car_count} carro(s) que atendem aos seus critérios:"

    def _format_single_car(self, car: dict[str, Any], index: int) -> str:
        """Formata um único carro com todas as informações."""
        try:
            # Extrair informações do carro
            brand_name = car.get("car_name", {}).get("brand", {}).get("name", "N/A")
            car_name = car.get("car_name", {}).get("name", "N/A")
            year = car.get("year_manufacture", "N/A")
            price = car.get("price", 0)
            color = car.get("color", {}).get("name", "N/A")
            fuel = car.get("fuel_type", "N/A")
            transmission = car.get("transmission", "N/A")
            mileage = car.get("mileage", 0)
            doors = car.get("doors", "N/A")

            # Formatar preço
            price_formatted = f"R$ {price:,.2f}" if price > 0 else "Preço não informado"

            # Formatar quilometragem
            mileage_formatted = f"{mileage:,} km" if mileage > 0 else "Não informado"

            # Montar string do carro
            car_text = f"{index}. **{brand_name} {car_name} ({year})**\n"
            car_text += f"   💰 Preço: {price_formatted}\n"
            car_text += f"   🎨 Cor: {color}\n"
            car_text += f"   ⛽ Combustível: {fuel}\n"
            car_text += f"   🔧 Transmissão: {transmission}\n"
            car_text += f"   🛣️ Quilometragem: {mileage_formatted}\n"
            car_text += f"   🚪 Portas: {doors}\n"

            return car_text

        except Exception as e:
            logger.warning(f"Erro ao formatar carro {index}: {e}")
            return f"{index}. **Erro ao carregar informações do carro**\n"

    def _generate_suggestions_footer(self, preferences: dict[str, Any]) -> str:
        """Gera rodapé com sugestões baseadas nas preferências."""
        suggestions = []

        if not preferences.get("faixa_preco"):
            suggestions.append("💰 faixa de preço")
        if not preferences.get("ano"):
            suggestions.append("📅 ano do veículo")
        if not preferences.get("cor"):
            suggestions.append("🎨 cor preferida")
        if not preferences.get("combustivel"):
            suggestions.append("⛽ tipo de combustível")

        if suggestions:
            return f"💡 Para refinar sua busca, posso ajudar com: {', '.join(suggestions)}"
        else:
            return "💡 Gostaria de saber mais detalhes sobre algum carro específico?"

    def _validate_preferences(self, preferences: dict[str, Any]) -> dict[str, Any]:
        """Valida e limpa preferências extraídas."""
        valid_preferences = {}

        # Mapear campos válidos
        field_mapping = {
            "marca": "marca",
            "modelo": "modelo",
            "faixa_preco": "faixa_preco",
            "ano": "ano",
            "combustivel": "combustivel",
            "transmissao": "transmissao",
            "cor": "cor",
            "portas": "portas",
            "quilometragem": "quilometragem",
            "uso": "uso",
        }

        for key, value in preferences.items():
            if key in field_mapping and value is not None:
                valid_preferences[field_mapping[key]] = value

        return valid_preferences

    def _convert_preferences_to_filters(self, preferences: dict[str, Any]) -> dict[str, Any]:
        """Modificar preferências em filtros MCP."""
        filters = {
            "brand_name": preferences.get("marca"),
            "price_min": None,
            "price_max": None,
            "year_manufacture_min": None,
            "year_manufacture_max": None,
            "year_model_min": None,
            "year_model_max": None,
            "fuel_type": preferences.get("combustivel"),
            "transmission": preferences.get("transmissao"),
            "color_name": preferences.get("cor"),
            "doors_min": None,
            "doors_max": None,
            "mileage_min": None,
            "mileage_max": None,
        }

        # Aplicar faixa de preço
        faixa_preco = preferences.get("faixa_preco")
        if faixa_preco == "economico":
            filters["price_max"] = 50000
        elif faixa_preco == "medio":
            filters["price_min"] = 30000
            filters["price_max"] = 100000
        elif faixa_preco == "luxo":
            filters["price_min"] = 100000

        # Aplicar ano: aceitar inteiro específico ou categorias
        ano = preferences.get("ano")
        if isinstance(ano, int):
            filters["year_manufacture_min"] = ano
            filters["year_manufacture_max"] = ano
            filters["year_model_min"] = ano
            filters["year_model_max"] = ano
        elif isinstance(ano, str):
            if ano == "recente":
                filters["year_manufacture_min"] = 2020
                filters["year_model_min"] = 2020
            elif ano == "antigo":
                filters["year_manufacture_max"] = 2015
                filters["year_model_max"] = 2015

        # Aplicar quilometragem
        quilometragem = preferences.get("quilometragem")
        if quilometragem and isinstance(quilometragem, (int, float)):
            filters["mileage_max"] = int(quilometragem)

        # Aplicar portas
        portas = preferences.get("portas")
        if portas and isinstance(portas, (int, float)):
            portas_int = int(portas)
            filters["doors_min"] = portas_int
            filters["doors_max"] = portas_int

        # Remover valores None
        return {k: v for k, v in filters.items() if v is not None}

    def _normalize_llm_filters(self, raw_filters: dict[str, Any]) -> dict[str, Any]:
        """
        Normaliza filtros produzidos pela LLM para o formato plano esperado pelos serializers/ORM.

        - Remove operadores como $eq/$gte/$lte/eq/gte/lte, mantendo o valor base
        - Converte dicts de range para *_min/_max
        - Mapeia sinônimos/português para chaves esperadas (ex.: marca -> brand_name)
        - Remove valores None/vazios
        """
        if not isinstance(raw_filters, dict):
            return {}

        normalized: dict[str, Any] = {}

        # Mapeamento de sinônimos de chaves
        key_synonyms = {
            "marca": "brand_name",
            "brand": "brand_name",
            "nome_marca": "brand_name",
            "modelo": "car_name",
            "nome_carro": "car_name",
            "cor": "color_name",
            "motor": "engine_name",
            "combustivel": "fuel_type",
            "transmissao": "transmission",
            "preco_min": "price_min",
            "preco_max": "price_max",
            "ano_min": "year_manufacture_min",
            "ano_max": "year_manufacture_max",
            "quilometragem_min": "mileage_min",
            "quilometragem_max": "mileage_max",
            "portas": "doors",  # pode virar doors_min/max abaixo
        }

        def strip_operator(value: Any) -> Any:
            if isinstance(value, dict):
                # Operadores comuns
                for op in ("$eq", "eq", "=", "value"):
                    if op in value:
                        return value[op]
                # Se vier min/max ou gte/lte, retorna o próprio dict para tratamento após
                if any(k in value for k in ("$gte", "gte", "min", "$lte", "lte", "max")):
                    return value
            return value

        # Primeiro, normalizar chaves e tirar operadores triviais ($eq)
        temp: dict[str, Any] = {}
        for k, v in raw_filters.items():
            key = key_synonyms.get(k, k)
            temp[key] = strip_operator(v)

        # Tratar ranges e valores planos
        for key, value in temp.items():
            if value is None or value == "":
                continue

            # Ranges: price/year/doors/mileage
            if isinstance(value, dict):
                # Mapear possíveis chaves
                min_val = None
                max_val = None
                if "$gte" in value or "gte" in value:
                    min_val = value.get("$gte", value.get("gte"))
                if "$lte" in value or "lte" in value:
                    max_val = value.get("$lte", value.get("lte"))
                if "min" in value:
                    min_val = value.get("min") if min_val is None else min_val
                if "max" in value:
                    max_val = value.get("max") if max_val is None else max_val

                if key in ("price", "year_manufacture", "mileage", "doors"):
                    if min_val is not None:
                        normalized[f"{key}_min"] = min_val
                    if max_val is not None:
                        normalized[f"{key}_max"] = max_val
                    continue

                # Se for um dict sem ser range conhecido, tentar reduzir para valor direto se houver uma única chave
                if len(value) == 1:
                    only_v = next(iter(value.values()))
                    normalized[key] = only_v
                # Caso contrário, ignora estruturas complexas
                continue

            # Valor plano
            if key == "doors":
                # Se vier número único para portas, duplicar para min/max
                try:
                    doors_int = int(value)
                    normalized["doors_min"] = doors_int
                    normalized["doors_max"] = doors_int
                except Exception:
                    pass
                continue

            if key in ("year", "ano"):
                # Se for número explícito, replicar para manufacture/model
                try:
                    year_int = int(value)
                    normalized["year_manufacture_min"] = year_int
                    normalized["year_manufacture_max"] = year_int
                    normalized["year_model_min"] = year_int
                    normalized["year_model_max"] = year_int
                    continue
                except Exception:
                    # categorias como "recente"/"antigo" serão tratadas na conversão de preferências
                    pass

            normalized[key] = value

        # Limpar valores None
        normalized = {k: v for k, v in normalized.items() if v is not None}
        return normalized

    def _generate_simple_question(self, missing_info: list[str]) -> str:
        """Gera pergunta simples como fallback."""
        if "marca" in missing_info:
            return "🚗 Qual marca de carro você prefere?"
        elif "faixa_preco" in missing_info:
            return "💰 Qual sua faixa de preço?"
        elif "ano" in missing_info:
            return "📅 Que ano de carro você procura?"
        elif "combustivel" in missing_info:
            return "⛽ Qual tipo de combustível prefere?"
        elif "transmissao" in missing_info:
            return "🔧 Prefere câmbio manual ou automático?"
        elif "cor" in missing_info:
            return "🎨 Tem alguma cor preferida?"
        elif "portas" in missing_info:
            return "🚪 Quantas portas prefere?"
        elif "quilometragem" in missing_info:
            return "🛣️ Qual a quilometragem máxima que aceita?"
        else:
            return "🤔 Que outras características são importantes para você?"

    def get_extract_preferences_prompt(
        self, user_input: str, previous_results: Optional[list[dict[str, Any]]] = None
    ) -> tuple[str, str]:
        """
        Retorna o prompt e system prompt para extração de preferências.

        Args:
            user_input: Input do usuário
            previous_results: Resultados da busca anterior (para refinamento)

        Returns:
            Tupla (system_prompt, user_prompt)

        """
        # Se há resultados anteriores, incluir contexto de refinamento
        if previous_results:
            context = self._build_refinement_context(previous_results)
            user_prompt = f"""Contexto da busca anterior:
{context}

Nova solicitação do usuário: {user_input}

Extraia as preferências considerando que o usuário quer refinar a busca anterior:"""
        else:
            user_prompt = f"Input do usuário: {user_input}\n\nExtraia as preferências:"

        return (LLMPrompts.EXTRACT_PREFERENCES_SYSTEM, user_prompt)

    def _build_refinement_context(self, previous_results: list[dict[str, Any]]) -> str:
        """
        Constrói contexto dos resultados anteriores para refinamento.

        Args:
            previous_results: Lista de carros da busca anterior

        Returns:
            String formatada com contexto dos resultados

        """
        if not previous_results:
            return "Nenhum resultado anterior disponível."

        context_lines = ["Resultados da busca anterior:"]

        for i, car in enumerate(previous_results[:5], 1):  # Limitar a 5 carros para não sobrecarregar
            try:
                brand = car.get("car_name", {}).get("brand", {}).get("name", "N/A")
                car_name = car.get("car_name", {}).get("name", "N/A")
                year = car.get("year_manufacture", "N/A")
                price = car.get("price", 0)
                color = car.get("color", {}).get("name", "N/A")
                fuel = car.get("fuel_type", "N/A")
                transmission = car.get("transmission", "N/A")
                mileage = car.get("mileage", 0)
                doors = car.get("doors", "N/A")

                price_formatted = f"R$ {price:,.2f}" if price > 0 else "Preço não informado"
                mileage_formatted = f"{mileage:,} km" if mileage > 0 else "Não informado"

                car_info = f"{i}. {brand} {car_name} ({year}) - {price_formatted} - Cor: {color} - Combustível: {fuel} - Transmissão: {transmission} - Quilometragem: {mileage_formatted} - Portas: {doors}"
                context_lines.append(car_info)
            except Exception as e:
                logger.warning(f"Erro ao formatar carro {i} para contexto: {e}")
                continue

        return "\n".join(context_lines)

    def is_refinement_request(self, user_input: str, previous_results: Optional[list[dict[str, Any]]] = None) -> bool:
        """
        Detecta se o usuário está tentando refinar uma busca anterior.

        Args:
            user_input: Input do usuário
            previous_results: Resultados da busca anterior

        Returns:
            True se é uma solicitação de refinamento

        """
        if not previous_results:
            return False

        # Palavras-chave que indicam refinamento
        refinement_keywords = [
            "dessa lista",
            "desses",
            "desta lista",
            "destes",
            "me mostre os de",
            "mostre apenas",
            "filtre por",
            "só os",
            "apenas os",
            "quero ver os",
            "refinar",
            "filtrar",
            "especificar",
        ]

        user_input_lower = user_input.lower()

        # Verificar se contém palavras-chave de refinamento
        for keyword in refinement_keywords:
            if keyword in user_input_lower:
                return True

        # Verificar se menciona características específicas que podem ser filtros
        specific_characteristics = [
            "cor",
            "preço",
            "ano",
            "combustível",
            "transmissão",
            "portas",
            "quilometragem",
            "marca",
            "modelo",
        ]

        for char in specific_characteristics:
            if char in user_input_lower:
                return True

        return False

    def get_generate_filters_prompt(self, preferences: dict[str, Any]) -> tuple[str, str]:
        """
        Retorna o prompt e system prompt para geração de filtros.

        Args:
            preferences: Preferências do usuário

        Returns:
            Tupla (system_prompt, user_prompt)

        """
        return (
            LLMPrompts.GENERATE_FILTERS_SYSTEM,
            f"Preferências do usuário: {preferences}\n\nConverta em filtros MCP:",
        )

    def get_format_results_prompt(
        self, cars: list[dict[str, Any]], user_preferences: dict[str, Any]
    ) -> tuple[str, str]:
        """
        Retorna o prompt e system prompt para formatação de resultados.

        Args:
            cars: Lista de carros encontrados
            user_preferences: Preferências do usuário

        Returns:
            Tupla (system_prompt, user_prompt)

        """
        return (
            LLMPrompts.FORMAT_RESULTS_SYSTEM,
            f"""Carros encontrados ({len(cars)} carros):
{cars}

Preferências do usuário: {user_preferences}

Apresente os resultados de forma detalhada e amigável, listando todos os carros com suas características principais:""",
        )

    def get_generate_question_prompt(self, preferences: dict[str, Any], missing_info: list[str]) -> tuple[str, str]:
        """
        Retorna o prompt e system prompt para geração de perguntas.

        Args:
            preferences: Preferências atuais
            missing_info: Informações que faltam

        Returns:
            Tupla (system_prompt, user_prompt)

        """
        return (
            LLMPrompts.GENERATE_QUESTION_SYSTEM,
            f"Preferências atuais: {preferences}\nInformações que faltam: {missing_info}\n\nGere uma pergunta:",
        )

    def get_generation_config(self, task: str) -> dict[str, Any]:
        """
        Retorna configuração de geração para uma tarefa específica.

        Args:
            task: Nome da tarefa (extract_preferences, generate_filters, etc.)

        Returns:
            Configuração de geração

        """
        return LLMPrompts.GENERATION_CONFIGS.get(task, {"temperature": 0.7, "max_tokens": 200})

    def get_question_template(self, info_type: str) -> str:
        """
        Retorna template de pergunta para um tipo de informação.

        Args:
            info_type: Tipo de informação (marca, faixa_preco, etc.)

        Returns:
            Template da pergunta

        """
        return LLMPrompts.QUESTION_TEMPLATES.get(info_type, "Pode me dar mais detalhes sobre isso?")

    @abstractmethod
    def is_available(self) -> bool:
        """
        Verifica se o provedor LLM está disponível.

        Returns:
            True se disponível, False caso contrário

        """
        pass

    @abstractmethod
    def generate_response(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        stream: bool = False,
    ) -> str:
        """
        Gera resposta usando o modelo LLM.

        Args:
            prompt: Prompt para o modelo
            system_prompt: Prompt do sistema (opcional)
            temperature: Temperatura para geração (0.0 a 1.0)
            max_tokens: Número máximo de tokens
            stream: Se deve usar streaming

        Returns:
            Resposta gerada pelo modelo

        """
        pass

    def extract_car_preferences(
        self, user_input: str, previous_results: Optional[list[dict[str, Any]]] = None
    ) -> dict[str, Any]:
        """
        Extrair preferências de carro do input do usuário.

        Implementação padrão que pode ser sobrescrita.

        Args:
            user_input: Input do usuário
            previous_results: Resultados da busca anterior (para refinamento)

        Returns:
            Dicionário com preferências extraídas

        """
        system_prompt, prompt = self.get_extract_preferences_prompt(user_input, previous_results)
        config = self.get_generation_config("extract_preferences")

        try:
            response = self.generate_response(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=config["temperature"],
                max_tokens=config["max_tokens"],
            )

            logger.debug(f"Resposta do sistema para extract_car_preferences: {response}")

            # Tentar extrair JSON da resposta
            json_str = self._extract_json_from_response(response)
            if json_str:
                try:
                    preferences = json.loads(json_str)
                    return self._validate_preferences(preferences)
                except json.JSONDecodeError as e:
                    logger.error(f"Erro ao decodificar JSON: {e}")
                    return {}
            else:
                logger.warning("Não foi possível extrair JSON da resposta")
                return {}

        except Exception as e:
            logger.error(f"Erro ao extrair preferências: {e}")
            return {}

    def generate_car_search_filters(self, preferences: dict[str, Any]) -> dict[str, Any]:
        """
        Modificar preferências em filtros de busca MCP.

        Implementação padrão que pode ser sobrescrita.

        Args:
            preferences: Preferências extraídas do usuário

        Returns:
            Filtros para busca MCP

        """
        system_prompt, prompt = self.get_generate_filters_prompt(preferences)
        config = self.get_generation_config("generate_filters")

        try:
            response = self.generate_response(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=config["temperature"],
                max_tokens=config["max_tokens"],
            )

            # Extrair JSON de forma mais robusta
            json_str = self._extract_json_from_response(response)
            if json_str:
                try:
                    filters = json.loads(json_str)
                    filters = self._normalize_llm_filters(filters)
                    return filters
                except json.JSONDecodeError as e:
                    logger.error(f"Erro ao decodificar JSON: {e}")
                    # Fallback para conversão direta
                    return self._convert_preferences_to_filters(preferences)
            else:
                logger.warning("Nenhum JSON encontrado na resposta, usando conversão direta")
                return self._convert_preferences_to_filters(preferences)

        except Exception as e:
            logger.error(f"Erro ao gerar filtros: {e}")
            # Fallback para conversão direta
            return self._convert_preferences_to_filters(preferences)

    def format_car_results(self, cars: list[dict[str, Any]], user_preferences: dict[str, Any]) -> str:
        """
        Formatar resultados de busca de carros.

        Implementação padrão que pode ser sobrescrita.

        Args:
            cars: Lista de carros encontrados
            user_preferences: Preferências do usuário

        Returns:
            Resultados formatados

        """
        if not cars:
            return "😔 Não encontrei carros que atendam aos seus critérios. Que tal ajustarmos a busca?"

        logger.info(f"Carros formatados com sucesso: {len(cars)} carros encontrados")

        # Usar formatação rápida direta (sem LLM)
        return self._format_cars_fast(cars, user_preferences)

    def generate_next_question(self, current_preferences: dict[str, Any], missing_info: list[str]) -> str:
        """
        Gerar próxima pergunta baseada no contexto.

        Implementação padrão que pode ser sobrescrita.

        Args:
            current_preferences: Preferências já coletadas
            missing_info: Informações que ainda faltam

        Returns:
            Próxima pergunta sugerida

        """
        if not missing_info:
            return "Perfeito! Tenho informações suficientes para buscar carros para você."

        # Usar prompts centralizados
        system_prompt, prompt = self.get_generate_question_prompt(current_preferences, missing_info)
        config = self.get_generation_config("generate_question")

        try:
            response = self.generate_response(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=config["temperature"],
                max_tokens=150,  # Limite baixo para perguntas concisas
            )
            logger.debug(f"Resposta do sistema para next question: {response}")
            return response

        except Exception as e:
            logger.error(f"Erro ao gerar pergunta: {e}")
            # Fallback para perguntas simples
            return self._generate_simple_question(missing_info)
