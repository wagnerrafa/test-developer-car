"""
Este módulo define classes de API que fornecem métodos HTTP para gerenciar objetos do modelo User.

É estendido da classe AbstractViewApi e inclui uma classe de permissão CheckHasPermission para autorização.
As APIs respondem com dados JSON e usam rest_framework.schemas.openapi.AutoSchema para gerar a documentação da API.
As classes de API usam o modelo User e o schema User para trabalhar com os dados.
"""

from drf_base_apps.core.abstract.views import AbstractViewApi
from drf_base_apps.core.drf_base_user.schemas import UserSchema
from drf_base_apps.utils import _, get_user_model


class UserApi(AbstractViewApi):
    """
    Define a classe de visualização UserApi para lidar com métodos HTTP relacionados ao User.

    Esta classe de visualização estende a classe AbstractViewApi, que fornece uma implementação básica
    para ações comuns de API. O UserApi suporta métodos HTTP POST e GET, e usa o UserSchema
    para validação de entrada/saída. A visualização requer usuários autenticados com permissões
    apropriadas para acessar os endpoints da API, conforme especificado pelas classes de permissão
    IsAuthenticated e CheckHasPermission.

    Atributos:
        http_method_names (list): Uma lista de métodos HTTP suportados por esta visualização.
        serializer_class (class): A classe de serialização para validação de entrada/saída.
        permission_classes (list): Uma lista de classes de permissão para autenticação e autorização de usuários.
        model (class): A classe de modelo associada a esta visualização.
        authentication_classes (list): Uma lista de classes de autenticação para verificar a identidade do usuário.
        query_params (list): Uma lista de dicionários, cada um especificando um parâmetro de consulta para a API.

    Exemplos:
        Para obter informações do usuário autenticado:
        ```
        GET /api/v1/user/
        Authorization: Bearer <token_jwt>
        ```
    """

    http_method_names = ["get"]
    serializer_class = UserSchema
    model = get_user_model()
    pagination = False
    many = False
    tags = [str(_("base"))]
    operation_id_base = "UserApi"

    docs = {
        "init": _(
            """API endpoint para gerenciar informações do usuário autenticado.
            Fornece acesso aos dados pessoais e de perfil do usuário logado,
            incluindo informações básicas como nome, email, CPF e status da conta.
            Acesso restrito apenas ao próprio usuário autenticado."""
        ),
        "get": _(
            """Recupera e retorna as informações completas do usuário autenticado.

            Este endpoint retorna todos os dados do perfil do usuário logado,
            incluindo informações pessoais, dados de contato e configurações
            de conta. Os dados são filtrados automaticamente para mostrar
            apenas informações do usuário autenticado.

            Retorna:
                JsonResponse: Objeto contendo dados completos do usuário autenticado,
                incluindo ID, nome, email, CPF, status da conta e outras informações
                de perfil relevantes.
            """
        ),
    }
