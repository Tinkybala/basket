from django.contrib import admin
from django.urls import path, include
from user import views as user_views

from . import views

urlpatterns = [
    path("", views.main, name="main"),
    path('admin/', admin.site.urls),
    path('profile/<int:user_id>/', user_views.profile, name='profile'),
    path('event/', include('event.urls')),
]