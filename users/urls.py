from django.conf.urls.static import static
from django.urls import path

from config import settings
from .views import (CreateUserView, VerifyAPIView, GetNewVerification, ChangeUserInformationView,
                    ChangeUserPhotoView, LoginView, LoginRefreshView, LogoutView, ForgotPasswordView, ResetPasswordView
                    )

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('login/refresh/', LoginRefreshView.as_view(), name='login_refresh'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('signup/', CreateUserView.as_view(), name='create_user'),
    path('verify/', VerifyAPIView.as_view(), name='verify_user'),
    path('new-verify/', GetNewVerification.as_view(), name='new_verify'),
    path('change-user/', ChangeUserInformationView.as_view(), name='change_user'),
    path('change-user-photo/', ChangeUserPhotoView.as_view(), name='change_user_photo'),
    path('forgot-password/', ForgotPasswordView.as_view(), name='forgot_password'),
    path('reset-password/', ResetPasswordView.as_view(), name='reset_password'),
]

