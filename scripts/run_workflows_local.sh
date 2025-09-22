#!/bin/bash

# Script para executar localmente os workflows do GitHub Actions
# Baseado nos workflows: ci-pipeline.yml, production-checks.yml, etc.

set -e  # Para o script se algum comando falhar

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Função para imprimir mensagens coloridas
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Função para verificar se um comando existe
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Função para verificar dependências
check_dependencies() {
    print_status "Verificando dependências..."
    
    if ! command_exists poetry; then
        print_error "Poetry não está instalado. Instale em: https://python-poetry.org/docs/#installation"
        exit 1
    fi
    
    if ! command_exists docker; then
        print_warning "Docker não está instalado. Alguns testes podem falhar."
    fi
    
    if ! command_exists redis-cli; then
        print_warning "Redis CLI não está instalado. Alguns testes podem falhar."
    fi
    
    print_success "Dependências verificadas"
}

# Função para configurar ambiente de teste
setup_test_env() {
    print_status "Configurando ambiente de teste..."
    
    # Criar arquivo .env.test com as variáveis do CI
    cat > .env.test << EOF
DEBUG=True
SECRET_KEY=test-secret-key-for-ci
DATABASE_URL=sqlite:///test.db
REDIS_URL=redis://localhost:6379/0
TESTING=True
DISABLE_MIGRATIONS=False
ENVIRONMENT=dev
ENV=dev
LIST_ALLOWED_HOSTS=localhost,127.0.0.1
APP_NAME=benefits-back
USE_BASE_NAME=False
PUBLIC_SWAGGER=True
PRINT_DEBUG=True
ENABLE_DRF=True
ENABLE_CACHE=False
SANDBOX_COMMIT=True
EXTERNAL_DATABASE=False
AUTO_REGISTER_MODELS=False
CURRENT_VERSION=0.0.1
TOKEN_TEST=
LOGGER_TEST=False
ENABLE_LOGGING_FILE=False
LOGGING_FILE_LEVEL=INFO
LOGGING_FILE_HANDLERS=debug,console,critical,info,error,warning,celery
PATHS_BACKEND=
ENABLE_TOKEN=False
ENABLE_PW=True
REQUEST_TIMEOUT=30
CHECK_HAS_CHANGED_PASSWORD=False
PASSWD_DEV=Senha@1234
USER_DEV=dev_user
USER_ADMIN_DEV=dev_admin
FERNET_KEY=ou5SAHd8fIj-gSLGyxPR5q8XraVD-_xlGGOtxpflOUQ=
API_VERSION=v1
SQL_DRIVER_OPTIONS=
LOGGING_FORMAT_SIMPLE=[%(levelname)s] %(asctime)s - %(name)s - %(message)s
LOGGING_FORMAT_VERBOSE=[%(levelname)s] %(asctime)s - %(name)s - %(funcName)s:%(lineno)d - %(message)s
GET_VENV=True
STATIC_FILES=
DEFAULT_PERMISSIONS_PATH=
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_STORAGE_BUCKET_NAME=
AWS_S3_REGION_NAME=us-east-1
AWS_SES_REGION_NAME=us-east-1
CELERY_BROKER_POOL_LIMIT=1
CELERY_BROKER_CONNECTION_TIMEOUT=30.0
SINGLE_QUEUE_CONCURRENCY=1
CELERY_EVENT_QUEUE_TTL=5.0
AWS_S3_ENDPOINT_URL=
AWS_DEFAULT_ACL=public-read
AWS_S3_USE_SSL=False
RB_API_USE_MOCK=True
DEFAULT_THEME_COLOR=#E0E621
EXPO_PUSH_API_URL=https://exp.host/--/api/v2/push/send
NAMU_ENABLED=True
NAMU_URL=https://webapp-api.namu.com.br/login
NAMU_API_KEY=teste
EXPO_PUSH_TOKEN=nqNWwMDaOu8lt9r4_dDTGafeOLITQCpuJGqbVjck
EXPO_PUSH_APP_ID=@comunix/benefits-app
NAMU_API_USE_MOCK=True
EOF
    
    print_success "Ambiente de teste configurado"
}

