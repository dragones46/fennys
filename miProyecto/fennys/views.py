from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import *
from .crypt import hash_password, verify_password
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from django.core.mail import send_mail
from django.conf import settings



def index(request):
    productos = Producto.objects.all()
    
    # Obtener el carrito de la sesión
    carrito = request.session.get('carrito', {})

    # Calcular el total del carrito
    total_carrito = 0
    cantidad_total = 0
    for item in carrito.values():
        total_carrito += int(item['cantidad']) * float(item['precio'])
        cantidad_total += int(item['cantidad'])

    return render(request, 'fennys/index.html', {
        'productos': productos,
        'carrito': carrito,
        'total_carrito': total_carrito,
        'cantidad_total': cantidad_total  # Pasar la cantidad total al contexto
    })

def productos(request):
    productos = Producto.objects.all()
    categorias = Categoria.objects.all()

    # Obtener el carrito de la sesión
    carrito = request.session.get('carrito', {})

    # Calcular el total del carrito
    total_carrito = 0
    cantidad_total = sum(item['cantidad'] for item in carrito.values())

    return render(request, 'fennys/productos/productos.html', {
        'productos': productos,
        'categorias': categorias,
        'cantidad_total': cantidad_total  # Pasar la cantidad total al contexto
    })


def contacto(request):
    if request.method == 'POST':
        # Recibir los datos del formulario
        nombre = request.POST.get('nombre')
        correo = request.POST.get('correo')
        mensaje = request.POST.get('mensaje')
        tipo_mensaje = request.POST.get('tipo_mensaje')

        # Definir el asunto con el tipo de mensaje
        asunto = f"{tipo_mensaje}: Nuevo mensaje de contacto de {nombre}"

        # Definir el color para el cuerpo del correo
        if tipo_mensaje == 'Exigencia':
            color = 'orange'
        elif tipo_mensaje == 'Reclamo':
            color = 'red'
        elif tipo_mensaje == 'Felicitación':
            color = 'green'
        elif tipo_mensaje == 'Sugerencia':
            color = 'blue'
        else:
            color = 'black'

        # Validar que todos los campos estén llenos
        if nombre and correo and mensaje:
            try:
                # Crear el mensaje con el correo del usuario incluido y color en el mensaje
                mensaje_correo = f"""
                    <p><strong>De:</strong> {nombre} &lt;{correo}&gt;</p>
                    <p><strong>Mensaje:</strong></p>
                    <p style="color:{color};">{mensaje}</p>
                """

                # Enviar el correo al administrador (a tu correo)
                send_mail(
                    asunto,
                    '',  # El cuerpo en blanco (ya lo pondremos en el HTML)
                    correo,  # El correo del que envía
                    [settings.CONTACT_EMAIL],  # Correo al que se enviará el mensaje
                    fail_silently=False,
                    html_message=mensaje_correo  # Esto permite el envío de HTML en el correo
                )

                # Mensaje de éxito
                messages.success(request, '¡Gracias por tu mensaje! Nos pondremos en contacto pronto.')
                return redirect('contacto')  # Redirige a la vista de contacto
            except Exception as e:
                # Si ocurre un error en el envío del correo
                messages.error(request, 'Hubo un error al enviar tu mensaje. Intenta nuevamente.')
                return redirect('contacto')
        else:
            # Si falta algún campo
            messages.error(request, 'Por favor, llena todos los campos correctamente.')
            return redirect('contacto')
    else:
        # Obtener el carrito de la sesión
        carrito = request.session.get('carrito', {})

        # Calcular el total del carrito
        total_carrito = 0
        cantidad_total = 0
        for item in carrito.values():
            total_carrito += int(item['cantidad']) * float(item['precio'])
            cantidad_total += int(item['cantidad'])

        # Si la solicitud es GET, solo se muestra el formulario vacío
        return render(request, 'fennys/contacto/contacto.html', {
            'carrito': carrito,
            'total_carrito': total_carrito,
            'cantidad_total': cantidad_total  # Pasar la cantidad total al contexto
        })


def lista_productos(request):
    # Obtener todas las categorías para el filtro
    categorias = Categoria.objects.all()
    categoria_id = request.GET.get('categoria')

    # Filtrar productos según la categoría seleccionada
    if categoria_id:
        productos = Producto.objects.filter(categoria_id=categoria_id)
        categoria_seleccionada = get_object_or_404(Categoria, id=categoria_id)
    else:
        productos = Producto.objects.all()
        categoria_seleccionada = None

    # Obtener el carrito de la sesión
    carrito = request.session.get('carrito', {})

    # Calcular el total del carrito
    total_carrito = 0
    for item in carrito.values():
        total_carrito += int(item['cantidad']) * float(item['precio'])

    # Calcular la cantidad total de productos en el carrito
    cantidad_total = sum(item['cantidad'] for item in carrito.values())

    return render(request, 'fennys/productos/lista_productos.html', {
        'productos': productos,
        'categorias': categorias,
        'categoria_seleccionada': categoria_seleccionada,
        'carrito': carrito,
        'total_carrito': total_carrito,
        'cantidad_total': cantidad_total  # Pasar la cantidad total al contexto
    })

