# Projeto Base BaseDjango Django

### O QUE É

> * Este é um projeto base em Django voltado para abstrair as camadas de model, view, schemas, admin e test. O objetivo
    principal é fornecer uma estrutura sólida para que desenvolvedores possam começar a desenvolver suas aplicações
    imediatamente, sem se preocupar com a estruturação básica do projeto. Contém também swagger para documentação de API e locust para teste de carga da plataforma

### A QUEM SE DESTINA / OBJETIVO

> * Usuários da BaseDjango que utilizam o Django como tecnologia de back-end podem aproveitar os benefícios de diminuir o
    tempo de implementação de funções padrão que todas as soluções obrigatoriamente utilizam. Além disso, o uso da base
    permite centralizar essas funções para manter uma manutenibilidade mais simples e segura.

## Instalação

1. Clone o repositório ou faça o download do código-fonte.
2. Instale as dependências: `poetry install`
3. Crie as migrações: `python manage.py makemigrations`
4. Execute as migrações: `python manage.py migrate`
5. Crie um super usuário: `python manage.py createsuperuser`
6. Inicie o servidor: `python manage.py runserver`

## Configurações Servidor

#### dependências

* poetry.lock

## Uso

Para começar a desenvolver a sua aplicação, você pode seguir os seguintes passos:

1. Defina os modelos em `models.py`, utilizando a classe `AbstractModel` como base.
2. Crie os serializers em `schema.py`, utilizando a classe `AbstractSchema` como base.
3. Crie as views em `views.py`, utilizando as classes `AbstractApi`, .
4. Crie os testes em `tests.py`, utilizando a classe `AbstractTest` como base.
5. (Opcional) Defina as configurações do admin em `admin.py`.

Comece criando um novo app com o comando `make startapp name=app_name`

# Configurações do Projeto

Este projeto suporta diferentes ambientes de execução, como desenvolvimento, produção, homologação e Azure. Você pode
especificar o ambiente desejado utilizando o argumento `--env` ao executar o script Python.

## Utilizando o Argumento --env

Para carregar as configurações do ambiente desejado, siga as instruções abaixo:

1. Certifique-se de ter os arquivos `.env.dev`, `.env.prod`, `.env.hml` ou `.env.azure` criado com as configurações
   adequadas para o ambiente que deseja usar.

2. Execute o script Python com o argumento `--env` seguido do nome do ambiente desejado. Por exemplo, para carregar as
   configurações do ambiente de desenvolvimento, execute o seguinte comando:

   ```bash
   python manage.py runserver --env dev

## Variáveis de Configuração

Este projeto possui algumas variáveis de configuração que podem ser definidas nos arquivos `.env`.
Abaixo estão as variáveis disponíveis e como utilizá-las.

### APP_NAME

Variável que define o nome da aplicação. Caso não seja definida, o valor padrão é 'app'.

### DEBUG

Variável booleana que define se o modo de depuração está ativado ou desativado. O valor padrão é False.

### ENABLE_DRF

Variável booleana que define se o drf_standardized_errors(output padrão de erros na resposta) está habilitado ou
desabilitado. O valor padrão é True.

### ENABLE_CACHE

Variável booleana que define se o cache está habilitado ou desabilitado. O valor padrão é False.

### EXTERNAL_DATABASE

Variável booleana que define se o banco de dados externo está habilitado ou desabilitado. O valor padrão é False. Essa
opção funciona apenas para ambiente DEV, em produção é configurado automaticamente para DB externo

### TOKEN_TEST

Variável que armazena o token utilizado para execução de testes em ambientes controlados.

### ENVIRONMENT

Variável que define o ambiente de execução do projeto. O valor padrão é 'dev'. Outros ambientes são  'prod', 'hml' e '
azure'

### LIST_ALLOWED_HOSTS

Variável que define uma lista separada por vírgulas dos hosts permitidos para acesso ao projeto. Caso não seja definida,
o valor padrão é uma string vazia.

### PASSWD_DEV

Variável que armazena a senha do usuário de desenvolvimento. O valor padrão é 'fake_passwd'.

### USER_DEV

Variável que armazena o nome do usuário de desenvolvimento. O valor padrão é 'dev_user'.

### USER_ADM_DEV

Variável que armazena o nome do usuário administrador de desenvolvimento. O valor padrão é 'dev_admin'.

### FERNET_KEY

Variável que armazena a chave Fernet utilizada para criptografia.

### API_VERSION

Variável que define a versão da API. O valor padrão é 'v1'.

### SANDBOX_COMMIT

Variável booleana que indica se os commits no banco de dados devem ser realizados ou revertidos.
Se SANDBOX_COMMIT for False e o método da requisição for 'POST', 'PUT' ou 'DELETE', a transação no banco de dados será
revertida após o processamento da requisição, garantindo que as mudanças não sejam salvas permanentemente, e retorna o
resultado da request como se fosse feita normalmente.

# Documentação da API

A API deste projeto possui uma documentação interativa fornecida pelo Swagger. Para acessar a documentação, siga as
instruções abaixo:

1. Certifique-se de ter o servidor em execução.p

2. Abra o seu navegador da web e digite a seguinte URL: `http://127.0.0.1:8000/app/api/v1/docs/swagger/`  
   Substitua `http://127.0.0.1:8000/app` pela URL do servidor em que a aplicação está sendo executada e o app pelo nome da sua aplicação configurada na .env na variável APP_NAME.  
   Substitua `v1` pela variável API_VERSION que está configurada na sua .env .

