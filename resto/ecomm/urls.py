from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    # URLs publiques
    path('', views.index, name='index'),
    path('menu/', views.menu, name='menu'),
    path('panier/', views.panier, name='panier'),
    path('add-to-cart/<int:item_id>/', views.add_to_cart, name='add_to_cart'),
    path('update-cart-item/<int:item_id>/', views.update_cart_item, name='update_cart_item'),
    path('checkout/', views.checkout, name='checkout'),
    path('order-confirmation/<int:order_id>/', views.order_confirmation, name='order_confirmation'),
    path('my-orders/', views.my_orders, name='my_orders'),
    path('make-reservation/', views.make_reservation, name='make_reservation'),
    path('my-reservations/', views.my_reservations, name='my_reservations'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='index'), name='logout'),
    path('contact/', views.contact, name='contact'),

    # URLs du tableau de bord administrateur
    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('dashboard/orders/', views.admin_orders, name='admin_orders'),
    path('dashboard/orders/<int:order_id>/status/', views.update_order_status, name='update_order_status'),
    path('dashboard/reservations/', views.admin_reservations, name='admin_reservations'),
    path('dashboard/reservations/events/', views.admin_reservation_events, name='admin_reservation_events'),
    path('dashboard/reservations/<int:reservation_id>/status/', views.update_reservation_status, name='update_reservation_status'),
    path('dashboard/menu/', views.admin_menu, name='admin_menu'),
    path('dashboard/menu/add/', views.admin_menu_add, name='admin_menu_add'),
    path('dashboard/menu/<int:item_id>/edit/', views.admin_menu_edit, name='admin_menu_edit'),
    path('dashboard/menu/<int:item_id>/delete/', views.admin_menu_delete, name='admin_menu_delete'),
    path('dashboard/menu/<int:item_id>/availability/', views.admin_menu_availability, name='admin_menu_availability'),
] 