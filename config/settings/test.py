import os
import tempfile

from .base import *  # noqa: F401, F403

# Allow synchronous DB operations from an async context.
# Required when combining pytest-playwright (which uses asyncio internally)
# with pytest-django (which uses synchronous DB access during teardown).
os.environ.setdefault("DJANGO_ALLOW_ASYNC_UNSAFE", "1")

# Use a file-based SQLite so live_server (browser tests) can access the DB
# from a separate thread. In-memory SQLite does not work with live_server.
_DB_PATH = os.path.join(tempfile.gettempdir(), "schreinerei_test.db")

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": _DB_PATH,
    }
}

PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]

STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"

# Silence migration output during tests
MIGRATION_MODULES = {}

# Use a temp media root for tests to avoid polluting production media
MEDIA_ROOT = os.path.join(tempfile.gettempdir(), "schreinerei_test_media")
