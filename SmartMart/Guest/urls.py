from django.contrib import admin
from django.urls import path
from . import views

app_name = "guest"
urlpatterns = [
    path('', views.index, name='index'),
    path('user/', views.user_register, name='user_register'),
    path('seller/', views.seller_registration, name='seller_registration'),
    path('ajax_place/', views.ajax_place, name='ajax_place'),
    path('login/',views.login,name='login'),
]