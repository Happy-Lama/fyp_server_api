from django.urls import path
from . import views

urlpatterns = [
    path('api/', views.index),
    path('transformers/latest/', views.get_latest_transformer_data),
    path('transformers/register/', views.register),
    path('transformers/average_values/', views.get_average_values),
]