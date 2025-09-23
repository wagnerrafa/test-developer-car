# Guia do Protocolo MCP via WebSocket

## Visão Geral

O Protocolo MCP (Model Context Protocol) via WebSocket foi implementado para fornecer busca dinâmica de carros em tempo real, mantendo compatibilidade com a infraestrutura existente e adicionando capacidades avançadas de filtros e comunicação bidirecional.

## Arquitetura

```
Cliente → WebSocket MCP → API REST → Banco de Dados
```

### Componentes Principais

1. **Schemas MCP** (`mcp_schemas.py`): Definições de dados e validações
2. **Handlers MCP** (`mcp_handlers.py`): Lógica de processamento das requisições
3. **Consumer WebSocket** (`mcp_consumer.py`): Interface WebSocket para comunicação
4. **Integração REST** (`mcp_rest_integration.py`): Reutilização das APIs existentes
5. **Testes** (`tests_mcp.py`): Cobertura de testes completa

## Endpoints WebSocket

### MCP V1
- **URL**: `/app/ws/V1/mcp/cars/`
- **Protocolo**: `MCP-V1`
- **Funcionalidades**: Busca básica, filtros, paginação

### MCP V2
- **URL**: `/app/ws/V1/mcp/cars/v2/`
- **Protocolo**: `MCP-V2`
- **Funcionalidades**: Todas do V1 + métricas, histórico persistente, sugestões

## Ações Suportadas

### 1. `search_cars`
Busca carros com filtros dinâmicos.

**Requisição:**
```json
{
  "type": "mcp_request",
  "request_id": "req_123",
  "data": {
    "action": "search_cars",
    "filters": {
      "brand_name": "Toyota",
      "year_manufacture_min": 2020,
      "year_manufacture_max": 2023,
      "price_min": 50000.0,
      "price_max": 100000.0,
      "fuel_type": "flex",
      "transmission": "automatic",
      "search": "corolla"
    },
    "pagination": {
      "page": 1,
      "page_size": 20,
      "ordering": "-created_at"
    }
  }
}
```

**Resposta:**
```json
{
  "type": "mcp_response",
  "request_id": "req_123",
  "success": true,
  "data": {
    "results": [
      {
        "id": "123e4567-e89b-12d3-a456-426614174000",
        "car_name": "Corolla",
        "brand": "Toyota",
        "car_model": "Sedan",
        "year_manufacture": 2023,
        "year_model": 2024,
        "engine": "1.6 Flex (1.6)",
        "fuel_type": "flex",
        "color": "Branco",
        "mileage": 15000,
        "doors": 4,
        "transmission": "automatic",
        "price": 120000.0,
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z"
      }
    ],
    "total": 150,
    "page": 1,
    "page_size": 20,
    "total_pages": 8
  },
  "timestamp": "2024-01-01T00:00:00Z"
}
```

### 2. `get_brands`
Obtém marcas disponíveis com contagem de carros.

**Requisição:**
```json
{
  "type": "mcp_request",
  "request_id": "req_124",
  "data": {
    "action": "get_brands"
  }
}
```

**Resposta:**
```json
{
  "type": "mcp_response",
  "request_id": "req_124",
  "success": true,
  "data": {
    "brands": [
      {
        "id": "456e7890-e89b-12d3-a456-426614174001",
        "name": "Toyota",
        "count": 25
      },
      {
        "id": "789e0123-e89b-12d3-a456-426614174002",
        "name": "Honda",
        "count": 18
      }
    ]
  },
  "timestamp": "2024-01-01T00:00:00Z"
}
```

### 3. `get_colors`
Obtém cores disponíveis com contagem de carros.

**Requisição:**
```json
{
  "type": "mcp_request",
  "request_id": "req_125",
  "data": {
    "action": "get_colors"
  }
}
```

### 4. `get_engines`
Obtém motores disponíveis com contagem de carros.

