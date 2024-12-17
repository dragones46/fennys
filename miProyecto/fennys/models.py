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
    fecha_nacimiento = models.DateField(null=True, blank=True)
    cedula = models.CharField(max_length=20, null=True, blank=True)  # Añadir el campo cedula

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
    precio = models.DecimalField(max_digits=10, decimal_places=0)
    inventario = models.IntegerField()
    categoria = models.ForeignKey(Categoria, related_name='productos', on_delete=models.CASCADE)
    foto = models.ImageField(upload_to='productos/', null=True, blank=True)

    def __str__(self):
        return self.nombre

# Modelo de Pedido
class Pedido(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)  # Agregar esta línea
    fecha = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    cantidad_total = models.IntegerField(default=0)  # Nuevo campo para contar productos

    def __str__(self):
        return f"Pedido {self.id} - Total: {self.total}"
    
# Modelo de Detalle del Pedido
class DetallePedido(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=1)
    precio = models.DecimalField(max_digits=10, decimal_places=2)

    @property
    def subtotal(self):
        return self.cantidad * self.precio
