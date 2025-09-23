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
5. Colete os arquivos estáticos: `python manage.py collectstatic`
6. Crie um super usuário: `python manage.py createsuperuser`
7. Inicie o servidor: `python manage.py runserver`

## Executando o Servidor

### Desenvolvimento Local
Para desenvolvimento local com suporte completo a WebSocket:

```bash
daphne config.asgi:application --port 8000 -v2
```

### Produção
Para ambiente de produção com múltiplos workers:

```bash
gunicorn config.asgi:application -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000 --workers 4
```

**Nota:** O servidor padrão do Django (`python manage.py runserver`) não suporta WebSocket. Use os comandos acima para funcionalidade completa.

## Configurações Servidor

#### dependências

* poetry.lock

## Uso

### Protocolo MCP via WebSocket

O projeto agora inclui implementação completa do **Protocolo MCP (Model Context Protocol)** via WebSocket para busca dinâmica de carros em tempo real.

#### Funcionalidades MCP
- **Busca em tempo real**: Filtros dinâmicos de carros via WebSocket
- **Filtros avançados**: Marca, ano, combustível, transmissão, cor, motor, preço
- **Paginação**: Suporte completo a paginação via MCP
- **Ordenação**: Por preço, ano, quilometragem, etc.
- **Histórico**: Manter histórico de buscas por sessão
- **Métricas**: Monitoramento de uso e performance

#### Endpoints WebSocket MCP
- **MCP V1**: `/app/ws/V1/mcp/cars/` - Funcionalidades básicas
- **MCP V2**: `/app/ws/V1/mcp/cars/v2/` - Funcionalidades avançadas + métricas

#### Ações Suportadas
- `search_cars`: Busca carros com filtros
- `get_brands`: Lista marcas disponíveis
- `get_colors`: Lista cores disponíveis
- `get_engines`: Lista motores disponíveis
- `get_car_details`: Detalhes de um carro específico
- `get_filters_options`: Opções disponíveis para cada filtro

#### Exemplo de Uso Cliente
```javascript
const client = new MCPCarClient('ws://localhost:8000/app/ws/V1/mcp/cars/');
await client.connect();

// Buscar carros Toyota com filtros
await client.searchCars({
    brand_name: 'Toyota',
    year_manufacture_min: 2020,
    price_max: 100000
}, {
    page: 1,
    page_size: 20,
    ordering: '-price'
});
```

Para documentação completa, consulte: [Guia MCP WebSocket](MCP_WEBSOCKET_GUIDE.md)

#### Demonstração Interativa
Acesse a demonstração interativa em: `http://localhost:8000/mcp-demo/`

A página de demonstração inclui:
- Interface visual para busca de carros
- Filtros dinâmicos em tempo real
- Conexão WebSocket automática
- Paginação e ordenação
- Exemplos de uso do protocolo MCP

### Agente Virtual de Busca de Carros

O projeto inclui um **Agente Virtual Inteligente** que permite buscar carros através de conversas naturais no terminal, utilizando LLM (Large Language Model) para entender preferências e gerar filtros de busca automaticamente.

#### Funcionalidades do Agente

- **Conversa Natural**: Interaja com o agente usando linguagem natural
- **Extração Inteligente**: O agente extrai preferências de carros automaticamente
- **Filtros Automáticos**: Converte preferências em filtros de busca MCP
- **Múltiplas LLMs**: Suporte a Ollama e SimpleLLM
- **Busca em Tempo Real**: Integração direta com o sistema MCP WebSocket
- **Interface Amigável**: Interface rica no terminal com progresso e feedback

#### Como Usar o Agente

##### 1. Executar o Agente

```bash
# Usar com SimpleLLM (padrão)
python manage.py run_car_agent

# Usar com Ollama (se disponível)
python manage.py run_car_agent --llm-provider=ollama

# Usar com Ollama e modelo específico
python manage.py run_car_agent --llm-provider=ollama --llm-model=llama3.1:8b
```

##### 2. Exemplos de Conversas

**Busca por Marca e Ano:**
```
🤖 Agente Virtual: Olá! Sou seu assistente para busca de carros. Como posso ajudar?

👤 Você: Quero um Audi 2016

🤖 Agente Virtual: ✅ Preferências extraídas com sucesso!
- Marca: Audi
- Ano: 2016

🔍 Buscando carros no banco de dados...
✅ Encontrei 3 carros que atendem aos seus critérios!
```

