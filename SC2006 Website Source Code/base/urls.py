from django.urls import path
from . import views

urlpatterns = [
    path('', views.loginPage, name="login"),
    path('register/', views.registerUser, name="register"),
    path('logout/', views.logoutUser, name="logout"),
    path('home/', views.home, name="home"),
    path('room/<str:pk>/', views.room, name="room"),
    path('roomJoinEvent/<str:pk>/', views.roomJoinEvent, name="roomJoinEvent"),
    path('mainJoinEvent/event/<str:pk>/', views.mainJoinEvent, name='mainJoinEvent'),
    path('quitEvent/event/<str:pk>/', views.quitEvent, name='quitEvent'),
    path('profile/<str:pk>', views.userProfile, name="user-profile"),
    path('create-room/', views.createRoom, name="create-room"),
    path('update-room/<str:pk>/', views.updateRoom, name="update-room"),  
    path('delete-room/<str:pk>/', views.deleteRoom, name="delete-room"), 
    path('delete-message/<str:pk>/', views.deleteMessage, name="delete-message"), 
    path('update-user/', views.updateUser, name="update-user"),
    
]
