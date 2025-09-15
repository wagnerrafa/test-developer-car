# Sistema de Permissões Baseado em Grupos

Este documento descreve o sistema de permissões baseado em grupos implementado no framework Site Example Django.

## Visão Geral

O sistema substitui os campos booleanos `has_rh_perm` e `has_clb_perm` por properties que verificam a pertinência a grupos específicos, além de adicionar suporte para os grupos INTRA e INTEGRATOR. Isso permite uma gestão mais flexível e granular das permissões.

## Grupos Padrão

O sistema define quatro grupos padrão:

1. **RH**: Permissões para recursos humanos
2. **CLB**: Permissões para colaboradores
3. **INTRA**: Permissões para intranet
4. **INTEGRATOR**: Permissões para integradores

## Properties no Modelo BaseUser

As seguintes properties foram adicionadas ao modelo `BaseUser`:

- `has_rh_perm_group`: Verifica se o usuário pertence ao grupo RH
- `has_clb_perm_group`: Verifica se o usuário pertence ao grupo CLB
- `has_intra_perm`: Verifica se o usuário pertence ao grupo INTRA
- `has_integrator_perm`: Verifica se o usuário pertence ao grupo INTEGRATOR

Os campos booleanos originais `has_rh_perm` e `has_clb_perm` foram mantidos para compatibilidade com código existente.

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

## Comandos de Gerenciamento

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
   - Selecionar um grupo (RH, CLB, INTRA, INTEGRATOR)
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

## Classe GroupPermissionManager

A classe `GroupPermissionManager` em `drf_base_apps.core.abstract.permissions` fornece uma API para gerenciar permissões programaticamente:

```python
from drf_base_apps.core.abstract.permissions import GroupPermissionManager

# Inicializar gerenciador
manager = GroupPermissionManager()

# Definir permissões para um grupo e app
manager.set_group_permissions('RH', 'drf_base_user', {
    'create': True,
    'read': True,
    'update': True,
    'delete': False
})

# Exportar configuração atual
config = manager.export_current_permissions()

# Salvar configuração em arquivo
manager.save_config('permissions.json')
```

## Migração de Código Existente

Para código que utiliza os campos booleanos originais, recomenda-se migrar para as novas properties:

```python
# Antes
if user.has_rh_perm:
    # ...

# Depois
if user.has_rh_perm_group:
    # ...
```

Os campos booleanos originais continuarão funcionando, mas não refletirão a pertinência aos grupos.
