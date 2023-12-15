from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from user.views import ProfileView, UserUpdateView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('user.urls')),
    path('content/', include('content.urls')),
    path('', TemplateView.as_view(template_name = 'index/base.html'), name='home'),
    path("u/<str:username>/", ProfileView.as_view(), name="profile"),
    path('account/', UserUpdateView.as_view(), name="account"),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)