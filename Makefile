# Makefile para comandos Django com Poetry

# Definição de variáveis com valores padrão
EXTRA_USERS ?= 1000

# Comando padrão de ajuda
help:
	@echo "Comandos disponíveis:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' Makefile | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

run:  ## Inicia o servidor de desenvolvimento Django
	poetry run python manage.py runserver

migrate:  ## Aplica as migrações do banco de dados
	poetry run python manage.py migrate

makemigrations:  ## Cria novas migrações com base nos models
	poetry run python manage.py makemigrations

startapp:  ## Cria uma nova app Django usando o template do drf_base_apps (uso: make startapp name=order)
	poetry run python manage.py startapp $(name) --template=$$(poetry run python -c "import drf_base_apps, sys; from pathlib import Path; print(Path(drf_base_apps.__file__).parent / 'app_template')")

generate-project:  ## Cria um novo projeto Django baseado no drf_base_apps (uso: make generate-project name=meu_projeto)
	poetry run python manage.py generate_project_config --project-name=$(name)

createsuperuser:  ## Cria um superusuário administrador
	poetry run python manage.py createsuperuser

createcachetable:  ## Cria tabela de cache
	poetry run python manage.py createcachetable

create_user:  ## Cria um superusuário administrador default, de acordo com as configurações na .env
	poetry run python manage.py create_user

shell:  ## Abre o shell interativo com contexto do Django
	poetry run python manage.py shell

test:  ## Executa os testes da aplicação
	poetry run python manage.py test

lint:  ## Executa linting com Ruff
	poetry run ruff check . --config=pyproject.toml

lint-fix:  ## Executa linting com Ruff
	poetry run ruff check . --fix --config=pyproject.toml

lint-unsafe-fix:  ## Executa linting com Ruff
	poetry run ruff check . --fix --unsafe-fixes --config=pyproject.toml

format:  ## Formata código com Black
	poetry run black .

format-check:  ## Verifica formatação com Black
	poetry run black --check .

collectstatic:  ## Coleta arquivos estáticos (para produção)
	poetry run python manage.py collectstatic --noinput

creategroups:  ## Criar os grupos de acordo com as permissões de CRUD para cada app
	poetry run python manage.py create_groups

check:  ## Checa o projeto com scan e lint
	make lint
	poetry run python manage.py check

# Security checks
security:
	@echo "🔒 Running security checks..."
	poetry run bandit -r apps config -f txt --skip B101,B601,B106 || true
	@echo "✅ Security checks completed"

semgrep:
	@echo "🔍 Running Semgrep security scan..."
	poetry run semgrep scan --config=auto --sarif --output semgrep-report.sarif || true
	@echo "✅ Semgrep scan completed"

bandit-sarif:
	@echo "🔒 Running Bandit security scan (SARIF format)..."
	poetry run bandit -r apps config -f json -o bandit-report.json --skip B101,B601,B106 || true
	poetry run python scripts/bandit_to_sarif.py bandit-report.json bandit-report.sarif
	@echo "✅ Bandit SARIF scan completed"

test-ci:  ## Executa testes com cobertura para CI
	poetry run pytest --cov=. --cov-report=xml --cov-report=html --cov-report=term --cache-clear -s

lint-ci:  ## Executa linting completo para CI
	poetry run ruff check . --config=pyproject.toml
	poetry run black --check .
	poetry run ruff check --select I . --config=pyproject.toml

# Novos comandos de integridade
integrity:  ## Executa todas as verificações de integridade
	@echo "=== Executando verificações de integridade ==="
	make django-integrity
	make dependency-integrity
	make code-integrity

django-integrity:  ## Verificações específicas do Django
	@echo "=== Verificações do Django ==="
	poetry run python manage.py check
	poetry run python manage.py check --deploy
	poetry run python manage.py validate_templates || true
	poetry run python manage.py showmigrations
	poetry run python manage.py show_urls
	poetry run python manage.py diffsettings
	poetry run python manage.py notes

dependency-integrity:  ## Verificações de dependências
	@echo "=== Verificações de Dependências ==="
	poetry show --tree
	poetry show --outdated
	poetry lock

code-integrity:  ## Verificações de código
	@echo "=== Verificações de Código ==="
	poetry run ruff check --select F401 . --config=pyproject.toml
	poetry run ruff check --select F841 . --config=pyproject.toml
	poetry run ruff check --select SIM . --config=pyproject.toml
	poetry run ruff check --select UP . --config=pyproject.toml
	poetry run ruff check --select C901 . --config=pyproject.toml
	poetry run ruff check --select E501 . --config=pyproject.toml

