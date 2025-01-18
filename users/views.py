from datetime import datetime

from django.shortcuts import render
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from shared.utility import send_email
from .models import User, DONE, CODE_VERIFIED, NEW, VIA_EMAIL, VIA_PHONE
from .serializers import SignUpSerializer
from rest_framework.generics import CreateAPIView

class CreateUserView(CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = SignUpSerializer

class VerifyAPIView(APIView):
    permission_classes = (IsAuthenticated)

    def post(self, request, *args, **kwargs):
        user = self.request.user
        code = request.data.get['code']

        self.check_verify(user, code)
        return Response(
            data = {
                "success": True,
                "auth_status": user.auth_status,
                "access_token": user.token()['access'],
                "refresh": user.token()['refresh_token'],
            }
        )

    @staticmethod
    def check_verify(user, code):
        verifies = user.verify_codes.filter(expiration_time__gte=datetime.now(), code=code, is_confirmed=False)
        if not verifies.exists():
            data = {
                "message": "Tasqidlash kodingiz xato yoki eskirgan!"
            }
            raise ValidationError(data)
        else:
            verifies.update(is_confirmed=True)

        if user.auth_status == NEW:
            user.auth_status = CODE_VERIFIED
            user.save()
        return True

class GetNewVerification(APIView):
    def get(self, request, *args, **kwargs):
        user = self.request.user
        self.check_verification(user)
        if user.auth_type == VIA_EMAIL:
            code = user.create_verify_code(VIA_EMAIL)
            send_email(user.email, code)
        elif user.auth_type == VIA_PHONE:
            code = user.create_verify_code(VIA_PHONE)
            send_email(user.phone_number, code)
        else:
            data = {
                "message": "Email yoki tel nomer notogri "
            }
            raise ValidationError(data)
        return Response(
            {
                "success": True,
                "message": "tasdiqlash kodingiz qaytadan jo'natildi "
            }
        )

    @staticmethod
    def check_verification(user, code):
            verifies = user.verify_codes.filter(expiration_time__gte=datetime.now(), is_confirmed=False)
            if verifies.exists():
                data = {
                    "message": "Kodingiz hali ishlatish uchun yaroqli biroz kutib turing"
                }
                raise ValidationError(data)