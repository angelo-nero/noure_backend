"""
URL configuration for backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from api.views import (
    CategoryViewSet, DiscussionViewSet, CommentViewSet, 
    login_view, NewsViewSet, ProgrammingLanguageViewSet, 
    CodeSnippetViewSet, BlogViewSet, TagViewSet,
    user_list, toggle_user_status, create_user, update_user,
    GroupViewSet
)
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve
import os
from django.http import JsonResponse

# Create a router for admin endpoints
admin_router = DefaultRouter()
admin_router.register(r'categories', CategoryViewSet, basename='admin-category')
admin_router.register(r'languages', ProgrammingLanguageViewSet, basename='admin-language')
admin_router.register(r'roles', GroupViewSet, basename='admin-role')

# Create a router for regular endpoints
router = DefaultRouter()
router.register(r'discussions', DiscussionViewSet)
router.register(r'comments', CommentViewSet)
router.register(r'news', NewsViewSet)
router.register(r'languages', ProgrammingLanguageViewSet)
router.register(r'snippets', CodeSnippetViewSet)
router.register(r'tags', TagViewSet)
router.register(r'blogs', BlogViewSet)

def debug_media(request):
    return JsonResponse({
        'MEDIA_ROOT': settings.MEDIA_ROOT,
        'MEDIA_URL': settings.MEDIA_URL,
        'BASE_DIR': str(settings.BASE_DIR),
        'media_root_exists': os.path.exists(settings.MEDIA_ROOT),
        'media_root_contents': os.listdir(settings.MEDIA_ROOT) if os.path.exists(settings.MEDIA_ROOT) else [],
    })

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/admin/', include(admin_router.urls)),  # Admin endpoints
    path('api/login/', login_view, name='login'),
    path('api/admin/users/create/', create_user, name='create-user'),
    path('api/admin/users/', user_list, name='user-list'),
    path('api/admin/users/<int:user_id>/update/', update_user, name='update-user'),
    path('api/admin/users/<int:user_id>/toggle/', toggle_user_status, name='toggle-user-status'),
    path('blog_images/<path:path>', serve, {
        'document_root': settings.MEDIA_ROOT,
    }),
    path('api/debug-media/', debug_media, name='debug-media'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

print("MEDIA_ROOT exists:", os.path.exists(settings.MEDIA_ROOT))
print("MEDIA_ROOT contents:", os.listdir(settings.MEDIA_ROOT) if os.path.exists(settings.MEDIA_ROOT) else "Directory not found")
