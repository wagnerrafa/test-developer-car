#!/bin/bash

# Script para otimizar performance do Ollama
echo "🚀 Otimizando performance do Ollama..."

# Verifica se o Ollama está rodando
if ! docker ps | grep -q "base_tests_ollama"; then
    echo "❌ Container Ollama não está rodando. Inicie com: docker-compose -f docker-compose.ollama.yml up -d"
    exit 1
fi

echo "📊 Verificando status atual do Ollama..."

# Verifica modelos carregados
echo "📋 Modelos disponíveis:"
docker exec base_tests_ollama ollama list

# Verifica uso de memória
echo "💾 Uso de memória:"
docker exec base_tests_ollama sh -c "free -h && echo '---' && ps aux --sort=-%mem | head -10"

# Otimizações de sistema
echo "⚡ Aplicando otimizações de sistema..."

# Aumenta limites de memória compartilhada
docker exec base_tests_ollama sh -c "echo 'kernel.shmmax = 2147483648' >> /etc/sysctl.conf" 2>/dev/null || true
docker exec base_tests_ollama sh -c "echo 'kernel.shmall = 524288' >> /etc/sysctl.conf" 2>/dev/null || true

# Otimiza configurações do Ollama
echo "🔧 Configurando variáveis de ambiente otimizadas..."
docker exec base_tests_ollama sh -c "
    export OLLAMA_NUM_PARALLEL=4
    export OLLAMA_MAX_LOADED_MODELS=2
    export OLLAMA_MAX_QUEUE=512
    export OLLAMA_KEEP_ALIVE=24h
    export OLLAMA_ORIGINS=*
"

# Pré-carrega o modelo para evitar latência
echo "🔄 Pré-carregando modelo para melhor performance..."
docker exec base_tests_ollama ollama run llama3.1:8b "Hello, this is a test to warm up the model." > /dev/null 2>&1

echo "✅ Otimizações aplicadas!"
echo ""
echo "📈 Dicas adicionais para melhor performance:"
echo "1. Use modelos menores (7b em vez de 13b) se possível"
echo "2. Reduza max_tokens para respostas mais curtas"
echo "3. Use temperature baixa (0.1-0.3) para respostas mais diretas"
echo "4. Considere usar GPU se disponível"
echo ""
echo "🔍 Para monitorar performance:"
echo "docker exec base_tests_ollama ollama ps"
echo "docker stats base_tests_ollama"
