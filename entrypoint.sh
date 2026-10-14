#!/bin/sh
set -e
echo "Rodando migrações..."
python src/manage.py migrate --noinput
python src/manage.py collectstatic --noinput
python src/manage.py createsuperuser --noinput || true
echo "Iniciando o servidor..."
exec "$@"