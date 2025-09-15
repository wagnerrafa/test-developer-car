"""URL patterns for custom log viewer."""

from django.urls import path, re_path
from log_viewer.views import log_download, log_json

from drf_base_apps.custom_log_viewer.views import CustomLogViewerView

app_name = "custom_log_viewer"

urlpatterns = [
    re_path(
        r"^json/(?P<file_name>[\.\w-]*)/(?P<page>[0-9]+)$",
        log_json,
        name="log_json_view",
    ),
    re_path(
        r"^json/(?P<file_name>[\.\w-]*)$",
        log_json,
        name="log_json_view",
    ),
    path(
        "download/single-file/",
        log_download,
        name="log_download_file_view",
    ),
    re_path(
        r"^download.zip$",
        log_download,
        name="log_download_zip_view",
    ),
    path(
        "",
        CustomLogViewerView.as_view(),
        name="log_file_view",
    ),
]
