from django.contrib.auth import authenticate
from django.contrib.auth.models import update_last_login
from django.contrib.auth.password_validation import validate_password
from django.core.validators import FileExtensionValidator
from rest_framework import serializers, exceptions
from django.db.models import Q
from rest_framework.generics import get_object_or_404
from rest_framework_simplejwt.serializers import TokenObtainSerializer, TokenRefreshSerializer
from rest_framework_simplejwt.tokens import AccessToken

from shared.utility import check_email_or_phone, send_email, send_phone_code, check_user_type
from .models import User, UserConfirmation, VIA_EMAIL, VIA_PHONE, CODE_VERIFIED, DONE, NEW, PHOTO_DONE
from rest_framework.exceptions import ValidationError, PermissionDenied, NotFound


class SignUpSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)

    def __init__(self, *args, **kwargs):
        super(SignUpSerializer, self).__init__(*args, **kwargs)
        self.fields['email_phone_number'] = serializers.CharField(required=False)

    class Meta:
        model = User
        fields = (
            'id',
            'auth_type',
            'auth_status'
        )
        extra_kwargs = {
            'auth_type': {'read_only': True, 'required': False},
            'auth_status': {'read_only': True, 'required': False},
        }

    def create(self, validated_data):
        user = super(SignUpSerializer, self).create(validated_data)
        if user.auth_type == VIA_EMAIL:
            code = user.create_verify_code(VIA_EMAIL)
            send_email(user.email, code)
        elif user.auth_type == VIA_PHONE:
            code = user.create_verify_code(VIA_PHONE)
            send_email(user.phone_number, code)
            # send_phone_code(user.phone_number, code)
        user.save()
        return user

    def validate(self, data):
        super(SignUpSerializer, self).validate(data)
        data = self.auth_validate(data)
        return data

    @staticmethod
    def auth_validate(data):
        print(data)
        user_input = str(data.get('email_phone_number')).lower()
        input_type = check_email_or_phone(user_input)
        if input_type == 'email':
            data = {
                'email': user_input,
                "auth_type": VIA_EMAIL
            }
        elif input_type == 'phone':
            data = {
                'phone_number': user_input,
                "auth_type": VIA_PHONE
            }
        else:
            data = {
                'success': False,
                'message': "Email yoki tel nomer jo'natishingiz kerak!"
            }
            raise ValidationError(data)
        return data

    def validate_email_phone_number(self, value):
        value = value.lower()
        if value and User.objects.filter(email=value).exists():
            data = {
                "success": False,
                "message": "Bu email allaqachon ma'lumotlar bazasida bor"
            }
            raise ValidationError(data)
        elif value and User.objects.filter(phone_number=value).exists():
            data = {
                "success": False,
                "message": "Bu telefon raqami allaqachon ma'lumotlar bazasida bor"
            }
            raise ValidationError(data)
        return value

    def to_representation(self, instance):
        # print("to_rep", instance)
        data = super(SignUpSerializer, self).to_representation(instance)
        data.update(instance.token())
        return data


class ChangeUserInformation(serializers.ModelSerializer):
    first_name = serializers.CharField(write_only=True, required=True)
    last_name = serializers.CharField(write_only=True, required=True)
    username = serializers.CharField(write_only=True, required=True)
    email = serializers.CharField(write_only=True, required=True)
    confirm_password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username', 'email', 'password', 'confirm_password')

    def validate(self, data):
        password = data.get('password', None)
        confirm_password = data.get('confirm_password', None)
        if password != confirm_password:
            raise ValidationError(
                {
                    "message": "Parollaringiz bir biriga mos kelmadi!"
                }
            )
        if password:
            validate_password(password)
            validate_password(confirm_password)

        return data

    @staticmethod
    def validate_username(username):
        if len(username) < 5 or len(username) > 35:
            raise ValidationError(
                {
                    "message": "Username 5 ta dan kam va 35 tadan ko'p bo'lmasligi kerak"
                }
            )

        if username.isdigit():
            raise ValidationError(
                {
                    "mesage": "Username faqatgina raqamdan iborat bo'lishi mukin emas"
                }
            )
        return username

    def update(self, instance, validated_data):
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.password = validated_data.get('password', instance.password)
        instance.username = validated_data.get('username', instance.username)

        if validated_data.get('password'):
            instance.set_password(validated_data.get('password'))
        if instance.auth_status == CODE_VERIFIED:
            instance.auth_status = DONE
        instance.save()
        return instance


