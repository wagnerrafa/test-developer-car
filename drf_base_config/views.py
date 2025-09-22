"""Views principais do sistema."""

from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.generic import TemplateView

from drf_base_config.settings import APP_NAME, CURRENT_VERSION, LOGOUT_REDIRECT_URL


@ensure_csrf_cookie
def frontend_index(request, *args, **kwargs):
    """Renderiza a página inicial do frontend."""
    if request.path == "/":
        return redirect("home")
    return render(
        request,
        template_name="index.html",
    )


@login_required
def user_logout(request):
    """Realiza o logout do usuário."""
    logout(request)
    return redirect(LOGOUT_REDIRECT_URL)


class AdminRequiredMixin(LoginRequiredMixin):
    """Verify that the current user is superuser."""

    def dispatch(self, request, *args, **kwargs):
        """Verifica se o usuário é superusuário antes de processar a requisição."""
        if not request.user.is_superuser:
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)


class CustomTemplateView(AdminRequiredMixin, TemplateView):
    """Template view customizada que requer privilégios de administrador."""

    pass


def sobre_base_django(request):
    """Renderiza a página Sobre a BaseDjango."""
    return render(
        request,
        template_name="sobre_base_django.html",
        context={"app_name": APP_NAME, "current_version": CURRENT_VERSION},
    )


def privacidade(request):
    """Renderiza a página de Privacidade."""
    return render(
        request, template_name="privacidade.html", context={"app_name": APP_NAME, "current_version": CURRENT_VERSION}
    )


def home(request):
    """Renderiza a página home sobre o projeto."""
    return render(
        request, template_name="home.html", context={"app_name": APP_NAME, "current_version": CURRENT_VERSION}
    )


def websocket_page(request):
    """Renderiza a página de WebSocket."""
    return render(
        request,
        template_name="websocket.html",
        context={
            "app_name": APP_NAME,
            "current_version": CURRENT_VERSION,
            "websocket_url": f"ws://{request.get_host()}/{APP_NAME}/ws/V1/general/",
        },
    )
