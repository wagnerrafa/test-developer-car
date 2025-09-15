"""
Comando Django para gerar arquivos de configuração baseados nos templates.

Este comando usa o startapp do Django com templates personalizados
para criar novos projetos baseados no drf_base_apps.
"""

import shutil
from pathlib import Path

from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    """Comando para gerar configurações de projeto Django."""

    help = """
    Gera arquivos de configuração Django baseados nos templates.

    Exemplo de uso:
        python manage.py generate_project_config --project-name=meu_projeto
        python manage.py generate_project_config --project-name=meu_projeto --output-dir=/path/to/output
    """

    def add_arguments(self, parser):
        """Adiciona argumentos ao comando."""
        parser.add_argument("--project-name", type=str, required=True, help="Nome do projeto Django (obrigatório)")
        parser.add_argument("--output-dir", type=str, default=".", help="Diretório de saída (padrão: diretório atual)")
        parser.add_argument("--force", action="store_true", help="Força a sobrescrita de arquivos existentes")
        parser.add_argument(
            "--template-dir",
            type=str,
            default=None,
            help="Diretório de templates personalizado (padrão: usa app_settings_template)",
        )

    def handle(self, *args, **options):
        """Executa o comando."""
        project_name = options["project_name"]
        output_dir = Path(options["output_dir"]).resolve()
        force = options["force"]
        template_dir = options["template_dir"]

        # Valida o nome do projeto
        if not self._is_valid_project_name(project_name):
            raise CommandError(
                f"Nome de projeto inválido: '{project_name}'. " "Use apenas letras, números, underscores e hífens."
            )

        # Define o diretório de templates
        if template_dir:
            template_path = Path(template_dir).resolve()
            if not template_path.exists():
                raise CommandError(f"Diretório de templates não encontrado: {template_path}")
        else:
            template_path = Path(settings.BASE_DIR) / "drf_base_apps" / "app_settings_template"
            if not template_path.exists():
                raise CommandError(f"Diretório de templates padrão não encontrado: {template_path}")

        # Cria o diretório de saída se não existir
        output_dir.mkdir(parents=True, exist_ok=True)

        self.stdout.write(self.style.SUCCESS(f"🚀 Gerando configurações para o projeto: {project_name}"))
        self.stdout.write(f"📁 Diretório de saída: {output_dir}")
        self.stdout.write(f"📋 Diretório de templates: {template_path}")

        try:
            # Usa o startapp do Django com template personalizado
            self._generate_project_with_startapp(project_name, template_path, output_dir, force)

            # Gera arquivos adicionais específicos
            self._generate_additional_files(project_name, output_dir, force)

            self.stdout.write(self.style.SUCCESS(f"✅ Configurações geradas com sucesso em: {output_dir}"))
            self.stdout.write(
                self.style.WARNING("⚠️  Lembre-se de ajustar as configurações conforme necessário para seu projeto!")
            )

        except Exception as e:
            raise CommandError(f"Erro ao gerar configurações: {e!s}") from e

    def _is_valid_project_name(self, name):
        """Valida se o nome do projeto é válido."""
        import re

        return bool(re.match(r"^[a-zA-Z][a-zA-Z0-9_-]*$", name))

    def _generate_project_with_startapp(self, project_name, template_path, output_dir, force):
        """Gera o projeto usando startapp com template personalizado."""
        project_path = output_dir / project_name

        if project_path.exists() and not force:
            self.stdout.write(
                self.style.WARNING(f"⚠️  Diretório já existe: {project_path} (use --force para sobrescrever)")
            )
            if force:
                shutil.rmtree(project_path)
            else:
                return

        try:
            # Chama o startapp com template personalizado
            call_command(
                "startapp",
                project_name,
                template=str(template_path),
                target=output_dir,
                verbosity=0,  # Reduz output verboso
            )

            self.stdout.write(f"✅ Projeto gerado com startapp: {project_path}")

        except Exception as e:
            raise CommandError(f"Erro ao executar startapp: {e!s}") from e

    def _generate_additional_files(self, project_name, output_dir, force):
        """Gera arquivos adicionais específicos."""
        # Gera manage.py na raiz do projeto
        self._generate_manage_py(project_name, output_dir, force)

        # Gera requirements.txt
        self._generate_requirements_txt(output_dir, force)

        # Gera README.md
        self._generate_readme(project_name, output_dir, force)

        # Gera .env.example
        self._generate_env_example(project_name, output_dir, force)

    def _generate_manage_py(self, project_name, output_dir, force):
        """Gera o arquivo manage.py."""
        output_file = output_dir / "manage.py"

        if output_file.exists() and not force:
            self.stdout.write(
                self.style.WARNING(f"⚠️  Arquivo já existe: {output_file} (use --force para sobrescrever)")
            )
            return

        content = f'''#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', '{project_name}.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
'''

        output_file.write_text(content, encoding="utf-8")
        # Torna o arquivo executável
        output_file.chmod(0o755)
        self.stdout.write(f"✅ manage.py gerado: {output_file}")

    def _generate_requirements_txt(self, output_dir, force):
        """Gera o arquivo requirements.txt."""
        output_file = output_dir / "requirements.txt"

        if output_file.exists() and not force:
            self.stdout.write(
                self.style.WARNING(f"⚠️  Arquivo já existe: {output_file} (use --force para sobrescrever)")
            )
            return

        content = """# Requirements para projeto Django baseado em drf_base_apps
# Instale as dependências com: pip install -r requirements.txt

# Django e DRF
Django>=4.2.0
djangorestframework>=3.14.0

# Dependências do drf_base_apps
split-settings>=1.2.0

# Banco de dados (escolha um)
# psycopg2-binary>=2.9.0  # PostgreSQL
# mysqlclient>=2.1.0      # MySQL
# sqlite3                  # SQLite (incluído no Python)

# Cache
redis>=4.5.0
django-redis>=5.2.0

# Segurança
cryptography>=41.0.0

# Desenvolvimento
python-decouple>=3.8
dj-database-url>=2.0.0

# Documentação da API
drf-yasg>=1.21.0

# Logging
drf-api-logger>=1.0.0
"""

        output_file.write_text(content, encoding="utf-8")
        self.stdout.write(f"✅ requirements.txt gerado: {output_file}")

    def _generate_env_example(self, project_name, output_dir, force):
        """Gera o arquivo .env.example."""
        output_file = output_dir / ".env.example"

        if output_file.exists() and not force:
            self.stdout.write(
                self.style.WARNING(f"⚠️  Arquivo já existe: {output_file} (use --force para sobrescrever)")
            )
            return

        content = f"""# Configurações de ambiente para {project_name}
# Copie este arquivo para .env e ajuste as configurações

# Configurações básicas
DEBUG=True
SECRET_KEY=your-secret-key-here
ENVIRONMENT=dev

# Configurações do banco de dados
DATABASE_URL=sqlite:///db.sqlite3
# DATABASE_URL=postgresql://user:password@localhost:5432/dbname
# DATABASE_URL=mysql://user:password@localhost:3306/dbname

# Configurações de cache
REDIS_URL=redis://localhost:6379/0

# Configurações de email
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Configurações de segurança
ALLOWED_HOSTS=localhost,127.0.0.1
CSRF_TRUSTED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

# Configurações de logging
LOG_LEVEL=INFO
LOG_FILE=logs/app.log

# Configurações específicas do projeto
APP_NAME={project_name}
API_VERSION=v1
"""

        output_file.write_text(content, encoding="utf-8")
        self.stdout.write(f"✅ .env.example gerado: {output_file}")

    def _generate_readme(self, project_name, output_dir, force):
        """Gera o arquivo README.md."""
        output_file = output_dir / "README.md"

        if output_file.exists() and not force:
            self.stdout.write(
                self.style.WARNING(f"⚠️  Arquivo já existe: {output_file} (use --force para sobrescrever)")
            )
            return

        content = f"""# {project_name.title()}

Projeto Django baseado em drf_base_apps.

## 🚀 Configuração Inicial

1. **Instale as dependências:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure as variáveis de ambiente:**
   ```bash
   cp .env.example .env
   # Edite o arquivo .env com suas configurações
   ```

3. **Execute as migrações:**
   ```bash
   python manage.py migrate
   ```

4. **Crie um superusuário:**
   ```bash
   python manage.py createsuperuser
   ```

5. **Execute o servidor:**
   ```bash
   python manage.py runserver
   ```

## 📁 Estrutura do Projeto

```
{project_name}/
├── {project_name}/           # Configurações do Django
│   ├── settings.py          # Configurações principais
│   ├── urls.py             # URLs principais
│   ├── wsgi.py             # Configuração WSGI
│   └── asgi.py             # Configuração ASGI
├── manage.py                # Script de gerenciamento Django
├── requirements.txt         # Dependências Python
├── .env.example            # Exemplo de variáveis de ambiente
└── README.md               # Este arquivo
```

## 🔧 Configurações

O projeto usa o sistema de configurações do drf_base_apps, que permite:
- Configurações base reutilizáveis
- Configurações específicas por ambiente
- Fácil manutenção e atualização

## 📚 Documentação

Para mais informações sobre o drf_base_apps, consulte a documentação oficial.

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request
"""

        output_file.write_text(content, encoding="utf-8")
        self.stdout.write(f"✅ README.md gerado: {output_file}")
