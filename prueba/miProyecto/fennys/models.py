from django.db import models
from django.contrib.auth.models import AbstractUser 

# Definición de los roles para los usuarios
class Role(models.TextChoices):
    ADMIN = 'Admin', 'Admin'
    TENDER = 'Tendero', 'Tendero'
    CLIENT = 'Cliente', 'Cliente'

# Modelo de Usuario personalizado
class Usuario(models.Model):
    rol = models.CharField(
        max_length=10,
        choices=Role.choices,
        default=Role.CLIENT,
    )
    estado = models.BooleanField(default=True)
    foto = models.ImageField(upload_to='usuarios/', null=True, blank=True)
    token_recuperar = models.CharField(max_length=255, null=True, blank=True)
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)

    def __str__(self):
        return self.nombre

# Modelo de Categoría de productos
class Categoria(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    foto = models.ImageField(upload_to='categorias/', null=True, blank=True)

    def __str__(self):
        return self.nombre

# Modelo de Producto
class Producto(models.Model):
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField()
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    inventario = models.IntegerField()
    categoria = models.ForeignKey(Categoria, related_name='productos', on_delete=models.CASCADE)
    foto = models.ImageField(upload_to='productos/', null=True, blank=True)

    def __str__(self):
        return self.nombre

# Modelo de Pedido
class Pedido(models.Model):
    fecha = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f'Pedido {self.id} - Total: {self.total}'

# Modelo de Detalle del Pedido (productos dentro de un pedido)
class DetallePedido(models.Model):
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('completado', 'Completado'),
        ('cancelado', 'Cancelado'),
    ]

    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.IntegerField()
    precio = models.DecimalField(max_digits=10, decimal_places=2)

    @property
    def subtotal(self):
        return self.cantidad * self.precio

    def __str__(self):
        return f'{self.cantidad} x {self.producto.nombre}'

# Modelo de Historial de Pedido (para registrar los pedidos cancelados o completados)
class HistorialPedido(models.Model):
    pedido = models.ForeignKey(Pedido, related_name='historial', on_delete=models.CASCADE)
    fecha = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=10, choices=DetallePedido.ESTADO_CHOICES)  # Cambiado a DetallePedido
    total = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Historial {self.id} - Pedido {self.pedido.id}"

# Modelo de Venta (para registrar las ventas realizadas)
class Venta(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, blank=True)
    fecha_venta = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Venta {self.id}"


