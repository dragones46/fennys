from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('productos/', views.productos, name='productos'),
    path('contacto/', views.contacto, name='contacto'),
    path('agregar/<int:producto_id>/', views.agregar_al_carrito, name='agregar_al_carrito'),
    path('registro/', views.registro, name='registro'),
    path('login/', views.login, name='login'),
    path('lista_productos/', views.lista_productos, name='lista_productos'),
    path('logout/', views.logout, name='logout'),
    path('cancelar_producto/<int:producto_id>/', views.cancelar_producto, name='cancelar_producto'),
    path('ver_perfil/', views.ver_perfil, name='ver_perfil'),
    path('editar_perfil/<int:user_id>/', views.editar_perfil, name='editar_perfil'),
    path('cambiar_clave/', views.cambiar_clave, name='cambiar_clave'),
    path('pagar/', views.pagar, name='pagar'),
    path('cancelar_pedido/<int:pedido_id>/', views.cancelar_pedido, name='cancelar_pedido'),
    path('cambiar_cantidad/<int:producto_id>/', views.cambiar_cantidad, name='cambiar_cantidad'),
]