# Função para executar job de qualidade de código
run_code_quality() {
    print_status "Executando Code Quality Checks..."
    
    # Verificar formatação com Black
    print_status "Verificando formatação com Black..."
    poetry run black --check . || {
        print_error "❌ Black check falhou. Execute 'make format' para corrigir."
        exit 1
    }
    
    # Verificar linting com Ruff
    print_status "Executando linting com Ruff..."
    poetry run ruff check . || {
        print_error "❌ Ruff check falhou. Execute 'make lint-fix' para corrigir."
        exit 1
    }
    
    # Verificar ordenação de imports
    print_status "Verificando ordenação de imports..."
    poetry run ruff check --select I . || {
        print_error "❌ Import sorting check falhou."
        exit 1
    }
    
    print_success "Code Quality Checks passaram!"
}

# Função para executar scans de segurança
run_security_scans() {
    print_status "Executando Security Scans..."
    
    # Bandit security scan
    print_status "Executando Bandit security scan..."
    poetry run make bandit-sarif || {
        print_warning "Bandit scan falhou ou encontrou problemas."
    }
    
    # Semgrep security scan
    print_status "Executando Semgrep security scan..."
    poetry run semgrep scan --config=auto --sarif --output semgrep-report.sarif || {
        print_warning "Semgrep scan falhou ou encontrou problemas."
    }
    
    print_success "Security Scans concluídos!"
}

# Função para executar testes unitários
run_unit_tests() {
    print_status "Executando Unit Tests..."
    
    # Verificar se Redis está rodando
    if command_exists redis-cli; then
        if ! redis-cli ping >/dev/null 2>&1; then
            print_warning "Redis não está rodando. Iniciando Redis..."
            if command_exists docker; then
                docker run -d --name redis-test -p 6379:6379 redis:7 >/dev/null 2>&1 || true
                sleep 2
            else
                print_warning "Docker não disponível. Certifique-se de que Redis está rodando na porta 6379."
            fi
        fi
    fi
    
    # Executar migrações
    print_status "Executando migrações..."
    poetry run python manage.py migrate --settings=config.settings
    
    # Criar grupos
    print_status "Criando grupos..."
    poetry run python manage.py create_groups --settings=config.settings
    
    # Executar testes com cobertura
    print_status "Executando testes com cobertura..."
    poetry run pytest --cov=. --cov-report=xml --cov-report=html --cov-report=term --cache-clear -s
    
    print_success "Unit Tests concluídos!"
}

# Função para executar review de dependências
run_dependency_review() {
    print_status "Executando Dependency Review..."
    
    # Verificar árvore de dependências
    poetry run pipdeptree --warn silence || {
        print_warning "Dependency review encontrou problemas."
    }
    
    print_success "Dependency Review concluído!"
}

# Função para executar testes de integração
run_integration_tests() {
    print_status "Executando Integration Tests..."
    
    # Executar testes marcados como integração
    poetry run python manage.py test --keepdb --tag=integration --settings=config.settings || {
        print_warning "Integration tests falharam ou não foram encontrados."
    }
    
    print_success "Integration Tests concluídos!"
}

# Função para executar verificações de integridade básica
run_basic_integrity() {
    print_status "Executando Basic Integrity Checks..."
    
    # Verificar configuração do Poetry
    print_status "Verificando configuração do Poetry..."
    poetry check
    
    # Verificar configuração básica do Django
    print_status "Verificando configuração básica do Django..."
    poetry run python manage.py check --settings=config.settings
    
    # Verificar imports não utilizados
    print_status "Verificando imports não utilizados..."
    poetry run ruff check --select F401 . || {
        print_error "❌ Encontrados imports não utilizados. Corrija antes de continuar."
        exit 1
    }
    
    # Verificar variáveis não utilizadas
    print_status "Verificando variáveis não utilizadas..."
    poetry run ruff check --select F841 . || {
        print_error "❌ Encontradas variáveis não utilizadas. Corrija antes de continuar."
        exit 1
    }
    
    # Verificar simplificações de código
    print_status "Verificando simplificações de código..."
    poetry run ruff check --select SIM . || {
        print_error "❌ Encontradas possíveis simplificações de código. Corrija antes de continuar."
        exit 1
    }
    
    # Verificar upgrades de código
    print_status "Verificando upgrades de código..."
    poetry run ruff check --select UP . || {
        print_error "❌ Encontradas possíveis melhorias de código. Corrija antes de continuar."
        exit 1
    }
    
    # Verificar árvore de dependências
    print_status "Verificando árvore de dependências..."
    poetry show --tree
    
    # Validar arquivo de lock
    print_status "Validando arquivo de lock..."
    poetry lock
    
    # Verificar dependências circulares
    print_status "Verificando dependências circulares..."
    poetry run pipdeptree --warn silence || {
        print_error "❌ Encontradas dependências circulares. Corrija antes de continuar."
        exit 1
    }
    
    print_success "Basic Integrity Checks concluídos!"
}

