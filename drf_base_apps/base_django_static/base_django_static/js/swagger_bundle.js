document.addEventListener('DOMContentLoaded', function () {

    const configElement = document.getElementById('config');
    const schemaUrl = configElement.getAttribute('data-schema-url');
    const csrfToken = configElement.getAttribute('data-csrf-token');
    const DisableTryItOutPlugin = function () {
        return {
            statePlugins: {
                spec: {
                    wrapSelectors: {
                        allowTryItOutFor: (defaultImpl) => (state, path) => {
                            let values = state.get('json').get("disable_try_it_out_urls");
                            const paths = Array.from(values.values());
                            return !paths.includes(path)
                        },
                    },
                },
            },
        };
    };

    if (typeof SwaggerUIBundle === 'undefined') {
        console.error('Erro ao carregar o SwaggerUIBundle');
    }
    const ui = SwaggerUIBundle({
        url: schemaUrl,
        dom_id: '#swagger-ui',
        presets: [
            SwaggerUIBundle.presets.apis,
            SwaggerUIBundle.SwaggerUIStandalonePreset
        ],
        plugins: [
            SwaggerUIBundle.plugins.DownloadUrl,
            DisableTryItOutPlugin
        ],
        layout: "BaseLayout",
        requestInterceptor: (request) => {
            request.headers['X-CSRFToken'] = csrfToken
            return request;
        }
    })
})

