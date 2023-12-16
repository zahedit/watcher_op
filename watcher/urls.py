from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static
from user import views
from user.views import follow_user, unfollow_user


urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('user.urls')),
    path('content/', include('content.urls')),
    path('', TemplateView.as_view(template_name = 'index/base.html'), name='home'),
    path("u/<str:username>/", views.dashboard, name="profile"),
    # path('account/', UserUpdateView.as_view(), name="account"),
    path('follow/<str:username>/', follow_user, name='follow'),
    path('unfollow/<str:username>/', unfollow_user, name='unfollow'),
    path('u/<str:username>/followers/', views.followers, name='followers'),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)