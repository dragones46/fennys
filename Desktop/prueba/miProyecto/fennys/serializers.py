from rest_framework import serializers
from .models import Usuario, Categoria, Producto, Pedido, DetallePedido, HistorialPedido, Venta

class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = ['id', 'rol', 'estado', 'foto', 'token_recuperar', 'nombre', 'apellido', 'email', 'password']
        extra_kwargs = {
            'password': {'write_only': True},
        }

class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = ['id', 'nombre', 'descripcion', 'foto']

class ProductoSerializer(serializers.ModelSerializer):
    categoria = CategoriaSerializer(read_only=True)
    categoria_id = serializers.PrimaryKeyRelatedField(queryset=Categoria.objects.all(), source='categoria', write_only=True)

    class Meta:
        model = Producto
        fields = ['id', 'nombre', 'descripcion', 'precio', 'inventario', 'categoria', 'categoria_id', 'foto']

class DetallePedidoSerializer(serializers.ModelSerializer):
    producto = ProductoSerializer(read_only=True)
    producto_id = serializers.PrimaryKeyRelatedField(queryset=Producto.objects.all(), source='producto', write_only=True)
    subtotal = serializers.ReadOnlyField()

    class Meta:
        model = DetallePedido
        fields = ['id', 'pedido', 'producto', 'producto_id', 'cantidad', 'precio', 'subtotal']

class PedidoSerializer(serializers.ModelSerializer):
    detalles = DetallePedidoSerializer(many=True, read_only=True, source='detallepedido_set')

    class Meta:
        model = Pedido
        fields = ['id', 'fecha', 'total', 'detalles']

class HistorialPedidoSerializer(serializers.ModelSerializer):
    pedido = PedidoSerializer(read_only=True)
    pedido_id = serializers.PrimaryKeyRelatedField(queryset=Pedido.objects.all(), source='pedido', write_only=True)

    class Meta:
        model = HistorialPedido
        fields = ['id', 'pedido', 'pedido_id', 'fecha', 'estado', 'total']

class VentaSerializer(serializers.ModelSerializer):
    usuario = UsuarioSerializer(read_only=True)
    usuario_id = serializers.PrimaryKeyRelatedField(queryset=Usuario.objects.all(), source='usuario', write_only=True)

    class Meta:
        model = Venta
        fields = ['id', 'usuario', 'usuario_id', 'fecha_venta']
