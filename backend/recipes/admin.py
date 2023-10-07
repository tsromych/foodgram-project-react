from django.contrib import admin
from django.contrib.admin import display

from . import models
from .forms import DeleteFildInlineFormSet


class RecipeTagsInline(admin.TabularInline):
    formset = DeleteFildInlineFormSet
    model = models.RecipeTags
    extra = 0
    min_num = 1


class RecipeIngredientsInline(admin.TabularInline):
    formset = DeleteFildInlineFormSet
    model = models.RecipeIngredients
    extra = 0
    min_num = 1


@admin.register(models.Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'color',
        'slug'
    )
    list_filter = ('name',)
    search_fields = ('name',)


@admin.register(models.Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'measurement_unit'
    )
    list_filter = ('name',)
    search_fields = ('name',)


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
    inlines = (RecipeIngredientsInline, RecipeTagsInline,)
    list_display_links = ('name',)

    @display(description='В избранном')
    def add_in_favorite(self, obj):
        return obj.recipes_favorite_related.count()


@admin.register(models.RecipeIngredients)
class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = (
        'recipe',
        'ingredient',
        'amount'
    )


@admin.register(models.Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'recipe'
    )


@admin.register(models.ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'recipe'
    )
