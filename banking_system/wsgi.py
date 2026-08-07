from django.core.wsgi import get_wsgi_application
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'banking_system.settings')

application = get_wsgi_application()

# ✅ Run migrations automatically
try:
    from django.core.management import call_command
    call_command('migrate')
except Exception as e:
    print("Migration error:", e)

# ✅ Create superuser automatically
from django.contrib.auth import get_user_model
User = get_user_model()

try:
    if not User.objects.filter(username='deepu').exists():
        User.objects.create_superuser(
            username='deepu',
            email='hunterb005king@gmail.com',
            password='Hunter@0852'
        )
        print("Superuser created")
except Exception as e:
    print("Superuser error:", e)