**Requisição:**
```json
{
  "type": "mcp_request",
  "request_id": "req_126",
  "data": {
    "action": "get_engines"
  }
}
```

### 5. `get_car_details`
Obtém detalhes de um carro específico.

**Requisição:**
```json
{
  "type": "mcp_request",
  "request_id": "req_127",
  "data": {
    "action": "get_car_details",
    "car_id": "123e4567-e89b-12d3-a456-426614174000"
  }
}
```

### 6. `get_filters_options`
Obtém opções disponíveis para filtros.

**Requisição:**
```json
{
  "type": "mcp_request",
  "request_id": "req_128",
  "data": {
    "action": "get_filters_options"
  }
}
```

**Resposta:**
```json
{
  "type": "mcp_response",
  "request_id": "req_128",
  "success": true,
  "data": {
    "filters_options": {
      "fuel_types": ["flex", "gasoline", "diesel", "electric"],
      "transmissions": ["automatic", "manual", "cvt"],
      "year_range": {
        "min_manufacture": 2020,
        "max_manufacture": 2024,
        "min_model": 2021,
        "max_model": 2024
      },
      "price_range": {
        "min": 25000.0,
        "max": 200000.0
      },
      "mileage_range": {
        "min": 0,
        "max": 100000
      },
      "doors_range": {
        "min": 2,
        "max": 8
      }
    }
  },
  "timestamp": "2024-01-01T00:00:00Z"
}
```

## Filtros Disponíveis

### Filtros de Relacionamento
- `brand_id` / `brand_name`: Filtro por marca
- `color_id` / `color_name`: Filtro por cor
- `engine_id` / `engine_name`: Filtro por motor
- `car_model_id` / `car_model_name`: Filtro por modelo
- `car_name_id` / `car_name`: Filtro por nome do carro

### Filtros Numéricos
- `year_manufacture_min` / `year_manufacture_max`: Ano de fabricação
- `year_model_min` / `year_model_max`: Ano do modelo
- `mileage_min` / `mileage_max`: Quilometragem
- `doors_min` / `doors_max`: Número de portas
- `price_min` / `price_max`: Preço

### Filtros de Escolha
- `fuel_type`: Tipo de combustível
- `transmission`: Tipo de transmissão

### Busca Textual
- `search`: Busca geral em nome, marca, modelo, cor e motor

## Paginação

```json
{
  "pagination": {
    "page": 1,           // Página atual (padrão: 1)
    "page_size": 20,     // Itens por página (padrão: 20, máx: 100)
    "ordering": "-created_at"  // Campo de ordenação (padrão: -created_at)
  }
}
```

### Campos de Ordenação Disponíveis
- `created_at` / `-created_at`: Data de criação
- `price` / `-price`: Preço
- `year_manufacture` / `-year_manufacture`: Ano de fabricação
- `year_model` / `-year_model`: Ano do modelo
- `mileage` / `-mileage`: Quilometragem

## Exemplo de Cliente JavaScript

