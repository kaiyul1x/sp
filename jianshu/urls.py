from django.urls.conf import path

from .views import PostDetailAPIView, TaskDetailAndDestroyAPIView, TaskCreateAPIView

app_name = 'jianshu'

urlpatterns = [
    path('post/<str:pk>/', PostDetailAPIView.as_view()),
    path('task/<str:pk>/', TaskDetailAndDestroyAPIView.as_view()),
    path('task/', TaskCreateAPIView.as_view()),
]
