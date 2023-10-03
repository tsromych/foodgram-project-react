from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from . import models


@admin.register(models.CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = (
        'id',
        'username',
        'email',
        'first_name',
        'last_name',
    )
    list_filter = (
        'username',
        'email'
    )


@admin.register(models.Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    pass
