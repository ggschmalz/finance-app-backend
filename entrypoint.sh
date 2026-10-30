#!/bin/sh
set -e

echo "Aguardando o banco de dados PostgreSQL..."
python << 'EOF'
import os
import socket
import time

host = os.getenv('DB_HOST', 'db')
port = int(os.getenv('DB_PORT', 5432))

while True:
    try:
        with socket.create_connection((host, port), timeout=2):
            break
    except (socket.error, OSError):
        time.sleep(0.5)
EOF

echo "PostgreSQL pronto para conexões!"

echo "Aplicando migrações do banco de dados..."
python manage.py migrate --noinput

echo "Iniciando comando: $@"
exec "$@"
