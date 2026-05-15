# Finance App Backend - Django API

Este é o backend do sistema de gestão financeira, desenvolvido com Django e Django REST Framework. A API gerencia transações financeiras, autenticação via Google OAuth2 e integração CI/CD com AWS.

## 🚀 Tecnologias

- **Python 3.12+**
- **Django 6.0**
- **Django REST Framework (DRF)**
- **PostgreSQL** (Banco de dados)
- **SimpleJWT** (Autenticação baseada em tokens)
- **Google OAuth2** (Login social)
- **Gunicorn** (Servidor de produção)
- **AWS Elastic Beanstalk & CodePipeline** (CI/CD)

---

## 🛠️ Instalação e Configuração Local

### 1. Clonar o repositório
```bash
git clone <url-do-repositorio>
cd finance-app-backend
```

### 2. Configurar o Ambiente Virtual (venv)
```bash
python -m venv venv
# No Windows:
.\venv\Scripts\activate
# No Linux/Mac:
source venv/bin/activate
```

### 3. Instalar Dependências
```bash
make install
# ou: pip install -r requirements.txt
```

### 4. Variáveis de Ambiente (.env)
Crie um arquivo `.env` na raiz do projeto baseado no `.env.example`:
```env
SECRET_KEY=sua_secret_key_aqui
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Banco de Dados (PostgreSQL)
DB_NAME=seu_banco
DB_USER=seu_usuario
DB_PASSWORD=sua_senha
DB_HOST=localhost
DB_PORT=5432

# Google OAuth2
GOOGLE_OAUTH2_CLIENT_ID=seu_client_id.apps.googleusercontent.com
```

### 5. Banco de Dados e Migrações
Certifique-se de que o PostgreSQL está rodando e execute:
```bash
make migrate
```

### 6. Criar Superusuário (Admin)
```bash
make su
```

---

## 🏃 Executando o Projeto

Para rodar o servidor de desenvolvimento:
```bash
make run
```
A API estará disponível em `http://localhost:8000`.

---

## 🧪 Comandos Úteis (Makefile)

O projeto utiliza um `Makefile` para simplificar tarefas comuns:
- `make run`: Inicia o servidor (acessível na rede local).
- `make migrate`: Aplica as migrações ao banco.
- `make mm`: Cria novas migrações.
- `make test`: Executa os testes unitários.
- `make shell`: Abre o shell do Django.

---

## ☁️ Deploy na AWS (CI/CD)

O projeto está configurado para deploy automático via **AWS CodePipeline**:

1. **GitHub**: Cada push na branch principal dispara o pipeline.
2. **CodeBuild**: Utiliza o arquivo `buildspec.yml` para instalar dependências e testar o código.
3. **Elastic Beanstalk**:
   - O arquivo `Procfile` define o uso do Gunicorn.
   - Pasta `.ebextensions/` gerencia migrações e arquivos estáticos automaticamente no deploy.

**Nota:** Lembre-se de configurar todas as variáveis de ambiente do `.env` no console do Elastic Beanstalk (**Configuration > Software**).

---

## 🔐 Autenticação Google OAuth2

Para o login funcionar, o `GOOGLE_OAUTH2_CLIENT_ID` deve ser o mesmo configurado no seu Frontend e no Google Cloud Console. No console do Google, certifique-se de adicionar as URLs do seu frontend aos "Origens JavaScript autorizadas".