def agregar_al_carrito(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)

    # Inicializar el carrito en la sesión si no existe
    if 'carrito' not in request.session:
        request.session['carrito'] = {}

    # Verificar el inventario
    if producto.inventario <= 0:
        messages.warning(request, f"{producto.nombre} está agotado.")
        return redirect('lista_productos')

    # Agregar el producto al carrito
    if str(producto.id) in request.session['carrito']:
        request.session['carrito'][str(producto.id)]['cantidad'] += 1
    else:
        request.session['carrito'][str(producto.id)] = {
            'nombre': producto.nombre,
            'precio': str(producto.precio),
            'cantidad': 1,
            'foto': producto.foto.url if producto.foto else None,
            'subtotal': float(producto.precio),
            'inventario': producto.inventario
        }

    # Guardar el carrito en la sesión
    request.session.modified = True

    # Calcular la cantidad total de productos en el carrito
    cantidad_total = sum(item['cantidad'] for item in request.session['carrito'].values())
    messages.success(request, f"{producto.nombre} ha sido agregado al carrito.")
    
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

def cancelar_producto(request, producto_id):
    if 'carrito' in request.session:
        if str(producto_id) in request.session['carrito']:
            del request.session['carrito'][str(producto_id)]
            request.session.modified = True
            messages.success(request, "Producto cancelado del carrito.")
        else:
            messages.warning(request, "El producto no está en el carrito.")
    else:
        messages.warning(request, "El carrito está vacío.")
    return redirect('ver_carrito')


def cambiar_cantidad(request, producto_id):
    if request.method == 'POST':
        cantidad = int(request.POST.get('cantidad'))
        
        # Verificar que el producto esté en el carrito
        if 'carrito' in request.session and str(producto_id) in request.session['carrito']:
            producto = request.session['carrito'][str(producto_id)]
            
            # Limitar la cantidad a no más que el inventario disponible
            if cantidad <= producto['inventario']:
                producto['cantidad'] = cantidad
                producto['subtotal'] = float(producto['precio']) * cantidad  # Calcular el subtotal aquí
                request.session.modified = True

                # Recalcular el total del carrito
                total_carrito = 0
                for item in request.session['carrito'].values():
                    total_carrito += item['subtotal']

                messages.success(request, "Cantidad actualizada en el carrito.")
                return JsonResponse({'success': True, 'total_carrito': total_carrito})

            else:
                messages.warning(request, "La cantidad excede el inventario disponible.")
        else:
            messages.warning(request, "El producto no está en el carrito.")
    
    return JsonResponse({'success': False})





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

        Usuario.objects.create(
            nombre=nombre,
            email=email,
            password=hash_password(password1)
        )
        messages.success(request, "Usuario creado exitosamente")
        return redirect("login")

    return render(request, 'fennys/usuarios/registro.html')

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
                    "foto": user.foto.url if user.foto else None
                }
                messages.success(request, "Has iniciado sesión exitosamente")
                return redirect("index")
            else:
                messages.warning(request, "Usuario o contraseña incorrectos")
        except Usuario.DoesNotExist:
            messages.warning(request, "Usuario no encontrado o no existe")

    return render(request, 'fennys/usuarios/inisiar_sesion.html')


def logout(request):
    if "logueo" in request.session:
        del request.session["logueo"]
        messages.success(request, "Sesión cerrada correctamente")
    else:
        messages.warning(request, "No hay sesión activa.")
    return redirect("index")

@login_required
def ver_perfil(request):
    logueo = request.session.get("logueo", False)
    if not logueo:
        return redirect('login')

    user = get_object_or_404(Usuario, pk=logueo["id"])

    ruta = "fennys/perfil/ver_perfil.html"

    roles = Role.choices
    estado = user.estado
    contexto = {'user': user, 'roles': roles, 'estado': estado, 'url': 'Perfil'}
    return render(request, ruta, contexto)

