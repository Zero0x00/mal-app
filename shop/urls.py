from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('cart/add/', views.add_to_cart, name='add_to_cart'),
    path('cart/custom_add/', views.custom_add_to_cart, name='custom_add_to_cart'),
    path('cart/view/<int:user_id>/', views.view_cart_items, name='view_cart_items'),
    path('coupon/validate/', views.validate_coupon, name='validate_coupon'),
    path('greet/', views.greet_user, name='greet_user'),
    path('greet_safely/', views.greet_safely, name='greet_safely'),
    path('pii/send/', views.send_user_data, name='send_user_data'),
]