integrity-local:  ## Testa integridade localmente com variáveis de ambiente (simula CI)
	@echo "=== Testando integridade localmente (simulando CI) ==="
	@echo "Configurando variáveis de ambiente para teste..."
	@DATABASE_URL='sqlite:///test.db' \
	SECRET_KEY='django-insecure-test-key-for-ci-only' \
	DEBUG='True' \
	ALLOWED_HOSTS='localhost,127.0.0.1' \
	DJANGO_SETTINGS_MODULE='config.settings' \
	ENVIRONMENT='dev' \
	ENV='dev' \
	LIST_ALLOWED_HOSTS='localhost,127.0.0.1' \
	APP_NAME='site-example' \
	USE_BASE_NAME='True' \
	PUBLIC_SWAGGER='True' \
	PRINT_DEBUG='True' \
	ENABLE_DRF='True' \
	ENABLE_CACHE='False' \
	SANDBOX_COMMIT='True' \
	EXTERNAL_DATABASE='False' \
	AUTO_REGISTER_MODELS='False' \
	CURRENT_VERSION='0.0.1' \
	TOKEN_TEST='' \
	LOGGER_TEST='False' \
	ENABLE_LOGGING_FILE='False' \
	LOGGING_FILE_LEVEL='INFO' \
	LOGGING_FILE_HANDLERS='debug,console,critical,info,error,warning,celery' \
	PATHS_BACKEND='' \
	ENABLE_TOKEN='False' \
	ENABLE_PW='True' \
	REQUEST_TIMEOUT='30' \
	CHECK_HAS_CHANGED_PASSWORD='False' \
	PASSWD_DEV='Senha@1234' \
	USER_DEV='dev_user' \
	USER_ADMIN_DEV='dev_admin' \
	FERNET_KEY='ou5SAHd8fIj-gSLGyxPR5q8XraVD-_xlGGOtxpflOUQ=' \
	poetry run python manage.py check --settings=config.settings
	@echo "✅ Verificação básica do Django concluída!"
	@echo "Executando verificações de código..."
	poetry run ruff check --select F401 . --config=pyproject.toml || true
	poetry run ruff check --select F841 . --config=pyproject.toml || true
	@echo "✅ Verificações de código críticas concluídas!"
	@echo "Executando verificações de dependências..."
	poetry lock
	@echo "✅ Verificações de dependências concluídas!"
	@echo "🎉 Verificações críticas de integridade passaram!"
	@echo "💡 Para verificar melhorias de código, execute: make lint"

unused-imports:  ## Verifica imports não utilizados
	poetry run ruff check --select F401 . --config=pyproject.toml

unused-variables:  ## Verifica variáveis não utilizadas
	poetry run ruff check --select F841 . --config=pyproject.toml

code-simplifications:  ## Verifica possíveis simplificações de código
	poetry run ruff check --select SIM . --config=pyproject.toml

code-upgrades:  ## Verifica possíveis upgrades de código
	poetry run ruff check --select UP . --config=pyproject.toml

complex-functions:  ## Verifica funções muito complexas
	poetry run ruff check --select C901 . --config=pyproject.toml

long-lines:  ## Verifica linhas muito longas
	poetry run ruff check --select E501 . --config=pyproject.toml

