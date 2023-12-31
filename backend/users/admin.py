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
    list_display_links = ('username',)


@admin.register(models.Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'author'
    )
