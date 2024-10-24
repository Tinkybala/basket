from django.urls import path
from . import views

urlpatterns = [
    path('<int:event_id>/', views.event_detail, name="event_detail"),
]