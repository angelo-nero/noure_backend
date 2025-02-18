from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ItemViewSet, 
    login_view,
    user_list,
    toggle_user_status,
    create_user,
    update_user,
    SnippetViewSet
)

router = DefaultRouter()
router.register(r'items', ItemViewSet)
router.register(r'snippets', SnippetViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('login/', login_view, name='login'),
    path('admin/users/create/', create_user, name='create-user'),
    path('admin/users/', user_list, name='user-list'),
    path('admin/users/<int:user_id>/update/', update_user, name='update-user'),
    path('admin/users/<int:user_id>/toggle/', toggle_user_status, name='toggle-user-status'),
] 