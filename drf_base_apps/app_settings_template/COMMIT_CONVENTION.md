# Convenção de Commits com Commitizen

Este projeto utiliza o **Commitizen** para padronizar os commits de forma interativa e amigável.

## 🚀 Como Usar

### Método Interativo (Recomendado)

```bash
# Adicionar arquivos e fazer commit interativo
make commit-all

# Ou apenas fazer commit interativo (arquivos já devem estar no staging)
make commit

# Ou usar diretamente
poetry run cz commit
```

### O que acontece:

1. **Menu de seleção do tipo** aparece automaticamente
2. **Digite o escopo** (opcional)
3. **Digite a descrição** da mudança
4. **Commit é criado** automaticamente no formato correto

## 🔒 Validação Automática

**⚠️ IMPORTANTE:** Commits manuais que não seguem o padrão serão **rejeitados automaticamente**.

### ✅ Commits Válidos:
```bash
git commit -m "feat: adiciona nova funcionalidade"
git commit -m "fix(auth): corrige erro de login"
git commit -m "docs: atualiza README"
```

### ❌ Commits Inválidos (serão rejeitados):
```bash
git commit -m "workflow poetry check"           # ❌ Sem tipo
git commit -m "adiciona funcionalidade"         # ❌ Sem tipo
git commit -m "update: corrige bug"             # ❌ Tipo inválido
git commit -m "feat: mensagem muito longa que excede o limite de 72 caracteres"  # ❌ Muito longo
```

### 🔧 Solução para commits rejeitados:
```bash
# Use o menu interativo
make commit-all

# Ou corrija a mensagem manualmente
git commit -m "chore: workflow poetry check"
```

## 📋 Tipos de Commit Disponíveis

- **feat**: Nova funcionalidade
- **fix**: Correção de bug
- **docs**: Alterações na documentação
- **style**: Alterações que não afetam o código (espaços, formatação, etc.)
- **refactor**: Refatoração de código
- **perf**: Melhorias de performance
- **test**: Adicionando ou corrigindo testes
- **chore**: Alterações em arquivos de build, configurações, etc.
- **ci**: Alterações em arquivos de CI/CD
- **revert**: Reverte um commit anterior
- **build**: Alterações que afetam o sistema de build
- **wip**: Work in progress
- **hotfix**: Correções urgentes
- **feature**: Sinônimo para feat
- **bugfix**: Sinônimo para fix

## 🎯 Exemplos de Uso

### Exemplo 1: Nova funcionalidade
```bash
make commit-all
# Menu aparece:
# ? Selecione o tipo de mudança: 
# ❯ feat: Nova funcionalidade
#   fix: Correção de bug
#   docs: Documentação
#   ...

# Você seleciona "feat"
# ? Escopo (opcional, ex: auth, cards, api): auth
# ? Descrição da mudança (máximo 72 caracteres): implementa login com Google OAuth

# Resultado: feat(auth): implementa login com Google OAuth
```

### Exemplo 2: Correção de bug
```bash
make commit-all
# ? Selecione o tipo de mudança: fix
# ? Escopo (opcional, ex: auth, cards, api): cards
# ? Descrição da mudança (máximo 72 caracteres): corrige validação de número de cartão

# Resultado: fix(cards): corrige validação de número de cartão
```

### Exemplo 3: Sem escopo
```bash
make commit-all
# ? Selecione o tipo de mudança: docs
# ? Escopo (opcional, ex: auth, cards, api): [Enter]
# ? Descrição da mudança (máximo 72 caracteres): atualiza README

# Resultado: docs: atualiza README
```

## ⚙️ Configuração

### Instalação

```bash
make install-pre-commit
```

### Comandos Disponíveis

```bash
# Instalar pre-commit e commitizen
make install-pre-commit

# Fazer commit interativo
make commit

# Adicionar todos os arquivos e fazer commit interativo
make commit-all

# Executar pre-commit em todos os arquivos
make pre-commit-run

# Atualizar hooks do pre-commit
make pre-commit-update
```

## 🔧 Configuração Avançada

A configuração do commitizen está no arquivo `.commitizen.toml`:

```toml
[tool.commitizen]
name = "cz_conventional_commits"
version = "0.1.0"
tag_format = "v$version"

[tool.commitizen.customize]
message_template = "{{change_type}}{{scope}}: {{message}}"
schema = "<type>(<scope>): <subject>"
```

## 💡 Dicas

- **Use sempre o menu interativo** para garantir consistência
- **Escopo é opcional** - deixe vazio se não for necessário
- **Descrição deve ser clara e concisa** (máximo 72 caracteres)
- **Mantenha as mensagens em português** para consistência
- **Use 'wip'** para commits temporários de trabalho em andamento
- **Se um commit for rejeitado**, use `make commit-all` para o menu interativo

## 🚫 Commits Manuais

Se precisar fazer um commit manual, **deve seguir o padrão**:

```bash
git commit -m "feat: nova funcionalidade"
git commit -m "fix(auth): corrige erro de login"
git commit -m "chore: atualiza dependências"
```

## 📚 Recursos Adicionais

- [Conventional Commits](https://www.conventionalcommits.org/)
- [Commitizen](https://commitizen-tools.github.io/commitizen/)
- [Pre-commit](https://pre-commit.com/) 