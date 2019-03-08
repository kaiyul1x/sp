from channels.routing import ProtocolTypeRouter, URLRouter
from django.urls.conf import path
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator

from jianshu.consumers import TaskProgressConsumer

application = ProtocolTypeRouter({
    'websocket': AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            URLRouter(
                [
                    path('ws/task/progress/<str:pk>/', TaskProgressConsumer)
                ]
            )
        )

    )
})