**Busca por Faixa de Preço:**
```
👤 Você: Preciso de um carro entre 30 e 50 mil reais

🤖 Agente Virtual: ✅ Preferências extraídas com sucesso!
- Faixa de preço: R$ 30.000 - R$ 50.000

🔍 Buscando carros no banco de dados...
✅ Encontrei 15 carros na sua faixa de preço!
```

**Busca por Combustível e Transmissão:**
```
👤 Você: Quero um carro flex automático

🤖 Agente Virtual: ✅ Preferências extraídas com sucesso!
- Combustível: Flex
- Transmissão: Automática

🔍 Buscando carros no banco de dados...
✅ Encontrei 8 carros flex automáticos!
```

##### 3. Preferências Suportadas

O agente entende as seguintes preferências:

- **Marca**: Toyota, Honda, Ford, Audi, BMW, etc.
- **Modelo**: Corolla, Civic, Focus, A4, X5, etc.
- **Ano**: 2015, 2016, 2020, "recente", "antigo"
- **Preço**: "econômico", "médio", "luxo", faixas específicas
- **Combustível**: Gasolina, Etanol, Flex, Diesel, Elétrico, Híbrido
- **Transmissão**: Manual, Automática, CVT, Semi-automática
- **Cor**: Branco, Preto, Prata, Azul, Vermelho, etc.
- **Portas**: 2, 4, 5 portas
- **Quilometragem**: "baixa", "média", "alta", valores específicos

##### 4. Configuração de LLM

O agente suporta diferentes provedores de LLM:

**SimpleLLM (Padrão):**
- Rápido e leve
- Ideal para desenvolvimento e testes
- Não requer configuração adicional

**Ollama:**
- Mais inteligente e preciso
- Requer instalação do Ollama
- Suporte a modelos como Llama, Mistral, etc.

**Configurar Ollama:**
```bash
# Instalar Ollama (se não estiver instalado)
curl -fsSL https://ollama.ai/install.sh | sh

# Baixar modelo (exemplo: Llama 3.1 8B)
ollama pull llama3.1:8b

# Executar agente com Ollama
python manage.py run_car_agent --llm-provider=ollama --llm-model=llama3.1:8b
```

##### 5. Comandos do Agente

Durante a conversa, você pode usar:

- **"sair"** ou **"quit"**: Encerrar o agente
- **"ajuda"** ou **"help"**: Mostrar ajuda
- **"limpar"** ou **"clear"**: Limpar histórico da conversa
- **"buscar"**: Forçar nova busca com preferências atuais

##### 6. Exemplo Completo de Sessão

```
🤖 Agente Virtual: Olá! Sou seu assistente para busca de carros. Como posso ajudar?

👤 Você: Preciso de um carro para família

🤖 Agente Virtual: Entendi! Para uma família, que tipo de carro você prefere? 
- Qual marca você tem em mente?
- Que faixa de preço seria ideal?
- Prefere automático ou manual?

👤 Você: Toyota automático até 80 mil

🤖 Agente Virtual: ✅ Preferências extraídas com sucesso!
- Marca: Toyota
- Transmissão: Automática
- Preço máximo: R$ 80.000

🔍 Buscando carros no banco de dados...
✅ Encontrei 12 carros Toyota automáticos até R$ 80.000!

📋 Resultados encontrados:
1. Toyota Corolla 2022 - R$ 75.000
2. Toyota Camry 2021 - R$ 78.000
3. Toyota RAV4 2020 - R$ 72.000
...

👤 Você: Quero ver mais detalhes do Corolla

🤖 Agente Virtual: Aqui estão os detalhes do Toyota Corolla 2022:
- Preço: R$ 75.000
- Ano: 2022
- Combustível: Flex
- Transmissão: Automática
- Cor: Prata
- Quilometragem: 15.000 km
- Motor: 2.0L 16V
- Portas: 4

👤 Você: Obrigado!

🤖 Agente Virtual: De nada! Foi um prazer ajudar. Até a próxima! 👋
```

