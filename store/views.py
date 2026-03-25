from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from .models import *
from .forms import RegistroFormularioPersonalizado
from django.db.models import Q
import mercadopago
from django.urls import reverse
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
import os
import datetime
import json
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse

def store(request):
    productos = Producto.objects.all()
    query = request.GET.get('q')

    if query:

        palabras = query.replace('-', ' ').split()

    
        for palabra in palabras:
            productos = productos.filter(
                Q(nombre__icontains=palabra) | Q(categoria__icontains=palabra)
            )

    context = {'products': productos, 'query': query}
    return render(request, 'store/store.html', context)

def registro(request):
    if request.method == 'POST':
        form = RegistroFormularioPersonalizado(request.POST)
        
        if form.is_valid():
        
            usuario_nuevo = form.save(commit=False)
            
            
            usuario_nuevo.first_name = form.cleaned_data.get('first_name')
            usuario_nuevo.last_name = form.cleaned_data.get('last_name')
            usuario_nuevo.email = form.cleaned_data.get('email')
            
           
            usuario_nuevo.save()
            
            username = form.cleaned_data.get('username')
            messages.success(request, f"¡Cuenta creada exitosamente wacho! Ya podés loguearte como {username}")
            return redirect('login')
            
    else:
        form = RegistroFormularioPersonalizado()

    context = {'form': form}
    return render(request, 'store/registro.html', context)



def carrito(request):
    if request.user.is_authenticated:
        usuario = request.user
        orden, created = Orden.objects.get_or_create(usuario=usuario, completado = False)

        items = orden.orderitem_set.all()
    else:
        items= []
        orden={'precio_total':0,'cantidad_items':0}

    context = {'items':items , 'orden':orden}

    return render (request,'store/carrito.html',context)


