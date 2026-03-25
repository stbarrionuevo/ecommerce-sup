from django.urls import path
from . import views

urlpatterns = [
    
    path('', views.store, name="store"),
    path('carrito/',views.carrito, name="carrito"),
    path('agregar_al_carrito/<int:producto_id>/', views.agregar_item, name="agregar_al_carrito"),
    path('registro/',views.registro, name="registro"),
    path('checkout/',views.checkout, name="checkout"),
    path('perfil/', views.perfil, name='perfil'),
    path('procesar_pedido/', views.procesar_pedido, name="procesar_pedido"),
    path('ticket/<int:orden_id>/', views.ticket_exito, name="ticket_exito"),
    path('webhook-mp/', views.webhook_mercadopago, name='webhook_mp')
]