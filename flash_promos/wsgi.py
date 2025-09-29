"""WSGI configuration for Flash Promos project."""
# Standard Python Libraries
import os

# Third-Party Libraries
from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "flash_promos.settings")
application = get_wsgi_application()
