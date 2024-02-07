from django.urls import path
from . import views

urlpatterns = [
    path('', views.index),
    path('get_csrf_token/', views.get_csrf_token),
    path('login/', views.login),
    path('logout/', views.logout),
    path('notifications/<str:filter>/', views.get_notifications),
]