##### 7. Troubleshooting

**Problema: "LLM não disponível"**
```bash
# Verificar se Ollama está rodando
ollama list

# Iniciar Ollama se necessário
ollama serve
```

**Problema: "Erro na busca"**
```bash
# Verificar se o servidor está rodando
python manage.py runserver

# Verificar logs
tail -f log/2025-09-23_info.log
```

**Problema: "Nenhum carro encontrado"**
- Verifique se há dados no banco: `python manage.py populate_cars`
- Tente critérios mais amplos
- Use "ajuda" para ver preferências suportadas

### Desenvolvimento de Aplicações

Para começar a desenvolver a sua aplicação, você pode seguir os seguintes passos:

1. Defina os modelos em `models.py`, utilizando a classe `AbstractModel` como base.
2. Crie os serializers em `schema.py`, utilizando a classe `AbstractSchema` como base.
3. Crie as views em `views.py`, utilizando as classes `AbstractApi`, .
4. Crie os testes em `tests.py`, utilizando a classe `AbstractTest` como base.
5. (Opcional) Defina as configurações do admin em `admin.py`.

Comece criando um novo app com o comando `make startapp name=app_name`

## Comandos de Management

### População de Dados Fictícios

O projeto inclui um comando de management para popular o banco de dados com dados fictícios de veículos, otimizado para performance usando `bulk_create`.

#### Comando: `populate_cars`

```bash
python manage.py populate_cars [opções]
```

#### Opções Disponíveis

- `--count N`: Número de carros a serem criados (padrão: 100)
- `--clear`: Limpa todos os dados existentes antes de popular
- `--batch-size N`: Tamanho do lote para operações bulk_create (padrão: 1000)

#### Exemplos de Uso

##### Via Management Command

```bash
# Criar 100 carros (padrão)
python manage.py populate_cars

# Criar 500 carros
python manage.py populate_cars --count 500

# Limpar dados existentes e criar 1000 carros
python manage.py populate_cars --count 1000 --clear

# Criar 2000 carros com lotes de 500
python manage.py populate_cars --count 2000 --batch-size 500
```

##### Via Makefile (Recomendado)

```bash
# Criar 100 carros (padrão)
make populate-cars

# Criar quantidade específica
make populate-cars COUNT=500

# Limpar dados existentes e criar 500 carros
make populate-cars-clear COUNT=500

# Criar grande quantidade (1000+ carros)
make populate-cars-large

# Criar quantidade massiva (5000+ carros)
make populate-cars-huge
```

#### Dados Gerados

O comando cria dados realistas para:

- **Marcas**: 30 marcas populares (Toyota, Honda, Ford, etc.)
- **Cores**: 18 cores comuns de veículos
- **Motores**: 50 especificações de motor (cilindrada e potência)
- **Modelos**: 100 tipos de carroceria (Sedan, SUV, Hatchback, etc.)
- **Nomes de Carros**: 3-5 nomes por marca com anos (2015-2024)
- **Carros**: Dados completos com todas as especificações

#### Características de Performance

- **Bulk Create**: Usa `bulk_create()` para inserções em lote
- **Transações**: Todas as operações são executadas em uma transação
- **Lotes Configuráveis**: Permite ajustar o tamanho dos lotes
- **Dados Relacionais**: Mantém integridade referencial entre modelos
- **Progresso**: Exibe progresso durante a criação dos dados

#### Dados Realistas

- Anos de fabricação e modelo (2015-2024)
- Quilometragem (0-200.000 km)
- Preços realistas (R$ 10.000 - R$ 999.999)
- Tipos de combustível e transmissão
- Número de portas (2, 4 ou 5)
- Descrições em português brasileiro

# Funcionalidade WebSocket

O projeto inclui suporte completo a WebSocket para comunicação em tempo real entre cliente e servidor.

## Características

- **Identificação única de usuários**: Usuários anônimos recebem UUIDs persistentes via cookies
- **Salas baseadas em sessão**: Cada usuário (autenticado ou anônimo) tem sua própria sala
- **Protocolo V1**: Suporte ao protocolo WebSocket V1
- **Interface web**: Página dedicada para teste de conexões WebSocket
- **Logs detalhados**: Sistema de logging para debug e monitoramento

