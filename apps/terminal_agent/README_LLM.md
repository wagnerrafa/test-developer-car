# Arquitetura de LLM Desacoplada

Este documento descreve a nova arquitetura desacoplada para provedores de LLM no agente virtual de carros.

## Visão Geral

A arquitetura foi refatorada para permitir fácil troca entre diferentes provedores de LLM, melhorando a flexibilidade e performance do sistema.

## Componentes

### 1. Interface Abstrata (`llm_interface.py`)
Define o contrato que todos os provedores LLM devem implementar:
- `is_available()`: Verifica disponibilidade
- `generate_response()`: Gera respostas
- `extract_car_preferences()`: Extrai preferências
- `generate_car_search_filters()`: Gera filtros
- `format_car_results()`: Formata resultados
- `generate_next_question()`: Gera perguntas

**Prompts Centralizados:**
- `LLMPrompts`: Classe com todos os prompts padronizados
- `get_*_prompt()`: Métodos para obter prompts específicos
- `get_generation_config()`: Configurações de geração por tarefa
- `get_question_template()`: Templates de perguntas padronizadas

### 2. Classe Base (`llm_base.py`)
Funcionalidades comuns reutilizáveis:
- Extração de JSON robusta
- Formatação de carros
- Simplificação de dados

### 3. Implementações

#### SimpleLLM (`simple_llm.py`)
- **Vantagens**: Muito rápido, sem dependências externas
- **Uso**: Desenvolvimento, testes, fallback
- **Performance**: Instantânea

#### OllamaClient (`ollama_client.py`)
- **Vantagens**: Modelos locais poderosos
- **Uso**: Produção com modelos avançados
- **Performance**: Depende do modelo escolhido

### 4. Factory (`llm_factory.py`)
Criação centralizada de provedores:
```python
# Criação automática (recomendado)
llm = LLMFactory.create_auto_llm()

# Criação específica
llm = LLMFactory.create_llm("simple")
llm = LLMFactory.create_llm("ollama", model="llama3.1:8b")
```

### 5. Configuração (`llm_config.py`)
Configurações centralizadas:
```python
# Variável de ambiente
export LLM_PROVIDER=simple  # ou ollama, auto
```

## Prompts Centralizados

### Vantagens dos Prompts Centralizados
- ✅ **Consistência**: Todos os LLMs usam os mesmos prompts
- ✅ **Manutenção**: Mudanças em um local afetam todos os LLMs
- ✅ **Padronização**: Comportamento uniforme entre implementações
- ✅ **Configuração**: Parâmetros de geração otimizados por tarefa

### Estrutura dos Prompts
```python
# Prompts por tarefa
LLMPrompts.EXTRACT_PREFERENCES_SYSTEM  # Extração de preferências
LLMPrompts.GENERATE_FILTERS_SYSTEM     # Geração de filtros
LLMPrompts.FORMAT_RESULTS_SYSTEM       # Formatação de resultados
LLMPrompts.GENERATE_QUESTION_SYSTEM    # Geração de perguntas

# Templates de perguntas
LLMPrompts.QUESTION_TEMPLATES          # Templates por tipo de informação

# Configurações de geração
LLMPrompts.GENERATION_CONFIGS          # Temperature e max_tokens por tarefa
```

### Uso nos LLMs
```python
# Obter prompt e configuração
system_prompt, prompt = self.get_extract_preferences_prompt(user_input)
config = self.get_generation_config("extract_preferences")

# Usar na geração
response = self.generate_response(
    prompt=prompt,
    system_prompt=system_prompt,
    temperature=config["temperature"],
    max_tokens=config["max_tokens"]
)
```

## Como Usar

### Uso Básico
```python
from apps.terminal_agent.llm_factory import LLMFactory

# Criação automática (tenta Ollama, fallback para Simple)
llm = LLMFactory.create_auto_llm()

# Verificar disponibilidade
if llm.is_available():
    response = llm.generate_response("Olá!")
```

### Uso Específico
```python
# Forçar uso do SimpleLLM (mais rápido)
llm = LLMFactory.create_llm("simple")

# Usar Ollama com configuração específica
llm = LLMFactory.create_llm("ollama", 
                           base_url="http://localhost:11434",
                           model="llama3.1:8b")
```

## Adicionando Novos Provedores

1. **Criar implementação**:
```python
from .llm_interface import LLMInterface
from .llm_base import LLMBase

class MeuLLM(LLMInterface, LLMBase):
    def is_available(self) -> bool:
        return True
    
    def generate_response(self, prompt: str, **kwargs) -> str:
        # Implementar lógica específica
        pass
    
    # Implementar outros métodos...
```

2. **Registrar no Factory**:
```python
from .llm_factory import LLMFactory
from .meu_llm import MeuLLM

LLMFactory.register_provider("meu_llm", MeuLLM)
```

3. **Usar**:
```python
llm = LLMFactory.create_llm("meu_llm")
```

## Performance

| Provedor | Velocidade | Qualidade | Dependências |
|----------|------------|-----------|--------------|
| SimpleLLM | ⚡⚡⚡ | ⭐⭐ | Nenhuma |
| OllamaClient | ⚡ | ⭐⭐⭐⭐⭐ | Ollama |

## Configuração de Ambiente

```bash
# Usar SimpleLLM (mais rápido)
export LLM_PROVIDER=simple

# Usar Ollama (mais inteligente)
export LLM_PROVIDER=ollama

# Seleção automática (padrão)
export LLM_PROVIDER=auto
```

## Troubleshooting

### SimpleLLM não funciona
- Verifique se não há erros de sintaxe
- SimpleLLM sempre deve estar disponível

### OllamaClient não funciona
- Verifique se Ollama está rodando: `docker ps | grep ollama`
- Inicie Ollama: `docker-compose -f docker-compose.ollama.yml up -d`
- Verifique logs: `docker logs base_tests_ollama`

### Performance lenta
- Use SimpleLLM para desenvolvimento
- Configure timeout menor no Ollama
- Verifique recursos do sistema
