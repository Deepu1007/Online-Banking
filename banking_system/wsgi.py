"""
WSGI config for banking_system project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""
from django.core.wsgi import get_wsgi_application
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'banking_system.settings')

application = get_wsgi_application()

# 👇 ADD THIS
try:
    from django.core.management import call_command
    call_command('migrate')
except Exception as e:
    print("Migration error:", e)