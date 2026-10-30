# Variáveis
PYTHON = python
MANAGE = $(PYTHON) manage.py
DC = docker compose

.PHONY: help run mm migrate su shell test install docker-up docker-down docker-build docker-logs docker-su docker-migrate

help:
	@echo "Comandos disponíveis (Local):"
	@echo "  make run            - Executa o servidor de desenvolvimento local"
	@echo "  make mm             - Cria novas migrações (makemigrations)"
	@echo "  make migrate        - Aplica as migrações no banco de dados"
	@echo "  make su             - Cria um superusuário"
	@echo "  make shell          - Abre o shell interativo do Django"
	@echo "  make test           - Executa os testes unitários"
	@echo "  make install        - Instala as dependências do requirements.txt"
	@echo ""
	@echo "Comandos disponíveis (Docker):"
	@echo "  make docker-up      - Sobe os contêineres (backend + postgres)"
	@echo "  make docker-down    - Para os contêineres"
	@echo "  make docker-build   - Reconstrói as imagens e sobe os contêineres"
	@echo "  make docker-logs    - Exibe os logs em tempo real"
	@echo "  make docker-su      - Cria superusuário dentro do contêiner"
	@echo "  make docker-migrate - Executa as migrações no contêiner"

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

# Atalhos Docker Compose
docker-up:
	$(DC) up

docker-down:
	$(DC) down

docker-build:
	$(DC) up --build

docker-logs:
	$(DC) logs -f

docker-su:
	$(DC) exec backend python manage.py createsuperuser

docker-migrate:
	$(DC) exec backend python manage.py migrate
