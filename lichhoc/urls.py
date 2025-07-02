from django.urls import path
from lichhoc import views

urlpatterns = [
    path('api/', views.lichhoc_api),
    path('', views.home),
]
