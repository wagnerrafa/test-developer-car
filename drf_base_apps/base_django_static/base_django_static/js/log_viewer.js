document.addEventListener('DOMContentLoaded', function () {

    const configElement = document.getElementById('django_log_viewer_config');
    const schemaUrl = configElement.getAttribute('data-schema-url');
    const filesPerPage = configElement.getAttribute('data-schema-files-per-page');

    let entityMap = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#39;',
        '/': '&#x2F;',
        '`': '&#x60;',
        '=': '&#x3D;'
    };

    function escapeHtml(string) {
        return String(string).replace(/[&<>"'`=\/]/g, function fromEntityMap(s) {
            return entityMap[s];
        });
    }

    function loadDataTable(table_name, url_json) {
        $(table_name).DataTable({
            pageLength: filesPerPage,
            columns: [{data: 0}, {data: 1}],
            ajax: function (data, callback, settings) {
                $.ajax({
                    type: 'get',
                    url: url_json,
                    success: function (response) {
                        const new_logs = [];
                        let next_page = response.next_page || 1;

                        try {
                            response.logs.forEach(function (text, numb, logs) {
                                text = escapeHtml(text);
                                new_logs.push([numb + 1, text]);
                            });
                        } catch {
                            console.warn("This log file doesn't exist");
                        }


                        callback({
                            data: new_logs,
                            recordsTotal: next_page,
                            recordsFiltered: next_page
                        });
                    }
                });
            }
        });
    }

    function loadDataTableFiles(table_name, url_json) {
        $(table_name).DataTable({
            pageLength: filesPerPage,
            columns: [{data: 1}],
            ajax: function (data, callback, settings) {
                $.ajax({
                    type: 'get',
                    url: url_json,
                    success: function (response) {
                        const new_logs = [];
                        let next_page = response.next_page_files || 1;
                        response.log_files.forEach(function (logs, numb) {
                            const keys = Object.keys(logs);
                            Object.entries(logs).forEach(([file_name, xtra]) => {
                                logs = '<a class="btn-load-json-log" href="javascript:;" ' +
                                    'data-file-name="' + file_name + '" ' +
                                    'data-href="' + url_json + file_name + '">' + xtra.display + '</a>'
                            });
                            new_logs.push([numb + 1, logs]);
                        });

                        callback({
                            data: new_logs,
                            recordsTotal: next_page,
                            recordsFiltered: next_page
                        });
                    }
                });
            }
        });
    }

    function loadDataTableTrigger(url_json) {
        let table_name = 'table#log-entries';
        if (!$.fn.dataTable.isDataTable(table_name)) {
            loadDataTable(table_name, url_json);
        } else {
            table_dt = $(table_name).DataTable();
            table_dt.destroy();
            loadDataTable(table_name, url_json);
        }
    }

    $(document).ready(function () {
        // just blank entry to get the `log_files`
        let url_json = schemaUrl;
        let table_name = 'table#log-files-list';
        loadDataTableFiles(table_name, url_json);
        let params = new URLSearchParams(window.location.search);
        loadDataTableTrigger(params.get("file"))

    });

    $(document).on('click', '.btn-load-json-log', function () {
        // console.log(this);
        $(this).closest('#log-files-list').find('li').removeClass('selected');
        $(this).closest('li').addClass('selected');
        loadDataTableTrigger($(this).data('href'));

        let btnDownloadSingleFile = $('.btn-download-this-log');
        let file_name = $(this).data('file-name');
        let href = btnDownloadSingleFile.attr('href');

        if (href.indexOf('file_name') > -1) {
            href = href.replace(/\bfile_name=(.*)\b/, 'file_name=' + file_name)
        } else {
            href = href + '?file_name=' + file_name
        }

        btnDownloadSingleFile.attr('href', href);
        btnDownloadSingleFile.show();
    });
});