from django.contrib import admin
from django.urls import path, include

from . import views

urlpatterns = [
    path("", views.main, name="main"),
    path('admin/', admin.site.urls),
    path('user/', include('user.urls')),
]