```javascript
class MCPCarClient {
    constructor(url) {
        this.url = url;
        this.ws = null;
        this.requestId = 0;
    }
    
    connect() {
        return new Promise((resolve, reject) => {
            this.ws = new WebSocket(this.url, 'MCP-V1');
            
            this.ws.onopen = () => {
                console.log('Conectado ao MCP WebSocket');
                resolve();
            };
            
            this.ws.onmessage = (event) => {
                const data = JSON.parse(event.data);
                this.handleMessage(data);
            };
            
            this.ws.onerror = (error) => {
                console.error('Erro WebSocket:', error);
                reject(error);
            };
        });
    }
    
    handleMessage(data) {
        switch(data.type) {
            case 'mcp_welcome':
                console.log('Bem-vindo ao MCP:', data.message);
                break;
            case 'mcp_response':
                this.handleResponse(data);
                break;
            case 'mcp_error':
                console.error('Erro MCP:', data.error);
                break;
        }
    }
    
    handleResponse(data) {
        // Processar resposta baseada no request_id
        console.log('Resposta MCP:', data);
    }
    
    sendRequest(action, data = {}) {
        const request = {
            type: 'mcp_request',
            request_id: `req_${++this.requestId}`,
            data: {
                action: action,
                ...data
            }
        };
        
        this.ws.send(JSON.stringify(request));
    }
    
    searchCars(filters = {}, pagination = {}) {
        this.sendRequest('search_cars', { filters, pagination });
    }
    
    getBrands() {
        this.sendRequest('get_brands');
    }
    
    getColors() {
        this.sendRequest('get_colors');
    }
    
    getEngines() {
        this.sendRequest('get_engines');
    }
    
    getCarDetails(carId) {
        this.sendRequest('get_car_details', { car_id: carId });
    }
    
    getFiltersOptions() {
        this.sendRequest('get_filters_options');
    }
}

// Uso
const client = new MCPCarClient('ws://localhost:8000/app/ws/V1/mcp/cars/');

client.connect().then(() => {
    // Buscar carros Toyota com filtros
    client.searchCars({
        brand_name: 'Toyota',
        year_manufacture_min: 2020,
        price_max: 100000
    }, {
        page: 1,
        page_size: 10,
        ordering: '-price'
    });
    
    // Obter marcas disponíveis
    client.getBrands();
    
    // Obter opções de filtros
    client.getFiltersOptions();
});
```

## Exemplo de Cliente Python

```python
import asyncio
import json
import websockets

class MCPCarClient:
    def __init__(self, url):
        self.url = url
        self.websocket = None
        self.request_id = 0
    
    async def connect(self):
        self.websocket = await websockets.connect(
            self.url, 
            subprotocols=['MCP-V1']
        )
        print("Conectado ao MCP WebSocket")
    
    async def send_request(self, action, data=None):
        self.request_id += 1
        request = {
            "type": "mcp_request",
            "request_id": f"req_{self.request_id}",
            "data": {
                "action": action,
                **(data or {})
            }
        }
        
        await self.websocket.send(json.dumps(request))
        response = await self.websocket.recv()
        return json.loads(response)
    
    async def search_cars(self, filters=None, pagination=None):
        return await self.send_request('search_cars', {
            'filters': filters or {},
            'pagination': pagination or {}
        })
    
    async def get_brands(self):
        return await self.send_request('get_brands')
    
    async def get_colors(self):
        return await self.send_request('get_colors')
    
    async def get_engines(self):
        return await self.send_request('get_engines')
    
    async def get_car_details(self, car_id):
        return await self.send_request('get_car_details', {'car_id': car_id})
    
    async def get_filters_options(self):
        return await self.send_request('get_filters_options')
    
    async def close(self):
        await self.websocket.close()

# Uso
async def main():
    client = MCPCarClient('ws://localhost:8000/app/ws/V1/mcp/cars/')
    
    try:
        await client.connect()
        
        # Buscar carros
        response = await client.search_cars(
            filters={
                'brand_name': 'Toyota',
                'year_manufacture_min': 2020,
                'price_max': 100000
            },
            pagination={
                'page': 1,
                'page_size': 10,
                'ordering': '-price'
            }
        )
        
        print("Resultados da busca:", response)
        
        # Obter marcas
        brands = await client.get_brands()
        print("Marcas disponíveis:", brands)
        
    finally:
        await client.close()

# Executar
asyncio.run(main())
```

## Tratamento de Erros

### Códigos de Erro Comuns

- `INVALID_JSON`: JSON inválido na requisição
- `UNSUPPORTED_ACTION`: Ação não suportada
- `MISSING_CAR_ID`: ID do carro obrigatório para get_car_details
- `CAR_NOT_FOUND`: Carro não encontrado
- `SEARCH_ERROR`: Erro na busca de carros
- `BRANDS_ERROR`: Erro ao obter marcas
- `COLORS_ERROR`: Erro ao obter cores
- `ENGINES_ERROR`: Erro ao obter motores
- `CAR_DETAILS_ERROR`: Erro ao obter detalhes do carro
- `FILTERS_OPTIONS_ERROR`: Erro ao obter opções de filtros
- `INTERNAL_ERROR`: Erro interno do servidor

