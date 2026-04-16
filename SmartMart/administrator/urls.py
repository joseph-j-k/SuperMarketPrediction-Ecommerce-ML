from django.contrib import admin
from django.urls import path
from . import views

app_name = "admin_pannel"
urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    
    path('district/', views.district, name='district'),
    path('district/eidt/<int:id>/', views.district_edit, name='district_edit'),
    path('district/delete/<int:id>/', views.district_delete, name='district_delete'),
    
    path('place/', views.place, name='place'),
    path('place/edit/<int:id>/',  views.place_edit, name='place_edit'),
    path('place/delete/<int:id>/', views.place_delete, name='place_delete'),
    
    path('category/', views.category, name='category'),
    path('category/edit/<int:id>/', views.category_edit, name='category_edit'),
    path('category/delete/<int:id>/', views.category_delete, name='category_delete'),
    
    path('sub_category/', views.sub_category, name='sub_category'),
    path('sub_category/edit/<int:id>/', views.sub_category_edit, name='sub_category_edit'),
    path('sub_category/delete/<int:id>/', views.sub_category_delete, name='sub_category_delete'),
    
    path('my_complaint/', views.my_complaint, name='my_complaint'),
    path('my_feedback/', views.my_feedback, name='my_feedback'),
    path('reply/<int:id>/', views.reply, name='reply'),
    
    path('sales-history/', views.sales_history, name='sales_history'),
    path('product_sales_distribution/',views.product_sales_distribution,name='product_sales_distribution'),
    path('sales-forecasting/', views.sales_forecasting, name='sales_forecasting'),
    path('analytics/', views.vendor_analytics, name='vendor_analytics'),



    path('logout/', views.logout, name='logout'),
]