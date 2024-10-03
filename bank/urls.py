from django.contrib import admin
from django.urls import path, include

import app.urls

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(app.urls)),
    path('api/auth/', include('knox.urls')),
]