### Exemplo de Resposta de Erro

```json
{
  "type": "mcp_error",
  "request_id": "req_123",
  "error": "Carro não encontrado",
  "error_code": "CAR_NOT_FOUND",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

## Funcionalidades V2 (MCP V2)

### Métricas de Uso
```javascript
// Solicitar métricas da sessão
client.sendRequest('get_metrics');
```

### Histórico de Buscas
```javascript
// Obter histórico de buscas
client.sendRequest('get_search_history');

// Limpar histórico
client.sendRequest('clear_search_history');
```

## Testes

### Executar Testes Unitários
```bash
python manage.py test apps.web_sockets.tests_mcp
```

### Executar Testes de Performance
```bash
python manage.py test apps.web_sockets.tests_mcp.MCPPerformanceTestCase
```

### Executar Testes WebSocket
```bash
pytest apps/web_sockets/tests_mcp.py::MCPWebSocketTestCase -v
```

## Configuração

### Variáveis de Ambiente
```bash
# Redis para WebSockets
REDIS_URL=redis://localhost:6379/6

# Configurações MCP
MCP_ENABLE_V2=true
MCP_MAX_SEARCH_HISTORY=50
MCP_DEFAULT_PAGE_SIZE=20
MCP_MAX_PAGE_SIZE=100
```

### Settings Django
```python
# config/settings.py

# WebSocket MCP
MCP_SETTINGS = {
    'ENABLE_V2': True,
    'MAX_SEARCH_HISTORY': 50,
    'DEFAULT_PAGE_SIZE': 20,
    'MAX_PAGE_SIZE': 100,
    'CACHE_TIMEOUT': 300,  # 5 minutos
}
```

## Monitoramento

### Logs
Os logs do MCP são registrados com o logger `apps.web_sockets.mcp_*`:

```python
import logging

# Configurar nível de log
logging.getLogger('apps.web_sockets.mcp_handlers').setLevel(logging.DEBUG)
logging.getLogger('apps.web_sockets.mcp_consumer').setLevel(logging.INFO)
```

### Métricas
- Total de requisições por sessão
- Taxa de sucesso
- Tempo de resposta
- Histórico de buscas

## Compatibilidade

### WebSockets Existentes
- Mantém compatibilidade total com WebSockets V1 existentes
- Não afeta funcionalidades atuais
- Adiciona novas rotas sem conflitos

### API REST
- Reutiliza todas as validações existentes
- Mantém permissões e autenticação
- Preserva serializers e views atuais

## Troubleshooting

### Problemas Comuns

1. **Conexão WebSocket falha**
   - Verificar se Redis está rodando
   - Verificar configuração de CHANNEL_LAYERS
   - Verificar logs do servidor

2. **Requisições MCP não respondem**
   - Verificar formato JSON da requisição
   - Verificar se a ação é suportada
   - Verificar logs de erro

3. **Performance lenta**
   - Verificar índices do banco de dados
   - Verificar configuração do Redis
   - Executar testes de performance

### Debug
```python
# Habilitar debug MCP
import logging
logging.getLogger('apps.web_sockets').setLevel(logging.DEBUG)
```

## Roadmap

### Próximas Funcionalidades
- [ ] Cache Redis para resultados de busca
- [ ] Notificações em tempo real para novos carros
- [ ] Autocomplete inteligente para filtros
- [ ] Exportação de resultados de busca
- [ ] Dashboard de métricas em tempo real
- [ ] Suporte a múltiplas sessões por usuário
- [ ] Compressão de dados para WebSocket
- [ ] Rate limiting por usuário
