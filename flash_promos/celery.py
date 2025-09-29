"""Celery configuration for Flash Promos project."""
# Standard Python Libraries
import os

# Third-Party Libraries
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "flash_promos.settings")

app = Celery("flash_promos")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    """Debug task for testing Celery."""
    print(f"Request: {self.request!r}")
