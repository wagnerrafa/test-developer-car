# Módulo Web Sockets

## Descrição

O módulo `web_sockets` é responsável por gerenciar a comunicação em tempo real dentro do sistema, utilizando a tecnologia de WebSockets para permitir interações instantâneas entre o cliente e o servidor.

### Modelos

- **WebSocketConnection**: Representa uma conexão WebSocket com propriedades como `user` e `status`.

  - **Campos**:
    - `user`: (`ForeignKey`) Referência para o usuário associado à conexão.
    - `status`: (`CharField`) Status da conexão WebSocket.

## Integração com Outros Módulos

O módulo `web_sockets` se integra com outros módulos fornecendo comunicação em tempo real que pode ser utilizada em notificações e atualizações ao vivo.

## Funcionalidades

O módulo `web_sockets` fornece uma API para gerenciar conexões WebSocket, permitindo que os usuários do sistema enviem e recebam mensagens em tempo real.

### Principais Funcionalidades:

1. **Gerenciamento de Conexões WebSocket**:
   - Permite estabelecer e gerenciar conexões WebSocket.
   - Suporta o envio e recebimento de mensagens em tempo real.

### Exemplo de Uso da API

#### Listar todas as conexões WebSocket:

```bash
GET /api/v1/websockets/
```

- **Resposta**: Retorna um JSON com a lista de conexões WebSocket, incluindo campos como `id`, `user`, `status`, entre outros.
  ```json
  {
    "count": 2,
    "next": null,
    "previous": null,
    "results": [
      {
        "id": 1,
        "user": "user1",
        "status": "Ativa"
      },
      {
        "id": 2,
        "user": "user2",
        "status": "Inativa"
      }
    ]
  }
  ```

#### Criar uma nova conexão WebSocket:

```bash
POST /api/v1/websockets/
```

- **Corpo da Requisição**: JSON com os detalhes da conexão.
  ```json
  {
    "user": "user3",
    "status": "Ativa"
  }
  ```

- **Resposta**: Retorna um JSON com os detalhes da conexão criada, incluindo o `id` da conexão e outros campos preenchidos.
  ```json
  {
    "id": 3,
    "user": "user3",
    "status": "Ativa"
  }
  ```

## Uso do Módulo

Para utilizar o módulo `web_sockets`, é necessário que o usuário tenha permissões adequadas para estabelecer conexões WebSocket. As rotas permitem gerenciar conexões com base em IDs específicos, facilitando a comunicação em tempo real no sistema.

- **Filtros Disponíveis**: Você pode aplicar os seguintes filtros na listagem de conexões WebSocket:
  - `user`: Filtrar por usuário associado à conexão.
  - `status`: Filtrar por status da conexão.

- **Exemplo de Uso com Filtros**:

```bash
GET /api/v1/websockets/?status=Ativa&limit=10&offset=0
```

- **Resposta**: Retorna um JSON com a lista de conexões WebSocket filtradas pelo status 'Ativa', limitado a 10 resultados por página. 