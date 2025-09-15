"""Views for custom log viewer."""

from typing import ClassVar

from log_viewer.views import LogViewerView

from drf_base_apps.utils import _


class CustomLogViewerView(LogViewerView):
    """
    Custom log viewer view class.

    Esta view personalizada estende a LogViewerView para fornecer uma interface
    web para visualização de logs do sistema. Permite aos usuários autenticados
    visualizar e navegar pelos arquivos de log de forma segura.

    Attributes:
        template_name (str): Nome do template HTML usado para renderizar os logs.

    """

    template_name = "log_viewer.html"

    docs: ClassVar[dict] = {
        "init": _(
            """Interface web para visualização de logs do sistema.
            Permite aos usuários autenticados visualizar e navegar pelos
            arquivos de log de forma segura e organizada."""
        ),
        "get": _(
            """Exibe a interface de visualização de logs.

            Este endpoint renderiza a interface web para visualização de logs,
            permitindo aos usuários navegar pelos arquivos de log disponíveis
            e visualizar seu conteúdo de forma organizada.

            Retorna:
                HttpResponse: Página HTML com a interface de visualização de logs."""
        ),
    }