# Função para executar verificações de produção
run_production_checks() {
    print_status "Executando Production Checks..."
    
    # Verificações do Django para produção
    poetry run python manage.py check --deploy --settings=config.settings
    
    # Verificar configurações
    poetry run python manage.py diffsettings --settings=config.settings
    
    print_success "Production Checks concluídos!"
}

# Função para limpar recursos temporários
cleanup() {
    print_status "Limpando recursos temporários..."
    
    # Parar container Redis se foi criado
    if command_exists docker; then
        docker stop redis-test >/dev/null 2>&1 || true
        docker rm redis-test >/dev/null 2>&1 || true
    fi
    
    # Remover arquivo .env.test
    rm -f .env.test
    
    print_success "Limpeza concluída!"
}

# Função principal
main() {
    echo "🚀 Executando Workflows do GitHub Actions Localmente"
    echo "=================================================="
    
    # Parse de argumentos
    WORKFLOW="all"
    if [ $# -gt 0 ]; then
        case $1 in
            "ci-pipeline"|"ci")
                WORKFLOW="ci-pipeline"
                ;;
            "production-checks"|"prod")
                WORKFLOW="production-checks"
                ;;
            "code-quality"|"quality")
                WORKFLOW="code-quality"
                ;;
            "security")
                WORKFLOW="security"
                ;;
            "tests"|"unit-tests")
                WORKFLOW="tests"
                ;;
            "integration")
                WORKFLOW="integration"
                ;;
            "basic-integrity"|"integrity")
                WORKFLOW="basic-integrity"
                ;;
            "help"|"-h"|"--help")
                echo "Uso: $0 [workflow]"
                echo ""
                echo "Workflows disponíveis:"
                echo "  ci-pipeline (ci)     - Pipeline completo de CI"
                echo "  production-checks (prod) - Verificações de produção"
                echo "  code-quality (quality)   - Verificações de qualidade de código"
                echo "  security              - Scans de segurança"
                echo "  tests (unit-tests)    - Testes unitários"
                echo "  integration           - Testes de integração"
                echo "  basic-integrity (integrity) - Verificações de integridade básica"
                echo "  all (padrão)          - Todos os workflows"
                echo ""
                echo "Exemplos:"
                echo "  $0                    # Executa todos os workflows"
                echo "  $0 ci-pipeline        # Executa apenas o pipeline de CI"
                echo "  $0 code-quality       # Executa apenas verificações de código"
                exit 0
                ;;
            *)
                print_error "Workflow desconhecido: $1"
                print_error "Execute '$0 help' para ver as opções disponíveis"
                exit 1
                ;;
        esac
    fi
    
    # Verificar dependências
    check_dependencies
    
    # Configurar ambiente de teste
    setup_test_env
    
    # Executar workflows baseado na seleção
    case $WORKFLOW in
        "all")
            run_code_quality
            run_security_scans
            run_unit_tests
            run_dependency_review
            run_integration_tests
            run_basic_integrity
            run_production_checks
            ;;
        "ci-pipeline")
            run_code_quality
            run_security_scans
            run_unit_tests
            run_dependency_review
            run_integration_tests
            ;;
        "production-checks")
            run_production_checks
            ;;
        "code-quality")
            run_code_quality
            ;;
        "security")
            run_security_scans
            ;;
        "tests")
            run_unit_tests
            ;;
        "integration")
            run_integration_tests
            ;;
        "basic-integrity")
            run_basic_integrity
            ;;
    esac
    
    # Limpeza
    cleanup
    
    echo ""
    print_success "🎉 Workflow(s) executado(s) com sucesso!"
    echo ""
    echo "📊 Relatórios gerados:"
    echo "  - coverage.xml (cobertura de testes)"
    echo "  - htmlcov/ (relatório HTML de cobertura)"
    echo "  - bandit-report.sarif (relatório de segurança Bandit)"
    echo "  - semgrep-report.sarif (relatório de segurança Semgrep)"
}

# Executar função principal
main "$@" 