## Como Usar

### 1. Acessar a Interface WebSocket

1. Inicie o servidor com suporte a WebSocket:
   ```bash
   daphne config.asgi:application --port 8000 -v2
   ```

2. Acesse a página inicial do servidor: `http://127.0.0.1:8000/`

3. Na seção "Acesso Rápido", clique no botão "WebSocket"

4. A página de teste WebSocket será aberta com:
   - Botão de conexão/desconexão
   - Campo para envio de mensagens
   - Área de exibição de mensagens recebidas
   - Status da conexão e informações do usuário

### 2. Conectar via JavaScript

```javascript
// Conectar ao WebSocket
const socket = new WebSocket('ws://127.0.0.1:8000/site-example/ws/V1/general/', 'V1');

// Eventos
socket.onopen = function(event) {
    console.log('Conectado ao WebSocket');
};

socket.onmessage = function(event) {
    const data = JSON.parse(event.data);
    console.log('Mensagem recebida:', data);
};

socket.onclose = function(event) {
    console.log('Conexão fechada');
};

// Enviar mensagem
socket.send(JSON.stringify({
    type: 'message',
    data: 'Olá, WebSocket!'
}));
```

### 3. Estrutura das Salas

- **Usuários autenticados**: `user_{id}_{session_key}`
- **Usuários anônimos**: `anonymous_{anon_id}` (UUID persistente)
- **Fallback**: `general` (caso raro sem identificação)

### 4. Tipos de Mensagem

#### Echo (Resposta automática)
```json
{
    "type": "echo",
    "original_message": "mensagem original",
    "message_type": "message",
    "user": "AnonymousUser",
    "room": "anonymous_uuid",
    "timestamp": "2025-09-22 14:41:34.611560"
}
```

#### Broadcast (Para todos na sala)
```json
{
    "type": "broadcast",
    "message": "mensagem para todos",
    "user": "AnonymousUser",
    "room": "anonymous_uuid",
    "timestamp": "2025-09-22 14:41:34.611560"
}
```

### 5. Configuração Técnica

#### Middleware de Identificação Anônima
O `AnonymousIdMiddleware` gera automaticamente UUIDs únicos para usuários anônimos:

```python
# config/middleware.py
class AnonymousIdMiddleware(MiddlewareMixin):
    """Middleware que gera um UUID persistente para usuários anônimos."""
    
    def process_request(self, request):
        """Gera ou recupera o ID anônimo do usuário."""
        if "anon_id" not in request.COOKIES:
            request.anon_id = str(uuid.uuid4())
        else:
            request.anon_id = request.COOKIES["anon_id"]
```

#### Consumer WebSocket
```python
# apps/web_sockets/views_sockets.py
class GeneralSocket(AbstractMeetingSocket):
    """WebSocket consumer para sala geral."""
    current_protocol = 'V1'
```

### 6. Logs e Debug

O sistema gera logs detalhados para monitoramento:

```
DEBUG Usuário Anônimo (ID: a1b2c3d4) conectando na sala anonymous_a1b2c3d4-e5f6-7890-abcd-ef1234567890
DEBUG Usuário ID: 1 conectado na sala user_1_9z4a73k2xtoe38owsdxtqm8edegh61ic
DEBUG Mensagem recebida de AnonymousUser: Olá, WebSocket!
```

### 7. Dependências Necessárias

Certifique-se de ter as seguintes dependências instaladas:

```toml
# pyproject.toml
channels = "^4.0.0"
channels-redis = "^4.1.0"
daphne = "^4.0.0"
gunicorn = "^21.2.0"
uvicorn = "^0.24.0"
```

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
    
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    
    library_path = sysconfig.get_paths()['purelib']
    settings_path = path.join(library_path, 'config', 'settings.py')
    
    extend_settings(settings_path)
    
    from config.settings import *
    
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
    from config.settings import BASE_API_URL
    
    from config import urls as base_urls
    
    from config.settings import MEDIA_URL, MEDIA_ROOT
    
    
    urlpatterns = [
        path('', include(base_urls)),
        path('my_path', include('my_app.urls')),
    ]
    
    
    urlpatterns += static("/" + MEDIA_URL, document_root=MEDIA_ROOT)

`