class ChangeUserPhotoSerializer(serializers.Serializer):
    photo = serializers.ImageField(validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png'])])

    def update(self, instance, validated_data):
        photo = validated_data.get('photo')
        if photo:
            instance.image = photo
            instance.auth_status = DONE
            instance.save()
        return instance


class LoginSerializer(TokenObtainSerializer):
    def __init__(self, *args, **kwargs):
        super(LoginSerializer, self).__init__(*args, **kwargs)
        self.fields['userinput'] = serializers.CharField(required=True)
        self.fields['username'] = serializers.CharField(read_only=True)

    def auth_validate(self, data):
        user_input = data.get('userinput')
        if check_user_type(user_input) == 'username':
            username = user_input
        elif check_user_type(user_input) == 'email':
            user = self.get_user(email__iexact=user_input)
            username = user.username
        elif check_user_type(user_input) == 'phone':
            user = self.get_user(phone_number=user_input)
            username = user.username
        else:
            data = {
                'success': False,
                'message': "Siz username, email yoki telefon raqami jo'natishingiz kerak!"
            }
            raise ValidationError(data)

        authentication_kwargs = {
            self.username_field: username,
            "password": data['password']
        }

        # user status tekshirilishi kerak
        current_user = User.objects.filter(username__iexact=username).first()
        if current_user is not None and current_user.auth_status in [NEW, CODE_VERIFIED]:
            raise ValidationError({
                "success": False,
                "message": "Siz ro'yhatdan to'liq o'tmagansiz"
            })

        user = authenticate(authentication_kwargs)

        if user is not None:
            self.user = user
        else:
            raise ValidationError({
                "success": False,
                "message": "Kechirasiz! login va parolingiz noto'g'ri! Iltimos tekshirib, qaytadan urinib ko'ring! "
            })

    def validate(self, data):
        self.auth_validate(data)
        if self.user.auth_status not in [DONE, PHOTO_DONE]:
            raise PermissionDenied("Siz login qila olmaysiz, ruxsatingiz yo'q!")
        data = self.user.token()
        data['auth_status'] = self.user.auth_status
        data['full_name'] = self.user.full_name
        return data

    def get_user(self, **kwargs):
        users = User.objects.filter(**kwargs)
        if not users.exists():
            raise ValidationError({
                "message": "No active account found"
            })
        return users.first()


# Login Refresh token
class LoginRefreshSerializer(TokenRefreshSerializer):

    def validate(self, attrs):
        data = super().validate(attrs)
        access_token_instance = AccessToken(data['access'])
        user_id = access_token_instance['user_id']
        user = get_object_or_404(User, id=user_id)
        update_last_login(None, user)


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()


class ForgotPasswordSerializer(serializers.Serializer):
    email_or_phone = serializers.CharField(write_only=True, required=True)

    def validate(self, attrs):
        email_or_phone = attrs.get('email_or_phone', None)
        if email_or_phone is None:
            raise ValidationError({
                "success": False,
                "message": "Email yoki teleefon raqami kiritilishi shart!"
            })
        user = User.objects.filter(Q(phone_number=email_or_phone) | Q(email=email_or_phone))
        if not user.exists():
            raise NotFound(detail="User topilmadi")
        attrs['user'] = user.first()
        return attrs



class ResetPasswordSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    password = serializers.CharField(min_length=8, write_only=True, required=True)
    confirm_password = serializers.CharField(min_length=8, write_only=True, required=True)

    class Meta:
        model = User
        fields = ('id', 'password', 'confirm_password')

    def validate(self, attrs):
        password = attrs.get('password', None)
        confirm_password = attrs.get('confirm_password', None)
        if password != confirm_password:
            raise ValidationError({
                "success": False,
                "message": "Parollaringiz bir-biriga teng emas!"
            })
        if password:
            validate_password(password)
            return attrs

    def update(self, instance, validated_data):
        password = validated_data.pop('password')
        instance.set_password(password)
        return super(ResetPasswordSerializer, self).update(instance, validated_data)