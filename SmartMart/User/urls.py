from django.urls import path
from . import views

app_name = "user"

urlpatterns = [
    path('user_home/', views.user_home, name='user_home'),
    path('profile/', views.profile, name='profile'),
    path('edit_profile/', views.edit_profile, name='edit_profile'),
    path('change_password/', views.change_password, name='change_password'),
    
    path('search/', views.search, name='search'),
    path('add_to_cart/<int:id>/', views.add_to_cart, name='add_to_cart'),
    path('my_cart/', views.my_cart, name='my_cart'),
    path('cart/update/<int:cart_id>/<str:action>/', views.update_cart_quantity, name='update_cart_quantity'),
    path('cart/remove/<int:cart_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('checkout/', views.checkout_view, name='checkout'),
    path('place-order/', views.place_order, name='place_order'),
    path('payment/', views.payment, name='payment'),
    path('order-success/', views.order_success, name='order_success'),
    path('order_list/', views.order_list, name='order_list'),
    path('order/<int:order_id>/', views.order_detail, name='order_detail'),
    
    path('feedback/', views.add_feedback, name='feedback'),
    path('complaint/', views.add_complaint, name='complaint'),
    
    path('rating/<int:product_id>/', views.rating, name='rating'),
    
    path('logout/', views.logout, name='logout'),

]