from django.urls import path
from . import views

urlpatterns = [
    path('', views.loginUser, name="login"),
    path('register/', views.registerUser, name="register"),
    path('logout/', views.logoutUser, name="logout"),
    path('home/', views.home, name="home"),
    path('room/<str:pk>/', views.room, name="room"),
    path('mainJoinEvent/event/<str:pk>/', views.mainJoinEvent, name='mainJoinEvent'),
    path('quitEvent/event/<str:pk>/', views.quitEvent, name='quitEvent'),
    path('profile/<str:pk>', views.userProfile, name="user-profile"),
    path('create-room/', views.createRoom, name="create-room"),
    path('update-room/<str:pk>/', views.updateRoom, name="update-room"),  
    path('delete-room/<str:pk>/', views.deleteRoom, name="delete-room"), 
    path('update-user/', views.updateUser, name="update-user"),
    path('activate/<uidb64>/<token>', views.activate, name='activate'),
    path('update-notification-preferences/', views.updateNotificationPreferences, name='update-notification-preferences'),
    path('telegram', views.Telegram.as_view(), name="telegram"),
    
    # Other URL patterns
    path('forget-password/', views.forget_password, name='forget_password'),
    path('verify-code/', views.verify_code, name='verify_code'),
    path('reset-password/', views.reset_password, name='reset_password'),
    path('delete-user/', views.deleteUser, name="delete-user"),



    # For Future Use
    path('delete-message/<str:pk>/', views.deleteMessage, name="delete-message") 
    
]
