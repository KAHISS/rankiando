# variaveis de ambientr
venv := "env/.env"
main := "src/manage.py"

default:
    @just --list

watch:
    docker compose --env-file {{venv}} up --watch   

build:
    docker compose --env-file {{venv}} up --build
    just down
    just watch

down:
    docker compose down

makemigrations:
    uv run python {{main}} makemigrations

newapp name path:
    uv run python {{main}} startapp {{name}} {{path}}

gitcommit menssage:
    git add .
    git commit -m "{{menssage}}"
    git push origin main

