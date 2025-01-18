from django.urls import path
from .views import CreateUserView, VerifyAPIView, GetNewVerification

urlpatterns = [
    path('signup/', CreateUserView.as_view(), name='create_user'),
    path('verify/', VerifyAPIView.as_view(), name='verify_user'),
    path('new-verify/', GetNewVerification.as_view(), name='new_verify'),
]