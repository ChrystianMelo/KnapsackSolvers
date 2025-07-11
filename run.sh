#!/bin/bash
set -e

echo "--- Ativando ambiente virtual ---"
source venv/bin/activate

echo "Deleting previous results..."
rm -rf "results" "data/PCA Components"   # -r = recursivo, -f = força sem perguntar

echo "--- Executando o projeto ---"

python3 src/main.py
# A desativação acontecerá automaticamente quando o script terminar
echo "--- Aplicação finalizada. Desativando o ambiente virtual. ---"
deactivate
