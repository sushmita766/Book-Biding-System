import os
from django.core.asgi import get_asgi_application



from django.conf import settings
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from channels.auth import AuthMiddlewareStack
import main_app.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bidandbuy.settings')

application = ProtocolTypeRouter({
    'http': get_asgi_application(),
    "websocket": AllowedHostsOriginValidator(
            AuthMiddlewareStack(URLRouter(main_app.routing.websocket_urlpatterns))
        ),
})