# Variáveis
PYTHON = python
MANAGE = $(PYTHON) manage.py

.PHONY: help run mm migrate su shell test install

help:
	@echo "Comandos disponíveis:"
	@echo "  make run      - Executa o servidor de desenvolvimento"
	@echo "  make mm       - Cria novas migrações (makemigrations)"
	@echo "  make migrate  - Aplica as migrações no banco de dados"
	@echo "  make su       - Cria um superusuário"
	@echo "  make shell    - Abre o shell interativo do Django"
	@echo "  make test     - Executa os testes unitários"
	@echo "  make install  - Instala as dependências do requirements.txt"

run:
	$(MANAGE) runserver 0.0.0.0:8000

mm:
	$(MANAGE) makemigrations

migrate:
	$(MANAGE) migrate

su:
	$(MANAGE) createsuperuser

shell:
	$(MANAGE) shell

test:
	$(MANAGE) test

install:
	pip install -r requirements.txt