@login_required(login_url='login')
def agregar_item(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    orden, created = Orden.objects.get_or_create(usuario=request.user, completado=False)
    

    variacion_id = request.POST.get('variacion_id')
    variacion_obj = None
    if variacion_id:
        variacion_obj = Variacion.objects.get(id=variacion_id)


    stock_disponible = variacion_obj.stock if variacion_obj else producto.stock


    nombre_mostrar = variacion_obj.valor if variacion_obj else producto.nombre


    order_item_qs = OrderItem.objects.filter(orden=orden, producto=producto, variacion=variacion_obj)

    if order_item_qs.exists():
        item = order_item_qs.first()
   
        if item.cantidad + 1 > stock_disponible:
            messages.error(request, f"NO HAY MÁS STOCK. Ya tenés el máximo disponible de {nombre_mostrar}.")
        else:
            item.cantidad += 1
            item.save()
            messages.success(request, f"Sumaste otra unidad de {nombre_mostrar} al carrito.")
            
    else:
        if stock_disponible >= 1:
            OrderItem.objects.create(
                producto=producto,
                orden=orden,
                variacion=variacion_obj,
                cantidad=1
            )
            messages.success(request, f"{nombre_mostrar} agregado al carrito.")
        else:
            messages.error(request, f"Lo sentimos, {nombre_mostrar} está sin stock.")

    return redirect('store')




@login_required(login_url='login')
def checkout(request):
    orden, created = Orden.objects.get_or_create(usuario=request.user, completado=False)
    items = orden.orderitem_set.all()

    if not items.exists():
        return redirect('store')
    
    context = {'orden':orden , 'items': items}
    return render(request,'store/checkout.html',context)

@login_required(login_url='login')
def procesar_pedido(request):
   
    
    if request.method == 'POST':
        orden, created = Orden.objects.get_or_create(usuario=request.user, completado=False)
        
       
        total = orden.precio_total
       
        
        metodo_envio = request.POST.get('metodo_envio')
        metodo_pago = request.POST.get('metodo_pago')
        
     
        
        if total > 0:   
            if metodo_envio == 'domicilio':
                orden.tipo_de_envio = 'Envio a Domicilio'
                orden.costo_de_envio = 15000 
            else:
               orden.tipo_de_envio = 'Retiro en Local'
               orden.costo_de_envio = 0 
               
            if metodo_pago == 'transferencia':
                orden.metodo_pago = 'transferencia'
                orden.completado = True
                orden.fecha = datetime.datetime.now()
                orden.save()

                correo_cliente = request.user.email
                if correo_cliente: 
                    dominio_actual = request.get_host()
                    contexto = {'orden': orden, 'items': orden.orderitem_set.all(),'dominio': dominio_actual}
                    html_mensaje = render_to_string('store/ticket_mail.html', contexto)
                    texto_plano = strip_tags(html_mensaje) 
                    
                
                    send_mail(
                        subject=f'Confirmación de Pedido #{orden.id} - Ecommerce de Suplemento',
                        message=texto_plano,
                        from_email=os.getenv('EMAIL_USER'), 
                        recipient_list=[correo_cliente],
                        html_message=html_mensaje,
                        fail_silently=False, 
                    )
               

                return redirect('ticket_exito', orden_id=orden.id)
                
            elif metodo_pago == 'efectivo':
                orden.metodo_pago = 'efectivo'
                orden.completado = True
                orden.fecha = datetime.datetime.now()
                orden.save()
                correo_cliente = request.user.email
                if correo_cliente: 
                    dominio_actual = request.get_host()
                    contexto = {'orden': orden, 'items': orden.orderitem_set.all(),'dominio': dominio_actual}
                    html_mensaje = render_to_string('store/ticket_mail.html', contexto)
                    texto_plano = strip_tags(html_mensaje) 
                    
                
                    send_mail(
                        subject=f'Confirmación de Pedido #{orden.id} - Ecommerce de Suplemento',
                        message=texto_plano,
                        from_email=os.getenv('EMAIL_USER'), 
                        recipient_list=[correo_cliente],
                        html_message=html_mensaje,
                        fail_silently=False, 
                    )
                return redirect('ticket_exito', orden_id=orden.id)
                
            elif metodo_pago == 'mp':
                orden.metodo_pago = 'mp'
                orden.save() 
                
                sdk = mercadopago.SDK(os.getenv('ACCESS_TOKEN_MP')) 

                items_mp = []
                for item in orden.orderitem_set.all():
                    items_mp.append({
                        "title": item.producto.nombre,
                        "quantity": int(item.cantidad),
                        "unit_price": float(item.producto.precio),
                        "currency_id": "ARS" 
                    })

                if orden.costo_de_envio > 0:
                    items_mp.append({
                        "title": "Costo de Envío",
                        "quantity": 1,
                        "unit_price": float(orden.costo_de_envio),
                        "currency_id": "ARS" 
                    })
                url_exito = request.build_absolute_uri(reverse('ticket_exito', args=[orden.id]))
                url_fallo = request.build_absolute_uri(reverse('carrito'))

                print(f"--> URL de Éxito generada: {url_exito}")

                
                preference_data = {
                    "items": items_mp,
                    "external_reference": str(orden.id),
                    "back_urls": {
                        "success": url_exito,
                        "failure": url_fallo,
                        "pending": url_exito
                    },
                    #"auto_return": "approved",
                }

                preference_response = sdk.preference().create(preference_data)
                print("--> RESPUESTA MP:", preference_response)
                
                if preference_response["status"] == 201:
                    return redirect(preference_response["response"]["init_point"])
                else:
                    messages.error(request, "Error con Mercado Pago.")
                    return redirect('carrito')
        else:
            print("--> ERROR LOGICO: El total dio 0, así que esquivó todo el proceso.")
            
    print("--> CAYÓ AL FINAL DE LA FUNCIÓN (Se redirige a Inicio)")
    return redirect('store')

@login_required(login_url='login')
def ticket_exito(request,orden_id):
    orden = get_object_or_404(Orden, id=orden_id, usuario=request.user,completado=True)
    items = orden.orderitem_set.all()

    context = {'orden':orden, 'items': items}
    return render (request, 'store/ticket.html',context)

@login_required(login_url='login')
def perfil(request):
   
    ordenes_pagadas = Orden.objects.filter(
        usuario=request.user, 
        completado=True
    ).order_by('-fecha')
    
    context = {'ordenes': ordenes_pagadas}
    return render(request, 'store/perfil.html', context)


@csrf_exempt 
def webhook_mercadopago(request):
    if request.method == 'POST':
        try:
           
            data = json.loads(request.body)
            
        
            if data.get('type') == 'payment':
                
        
                sdk = mercadopago.SDK(os.getenv('ACCESS_TOKEN_MP'))
                payment_id = data.get('data', {}).get('id')
                payment_info = sdk.payment().get(payment_id)

          
                if payment_info["status"] == 200:
                    pago = payment_info["response"]
                    estado_pago = pago["status"]
                    orden_id = pago["external_reference"] 

                   
                    if estado_pago == 'approved':
                        orden = Orden.objects.get(id=orden_id)
                        orden.pagado = True
                        orden.save()
                        
                        print(f"✅ ¡ÉXITO! Se acreditó el pago de la orden #{orden.id}")
                        

        except Exception as e:
            print(f"❌ Error procesando el webhook: {e}")

        
        return HttpResponse(status=200) 
        
    return HttpResponse(status=404)