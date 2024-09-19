from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from app.views import csrf_token_view
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('app.urls')),
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('csrf-token/', csrf_token_view, name='csrf-token'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
