from django.contrib import admin
from .models import *
from django.utils.html import mark_safe

@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ['id', 'nombre', 'email', 'rol', 'estado', 'foto']
    search_fields = ['nombre', 'email']
    list_filter = ['rol', 'estado']
    list_editable = ['rol', 'estado']

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ['id', 'nombre', 'precio', 'inventario', 'categoria', 'ver_foto']
    search_fields = ['nombre', 'precio']
    list_editable = ['precio', 'inventario']

    def ver_foto(self, obj):
        if obj.foto:
            return mark_safe(f"<a href='{obj.foto.url}'><img src='{obj.foto.url}' width='15%'></a>")
        return ""

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ['id', 'nombre', 'descripcion', 'ver_foto']
    search_fields = ['nombre']
    list_editable = ['descripcion']

    def ver_foto(self, obj):
        if obj.foto:
            return mark_safe(f"<a href='{obj.foto.url}'><img src='{obj.foto.url}' width='15%'></a>")
        return ""
