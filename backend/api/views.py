from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredients,
                            ShoppingCart, Tag, User)
from users.models import Subscription
from .filters import IngredientFilter, RecipeFilter
from .pagination import CustomPagination
from .permissions import IsAuthorOrReadOnly
from .serializers import (IngredientSerializer, RecipeCreateSerializer,
                          RecipeReadSerializer, RecipeSerializer,
                          SubscribeSerializer, TagSerializer,
                          UserReadSerializer)


class CustomUserViewSet(UserViewSet):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    pagination_class = CustomPagination

    @action(
        detail=False,
        methods=['get'],
        permission_classes=(IsAuthenticated,)
    )
    def me(self, request):
        serializer = UserReadSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        detail=False,
        methods=['get'],
        serializer_class=SubscribeSerializer,
        permission_classes=(IsAuthenticated,)
    )
    def subscriptions(self, request):
        queryset = User.objects.filter(subscribing__user=request.user)
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(
            page,
            many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)


class SubscribeViewSet(mixins.ListModelMixin,
                       mixins.CreateModelMixin,
                       mixins.DestroyModelMixin,
                       viewsets.GenericViewSet):
    permission_classes = (IsAuthenticated,)
    pagination_class = CustomPagination

    def create(self, request, author_id=None):
        user = request.user
        author = get_object_or_404(User, id=author_id)
        serializer = SubscribeSerializer(
            author,
            data=request.data,
            context={'author': author, 'request': request}
        )
        if serializer.is_valid(raise_exception=True):
            Subscription.objects.create(user=user, author=author)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, tatus=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, author_id=None):
        user = request.user
        author = get_object_or_404(User, id=author_id)
        subscribe = Subscription.objects.filter(user=user, author=author)
        if not subscribe:
            return Response(
                'Подписки не существует, или она уже удалена',
                status=status.HTTP_400_BAD_REQUEST
            )
        subscribe.delete()
        return Response('Вы успешно отписались от автора',
                        status=status.HTTP_204_NO_CONTENT)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    permission_classes = (AllowAny, )
    serializer_class = IngredientSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter
    pagination_class = None


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    permission_classes = (AllowAny, )
    serializer_class = TagSerializer
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    pagination_class = CustomPagination
    permission_classes = (IsAuthorOrReadOnly, )
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeReadSerializer
        return RecipeCreateSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            data=request.data,
            context={'user': request.user, 'request': request}
        )
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(
            instance,
            data=request.data,
            partial=True
        )
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def recipe_additional_info(self, model, req, pk):
        user = req.user
        if req.method == 'POST':
            if not Recipe.objects.filter(id=pk).exists():
                return Response(
                    'Указанного рецепта не существует',
                    status=status.HTTP_400_BAD_REQUEST
                )
            recipe = Recipe.objects.get(id=pk)
            if model.objects.filter(user=user, recipe=recipe).exists():
                return Response(
                    'Рецепт уже добавлен',
                    status=status.HTTP_400_BAD_REQUEST
                )
            model.objects.create(user=user, recipe=recipe)
            serializer = RecipeSerializer(recipe, context={'request': req})
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )

        if req.method == 'DELETE':
            recipe = get_object_or_404(Recipe, id=pk)
            current_model = model.objects.filter(user=user, recipe=recipe)
            if not current_model.exists():
                return Response(
                    'Указанного рецепта нет, или он уже удален',
                    status=status.HTTP_400_BAD_REQUEST
                )
            current_model.delete()
            return Response(
                'Рецепт успешно удален',
                status=status.HTTP_204_NO_CONTENT
            )

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=(IsAuthenticated,),
    )
    def favorite(self, request, **kwargs):
        return self.recipe_additional_info(Favorite, request, kwargs['pk'])

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=(IsAuthenticated,),
        pagination_class=None
    )
    def shopping_cart(self, request, **kwargs):
        return self.recipe_additional_info(ShoppingCart, request, kwargs['pk'])

    @action(
        detail=False,
        methods=['get'],
        permission_classes=(IsAuthenticated,)
    )
    def download_shopping_cart(self, request, **kwargs):
        ingredients = (
            RecipeIngredients.objects
            .filter(recipe__recipes_shoppingcart_related__user=request.user)
            .values('ingredient')
            .annotate(total_amount=Sum('amount'))
            .values_list('ingredient__name', 'total_amount',
                         'ingredient__measurement_unit')
        )
        file_list = []
        [file_list.append(
            '{} - {} {}.'.format(*ingredient)) for ingredient in ingredients]
        file = HttpResponse('Cписок покупок:\n' + '\n'.join(file_list),
                            content_type='text/plain')
        file['Content-Disposition'] = ('attachment; '
                                       'filename="shopping_cart.txt"')
        return file
