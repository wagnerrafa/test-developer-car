function carregarScript(url, callback) {
    let script = document.createElement('script');
    script.src = url;
    script.nonce = "{{nonce_value}}"
    script.onload = callback;
    script.onerror = function () {
        console.error('Erro ao carregar o script:', url);
        document.querySelector('.error-message').style.display = 'block';
    };

    document.head.appendChild(script);
}

// Carregar o primeiro script
carregarScript("{% static '/frontend/js/chunk-vendors.js' %}", function () {
})

// Carregar o segundo script
carregarScript("{% static '/frontend/js/app.js' %}", function () {
})