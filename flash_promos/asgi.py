"""ASGI configuration for Flash Promos project."""
# Standard Python Libraries
import os

# Third-Party Libraries
from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "flash_promos.settings")
application = get_asgi_application()