3. A página do Swagger será exibida, mostrando todos os endpoints disponíveis, os parâmetros necessários, as respostas
   esperadas e outras informações relevantes sobre a API.

4. Utilize a interface do Swagger para explorar e testar os endpoints da API. Você pode enviar solicitações HTTP
   diretamente pela interface do Swagger e visualizar as respostas correspondentes.

# Documentação de teste da API

A API deste projeto possui uma documentação interativa fornecida pelo Swagger para testes e gravações de exemplo. Para
acessar a documentação, siga as
instruções abaixo:

1. Certifique-se de ter o servidor em execução.

2. Abra o seu navegador da web e digite a seguinte URL: `http://127.0.0.1:8000/app/api/v1/docs/swagger/cache/`  
   Substitua `http://127.0.0.1:8000/app` pela URL do servidor em que a aplicação está sendo executada e o app pelo nome da sua aplicação configurada na .env na variável APP_NAME.  
   Substitua `v1` pela variável API_VERSION que está configurada na sua .env .

3. A página do Swagger será exibida, mostrando todos os endpoints disponíveis, os parâmetros necessários, as respostas
   esperadas e outras informações relevantes sobre a API.

4. Utilize a interface do Swagger para explorar e testar os endpoints da API. Você pode enviar solicitações HTTP
   diretamente pela interface do Swagger e visualizar as respostas correspondentes.

5. Todos as requests feitas serão realizadas numa SANDBOX de teste, portanto os dados enviados não serão salvo em banco,
   mas seus resultados serão refletidos como se fosse feita.

6. Todos os Body e Parameters vão ser salvos, e ao atualizar a página, terá os resultados anteriores

7. Para limpar o formulário de cache, acesse `http://127.0.0.1:8000/app/api/v1/docs/swagger/save/`

# Executando Testes com python manage.py test

O comando python manage.py test é usado para executar testes em um projeto Django. É um comando de gerenciamento
fornecido pelo Django que ajuda a automatizar o processo de execução de testes para a sua aplicação.

## Como Executar

### Testes via Django:

1. Abra um terminal ou prompt de comando.
2. Navegue até o diretório raiz do seu projeto Django.
3. Execute o seguinte comando `python manage.py test`
4. O Django irá automaticamente descobrir e executar todos os testes definidos no

# Configuração do settings.py

## Por padrão a maior parte das configurações do settings do django está definida na base, precisando apenas ser extendida no seu app

`

    import sysconfig
    import os

    from os import path
    from decouple import config
    from split_settings.tools import include as extend_settings
    
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "drf_base_config.settings")
    
    library_path = sysconfig.get_paths()['purelib']
    settings_path = path.join(library_path, 'drf_base_config', 'settings.py')
    
    extend_settings(settings_path)
    
    from drf_base_config.settings import *
    
    INSTALLED_APPS += [
    'my_app',
    ]

`

# Sistema de Permissões Baseado em Grupos

O sistema de permissões baseado em grupos substitui os campos booleanos `has_rh_perm` e `has_clb_perm` por properties que verificam a pertinência a grupos específicos, além de adicionar suporte para os grupos INTRA e INTEGRATOR. Isso permite uma gestão mais flexível e granular das permissões.

