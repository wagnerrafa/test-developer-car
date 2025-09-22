"""
Custom Django middleware for security and content-type handling.

This module includes two middleware classes:
1. `CustomSecurityMiddleware`: Inherits from `SessionMiddleware` and adds
   XSS protection header (`X-XSS-Protection`) to the response if enabled
   in Django settings (`SECURE_BROWSER_XSS_FILTER`).

2. `CharsetMiddleware`: Middleware to ensure `Content-Type` header includes
   proper charset information (`DEFAULT_CHARSET`) for responses.

Classes:
- `CustomSecurityMiddleware`: Middleware to add XSS protection header.
- `CharsetMiddleware`: Middleware to ensure correct Content-Type with charset.

Usage:
1. Configure `CustomSecurityMiddleware` in Django settings middleware list.
   Ensure `SECURE_BROWSER_XSS_FILTER` is set to `True` to enable XSS protection.

2. Use `CharsetMiddleware` to automatically append or set `Content-Type`
   with `DEFAULT_CHARSET` if not explicitly provided in the response.

"""

import json
import logging
import time
import uuid

from django.conf import settings
from django.conf.global_settings import DEFAULT_CHARSET
from django.utils import timezone
from django.utils.deprecation import MiddlewareMixin
from drf_api_logger.models import APILogsModel

from drf_base_config.settings import APP_NAME


class CharsetMiddleware:
    """
    Middleware class to ensure proper Content-Type header with charset.

    Methods:
    - __init__(get_response): Initializes the middleware with get_response callable.
    - __call__(request): Processes the request to ensure Content-Type includes charset.

    """

    def __init__(self, get_response):
        """
        Initialize middleware with a callable for getting the response.

        Args:
            get_response: Callable to retrieve response for processing.

        """
        self.get_response = get_response

    def __call__(self, request):
        """
        Process the request to ensure Content-Type header includes charset.

        Args:
            request: The HTTP request object.

        Returns:
            HttpResponse: Processed HTTP response with ensured Content-Type header.

        """
        # FORTIFY: (Web Server Misconfiguration: Insecure Content-Type Setting)
        response = self.get_response(request)
        if not response.has_header("Content-Type"):
            response["Content-Type"] = f"text/html; charset={DEFAULT_CHARSET}"
        elif "charset" not in response["Content-Type"]:
            response["Content-Type"] += f"; charset={DEFAULT_CHARSET}"
        return response


class CacheControlMiddleware:
    """Middleware para adicionar headers de controle de cache."""

    def __init__(self, get_response):
        """Inicializa o middleware com a função de resposta."""
        self.get_response = get_response

    def __call__(self, request):
        """Adiciona headers de controle de cache à resposta."""
        response = self.get_response(request)

        if not response.has_header("Cache-Control"):
            response["Cache-Control"] = "no-cache, no-store, must-revalidate"

        return response


class DisableCSRF(MiddlewareMixin):
    """Middleware para desabilitar verificações CSRF."""

    def process_request(self, request):
        """Desabilita as verificações CSRF para a requisição."""
        request._dont_enforce_csrf_checks = True


