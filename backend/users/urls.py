from django.urls import include, path
from rest_framework import routers

from api.views import CustomUserViewSet, SubscribeViewSet

app_name = 'users'

router_v1 = routers.DefaultRouter()
router_v1.register('users', CustomUserViewSet, basename='users')

urlpatterns = [
    path('users/<int:author_id>/subscribe/',
         SubscribeViewSet.as_view({'post': 'create', 'delete': 'delete'}),
         name='subscribe'),
    path('', include(router_v1.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
