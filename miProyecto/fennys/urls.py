from django.urls import path
from . import views

urlpatterns = [
    # Rutas inicio
    path('', views.index, name='index'),
    
    # Rutas de productos
    path('productos/', views.productos, name='productos'),
    path('productos/categoria/<int:categoria_id>/', views.filtrar_por_categoria, name='filtrar_por_categoria'),
    path('productos/<int:producto_id>/', views.detalle_producto, name='detalle_producto'),
    path('lista_productos/', views.lista_productos, name='lista_productos'),

    # Rutas de usuarios
    path('contacto/', views.contacto, name='contacto'),
    path('agregar/<int:producto_id>/', views.agregar_al_carrito, name='agregar_al_carrito'),
    path('registro/', views.registro, name='registro'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('ver_perfil/', views.ver_perfil, name='ver_perfil'),
    path('editar_perfil/<int:user_id>/', views.editar_perfil, name='editar_perfil'),
    path('cambiar_clave/', views.cambiar_clave, name='cambiar_clave'),

    # Rutas de carrito
    path('cancelar_producto/<int:producto_id>/', views.cancelar_producto, name='cancelar_producto'),
    path('pagar/', views.pagar, name='pagar'),
    path('cancelar_pedido/<int:pedido_id>/', views.cancelar_pedido, name='cancelar_pedido'),
    path('cambiar_cantidad/<int:producto_id>/', views.cambiar_cantidad, name='cambiar_cantidad'),
    path('carrito/', views.ver_carrito, name='ver_carrito'),
    path('eliminar_producto/<int:producto_id>/', views.eliminar_producto, name='eliminar_producto'),
    path('borrar_todo/', views.borrar_todo, name='borrar_todo'),
    path('cancelar_todo/', views.cancelar_todo, name='cancelar_todo'),
]