## Grupos Padrão

O sistema define quatro grupos padrão:

1. **RH**: Permissões para recursos humanos
2. **CLB**: Permissões para colaboradores
3. **INTRA**: Permissões para intranet
4. **INTEGRATOR**: Permissões para integradores

## Comandos de Gerenciamento de Permissões

### Criar Grupos

```bash
python manage.py create_groups [--json-file=caminho/para/arquivo.json]
```

Cria os grupos padrão (RH, CLB, INTRA, INTEGRATOR) e configura permissões iniciais baseadas na estrutura JSON padrão ou em um arquivo JSON fornecido.

**Parâmetros:**
- `--json-file`: (Opcional) Caminho para um arquivo JSON personalizado com configurações de permissões.

**Exemplos de uso:**

1. Criar grupos com permissões padrão:
   ```bash
   python manage.py create_groups
   ```

2. Criar grupos com permissões personalizadas:
   ```bash
   python manage.py create_groups --json-file=minha_configuracao.json
   ```

### Exportar Permissões

```bash
python manage.py export_permissions --output=caminho/para/arquivo.json
```

Exporta a configuração atual de permissões para um arquivo JSON. Útil para backup ou para transferir configurações entre ambientes.

**Parâmetros:**
- `--output`: (Obrigatório) Caminho para o arquivo JSON onde as permissões serão salvas.

**Exemplos de uso:**

1. Exportar para um arquivo específico:
   ```bash
   python manage.py export_permissions --output=permissoes_atuais.json
   ```

2. Exportar para o diretório de fixtures:
   ```bash
   python manage.py export_permissions --output=drf_base_apps/core/abstract/fixtures/permissoes_backup.json
   ```

### Importar Permissões

```bash
python manage.py import_permissions --input=caminho/para/arquivo.json [--update-default]
```

Importa configuração de permissões de um arquivo JSON. Útil para restaurar backups ou aplicar configurações predefinidas.

**Parâmetros:**
- `--input`: (Obrigatório) Caminho para o arquivo JSON com as permissões a serem importadas.
- `--update-default`: (Opcional) Se fornecido, atualiza também o arquivo de permissões padrão.

**Exemplos de uso:**

1. Importar de um arquivo específico:
   ```bash
   python manage.py import_permissions --input=permissoes_atuais.json
   ```

2. Importar e atualizar o arquivo padrão:
   ```bash
   python manage.py import_permissions --input=permissoes_atuais.json --update-default
   ```

### Testar Permissões de Grupos

```bash
python manage.py test_group_permissions [--group=NOME_DO_GRUPO]
```

Testa a funcionalidade de permissões baseadas em grupos, verificando se as permissões estão corretamente configuradas.

**Parâmetros:**
- `--group`: (Opcional) Nome do grupo específico para testar. Se não fornecido, testa todos os grupos.

**Exemplos de uso:**

1. Testar todos os grupos:
   ```bash
   python manage.py test_group_permissions
   ```

2. Testar um grupo específico:
   ```bash
   python manage.py test_group_permissions --group=RH
   ```

### Interface Interativa

```bash
python manage.py manage_permissions
```

Abre uma interface interativa no terminal para gerenciar grupos e permissões, similar ao npm plop. Esta interface permite:

1. Gerenciar grupos (criar, visualizar, editar)
2. Gerenciar permissões (visualizar, configurar)
3. Importar configuração de um arquivo JSON
4. Exportar configuração para um arquivo JSON

**Guia passo a passo:**

1. **Menu Principal:**
   - Opção 1: Gerenciar grupos
   - Opção 2: Gerenciar permissões
   - Opção 3: Importar configuração
   - Opção 4: Exportar configuração
   - Opção 5: Sair

2. **Gerenciar Grupos:**
   - Visualizar grupos existentes
   - Criar novo grupo
   - Voltar ao menu principal

3. **Gerenciar Permissões:**
   - Visualizar permissões de um grupo: Mostra todas as permissões CRUD por app para o grupo selecionado
   - Configurar permissões de um grupo: Permite selecionar um grupo, um app e configurar permissões CRUD
   - Voltar ao menu principal

4. **Configurar Permissões:**
   - Selecionar um grupo (USER, ADMIN)
   - Selecionar um app (lista de apps disponíveis)
   - Configurar permissões CRUD (Create, Read, Update, Delete)
   - Opção para atualizar o arquivo de permissões padrão

