from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views

from app.views import csrf_token_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('app.urls')),
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    path('csrf-token/', csrf_token_view, name='csrf-token'),
]
