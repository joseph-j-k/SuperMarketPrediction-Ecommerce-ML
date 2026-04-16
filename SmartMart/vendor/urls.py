from django.urls import path
from .import views

app_name ="vendor"
urlpatterns=[
    path('vendor_home/', views.vendor_home, name='vendor_home'),
    path('profile/', views.profile, name='profile'),
    path('edit_profile/', views.edit_profile, name='edit_profile'),
    path('change_password/', views.change_password, name='change_password'),
    
    path('ajax_subcategory/', views.ajax_subcategory, name='ajax_subcategory'),
    path('product/', views.product, name='product'),
    path('product_list/', views.product_list, name='product_list'),
    path('delete_product/delete/<int:id>/', views.delete_product, name='delete_product'),
    
    path('order_list/', views.order_list, name='order_list'),
    path('order/<int:order_id>/', views.order_detail, name='order_detail'),
    
    path('feedback/', views.add_feedback, name='feedback'),
    path('complaint/', views.add_complaint, name='complaint'),
    
    path('sales/history/', views.vendor_sales_history, name='sales_history'),
    path('sales/forecast/', views.vendor_sales_forecast, name='sales_forecast'),

    path('logout/', views.logout, name='logout'),
]