5. **Importar Configuração:**
   - Informar o caminho para o arquivo JSON
   - Opção para atualizar o arquivo de permissões padrão

6. **Exportar Configuração:**
   - Informar o caminho para salvar o arquivo JSON

**Exemplo de fluxo para configurar permissões:**

1. Execute `python manage.py manage_permissions`
2. Selecione a opção 2 (Gerenciar permissões)
3. Selecione a opção 2 (Configurar permissões de um grupo)
4. Selecione o número correspondente ao grupo desejado (ex: 4 para RH)
5. Digite o nome do app (ex: drf_api_logger)
6. Configure as permissões CRUD respondendo Sim/Não para cada tipo
7. Confirme as alterações
8. Escolha se deseja atualizar o arquivo de permissões padrão

## Estrutura JSON para Permissões

As permissões são definidas em uma estrutura JSON que permite configurar permissões CRUD (Create, Read, Update, Delete) por app para cada grupo:

```json
{
    "RH": {
        "apps": {
            "drf_base_user": {
                "create": true,
                "read": true,
                "update": true,
                "delete": false
            }
        }
    },
    "CLB": {
        "apps": {
            "drf_base_user": {
                "create": false,
                "read": true,
                "update": true,
                "delete": false
            }
        }
    }
}
```

# Geração de Novos Projetos

## Comando generate_project_config

O comando `generate_project_config` permite criar novos projetos Django baseados no drf_base_apps, gerando automaticamente todos os arquivos de configuração necessários.

### Como Usar

```bash
python manage.py generate_project_config --project-name=NOME_DO_PROJETO [--output-dir=DIRETORIO] [--force]
```

**Parâmetros:**
- `--project-name`: (Obrigatório) Nome do projeto a ser criado
- `--output-dir`: (Opcional) Diretório onde o projeto será criado (padrão: diretório atual)
- `--force`: (Opcional) Sobrescreve arquivos existentes se fornecida

**Exemplos de uso:**

1. Criar projeto no diretório atual:
   ```bash
   python manage.py generate_project_config --project-name=meu_projeto
   ```

2. Criar projeto em diretório específico:
   ```bash
   python manage.py generate_project_config --project-name=meu_projeto --output-dir=/caminho/para/projetos
   ```

3. Sobrescrever projeto existente:
   ```bash
   python manage.py generate_project_config --project-name=meu_projeto --force
   ```

### Estrutura Gerada

O comando gera a seguinte estrutura de arquivos:

```
meu_projeto/
├── __init__.py          # Arquivo de inicialização Python
├── settings.py          # Configurações do Django baseadas no drf_base_apps
├── urls.py             # Configuração de URLs principal
├── wsgi.py             # Configuração WSGI para produção
└── asgi.py             # Configuração ASGI para async
```

### Arquivos de Configuração

- **settings.py**: Configurações Django pré-configuradas com drf_base_apps
- **urls.py**: Estrutura de URLs base com suporte a API e admin
- **wsgi.py**: Configuração WSGI para servidores web tradicionais
- **asgi.py**: Configuração ASGI para servidores async modernos

### Após a Geração

1. **Navegue para o diretório do projeto:**
   ```bash
   cd meu_projeto
   ```

2. **Instale as dependências com Poetry:**
   ```bash
   poetry install
   ```

3. **Configure as variáveis de ambiente:**
   ```bash
   cp .env.example .env
   # Edite o arquivo .env com suas configurações
   ```

4. **Execute as migrações:**
   ```bash
   poetry run python manage.py migrate
   ```

5. **Crie um superusuário:**
   ```bash
   poetry run python manage.py createsuperuser
   ```

6. **Execute o servidor:**
   ```bash
   poetry run python manage.py runserver
   ```

# Configuração do urls.py

## Por padrão a maior parte das configurações de urls do django está definida na base, precisando apenas ser extendida no seu app

`

    from django.urls import path, include
    from django.conf.urls.static import static
    from drf_base_config.settings import BASE_API_URL
    
    from drf_base_config import urls as base_urls
    
    from drf_base_config.settings import MEDIA_URL, MEDIA_ROOT
    
    
    urlpatterns = [
        path('', include(base_urls)),
        path('my_path', include('my_app.urls')),
    ]
    
    
    urlpatterns += static("/" + MEDIA_URL, document_root=MEDIA_ROOT)

`
