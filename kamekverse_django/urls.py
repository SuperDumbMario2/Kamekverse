"""
URL configuration for kamekverse_django project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from django.urls import path
from kamekverse import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.index),
    path('signup/', views.signup),
    path('login/', views.login),
    path('titles/<int:olive_title_id>/<int:olive_community_id>/hot', views.community_hot),
    path('titles/<int:olive_title_id>/<int:olive_community_id>/cold', views.community_cold),
    path('titles/<int:olive_title_id>/<int:olive_community_id>/new', views.community),
    path('titles/<int:olive_title_id>/<int:olive_community_id>', views.community),
    path('posts/<str:id>/empathies', views.posts_empathies_endpoint),
    path('posts/<str:id>/empathies.delete', views.posts_empathies_delete_endpoint),
    path('posts/<str:id>/nahs', views.posts_nahs_endpoint),
    path('posts/<str:id>/nahs.delete', views.posts_nahs_delete_endpoint),
    path('posts/<str:id>/replies', views.posts_replies_endpoint),
    path('posts/<str:id>/embed', views.post),
    path('posts/<str:id>.set_spoiler', views.post_set_spoiler),
    path('posts/<str:id>.delete', views.post_delete),
    path('posts/<str:id>', views.post),
    path('posts', views.posts_endpoint),
    path('users/<str:username>', views.user),
    path('replies/<str:id>/empathies', views.replies_empathies_endpoint),
    path('replies/<str:id>/empathies.delete', views.replies_empathies_delete_endpoint),
    path('replies/<str:id>/nahs', views.replies_nahs_endpoint),
    path('replies/<str:id>/nahs.delete', views.replies_nahs_delete_endpoint),
    path('js/embedded.min.js', views.embeddedminjs),
    path('api/server_config', views.api_server_config),
    path('logout', views.logoutv),
    path('toggle_neo', views.toggleneo),
    path('guide/terms', views.guide_terms),
    path('admin/', admin.site.urls),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
