"""
Define API views for health check endpoints in the application.

It provides endpoints to monitor the application's health status and readiness.

The views are built on top of AbstractViewApi and include:
- HealthLiveApi: Basic health check endpoint
- HealthReadApi: Readiness check endpoint
- HealthStartApi: Startup check endpoint

All endpoints return JSON responses and are documented using OpenAPI schema.
"""

from typing import ClassVar

from rest_framework import permissions, status

from drf_base_apps.core.abstract.views import AbstractViewApi
from drf_base_apps.schemas import HealthSchema
from drf_base_apps.utils import _, doc, get_user_model


class HealthLiveApi(AbstractViewApi):
    """
    API endpoint for basic health check monitoring.

    This view provides a simple health check endpoint that can be used to verify
    if the application is running and responding to requests. It extends the
    AbstractViewApi class and implements a GET method that returns a basic
    health status.

    Attributes:
        http_method_names (list): List of allowed HTTP methods (GET only)
        serializer_class (class): HealthSchema for request/response validation
        permission_classes (list): List of permission classes (AllowAny)
        model (class): User model reference
        pagination (bool): Disabled pagination
        many (bool): Single object response
        tags (list): API documentation tags
        docs (dict): API documentation details

    Example:
        ```bash
        GET /api/v1/health/
        Response: {"status": "ok"}
        ```

    """

    http_method_names = ["get"]
    serializer_class = HealthSchema
    permission_classes = [permissions.AllowAny]
    model = get_user_model()
    pagination = False
    many = False
    tags = [str(_("base"))]
    docs: ClassVar[dict] = {
        "init": _(
            """Endpoint de verificação de saúde que confirma se a aplicação está rodando e respondendo a requisições.
            Este endpoint fornece um status básico de saúde que pode ser usado por balanceadores de carga,
            sistemas de monitoramento e plataformas de orquestração de containers para verificar a
            disponibilidade e responsividade da aplicação."""
        ),
        "get": _(
            """Recupera o status atual de saúde da aplicação.

            Este endpoint executa uma verificação básica de saúde para confirmar que a aplicação
            está rodando e pode responder a requisições HTTP. É projetado para ser leve e rápido,
            tornando-o adequado para monitoramento frequente de saúde.

            Retorna:
                JsonResponse: Uma resposta JSON contendo o status de saúde com HTTP 200 OK.
                Exemplo: {"status": "ok"}"""
        ),
    }

    @doc(
        _(
            """Retrieve the current health status of the application.

    This endpoint performs a basic health check and returns a simple status response.
    It can be used by load balancers or monitoring systems to verify the application's
    availability.

    Returns:
        JsonResponse: A JSON response containing the health status with HTTP 200 OK.
    """
        )
    )
    def get(self, request, *args, **kwargs):
        """Handle GET requests for health check."""
        return self.response({"status": "ok"}, status_=status.HTTP_200_OK)


class HealthReadApi(HealthLiveApi):
    """
    API endpoint for application readiness check.

    This view extends HealthLiveApi to provide a readiness check endpoint.
    It verifies if the application is ready to handle requests, including
    database connectivity and other critical services.

    Attributes:
        operation_id_base (str): Base identifier for OpenAPI documentation

    """

    operation_id_base = "HealthReadApi"
    docs: ClassVar[dict] = {
        "init": _(
            """Endpoint de verificação de prontidão que confirma se a aplicação está pronta para processar requisições.
            Este endpoint executa verificações abrangentes para garantir que a aplicação
            está totalmente operacional e pronta para processar requisições de usuários, incluindo
            conectividade com banco de dados, dependências de serviços externos e recursos do sistema."""
        ),
        "get": _(
            """Recupera o status de prontidão da aplicação.

            Este endpoint executa uma verificação abrangente da prontidão da aplicação,
            incluindo conectividade com banco de dados, dependências de serviços externos e recursos
            do sistema. É mais detalhado que a verificação básica de saúde e deve ser
            usado para determinar se a aplicação está pronta para processar tráfego de produção.

            Retorna:
                JsonResponse: Uma resposta JSON contendo o status de prontidão com HTTP 200 OK.
                Exemplo: {"status": "ready", "database": "connected", "services": "available"}
            """
        ),
    }


class HealthStartApi(HealthLiveApi):
    """
    API endpoint for application startup check.

    This view extends HealthLiveApi to provide a startup check endpoint.
    It verifies if the application has completed its initialization process
    and is ready to begin handling requests.

    Attributes:
        operation_id_base (str): Base identifier for OpenAPI documentation

    """

    operation_id_base = "HealthStartApi"
    docs: ClassVar[dict] = {
        "init": _(
            """Endpoint de verificação de inicialização que confirma se a aplicação completou o processo de inicialização.
            Este endpoint verifica se a aplicação finalizou seu processo de inicialização
            e está pronta para começar a operação normal."""
        ),
        "get": _(
            """Recupera o status de inicialização da aplicação.

            Este endpoint verifica se a aplicação completou seu processo de inicialização
            e está pronta para começar a operação normal.

            Retorna:
                JsonResponse: Uma resposta JSON contendo o status de inicialização com HTTP 200 OK.
            """
        ),
    }