@login_required
def editar_perfil(request, user_id):
    user = get_object_or_404(Usuario, pk=user_id)

    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        email = request.POST.get('email')
        cedula = request.POST.get('cedula')
        fecha_nacimiento = request.POST.get('fechaNacimiento')
        foto_nueva = request.FILES.get('foto_nueva')

        user.nombre = nombre
        user.email = email
        user.cedula = cedula
        user.fecha_nacimiento = fecha_nacimiento

        if foto_nueva:
            user.foto = foto_nueva

        user.save()

        # Actualizar la sesión del usuario
        if 'logueo' in request.session:
            request.session['logueo']['foto'] = user.foto.url if user.foto else None
            request.session.modified = True

        messages.success(request, "Perfil actualizado exitosamente")
        return redirect('ver_perfil')

    return render(request, 'fennys/perfil/editar_perfil.html', {'user': user})


@login_required
def cambiar_clave(request):
    if request.method == 'POST':
        clave_actual = request.POST.get('clave')
        nueva1 = request.POST.get('nueva1')
        nueva2 = request.POST.get('nueva2')

        user = get_object_or_404(Usuario, pk=request.session["logueo"]["id"])

        if not verify_password(clave_actual, user.password):
            messages.error(request, "La contraseña actual es incorrecta")
            return redirect('ver_perfil')

        if nueva1 != nueva2:
            messages.error(request, "Las nuevas contraseñas no coinciden")
            return redirect('ver_perfil')

        user.password = hash_password(nueva1)
        user.save()
        messages.success(request, "Contraseña cambiada exitosamente")
        return redirect('ver_perfil')

    return redirect('ver_perfil')

def pagar(request):
    if 'carrito' in request.session and request.session['carrito']:
        carrito = request.session['carrito']
        
        for key, item in carrito.items():
            producto = get_object_or_404(Producto, id=key)
            
            # Reducir el inventario de cada producto según la cantidad comprada
            if producto.inventario >= item['cantidad']:
                producto.inventario -= item['cantidad']
                producto.save()
            else:
                messages.warning(request, f"Inventario insuficiente para {producto.nombre}. No se realizó el pago.")

        # Vaciar el carrito después de procesar el pago
        request.session['carrito'] = {}
        request.session.modified = True
        messages.success(request, "Pago realizado correctamente.")
    else:
        messages.warning(request, "No hay productos en el carrito para pagar.")
    return redirect('lista_productos')

def ver_carrito(request):
    carrito = request.session.get('carrito', {})

    # Calcular el total del carrito
    total_carrito = 0
    cantidad_total = 0
    for item in carrito.values():
        # Asegurarse de que 'subtotal' siempre esté presente
        if 'subtotal' not in item:
            item['subtotal'] = float(item['precio']) * item['cantidad']  # Calcularlo si no existe
        total_carrito += item['subtotal']  # Actualizar el total
        cantidad_total += item['cantidad']  # Actualizar la cantidad total

    return render(request, 'fennys/productos/carrito.html', {
        'carrito': carrito,
        'total_carrito': total_carrito,
        'cantidad_total': cantidad_total
    })

def borrar_todo(request):
    if 'carrito' in request.session:
        request.session['carrito'] = {}
        request.session.modified = True
        messages.success(request, "El carrito ha sido borrado exitosamente.")
    else:
        messages.warning(request, "El carrito está vacío.")
    return redirect('ver_carrito')  # Redirige a la página del carrito

def eliminar_producto(request, producto_id):
    if 'carrito' in request.session:
        carrito = request.session['carrito']
        if str(producto_id) in carrito:
            del carrito[str(producto_id)]  # Eliminar el producto específico
            request.session.modified = True
            messages.success(request, "Producto eliminado del carrito.")
        else:
            messages.warning(request, "El producto no está en el carrito.")
    else:
        messages.warning(request, "El carrito está vacío.")
    return redirect('ver_carrito')


def cancelar_todo(request):
    if 'carrito' in request.session:
        request.session['carrito'] = {}
        request.session.modified = True
        messages.success(request, "Todas las compras han sido canceladas.")
    else:
        messages.warning(request, "El carrito está vacío.")
    return redirect('ver_carrito')

def filtrar_por_categoria(request, categoria_id=None):
    # Obtener todas las categorías para el filtro
    categorias = Categoria.objects.all()

    # Filtrar productos según la categoría seleccionada
    if categoria_id:
        productos = Producto.objects.filter(categoria_id=categoria_id)
        categoria_seleccionada = get_object_or_404(Categoria, id=categoria_id)
    else:
        productos = Producto.objects.all()
        categoria_seleccionada = None

    return render(request, 'fennys/productos/lista_productos.html', {
        'productos': productos,
        'categorias': categorias,
        'categoria_seleccionada': categoria_seleccionada,
    })


def detalle_producto(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    categorias = Categoria.objects.all()
    return render(request, 'fennys/productos/detalle_producto.html', {'producto': producto, 'categorias': categorias})