"""
Example_Config settings configuration.

This module extends the base drf_base_config settings with project-specific
configurations. It uses split_settings to include the base configuration
and then adds project-specific overrides.
"""

import os
import sysconfig
from os import path
from pathlib import Path

from split_settings.tools import include as extend_settings

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "example_config.settings")

library_path = sysconfig.get_paths()["purelib"]

settings_path = path.join(Path(__file__).resolve().parent.parent, "drf_base_config", "settings.py")

extend_settings(settings_path)

# Import base settings - this will populate the global namespace
from drf_base_config.settings import *

# Add project-specific apps to INSTALLED_APPS
INSTALLED_APPS += ["apps.cars", "apps.terminal_agent"]

ROOT_URLCONF = "config.urls"

# Definição de configurações sockets
channel_redis_url = config("REDIS_URL", default="redis://localhost:6379/6")
channel_redis_cache = config("REDIS_URL", default="redis://localhost:6379/7")
celery_url = os.environ.get("REDIS_URL", "redis://127.0.0.1:6379/8")

BASE_SOCKETS = f"{APP_NAME}/ws/V1/"
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "apps.web_sockets.channel_layer.ExtendedRedisChannelLayer",
        "CONFIG": {
            "hosts": [channel_redis_url],
            "symmetric_encryption_keys": [SECRET_KEY],
            "capacity": 500,  # default 100
        },
    },
    "general": {
        "BACKEND": "apps.web_sockets.channel_layer.ExtendedRedisChannelLayer",
        "CONFIG": {
            "hosts": [channel_redis_url],
            "symmetric_encryption_keys": [SECRET_KEY],
            "capacity": 500,  # default 100
        },
    },
}
