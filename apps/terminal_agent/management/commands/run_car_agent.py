"""
Comando de management para executar o agente virtual de carros.

Este comando inicia uma sessão interativa no terminal onde o usuário
pode conversar com o agente virtual para buscar carros.
"""

import logging
import sys
from typing import Any

from django.core.management.base import BaseCommand
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, TimeElapsedColumn
from rich.prompt import Prompt
from rich.status import Status
from rich.text import Text

from apps.terminal_agent.llm_factory import LLMFactory
from apps.terminal_agent.llm_interface import LLMInterface
from apps.web_sockets.mcp_handlers import CarMCPHandler

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """Comando para executar o agente virtual de carros."""

    help = "Executa o agente virtual conversacional para busca de carros"

    def __init__(self, *args, **kwargs):
        """Inicializar o comando do agente de carros."""
        super().__init__(*args, **kwargs)
        self.console = Console()
        self.mcp_handler = CarMCPHandler()
        self.llm: LLMInterface | None = None  # Será inicializado no handle()
        self.conversation_state = {
            "preferences": {},
            "search_history": [],
            "current_results": [],
        }

    def add_arguments(self, parser):
        """Adiciona argumentos do comando."""
        parser.add_argument(
            "--llm-provider",
            type=str,
            choices=["simple", "ollama", "auto"],
            default="simple",
            help="Provedor LLM a ser usado (simple, ollama, auto). Padrão: simple",
        )
        parser.add_argument(
            "--ollama-url",
            type=str,
            default="http://localhost:11434",
            help="URL do servidor Ollama (apenas para provedor ollama)",
        )
        parser.add_argument(
            "--model",
            type=str,
            default="llama3.1:8b",
            help="Modelo Ollama a ser usado (apenas para provedor ollama)",
        )

    def handle(self, *args, **options):
        """Executa o comando principal."""
        # Inicializar LLM baseado no provedor selecionado
        self._initialize_llm(options)

        # Verificar se LLM está disponível
        if not self.llm.is_available():
            logger.info(
                Panel(
                    "[red]❌ Provedor LLM não está disponível![/red]\n" "Tentando usar fallback...",
                    title="Erro de Conexão",
                    border_style="red",
                )
            )
            # Tentar recriar com fallback
            self.llm = LLMFactory.create_llm("simple")

        # Iniciar agente
        self._start_agent()

    def _initialize_llm(self, options):
        """Inicializa o provedor LLM baseado nas opções."""
        provider = options.get("llm_provider", "simple")

        try:
            if provider == "auto":
                self.llm = LLMFactory.create_auto_llm(base_url=options.get("ollama_url"), model=options.get("model"))
                provider_name = "Auto (Ollama/SimpleLLM)"
            elif provider == "ollama":
                self.llm = LLMFactory.create_llm(
                    "ollama", base_url=options.get("ollama_url"), model=options.get("model")
                )
                provider_name = f"Ollama ({options.get('model')})"
            else:  # simple
                self.llm = LLMFactory.create_llm("simple")
                provider_name = "SimpleLLM"

            logger.info(
                Panel(
                    f"[green]✅ Provedor LLM inicializado: {provider_name}[/green]",
                    title="Configuração",
                    border_style="green",
                )
            )

        except Exception as e:
            logger.info(
                Panel(
                    f"[yellow]⚠️ Erro ao inicializar {provider}: {e}[/yellow]\n" "Usando SimpleLLM como fallback...",
                    title="Aviso",
                    border_style="yellow",
                )
            )
            self.llm = LLMFactory.create_llm("simple")

    def _start_agent(self):
        """Inicia a sessão do agente virtual."""
        # Verificar se está sendo executado via pipe
        is_piped = not sys.stdin.isatty()

        if not is_piped:
            self.console.clear()

        # Mostrar carregamento inicial
        with Status("[bold green]Inicializando agente virtual...", spinner="dots") as status:
            status.update("[bold green]Carregando modelos de IA...")
            # Simular carregamento inicial
            import time

            time.sleep(1)

            status.update("[bold green]Conectando ao banco de dados...")
            time.sleep(0.5)

            status.update("[bold green]Preparando interface...")
            time.sleep(0.5)

        self._display_welcome()

        if is_piped:
            # Modo pipe - processar entrada do stdin
            self._process_piped_input()
        else:
            # Modo interativo - loop normal
            self._process_interactive_input()

    def _process_piped_input(self):
        """Processa entrada via pipe."""
        try:
            for line in sys.stdin:
                user_input = line.strip()
                if user_input:
                    response = self._process_user_input(user_input)
                    self._display_agent_response(response)
        except EOFError:
            pass
        except Exception as e:
            logger.error(f"Erro no processamento via pipe: {e}")
            logger.error(f"Erro: {e}")

    def _process_interactive_input(self):
        """Processa entrada interativa."""
        while True:
            try:
                # Obter entrada do usuário
                user_input = Prompt.ask("\n[bold blue]Você[/bold blue]")

                if user_input.lower() in ["sair", "exit", "quit", "bye"]:
                    self._display_goodbye()
                    break

                # Processar entrada
                response = self._process_user_input(user_input)
                self._display_agent_response(response)

            except KeyboardInterrupt:
                self._display_goodbye()
                break
            except Exception as e:
                logger.error(f"Erro na sessão: {e}")
                logger.error(f"Erro: {e}")

    def _display_welcome(self):
        """Exibe mensagem de boas-vindas."""
        # Detectar tipo de LLM
        llm_type = type(self.llm).__name__
        llm_info = f"Powered by Ollama ({self.llm.model})" if "Ollama" in llm_type else "Powered by SimpleLLM"

        welcome_text = Text()
        welcome_text.append("🚗 ", style="bold blue")
        welcome_text.append("Assistente Virtual de Carros", style="bold green")
        welcome_text.append(f"\n[dim]{llm_info}[/dim]", style="dim")
        welcome_text.append("\n\n", style="white")
        welcome_text.append("Olá! Sou seu assistente virtual para busca de carros.", style="white")
        welcome_text.append("\n", style="white")
        welcome_text.append("Posso te ajudar a encontrar o carro ideal baseado nas suas preferências.", style="white")
        welcome_text.append("\n\n", style="white")
        welcome_text.append("Digite 'sair' para encerrar a conversa.", style="dim")

        logger.info("🤖 Agente Virtual iniciado")

    def _display_goodbye(self):
        """Exibe mensagem de despedida."""
        goodbye_text = Text()
        goodbye_text.append("Obrigado por usar o Assistente Virtual de Carros!", style="green")
        goodbye_text.append("\n", style="white")
        goodbye_text.append("Espero ter ajudado você a encontrar o carro ideal! 🚗", style="white")

        logger.info("👋 Agente Virtual finalizado")

    def _display_agent_response(self, response: str):
        """Exibe resposta do agente."""
        agent_text = Text()
        agent_text.append("🤖 ", style="bold blue")
        agent_text.append("Assistente", style="bold blue")
        agent_text.append("\n\n", style="white")
        agent_text.append(response, style="white")

        logger.info("Agente Virtual ativo")

    def _process_user_input(self, user_input: str) -> str:
        """Processa entrada do usuário e gera resposta."""
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                TimeElapsedColumn(),
                console=self.console,
                transient=True,
            ) as progress:

                # Passo 1: Extrair preferências usando Ollama
                task1 = progress.add_task("🤖 Analisando sua solicitação com IA...", total=None)
                logger.info("Analisando sua solicitação com IA...")
                preferences = self.llm.extract_car_preferences(user_input)
                progress.update(task1, description="✅ Preferências extraídas com sucesso!")

                # Atualizar estado da conversa
                self.conversation_state["preferences"].update(preferences)

                # Verificar se temos informações suficientes para buscar
                if self._has_sufficient_info():
                    # Passo 2: Gerar filtros MCP
                    task2 = progress.add_task("🔧 Convertendo preferências em filtros de busca...", total=None)
                    filters = self.llm.generate_car_search_filters(self.conversation_state["preferences"])
                    progress.update(task2, description="✅ Filtros gerados com sucesso!")

                    # Passo 3: Buscar carros via MCP
                    task3 = progress.add_task("🔍 Buscando carros no banco de dados...", total=None)
                    logger.info(f"Buscando carros com filtros: {filters}")
                    search_results = self._search_cars(filters)
                    progress.update(task3, description="✅ Busca concluída!")

                    if search_results and search_results.get("results") and len(search_results["results"]) > 0:
                        # Passo 4: Formatar resultados
                        task4 = progress.add_task("📝 Formatando resultados...", total=None)
                        response = self.llm.format_car_results(
                            search_results["results"], self.conversation_state["preferences"]
                        )
                        progress.update(task4, description="✅ Resultados formatados!")

                        # Salvar histórico
                        self.conversation_state["search_history"].append(
                            {"filters": filters, "results": search_results, "user_input": user_input}
                        )
                        self.conversation_state["current_results"] = search_results["results"]
                    else:
                        logger.warning(f"Nenhum carro encontrado. Filtros: {filters}, Resultados: {search_results}")
                        response = "😔 Não encontrei carros que atendam aos seus critérios. Que tal ajustarmos a busca?"
                else:
                    # Passo 2: Gerar próxima pergunta
                    task2 = progress.add_task("❓ Gerando pergunta de esclarecimento...", total=None)
                    missing_info = self._get_missing_info()
                    response = self.llm.generate_next_question(self.conversation_state["preferences"], missing_info)
                    progress.update(task2, description="✅ Pergunta gerada!")

            return response

        except Exception as e:
            logger.error(f"Erro ao processar entrada: {e}")
            return f"Desculpe, houve um erro ao processar sua solicitação: {e}"

    def _has_sufficient_info(self) -> bool:
        """Verifica se temos informações suficientes para buscar."""
        prefs = self.conversation_state["preferences"]

        # Pelo menos uma preferência deve estar definida
        return any(prefs.values())

    def _get_missing_info(self) -> list:
        """Retorna lista de informações que ainda faltam."""
        prefs = self.conversation_state["preferences"]
        missing: list[str] = []

        # Chaves esperadas pela LLM para geração de perguntas
        if not prefs.get("marca") and not prefs.get("modelo"):
            missing.append("marca")
        if not prefs.get("faixa_preco"):
            missing.append("faixa_preco")
        if not prefs.get("ano"):
            missing.append("ano")

        return missing

    def _search_cars(self, filters: dict[str, Any]) -> dict[str, Any]:
        """Executa busca de carros via MCP."""
        try:
            from apps.web_sockets.serializers import CarFilterSerializer, PaginationSerializer

            # Remover valores None dos filtros
            clean_filters = {k: v for k, v in filters.items() if v is not None}

            # Criar e validar serializers
            logger.debug(f"Buscando carros com clean_filters _search_cars: {clean_filters}")
            filter_serializer = CarFilterSerializer(data=clean_filters)
            if not filter_serializer.is_valid():
                logger.error(f"Filtros inválidos: {filter_serializer.errors}")
                return {"results": [], "total": 0}

            pagination_serializer = PaginationSerializer(data={"page": 1, "page_size": 10, "ordering": "-created_at"})
            if not pagination_serializer.is_valid():
                logger.error(f"Paginação inválida: {pagination_serializer.errors}")
                return {"results": [], "total": 0}

            # Construir payload MCP (compatível com CarMCPHandler)
            mcp_request = {
                "data": {
                    "action": "search_cars",
                    **filter_serializer.validated_data,
                    **pagination_serializer.validated_data,
                }
            }

            # Chamar handler MCP de forma assíncrona
            import asyncio

            async def _call_handler():
                return await self.mcp_handler.handle_request(mcp_request)

            response = asyncio.run(_call_handler())

            # Normalizar resposta
            if response.get("success"):
                data = response.get("data", {})
                return {
                    "results": data.get("results", []),
                    "total": data.get("total", 0),
                    "page": data.get("page"),
                    "page_size": data.get("page_size"),
                    "total_pages": data.get("total_pages"),
                }
            else:
                logger.error(f"Erro MCP: {response.get('error')}")
                return {"results": [], "total": 0}

        except Exception as e:
            logger.error(f"Erro na busca MCP: {e}", exc_info=True)
            return {"results": [], "total": 0}