class ForceAPILoggingMiddleware:
    """
    Middleware personalizado para garantir que todos os requests sejam logados.

    Independentemente de filtros do drf_api_logger.
    """

    def __init__(self, get_response):
        """Inicializa o middleware com a função de resposta."""
        self.get_response = get_response

    def __call__(self, request):
        """Processa a requisição e força o logging."""
        start_time = time.time()

        # Processa a requisição
        response = self.get_response(request)

        # Calcula o tempo de execução
        execution_time = time.time() - start_time

        # Garante que o log seja salvo independentemente de filtros
        try:
            # Verifica se é uma requisição que deve ser logada
            if hasattr(request, "resolver_match") and request.resolver_match:
                # Obtém informações da requisição
                api = request.build_absolute_uri()

                # Usa as configurações do settings para verificar URLs a serem ignoradas
                skip_full_paths = getattr(settings, "DRF_API_LOGGER_SKIP_FULL_PATH", [])
                skip_url_names = getattr(settings, "DRF_API_LOGGER_SKIP_URL_NAME", [])

                # Verifica se deve pular completamente o log
                should_skip_completely = False
                path_info = request.path_info

                # Verifica URLs por caminho completo (DRF_API_LOGGER_SKIP_FULL_PATH)
                for skip_path in skip_full_paths:
                    if path_info.endswith(skip_path) or path_info.startswith(skip_path):
                        should_skip_completely = True
                        break

                # Verifica URLs específicas do app
                if not should_skip_completely and (
                    f"/{APP_NAME}/" == path_info or path_info == "/" or f"/{APP_NAME}" == path_info
                ):
                    should_skip_completely = True

                if should_skip_completely:
                    return response

                # Verifica se deve mascarar body e response (DRF_API_LOGGER_SKIP_URL_NAME)
                should_mask_sensitive_data = False
                if hasattr(request.resolver_match, "url_name") and request.resolver_match.url_name:
                    url_name = request.resolver_match.url_name
                    if url_name in skip_url_names:
                        should_mask_sensitive_data = True

                headers = dict(request.headers)
                method = request.method
                status_code = response.status_code

                # Remove informações sensíveis dos headers
                sensitive_headers = ["authorization", "cookie", "x-csrftoken"]
                for header in sensitive_headers:
                    if header in headers:
                        headers[header] = "[HIDDEN]"

                # Obtém o corpo da requisição (se aplicável)
                body = ""
                if not should_mask_sensitive_data and hasattr(request, "body") and request.body:
                    try:
                        body = request.body.decode("utf-8")
                        # Limita o tamanho do body para evitar logs muito grandes
                        if len(body) > 10000:
                            body = body[:10000] + "... [TRUNCATED]"
                    except UnicodeDecodeError:
                        body = "[BINARY_DATA]"
                    except Exception as e:
                        logging.warning(f"Erro ao decodificar body da requisição: {e}")
                        body = "[ERROR_DECODING]"
                elif should_mask_sensitive_data:
                    body = "[SENSITIVE_DATA_MASKED]"

                # Obtém a resposta (se aplicável)
                response_body = ""
                if not should_mask_sensitive_data and hasattr(response, "content") and response.content:
                    try:
                        response_body = response.content.decode("utf-8")
                        # Limita o tamanho da resposta para evitar logs muito grandes
                        if len(response_body) > 10000:
                            response_body = response_body[:10000] + "... [TRUNCATED]"
                    except UnicodeDecodeError:
                        response_body = "[BINARY_DATA]"
                    except Exception as e:
                        logging.warning(f"Erro ao decodificar resposta: {e}")
                        response_body = "[ERROR_DECODING]"
                elif should_mask_sensitive_data:
                    response_body = "[SENSITIVE_DATA_MASKED]"

                try:
                    APILogsModel.objects.create(
                        api=api,
                        headers=json.dumps(headers, indent=4),
                        body=body,
                        method=method,
                        client_ip_address=request.META.get("REMOTE_ADDR", ""),
                        response=response_body,
                        status_code=status_code,
                        execution_time=str(execution_time),
                        added_on=timezone.now(),
                    )
                except (ValueError, TypeError) as e:
                    logging.error(f"Erro de validação ao criar log da API: {e}")
                except Exception as e:
                    logging.error(f"Erro inesperado ao salvar log da API: {e}")

        except Exception as e:
            # Em caso de erro, não interrompe o fluxo da aplicação
            # Apenas registra o erro no console para debug
            logging.debug(f"Erro ao salvar log da API: {e}")

        return response


class AnonymousIdMiddleware(MiddlewareMixin):
    """
    Middleware que gera um UUID persistente para usuários anônimos.

    Isso garante que todos os usuários tenham uma identificação única
    mesmo sem estar autenticados.
    """

    def process_request(self, request):
        """Gera ou recupera o ID anônimo do usuário."""
        # Verificar se já existe o cookie anon_id
        if "anon_id" not in request.COOKIES:
            # Gerar um novo UUID para o usuário anônimo
            request.anon_id = str(uuid.uuid4())
        else:
            # Usar o UUID existente
            request.anon_id = request.COOKIES["anon_id"]

    def process_response(self, request, response):
        """Define o cookie anon_id na resposta se necessário."""
        # Se foi gerado um novo anon_id, definir o cookie
        if hasattr(request, "anon_id") and "anon_id" not in request.COOKIES:
            response.set_cookie(
                "anon_id", request.anon_id, httponly=True, samesite="Lax", max_age=365 * 24 * 60 * 60  # 1 ano
            )
        return response
