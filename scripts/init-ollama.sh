#!/bin/bash

# Script para inicializar o Ollama e baixar modelos automaticamente
echo "🚀 Iniciando Ollama..."

# Inicia o servidor Ollama em background
ollama serve &
OLLAMA_PID=$!

# Aguarda o servidor estar pronto
echo "⏳ Aguardando servidor Ollama ficar pronto..."
sleep 20

# Verifica se o modelo já existe
if ollama list | grep -q "llama3.1:8b"; then
    echo "✅ Modelo llama3.1:8b já está disponível!"
else
    echo "📥 Baixando modelo llama3.1:8b..."
    ollama pull llama3.1:8b
    echo "✅ Modelo baixado com sucesso!"
fi

echo "🎉 Inicialização concluída! Modelos disponíveis:"
ollama list

# Mantém o processo rodando
wait $OLLAMA_PID
