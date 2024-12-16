from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib import messages
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from django.urls import reverse
from urllib.parse import urlencode
from django.core.exceptions import ObjectDoesNotExist

from django.db.models import Q

#Para sacar totales de eventos.
from django.db.models import Sum
from django.shortcuts import render
import locale



from django.db.models import F
from collections import defaultdict

from django.utils import timezone
from datetime import timedelta

# Para tomar el from desde el settings
from django.conf import settings
from django.core.mail import EmailMessage, send_mail
import threading

# Para que muestre más detalles de un error
import traceback

# Importamos todos los modelos de la base de datos
from django.db import IntegrityError, transaction
from django.http import JsonResponse
import json

from django.utils import timezone

#APIVIEW
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny


#PARA EL PDF
from xhtml2pdf import pisa
from django.template.loader import render_to_string
import os
import tempfile
from django.core.files import File

from django.urls import reverse


from rest_framework import viewsets

from .serializers import *
from rest_framework import viewsets


#Importar el crypt
from .crypt import *

#Importar todos los modelos de la base de datos.
from .models import *

#Validar la fecha de Nacimiento
from datetime import datetime

# Para restringir las vistas
#from .decorators import rol_requerido
# Create your views here.

def index(request):
    productos = Producto.objects.all()
    return render(request, 'fennys/index.html', {'productos': productos})


def productos(request):
    productos_disponibles = Producto.objects.all()  # Obtenemos todos los productos desde la base de datos
    return render(request, 'fennys/productos/productos.html', {'productos': productos_disponibles})

# Vista para la página de contacto
def contacto(request):
    return render(request, 'fennys/contacto/contacto.html')
def lista_productos(request):
    productos = Producto.objects.all()
    return render(request, 'fennys/productos/lista_productos.html', {'productos': productos})

def agregar_al_carrito(request, producto_id):
    producto = Producto.objects.get(id=producto_id)
    pedido, created = Pedido.objects.get_or_create(total=0)  # Crear un nuevo pedido si no existe

    # Agregar el producto al pedido
    detalle = DetallePedido.objects.create(pedido=pedido, producto=producto, cantidad=1, precio=producto.precio)
    pedido.total += detalle.subtotal
    pedido.save()

    return redirect('lista_productos')

def cancelar_pedido(request, producto_id):
    try:
        # Aquí deberías tener lógica para cancelar un pedido específico
        # Por ejemplo, si estás eliminando un producto del carrito
        detalle = DetallePedido.objects.get(producto_id=producto_id)
        detalle.delete()
        messages.success(request, "Producto cancelado correctamente.")
    except DetallePedido.DoesNotExist:
        messages.error(request, "El producto no se encontró en el pedido.")
    return redirect('lista_productos')

def registro(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        if password1 != password2:
            messages.warning(request, "Las contraseñas no coinciden")
            return redirect("registro")

        if Usuario.objects.filter(email=email).exists():
            messages.warning(request, "El correo ya está registrado")
            return redirect("registro")

        # Crear el usuario
        Usuario.objects.create(
            nombre=nombre,
            email=email,
            password=hash_password(password1)
        )
        messages.success(request, "Usuario creado exitosamente")
        return redirect("login")

    return render(request, 'fennys/usuarios/registro.html')

# Vista para el login
def login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            user = Usuario.objects.get(email=email)
            if verify_password(password, user.password):
                request.session["logueo"] = {
                    "id": user.id,
                    "nombre": user.nombre,
                    "rol": user.rol,
                    "nombre_rol": user.get_rol_display(),
                    "foto": user.foto.url if user.foto else None  # Guardar la foto en la sesión
                }
                messages.success(request, "Has iniciado sesión exitosamente")
                return redirect("index")
            else:
                messages.error(request, "Credenciales incorrectas")
        except Usuario.DoesNotExist:
            messages.error(request, "Credenciales incorrectas")

    return render(request, 'fennys/usuarios/inisiar_sesion.html')

def logout(request):
    try:
        del request.session["logueo"]
        messages.success(request, "Sesión cerrada correctamente")
    except KeyError:
        messages.warning(request, "No hay sesión activa.")
    return redirect("index")