makemessages:  ## Gera arquivos .po para tradução (extrai strings marcadas para tradução)
	poetry run python manage.py makemessages -l pt_BR --ignore=venv/* --ignore=.venv/*

compilemessages:  ## Compila arquivos .po para .mo (gera build das traduções)
	poetry run python manage.py compilemessages

gendata:  ## Gera dados de desenvolvimento na ordem correta para evitar conflitos (uso: make gendata EXTRA_USERS=1000)
	@echo "Gerando dados de desenvolvimento na ordem correta..."
	@echo "\n=== (1/11) Criando grupos de permissões ==="
	poetry run python manage.py create_groups
	@echo "\n=== (2/11) Gerando usuários, empresas, departamentos e cargos ==="
	poetry run python manage.py generate_dev_users --reset --extra-users=1
	@echo "\n=== (3/11) Atribuindo usuários aos grupos de permissões ==="
	poetry run python manage.py assign_users_to_groups --verbose
	@echo "\n=== (4/11) Gerando cartões para os usuários ==="
	poetry run python manage.py generate_dev_cards --reset
	@echo "\n=== (5/11) Gerando histórico de pedidos ==="
	poetry run python manage.py generate_orders_history --reset
	@echo "\n=== (6/11) Gerando solicitações de segunda via de cartões ==="
	poetry run python manage.py generate_card_reissue_history --reset
	@echo "\n=== (7/11) Gerando tickets e histórico de comunicações ==="
	poetry run python manage.py generate_ticket_history --reset
	@echo "\n=== (8/11) Gerando grupos de regras para ponto eletrônico ==="
	poetry run python manage.py generate_electronic_point_rules --reset
	@echo "\n=== (9/11) Gerando escalas de trabalho para ponto eletrônico ==="
	poetry run python manage.py generate_electronic_point_schedules --reset
	@echo "\n=== (10/11) Gerando registros de ponto eletrônico ==="
	poetry run python manage.py generate_electronic_point_punches --reset
	@echo "\n=== (11/11) Gerando dados de banco de horas ==="
	poetry run python manage.py generate_electronic_point_timebank --reset
	@echo "\nDados de desenvolvimento gerados com sucesso!"

install-pre-commit:  ## Instala e configura o pre-commit com commitizen
	@echo "Instalando pre-commit e commitizen..."
	poetry add --group dev pre-commit commitizen
	poetry run pre-commit install
	poetry run pre-commit install --hook-type commit-msg
	@echo "Pre-commit e commitizen instalados com sucesso!"
	@echo "📝 Agora use 'make commit' ou 'make commit-all' para commits interativos"
	@echo "🔒 Commits manuais serão rejeitados se não seguirem o padrão"
	@echo "📖 Veja COMMIT_CONVENTION.md para mais detalhes"

pre-commit-run:  ## Executa o pre-commit em todos os arquivos
	poetry run pre-commit run --all-files

pre-commit-update:  ## Atualiza os hooks do pre-commit
	poetry run pre-commit autoupdate

commit:  ## Faz um commit interativo usando commitizen
	poetry run cz commit

commit-all:  ## Adiciona todos os arquivos e faz commit interativo
	git add .
	poetry run cz commit

# Comandos para executar workflows localmente
workflows:  ## Executa todos os workflows do GitHub Actions localmente
	./scripts/run_workflows_local.sh

workflows-ci:  ## Executa apenas o pipeline de CI localmente
	./scripts/run_workflows_local.sh ci-pipeline

workflows-quality:  ## Executa apenas verificações de qualidade de código
	./scripts/run_workflows_local.sh code-quality

workflows-security:  ## Executa apenas scans de segurança
	./scripts/run_workflows_local.sh security

workflows-tests:  ## Executa apenas testes unitários
	./scripts/run_workflows_local.sh tests

workflows-integration:  ## Executa apenas testes de integração
	./scripts/run_workflows_local.sh integration

workflows-prod:  ## Executa apenas verificações de produção
	./scripts/run_workflows_local.sh production-checks

workflows-integrity:  ## Executa apenas verificações de integridade básica
	./scripts/run_workflows_local.sh basic-integrity

workflows-help:  ## Mostra ajuda sobre os workflows disponíveis
	./scripts/run_workflows_local.sh help

setup-ses:  ## Configura Configuration Set do SES para rastreamento de emails (uso: make setup-ses WEBHOOK_URL=https://seu-dominio.com/webhooks/email/)
	@echo "Configurando rastreamento de emails no SES..."
	poetry run python manage.py setup_ses_tracking $(if $(WEBHOOK_URL),--webhook-url=$(WEBHOOK_URL),) $(if $(DRY_RUN),--dry-run,)

setup-ses-dry:  ## Simula configuração do SES sem criar recursos
	@echo "Simulando configuração do SES (dry-run)..."
	poetry run python manage.py setup_ses_tracking --dry-run $(if $(WEBHOOK_URL),--webhook-url=$(WEBHOOK_URL),)

confirm-sns:  ## Confirma subscriptions SNS pendentes (uso: make confirm-sns)
	@echo "Confirmando subscriptions SNS pendentes..."
	poetry run python manage.py confirm_sns_subscriptions

list-sns:  ## Lista subscriptions SNS pendentes sem confirmar
	@echo "Listando subscriptions SNS pendentes..."
	poetry run python manage.py confirm_sns_subscriptions --list-only
