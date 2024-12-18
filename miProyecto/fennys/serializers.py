from rest_framework import serializers
from .models import *

class UsuarioSerializer(serializers.HyperlinkedModelSerializer, serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = ['id', 'rol', 'estado', 'foto', 'token_recuperar', 'nombre', 'apellido', 'email', 'password']
        extra_kwargs = {
            'password': {'write_only': True},
        }

class CategoriaSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Categoria
        fields = ['id', 'nombre', 'descripcion', 'foto']

class ProductoSerializer(serializers.HyperlinkedModelSerializer):
    categoria = CategoriaSerializer(read_only=True)
    categoria_id = serializers.PrimaryKeyRelatedField(queryset=Categoria.objects.all(), source='categoria', write_only=True)

    class Meta:
        model = Producto
        fields = ['id', 'nombre', 'descripcion', 'precio', 'inventario', 'categoria', 'categoria_id', 'foto']

class DetallePedidoSerializer(serializers.HyperlinkedModelSerializer):
    producto = ProductoSerializer(read_only=True)
    producto_id = serializers.PrimaryKeyRelatedField(queryset=Producto.objects.all(), source='producto', write_only=True)
    subtotal = serializers.ReadOnlyField()

    class Meta:
        model = DetallePedido
        fields = ['id', 'pedido', 'producto', 'producto_id', 'cantidad', 'precio', 'subtotal']

class PedidoSerializer(serializers.HyperlinkedModelSerializer):
    detalles = DetallePedidoSerializer(many=True, read_only=True, source='detallepedido_set')

    class Meta:
        model = Pedido
        fields = ['id', 'fecha', 'total', 'detalles']


