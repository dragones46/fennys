from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Usuario, Role, Producto, Pedido, DetallePedido
from .crypt import hash_password, verify_password

def index(request):
    productos = Producto.objects.all()
    return render(request, 'fennys/index.html', {'productos': productos})

def productos(request):
    productos_disponibles = Producto.objects.all()
    return render(request, 'fennys/productos/productos.html', {'productos': productos_disponibles})

def contacto(request):
    return render(request, 'fennys/contacto/contacto.html')



def lista_productos(request):
    productos = Producto.objects.all()
    
    # Obtener el carrito de la sesión
    carrito = request.session.get('carrito', {})
    
    # Calcular el total del carrito
    total_carrito = 0
    for item in carrito.values():
        total_carrito += int(item['cantidad']) * float(item['precio'])
    
    print(carrito)  # Para depurar el contenido del carrito

    return render(request, 'fennys/productos/lista_productos.html', {
        'productos': productos,
        'carrito': carrito,
        'total_carrito': total_carrito
    })

def agregar_al_carrito(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)

    # Inicializar el carrito en la sesión si no existe
    if 'carrito' not in request.session:
        request.session['carrito'] = {}

    # Agregar el producto al carrito
    if str(producto.id) in request.session['carrito']:
        request.session['carrito'][str(producto.id)]['cantidad'] += 1
    else:
        request.session['carrito'][str(producto.id)] = {
            'nombre': producto.nombre,
            'precio': str(producto.precio),
            'cantidad': 1,
            'foto': producto.foto.url if producto.foto else None
        }

    # Guardar el carrito en la sesión
    request.session.modified = True
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
            messages.success(request, "Producto eliminado del carrito.")
        else:
            messages.warning(request, "El producto no está en el carrito.")
    else:
        messages.warning(request, "El carrito está vacío.")
    return redirect('lista_productos')

def cambiar_cantidad(request, producto_id):
    if request.method == 'POST':
        cantidad = int(request.POST.get('cantidad'))
        if 'carrito' in request.session and str(producto_id) in request.session['carrito']:
            request.session['carrito'][str(producto_id)]['cantidad'] = cantidad
            request.session.modified = True
            messages.success(request, "Cantidad actualizada en el carrito.")
        else:
            messages.warning(request, "El producto no está en el carrito.")
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
                messages.warning(request, "usuario o contraseña incorrectos")
        except Usuario.DoesNotExist:
            messages.warning(request, "usuario no encontrado o no existe")

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
        # Procesar el pago
        request.session['carrito'] = {}
        request.session.modified = True
        messages.success(request, "Pago realizado correctamente.")
    else:
        messages.warning(request, "No hay productos en el carrito para pagar.")
    return redirect('lista_productos')



