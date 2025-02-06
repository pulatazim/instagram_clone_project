from django.contrib import admin
from .models import User, UserConfirmation


class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'email', 'phone_number')


class UserConfirmationAdmin(admin.ModelAdmin):
    list_display = ('user', 'code', 'is_confirmed', 'expiration_time')


admin.site.register(User, UserAdmin)
admin.site.register(UserConfirmation, UserConfirmationAdmin)
