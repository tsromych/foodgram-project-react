from django.db import transaction
from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework.serializers import (IntegerField, ModelSerializer,
                                        PrimaryKeyRelatedField, ReadOnlyField,
                                        SerializerMethodField, ValidationError)

from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredients,
                            ShoppingCart, Tag, User)
from users.models import Subscription
from .utils import Base64ImageField


class UserReadSerializer(UserSerializer):
    """Cписок пользователей (метод GET)."""
    is_subscribed = SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed'
        )

    def get_is_subscribed(self, obj):
        if (self.context.get('request')
           and not self.context['request'].user.is_anonymous):
            return Subscription.objects.filter(
                user=self.context['request'].user,
                author=obj).exists()
        return False


class RecipeSerializer(ModelSerializer):
    """Список рецептов."""
    name = ReadOnlyField()
    cooking_time = ReadOnlyField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )


class SubscribeSerializer(UserCreateSerializer):
    """Подписка на автора и отписка (методы GET, POST, DELETE)."""
    email = ReadOnlyField()
    username = ReadOnlyField()
    is_subscribed = SerializerMethodField()
    recipes = SerializerMethodField()
    recipes_count = SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count'
        )
        extra_kwargs = {
            'first_name': {'required': False, 'allow_blank': False},
            'last_name': {'required': False, 'allow_blank': False},
        }

    def validate(self, data):
        if self.context['request'].method == 'POST':
            user = self.context['request'].user
            author = self.context['author']
            if user == author:
                raise ValidationError('Нельзя подписаться на самого себя')
            if Subscription.objects.filter(user=user, author=author).exists():
                raise ValidationError('Нельзя оформить подписку дважды')
        return data

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        return (
            user.is_authenticated
            and Subscription.objects.filter(user=user, author=obj).exists()
        )

    def get_recipes(self, obj):
        request = self.context.get('request')
        recipes_limit = request.GET.get('recipes_limit')
        recipes = obj.recipes.all()
        if recipes_limit:
            recipes = recipes[:int(recipes_limit)]
        serializer = RecipeSerializer(recipes, many=True, read_only=True)
        return serializer.data

    def get_recipes_count(self, obj):
        return obj.recipes.count()


class IngredientSerializer(ModelSerializer):
    """Список ингредиентов (метод GET)."""

    class Meta:
        model = Ingredient
        fields = '__all__'


class TagSerializer(ModelSerializer):
    """Список тегов (метод GET)."""

    class Meta:
        model = Tag
        fields = '__all__'


class RecipeIngredientSerializer(ModelSerializer):
    """Список ингредиентов с количеством."""
    id = ReadOnlyField(source='ingredient.id')
    name = ReadOnlyField(source='ingredient.name')
    measurement_unit = ReadOnlyField(
        source='ingredient.measurement_unit')

    class Meta:
        model = RecipeIngredients
        fields = (
            'id',
            'name',
            'measurement_unit',
            'amount'
        )


class RecipeReadSerializer(ModelSerializer):
    """Список рецептов (метод GET)."""
    author = UserReadSerializer(read_only=True)
    tags = TagSerializer(many=True)
    ingredients = RecipeIngredientSerializer(
        many=True,
        read_only=True,
        source='recipes'
    )
    is_favorited = SerializerMethodField()
    is_in_shopping_cart = SerializerMethodField()
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time'
        )

    def get_is_favorited(self, obj):
        user = self.context['request'].user
        return (
            user.is_authenticated
            and Favorite.objects.filter(user__id=user.id, recipe=obj).exists()
        )

    def get_is_in_shopping_cart(self, obj):
        user = self.context['request'].user
        return (
            user.is_authenticated
            and ShoppingCart.objects.filter(user=user, recipe=obj).exists()
        )


class RecipeIngredientCreateSerializer(ModelSerializer):
    """Ингредиент и количество для создания рецепта."""
    id = IntegerField()

    class Meta:
        model = RecipeIngredients
        fields = (
            'id',
            'amount'
        )


class RecipeCreateSerializer(ModelSerializer):
    """Создание, изменение и удаление рецепта (методы POST, PATCH, DELETE)."""
    tags = PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True,
    )
    author = UserReadSerializer(read_only=True)
    ingredients = RecipeIngredientCreateSerializer(many=True)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'ingredients',
            'tags',
            'image',
            'name',
            'text',
            'cooking_time',
            'author'
        )
        extra_kwargs = {
            'ingredients': {'required': True, 'allow_blank': False},
            'tags': {'required': True, 'allow_blank': False},
            'name': {'required': True, 'allow_blank': False},
            'text': {'required': True, 'allow_blank': False},
            'image': {'required': True, 'allow_blank': False},
            'cooking_time': {'required': True},
        }

    def tags_and_ingredients_validating(self, current_obj, class_name):
        MODELS_DICT = {
            'tags': Tag,
            'ingredients': Ingredient
        }
        obj_list = []
        for item in current_obj:
            id = item if class_name == 'tags' else item['id']
            if not MODELS_DICT[class_name].objects.filter(id=id).exists():
                raise ValidationError('Указано несуществующее значение')
            current_model = MODELS_DICT[class_name].objects.get(id=id)
            if current_model in obj_list:
                raise ValidationError('Значения не могут повторяться')
            obj_list.append(current_model)

    def validate(self, data):
        tags = self.initial_data.get('tags')
        if not tags:
            raise ValidationError('Нужно указать минимум 1 тег.')
        self.tags_and_ingredients_validating(tags, 'tags')

        ingredients = data.get('ingredients')
        if not ingredients:
            raise ValidationError('Нужно указать минимум 1 ингредиент.')
        self.tags_and_ingredients_validating(ingredients, 'ingredients')
        return data

    @transaction.atomic
    def tags_and_ingredients_set(self, recipe, tags, ingredients):
        recipe.tags.set(tags)
        RecipeIngredients.objects.bulk_create(
            [RecipeIngredients(
                recipe=recipe,
                ingredient=Ingredient.objects.get(pk=ingredient['id']),
                amount=ingredient['amount']
            ) for ingredient in ingredients]
        )

    @transaction.atomic
    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(
            author=self.context['user'],
            **validated_data
        )
        self.tags_and_ingredients_set(recipe, tags, ingredients)
        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        instance.image = validated_data.get('image', instance.image)
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time)
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        RecipeIngredients.objects.filter(
            recipe=instance,
            ingredient__in=instance.ingredients.all()).delete()
        self.tags_and_ingredients_set(instance, tags, ingredients)
        instance.save()
        return instance

    def to_representation(self, instance):
        return RecipeReadSerializer(instance, context=self.context).data
