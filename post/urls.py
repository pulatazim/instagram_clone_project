from django.urls import path
from .views import PostListApiView

urlpatterns = [
    path('posts/', PostListApiView.as_view(), name='post-list'),
]