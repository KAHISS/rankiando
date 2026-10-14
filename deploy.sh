#!/bin/bash
# deploy.sh — builda a imagem de produção e envia pro GitHub Container Registry
#
# Uso:
#   ./deploy.sh <nome-da-imagem>            -> builda e envia só como "latest"
#   ./deploy.sh <nome-da-imagem> <versao>   -> builda e envia como "versao" e também "latest"

set -e

if [ -z "$1" ]; then
  echo "Erro: Você precisa informar o nome da imagem."
  echo "Uso: ./deploy.sh <nome-da-imagem> [versao]"
  exit 1
fi

IMAGE="ghcr.io/kahiss/$1"
VERSION="$2"

echo "==> Buildando imagem de produção..."
if [ -n "$VERSION" ]; then
  docker build --target production -t "$IMAGE:$VERSION" -t "$IMAGE:latest" .
else
  docker build --target production -t "$IMAGE:latest" .
fi

echo "==> Enviando pro GHCR..."
if [ -n "$VERSION" ]; then
  docker push "$IMAGE:$VERSION"
fi
docker push "$IMAGE:latest"

echo ""
echo "==> Pronto! Agora, na VPS, rode:"
echo "    cd ~/app_repo && docker compose -f compose.prod.yaml pull && docker compose -f compose.prod.yaml up -d"
