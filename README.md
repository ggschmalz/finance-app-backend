# Finance App Backend - Django API

Este é o backend do sistema de gestão financeira, desenvolvido com Django e Django REST Framework. A API gerencia transações financeiras, autenticação via Google OAuth2 e integração CI/CD com AWS.

## 🚀 Tecnologias

- **Python 3.12+**
- **Django 6.0**
- **Django REST Framework (DRF)**
- **PostgreSQL 16** (Banco de dados)
- **Docker & Docker Compose** (Containerização e orquestração)
- **SimpleJWT** (Autenticação baseada em tokens)
- **Google OAuth2** (Login social)
- **Gunicorn** (Servidor de produção)
- **AWS Elastic Beanstalk & CodePipeline** (CI/CD)

---

## 🐳 Executando com Docker Compose (Recomendado)

O projeto está configurado para subir tanto a API Django quanto o banco de dados PostgreSQL com um único comando.

### Arquitetura dos Contêineres

| Serviço | Contêiner | Imagem / Build | Porta Host | Descrição |
| :--- | :--- | :--- | :--- | :--- |
| **`db`** | `finance_postgres_db` | `postgres:16-alpine` | `5432:5432` | Banco PostgreSQL com dados persistidos em volume |
| **`backend`** | `finance_django_backend` | `Dockerfile` (Python 3.12-slim) | `8000:8000` | API Django com hot-reload e migrações automáticas |

---

### Passo a Passo para Execução

#### 1. Configurar variáveis de ambiente (`.env`)
Copie o arquivo de exemplo caso ainda não tenha um `.env`:
```bash
# Linux / macOS / Git Bash:
cp .env.example .env

# Windows (PowerShell):
Copy-Item .env.example .env
```
> **Nota:** No Docker Compose, o backend conecta-se ao banco pelo hostname interno `db`. Essa configuração já é gerenciada automaticamente pelo `docker-compose.yml`.

#### 2. Iniciar os serviços
Suba os contêineres construindo as imagens:
```bash
docker compose up --build
```
*(ou pelo Makefile: `make docker-build` ou `make docker-up`)*

> ⚙️ **Inicialização Inteligente:** O script [`entrypoint.sh`](file:///C:/Users/guilh/OneDrive/Documentos/TCC/finance-app-backend/entrypoint.sh) aguarda a inicialização completa do PostgreSQL (`healthcheck`) e executa as migrações (`python manage.py migrate`) automaticamente antes de iniciar o servidor.

A API estará acessível em: **[http://localhost:8000](http://localhost:8000)**

---

### Gerenciamento do Banco de Dados no Docker

#### 🗄️ Persistência dos Dados
Os dados do PostgreSQL ficam gravados no volume nomeado `postgres_data`. Eles **não são perdidos** ao parar os contêineres com `docker compose down`.
* Para resetar o banco do zero (apagando os volumes):
  ```bash
  docker compose down -v
  ```

#### 🔌 Conexão Externa (DBeaver, pgAdmin, TablePlus, VS Code)
A porta `5432` está exposta no host:
- **Host:** `localhost`
- **Porta:** `5432`
- **Database:** `${DB_NAME}` (padrão: `finance_db`)
- **Usuário:** `${DB_USER}` (padrão: `postgres`)
- **Senha:** `${DB_PASSWORD}` (definida no seu `.env`)

#### 💻 Acessar o terminal `psql` interativo:
```bash
docker compose exec db psql -U postgres -d finance_db
```

---

### Comandos Úteis do Django no Docker

* **Criar Superusuário (Admin):**
  ```bash
  docker compose exec backend python manage.py createsuperuser
  # ou: make docker-su
  ```

* **Executar Testes Automatizados:**
  ```bash
  docker compose exec backend python manage.py test
  ```

* **Gerar / Aplicar Novas Migrações Manualmente:**
  ```bash
  docker compose exec backend python manage.py makemigrations
  docker compose exec backend python manage.py migrate
  ```

* **Acessar o Django Shell interativo:**
  ```bash
  docker compose exec backend python manage.py shell
  ```

* **Visualizar logs em tempo real:**
  ```bash
  docker compose logs -f
  # ou apenas do backend: docker compose logs -f backend
  ```

* **Parar os contêineres:**
  ```bash
  docker compose down
  # ou: make docker-down
  ```

---

## 🛠️ Instalação e Execução Local (Sem Docker)

Caso prefira executar diretamente no sistema operacional:

### 1. Configurar o Ambiente Virtual (venv)
```bash
python -m venv venv

# No Windows:
.\venv\Scripts\activate

# No Linux/Mac:
source venv/bin/activate
```

### 2. Instalar Dependências
```bash
make install
# ou: pip install -r requirements.txt
```

### 3. Configurar `.env` e Banco de Dados
Certifique-se de ter um PostgreSQL local rodando na porta `5432` e configure `DB_HOST=localhost` no seu `.env`:
```bash
make migrate
```

### 4. Executar a Aplicação
```bash
make run
```
A API estará disponível em `http://localhost:8000`.

---

## 🧪 Resumo de Comandos do Makefile

O projeto conta com atalhos configurados no [`Makefile`](file:///C:/Users/guilh/OneDrive/Documentos/TCC/finance-app-backend/Makefile):

| Comando | Finalidade |
| :--- | :--- |
| `make docker-up` | Inicia os contêineres (PostgreSQL + Django) |
| `make docker-build` | Reconstrói a imagem e sobe os contêineres |
| `make docker-down` | Encerra os contêineres |
| `make docker-logs` | Acompanha os logs em tempo real |
| `make docker-su` | Cria um superusuário dentro do contêiner |
| `make docker-migrate`| Aplica migrações dentro do contêiner |
| `make run` | Executa o servidor Django localmente |
| `make test` | Executa a suíte de testes unitários |
| `make migrate` | Aplica migrações no banco local |
| `make mm` | Gera arquivos de migração (`makemigrations`) |

---

## ☁️ Deploy na AWS (CI/CD)

O projeto está configurado para deploy contínuo via **AWS CodePipeline**:

1. **GitHub**: Cada push na branch `main` dispara o pipeline.
2. **CodeBuild**: Utiliza o arquivo `buildspec.yml` para instalar dependências e testar o código.
3. **Elastic Beanstalk**:
   - O arquivo `Procfile` define a execução via **Gunicorn**.
   - A pasta `.ebextensions/` gerencia arquivos estáticos e migrações no deploy.

---

## 🔐 Autenticação Google OAuth2

Para o login com Google funcionar corretamente:
1. Obtenha o `Client ID` no console do Google Cloud.
2. Defina-o na variável `GOOGLE_OAUTH2_CLIENT_ID` no `.env`.
3. No Google Cloud Console, adicione as URLs do seu frontend às **"Origens JavaScript autorizadas"** (ex: `http://localhost:5173`).
