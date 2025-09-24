#!/bin/bash

# Script otimizado para inicializar o Ollama com configurações de performance
echo "🚀 Iniciando Ollama com otimizações de performance..."

# Configurações de sistema otimizadas
export OLLAMA_NUM_PARALLEL=4
export OLLAMA_MAX_LOADED_MODELS=2
export OLLAMA_MAX_QUEUE=512
export OLLAMA_KEEP_ALIVE=24h
export OLLAMA_ORIGINS=*

# Inicia o servidor Ollama em background
ollama serve &
OLLAMA_PID=$!

# Aguarda o servidor estar pronto
echo "⏳ Aguardando servidor Ollama ficar pronto..."
sleep 15

# Verifica se o modelo já existe
if ollama list | grep -q "llama3.1:8b"; then
    echo "✅ Modelo llama3.1:8b já está disponível!"
else
    echo "📥 Baixando modelo llama3.1:8b..."
    ollama pull llama3.1:8b
    echo "✅ Modelo baixado com sucesso!"
fi

# Tenta baixar modelo menor para comparação de performance
if ! ollama list | grep -q "llama3.1:7b"; then
    echo "📥 Baixando modelo menor llama3.1:7b para melhor performance..."
    ollama pull llama3.1:7b
    echo "✅ Modelo menor baixado!"
fi

# Pré-carrega o modelo para evitar latência inicial
echo "🔥 Aquecendo modelo para melhor performance..."
ollama run llama3.1:8b "Teste de aquecimento do modelo." > /dev/null 2>&1

echo "🎉 Inicialização otimizada concluída!"
echo ""
echo "📊 Modelos disponíveis:"
ollama list
echo ""
echo "⚡ Para usar o modelo mais rápido:"
echo "   - llama3.1:7b (mais rápido, menos preciso)"
echo "   - llama3.1:8b (balanceado)"
echo ""
echo "🔧 Para monitorar performance:"
echo "   ollama ps"

# Mantém o processo rodando
wait $OLLAMA_PID
