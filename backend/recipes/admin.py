from django.contrib import admin
from django.contrib.admin import display

from . import models


@admin.register(models.Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'color',
        'slug'
    )


@admin.register(models.Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'measurement_unit'
    )
    list_filter = ('name',)


@admin.register(models.Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'author',
        'add_in_favorite'
    )
    list_filter = (
        'name',
        'author',
        'tags'
    )
    readonly_fields = ('add_in_favorite',)

    @display(description='В избранном')
    def add_in_favorite(self, obj):
        return obj.in_favorite.count()


@admin.register(models.RecipeIngredients)
class RecipeIngredientAdmin(admin.ModelAdmin):
    pass


@admin.register(models.Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    pass


@admin.register(models.ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    pass
