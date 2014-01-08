# -*- encoding: utf-8 -*-
from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic import TemplateView,ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.core.urlresolvers import reverse_lazy, reverse
from django.core.validators import email_re
from django.contrib.auth.decorators import login_required
from django.template.context import RequestContext
from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404, render_to_response
from django.forms import ModelForm
from datetime import date
from reportlab.pdfgen import canvas
from forms import *
from app.models import *

class ClienteForm(ModelForm):
    class Meta:
        model = Cliente

class VehiculoForm(ModelForm):
    class Meta:
        model = Vehiculo

@login_required()
def home(request):
    print request.user.id
    if request.user.username == 'xarly16':
        template = 'MenuAdmin.html'
    else:
        ID = request.user.id
        empleado = Empleado.objects.filter(user=ID)[0]
        print empleado.cargoID.id
        if empleado.cargoID.id == 1:
            template = 'MenuServicio.html'
        elif empleado.cargoID.id == 2:
            template = 'MenuServicio.html'
        elif empleado.cargoID.id == 3:
            template = 'MenuBodega.html'
        elif empleado.cargoID.id == 4:
            template = 'MenuMecanico.html'
        elif empleado.cargoID.id == 5:
            template = 'MenuAdmin.html'
        elif empleado.cargoID.id == 6:
            template = 'construccion.html'
    return render_to_response(template, {'user': request.user}, context_instance=RequestContext(request))

@login_required()
def main(request):
    return render_to_response('main.html', {'user': request.user}, context_instance=RequestContext(request))

@login_required()
def MenuAdmin(request, template_name='MenuAdmin.html'):
    data = {}
    return render(request, template_name, data)

@login_required()
def construccion(request, template_name='construccion.html'):
    data = {}
    return render(request, template_name, data)

@login_required()
def MenuBodega(request, template_name='MenuBodega.html'):
    data = {}
    return render(request, template_name, data)

@login_required()
def ingresaventa(request, template_name='ingresaventa.html'):
    OT = False
    Productos = False
    ordenNoEncontrada = False
    otEncontrada = False
    primera = False
    finalizarCompra = False
    carrito = []
    otBuscada = OrdenDeTrabajo()
    detalleOT = DetalleOT()
    listaProd = []
    total = 0
    if request.method == 'POST' and 'OT' in request.POST:
        OT = True
        primera = True
    elif request.method == 'POST' and 'Productos' in request.POST:
        Productos = True
        listaProd = Material.objects.all()
    elif request.method == 'POST' and 'buscarOT' in request.POST:
        numero = request.POST['numeroBuscado']
        otBuscada = OrdenDeTrabajo.objects.filter(numeroOrden = numero)
        if len(otBuscada) != 0:
            otBuscada = otBuscada[0]
            otBuscada.estadoID = EstadoOT.objects.filter(id=4)[0]
            fecha = date.today()
            otBuscada.fechaTermino = str(fecha.year)+'-'+str(fecha.month)+'-'+str(fecha.day)
            otEncontrada = True
            OT = True
            detalleOT = DetalleOT.objects.filter(numeroOrden=numero)
            for S in detalleOT:
                total+=S.sevicioID.precioServicio
        else:
            otBuscada = OrdenDeTrabajo()
            ordenNoEncontrada = True
            OT = True
        pass
    elif request.method == 'POST' and 'finalizarOT' in request.POST:
        numero = request.POST['numeroOrden']
        otBuscada = OrdenDeTrabajo.objects.filter(numeroOrden = numero)
        otBuscada = otBuscada[0]
        otBuscada.estadoID = EstadoOT.objects.filter(id=4)[0]
        fecha = date.today()
        otBuscada.fechaTermino = str(fecha.year)+'-'+str(fecha.month)+'-'+str(fecha.day)
        total = request.POST['total']
        nuevaVenta = Venta()
        nuevaVenta.precioVenta = total
        nuevaVenta.pagoID = otBuscada.pagoID
        nuevaVenta.clienteRut = otBuscada.clienteRut
        nuevaVenta.empleadoID = Empleado.objects.filter(id=1)[0]
        nuevaVenta.save()
        otBuscada.numeroVenta = nuevaVenta
        otBuscada.save()
        return HttpResponseRedirect(reverse('MenuServicio'))
    elif request.method == 'POST' and 'agregar' in request.POST:
        Productos = True
        listaProd = Material.objects.all()
        for P in listaProd:
            temp = request.POST[str(P.id)]
            if ("C"+str(P.id)) in request.POST and (temp > '0' or temp == ''):
                if temp == '':
                    temp = request.POST["Cant"+str(P.id)]                
                P.precioNeto=int(temp)
                total += P.precioMaterial * int(temp)
                carrito.append(P)
            elif temp > '0':
                P.precioNeto=int(temp)
                total += P.precioMaterial * int(temp)
                carrito.append(P)
        pass
    elif request.method == 'POST' and 'terminarCompra' in request.POST:
        finalizarCompra = True
        listaProd = Material.objects.all()
        for P in listaProd:
            temp = request.POST[str(P.id)]
            if ("C"+str(P.id)) in request.POST and (temp > '0' or temp == ''):
                if temp == '':
                    temp = request.POST["Cant"+str(P.id)]                
                P.precioNeto=int(temp)
                total += P.precioMaterial * int(temp)
                carrito.append(P)
            elif temp > '0':
                P.precioNeto=int(temp)
                total += P.precioMaterial * int(temp)
                carrito.append(P)
        nuevaVenta = Venta(precioVenta=total)
        nuevaVenta.empleadoID = Empleado.objects.filter(id=1)[0]
        nuevaVenta.pagoID = FormaPago.objects.filter(id=2)[0]
        nuevaVenta.clienteRut = Cliente.objects.filter(rutCliente='19')[0]
        nuevaVenta.save()
        for P in carrito:
            nuevoDetalle = DetalleVenta()
            nuevoDetalle.numeroVenta = nuevaVenta
            nuevoDetalle.codigoMaterial = P
            nuevoDetalle.cantidadMaterial = P.precioNeto
            nuevoDetalle.save()
            material = Material.objects.filter(id=P.id)[0]
            material.stockMaterial-=P.precioNeto
            material.save()
            return HttpResponseRedirect(reverse('MenuServicio'))

    data = {
        'primera': primera,
        'carrito': carrito,
        'total': total,
        'OT': OT,
        'Productos': Productos,
        'ordenNoEncontrada': ordenNoEncontrada,
        'otEncontrada': otEncontrada,
        'otBuscada': otBuscada,
        'detalleOT': detalleOT,
        'listaProd': listaProd,
    }
    return render(request, template_name, data)

@login_required()
def ingresaorden(request):
    print "FUNCION\n\n"
    NC = '0'
    servicios = Servicio.objects.all()
    comunas = Comuna.objects.all()
    clienteBuscado = Cliente()
    comunaBuscada = Comuna()
    vehiculoBuscado = Vehiculo()
    marcaBuscada = Marca()
    modeloBuscado = Modelo()
    formu = RegiClienteForm()
    form = RegiVehiculoForm()
    formul = FormOT()
    rutInvalido = False
    telefonoInvalido = False
    correoInvalido = False
    patenteInvalida = False
    clientenuevo = False
    camposVacios = False
    if request.method == 'POST' and 'buscarut' in request.POST:
        print "FUNCION!!22222"
        RNC = request.POST['NC']
        form = RegiVehiculoForm()
        formu = RegiClienteForm()
        form2 = FormOT()
        rut = request.POST['rutCliente']
        rut = rut.replace('.','').replace('-','')
        patente = request.POST['patenteVehiculo']
        patente = patente.upper()
        clienteBuscado = Cliente.objects.filter(rutCliente=rut)
        modeloBuscado = Modelo()
        marcaBuscada = Marca()
        comunaBuscada = Comuna()
        form = RegiVehiculoForm(request.POST)
        if len(clienteBuscado)>0:
            if RNC == '0':
                NC = '1'
            else:
                NC = '2'
            clienteBuscado = clienteBuscado[0]
        vehiculoBuscado = Vehiculo.objects.filter(patenteVehiculo=patente)
        if len(vehiculoBuscado) > 0:
            if RNC == '0':
                NC = '1'
            else:
                NC = '2'
            vehiculoBuscado = vehiculoBuscado[0]
            modeloBuscado = vehiculoBuscado.modeloID
            marcaBuscada = modeloBuscado.marcaID
            form.colorVehiculo = vehiculoBuscado.colorVehiculo
            form.anioVehiculo = vehiculoBuscado.anioVehiculo
    elif request.method == 'POST' and 'buscapatente' in request.POST:
        print "FUNCION!!333333"
        RNC = request.POST['NC']
        form = RegiVehiculoForm()
        formu = RegiClienteForm()
        form2 = FormOT()
        rut = request.POST['rutCliente']
        rut = formatoNombre(rut)
        patente = request.POST['patenteVehiculo']
        patente = patente.upper()
        clienteBuscado = Cliente.objects.filter(rutCliente=rut)
        modeloBuscado = Modelo()
        marcaBuscada = Marca()
        comunaBuscada = Comuna()
        form = RegiVehiculoForm(request.POST)
        if len(clienteBuscado)>0:
            if RNC == '0':
                NC = '1'
            else:
                NC = '2'
            clienteBuscado = clienteBuscado[0]
        vehiculoBuscado = Vehiculo.objects.filter(patenteVehiculo=patente)
        if len(vehiculoBuscado) > 0:
            if RNC == '0':
                NC = '1'
            else:
                NC = '2'
            vehiculoBuscado = vehiculoBuscado[0]
            modeloBuscado = vehiculoBuscado.modeloID
            marcaBuscada = modeloBuscado.marcaID
            form.colorVehiculo = vehiculoBuscado.colorVehiculo
            form.anioVehiculo = vehiculoBuscado.anioVehiculo
    elif request.method == 'POST':
        form = RegiVehiculoForm(request.POST)
        formul = FormOT(request.POST)
        while request.POST['comuna'] != '':
            rut = request.POST['rutCliente']
            if rut == '':
                camposVacios = True
                break
            rut = rut.replace('.','').replace('-','')
            if not rut.isdigit() and rut[-1] != 'K' and rut[-1] != 'k':
                rutInvalido = True
            elif len(rut) < 2:
                rutInvalido = True
            elif rut[len(rut)-1] != validaRut(int(rut[:-1])):
                rutInvalido = True
            telefono = request.POST['telefonoCliente']
            if telefono == '':
                camposVacios = True
                break
            if len(telefono) <8 or not telefono.isdigit():
                telefonoInvalido = True
            correo = request.POST['correoCliente']
            if correo == '':
                camposVacios = True
                break
            if ((validaEmail(correo)) != True ):
                correoInvalido = True
            direccion = request.POST['direccionCliente']
            nombre = request.POST['nombreCliente']
            apellido =request.POST['apellidoCliente']
            if direccion == '' or nombre == '' or apellido == '':
                camposVacios = True
            comuna = request.POST['comuna']
            if comuna == '0':
                comuna = request.POST['comunaa']
                nuevacomuna = Comuna(nombreComuna=comuna)
                nuevacomuna.save()
            else:
                comuna = request.POST['comuna']
            comuna = Comuna.objects.filter(nombreComuna=comuna)           
            if correoInvalido or rutInvalido or telefonoInvalido:
                break
            clientenuevo = Cliente(rutCliente=rut, nombreCliente=nombre, apellidoCliente=apellido, direccionCliente=direccion, correoCliente=correo, telefonoCliente=telefono) 
            clientenuevo.ComunaCliente=comuna[0]
            clientenuevo.estadoCliente= True
            if request.POST['patenteVehiculo']!='' and request.POST['anioVehiculo']!='' and request.POST['colorVehiculo']!='':
                marcaVehiculo = request.POST['Marca']
                nombreMarcaVehiculo = formatoNombre(marcaVehiculo)
                modeloVehiculo = request.POST['Modelo']
                nombreModeloVehiculo = formatoNombre(modeloVehiculo)
                patente = request.POST['patenteVehiculo']
                patente = patente.upper()
                anio = request.POST['anioVehiculo']
                color = request.POST['colorVehiculo']
                marcaVehiculo = Marca.objects.filter(nombreMarca=nombreMarcaVehiculo)
                if len(marcaVehiculo)==0:
                    nuevaMarca=Marca(nombreMarca=nombreMarcaVehiculo)
                    nuevaMarca.save()
                marcaVehiculo = Marca.objects.filter(nombreMarca=nombreMarcaVehiculo)
                modeloVehiculo = Modelo.objects.filter(nombreModelo=nombreModeloVehiculo)
                if len(modeloVehiculo) == 0:
                    nuevoModelo = Modelo(nombreModelo=nombreModeloVehiculo)
                    nuevoModelo.marcaID = marcaVehiculo[0]
                    nuevoModelo.save()
                modeloVehiculo = Modelo.objects.filter(nombreModelo=nombreModeloVehiculo)
                if not validarPatente(patente):
                    patenteInvalida = True
                    break
                if len(Cliente.objects.filter(rutCliente=rut)) == 0:
                    clientenuevo.save()
                else:
                    print Cliente.objects.filter(rutCliente=rut)
                clientenuevo = Cliente.objects.filter(rutCliente=rut)
                vehiculonuevo = Vehiculo(patenteVehiculo=patente, colorVehiculo=color, anioVehiculo=anio)
                vehiculonuevo.clienteRut = clientenuevo[0]
                vehiculonuevo.modeloID = modeloVehiculo[0]
                if len(Vehiculo.objects.filter(patenteVehiculo=patente))==0:
                    vehiculonuevo.save()
                else:
                    print Vehiculo.objects.filter(patenteVehiculo=patente)
                vehiculonuevo = Vehiculo.objects.filter(patenteVehiculo=patente)
                observaciones = request.POST['observaciones']
                if observaciones == '':
                    observaciones = 'Sin observaciones'
                km = '0'
                if formul.is_valid():
                    km = formul.cleaned_data['kmVehiculo']
                comb = request.POST['Comb']
                fecha = date.today()
                fecha = str(fecha.year)+'-'+str(fecha.month)+'-'+str(fecha.day)
                nuevaOT = OrdenDeTrabajo(observaciones=observaciones, kmVehiculo=km, combustibleVehiculo=comb, fechaTermino=fecha)
                nuevaOT.pagoID = FormaPago.objects.filter(id=2)[0]
                nuevaOT.estadoID = EstadoOT.objects.filter(id=1)[0]
                nuevaOT.clienteRut = clientenuevo[0]
                nuevaOT.patenteVehiculo = vehiculonuevo[0]
                nuevaOT.numeroVenta = Venta()
                nuevaOT.save()
                ListaServicios = request.POST.getlist('Servicio'), nuevaOT.numeroOrden
                for S in ListaServicios[0]:                
                    nuevoDetalle = DetalleOT()
                    nuevoDetalle.numeroOrden = OrdenDeTrabajo.objects.filter(numeroOrden = nuevaOT.numeroOrden)[0]
                    nuevoDetalle.sevicioID = Servicio.objects.filter(id=S)[0]            
                    nuevoDetalle.save()                
                return HttpResponseRedirect(reverse('MenuServicio'))
        pass
    
    else:
        clienteBuscado = Cliente()
        comunaBuscada = Comuna()
        vehiculoBuscado = Vehiculo()
        marcaBuscada = Marca()
        modeloBuscado = Modelo()
    
    
    data = {
        'rutInvalido': rutInvalido,
        'telefonoInvalido': telefonoInvalido,
        'correoInvalido': correoInvalido,
        'patenteInvalida': patenteInvalida,
        'clientenuevo': clientenuevo,
        'camposVacios': camposVacios,
        'servicios': servicios,
        'comunas': comunas,
        'NC': NC,
        'marcaBuscada':marcaBuscada,
        'modeloBuscado': modeloBuscado,
        'clienteBuscado': clienteBuscado,
        'comunaBuscada': comunaBuscada,
        'vehiculoBuscado': vehiculoBuscado,
        'cliente': clienteBuscado,
        'form': form,
        'formu': formu,
        'formul': formul,
    }
    return render_to_response('ingresaorden.html', data, context_instance=RequestContext(request))

@login_required
def buscaot(request):
    OT = False
    otEncontrada = False
    total = 0
    otBuscada = OrdenDeTrabajo()
    detalleOT = DetalleOT()
    clienteBuscado = Cliente()
    if request.method == 'POST' and 'finalizarOT' in request.POST:
        nuevoEstado = request.POST['EstadoOT']
        nuevoEstado = EstadoOT.objects.filter(id = nuevoEstado)[0]
        otBuscada = OrdenDeTrabajo.objects.filter(numeroOrden = request.POST["numeroOrden"])[0]
        otBuscada.estadoID = nuevoEstado
        otBuscada.save()
        return render_to_response('MenuServicio.html', {'guardado': True}, context_instance=RequestContext(request))
    elif request.method == 'POST':
        numero = request.POST['numeroBuscado']
        if numero != '' and numero.isdigit():
            otBuscada = OrdenDeTrabajo.objects.filter(numeroOrden = numero)
            if len(otBuscada) != 0:
                otBuscada = otBuscada[0]
                otEncontrada = True
                OT = True
                detalleOT = DetalleOT.objects.filter(numeroOrden=numero)
                for S in detalleOT:
                    total+=S.sevicioID.precioServicio
            else:
                otBuscada = OrdenDeTrabajo()
                ordenNoEncontrada = True
                OT = True
            pass
        else:
            pass

    else:
        otEncontrada = True
    data={
        'total': total,
        'OT': OT,
        'otEncontrada': otEncontrada,
        'otBuscada': otBuscada,
        'detalleOT': detalleOT,

    }
    return render_to_response('buscaot.html', data, context_instance=RequestContext(request))

@login_required
def buscaotMecanico(request):
    OT = False
    otEncontrada = False
    total = 0
    otBuscada = OrdenDeTrabajo()
    detalleOT = DetalleOT()
    clienteBuscado = Cliente()
    if request.method == 'POST' and 'finalizarOT' in request.POST:
        nuevoEstado = request.POST['EstadoOT']
        nuevoEstado = EstadoOT.objects.filter(id = nuevoEstado)[0]
        otBuscada = OrdenDeTrabajo.objects.filter(numeroOrden = request.POST["numeroOrden"])[0]
        otBuscada.estadoID = nuevoEstado
        otBuscada.save()
        return render_to_response('MenuMecanico.html', {'guardado': True}, context_instance=RequestContext(request))
    elif request.method == 'POST':
        numero = request.POST['numeroBuscado']
        if numero != '' and numero.isdigit():
            otBuscada = OrdenDeTrabajo.objects.filter(numeroOrden = numero)
            if len(otBuscada) != 0:
                otBuscada = otBuscada[0]
                otEncontrada = True
                OT = True
                detalleOT = DetalleOT.objects.filter(numeroOrden=numero)
                for S in detalleOT:
                    total+=S.sevicioID.precioServicio
            else:
                otBuscada = OrdenDeTrabajo()
                ordenNoEncontrada = True
                OT = True
            pass
        else:
            pass

    else:
        otEncontrada = True
    data={
        'total': total,
        'OT': OT,
        'otEncontrada': otEncontrada,
        'otBuscada': otBuscada,
        'detalleOT': detalleOT,

    }
    return render_to_response('buscaotMecanico.html', data, context_instance=RequestContext(request))


@login_required
def anulaot(request):
    OT = False
    otEncontrada = False
    total = 0
    otBuscada = OrdenDeTrabajo()
    detalleOT = DetalleOT()
    clienteBuscado = Cliente()
    if request.method == 'POST' and 'finalizarOT' in request.POST:
        nuevoEstado = EstadoOT.objects.filter(id = 5)[0]
        otBuscada = OrdenDeTrabajo.objects.filter(numeroOrden = request.POST["numeroOrden"])[0]
        otBuscada.estadoID = nuevoEstado
        otBuscada.save()
        return render_to_response('MenuServicio.html', {'guardado': True}, context_instance=RequestContext(request))
    elif request.method == 'POST':
        numero = request.POST['numeroBuscado']
        if numero != '':
            otBuscada = OrdenDeTrabajo.objects.filter(numeroOrden = numero)
            if len(otBuscada) != 0:
                otBuscada = otBuscada[0]
                otEncontrada = True
                OT = True
                detalleOT = DetalleOT.objects.filter(numeroOrden=numero)
                for S in detalleOT:
                    total+=S.sevicioID.precioServicio
            else:
                otBuscada = OrdenDeTrabajo()
                ordenNoEncontrada = True
                OT = True
            pass
        else:
            pass

    else:
        otEncontrada = True
    data={
        'total': total,
        'OT': OT,
        'otEncontrada': otEncontrada,
        'otBuscada': otBuscada,
        'detalleOT': detalleOT,

    }
    return render_to_response('anulaot.html', data, context_instance=RequestContext(request))

@login_required()
def cliente_list(request, template_name='cliente_list.html'):
    servers = Cliente.objects.all()
    data = {}
    data['servers'] = servers
    return render(request, template_name, data)

@login_required()
def vehiculo_list(request, template_name='vehiculo_list.html'):
    if request.method == 'POST'  and request.POST['patente'] != '':
        vehiculos = Vehiculo.objects.filter(patenteVehiculo = request.POST['patente'])
    else:
        vehiculos = Vehiculo.objects.all()
    data = {}
    data['vehiculos'] = vehiculos
    return render(request, template_name, data)

@login_required()
def venta_list(request, template_name='venta_list.html'):
    if request.method == 'POST'  and request.POST['venta'].isdigit():
        ventas = Vehiculo.objects.filter(patenteVehiculo = request.POST['venta'])
    else:
        ventas = Venta.objects.all()
    data = {}
    data['ventas'] = ventas
    return render(request, template_name, data)


@login_required()
def vermaterial(request, template_name='material_list.html'):
    if request.method == 'POST'  and request.POST['codigo'] != '':
        materiales = Material.objects.filter(codigoMaterial = request.POST['codigo'])
    else:
        materiales = Material.objects.all()
    data = {}
    data['materiales'] = materiales
    return render(request, template_name, data)

@login_required()
def buscarcliente(request, template_name='buscarcliente.html'):
    noexiste = False
    if request.method == 'POST' and 'guardar' in request.POST:
        pass
    elif request.method == 'POST' and request.POST['rutCliente']!='':
        cliente = Cliente.objects.filter(rutCliente = request.POST['rutCliente'])
        if len(cliente)==0:
            noexiste = True
            cliente = RegiClienteForm
            muestra = True
        else:
            cliente=cliente[0]
            muestra = False
    elif request.method == 'POST' and request.POST['rutCliente']=='':
        cliente = Cliente.objects.filter(rutCliente = request.POST['rutCliente'])[0] 
        muestra = False
    else:
        cliente = RegiClienteForm
        muestra = True
    data = {
        'cliente': cliente,
        'muestra': muestra,
        'noexiste': noexiste,
    }
    return render(request, template_name, data)

@login_required()
def buscarvehiculo(request, template_name='buscarvehiculo.html'):
    noexiste = False
    marca = Marca()
    modelo = Modelo()
    if request.method == 'POST' and request.POST['patenteVehiculo']!='':
        vehiculo = Vehiculo.objects.filter(patenteVehiculo = request.POST['patenteVehiculo'].upper())
        if len(vehiculo)==0:
            noexiste = True
            vehiculo = RegiVehiculoForm
            muestra = True
        else:
            vehiculo=vehiculo[0]
            modelo = vehiculo.modeloID
            marca = modelo.marcaID
            muestra = False
    elif request.method == 'POST' and request.POST['patenteVehiculo']=='':
        vehiculo = Vehiculo.objects.filter(patenteVehiculo= request.POST['patenteVehiculo'].upper())[0] 
        muestra = False
    else:
        vehiculo = RegiVehiculoForm
        muestra = True
    data = {
        'marca': marca,
        'modelo': modelo,
        'vehiculo': vehiculo,
        'muestra': muestra,
        'noexiste': noexiste,
    }
    return render(request, template_name, data)

@login_required()
def verclientes(request, template_name='modificacliente.html'):
    if request.method == 'POST'  and request.POST['rut'] != '':
        clientes = Cliente.objects.filter(rutCliente = request.POST['rut'].replace('.','').replace('-',''))
    else:
        clientes = Cliente.objects.filter(estadoCliente=True)
    data = {}
    data['clientes'] = clientes
    return render(request, template_name, data)

@login_required()
def buscarprov(request, template_name='buscarprov.html'):
    if request.method == 'POST'  and request.POST['rut'] != '':
        proveedores = Proveedor.objects.filter(rutProveedor = request.POST['rut'].replace('.','').replace('-',''))
    else:
        proveedores = Proveedor.objects.filter(estadoProveedor=True)
    data = {}
    data['proveedores'] = proveedores
    return render(request, template_name, data)

@login_required()
def regiproveedor(request):
    rutInvalido = False
    telefonoInvalido = False
    correoInvalido = False
    if request.method == 'POST':  
        form = RegiProveedorForm(request.POST )
        while form.is_valid() :
            rut = form.cleaned_data['rutProveedor']
            rut = rut.replace('.','').replace('-','')
            if not rut.isdigit() and rut[-1] != 'K' and rut[-1] != 'k':
                rutInvalido = True
            elif len(rut) < 2:
                rutInvalido = True
            elif rut[len(rut)-1] != validaRut(int(rut[:-1])):
                rutInvalido = True
            telefono = form.cleaned_data['telefonoProveedor']
            if len(telefono) <8 or not telefono.isdigit():
                telefonoInvalido = True
            correo = form.cleaned_data['correoProveedor']
            if ((validaEmail(correo)) != True ):
                correoInvalido = True
            nombre = form.cleaned_data['nombreProveedor']
            ruts = Proveedor.objects.filter(rutProveedor=rut)
            if len(ruts) > 0:
                rutInvalido = True           
            if correoInvalido or rutInvalido or telefonoInvalido:
                break
            proveedornuevo = Proveedor(rutProveedor=rut, nombreProveedor=nombre, correoProveedor=correo, telefonoProveedor=telefono) 
            proveedornuevo.estadoProveedor=True
            proveedornuevo.save()

            return HttpResponseRedirect(reverse('MenuBodega'))
    else:
        form =RegiProveedorForm()
    data = {
        'telefonoInvalido': telefonoInvalido,
        'rutInvalido': rutInvalido,
        'correoInvalido': correoInvalido,
        'form': form,
    }
    return render_to_response('regiproveedor.html', data, context_instance=RequestContext(request))


@login_required()
def MenuServicio(request, template_name='MenuServicio.html'):
    data = {}
    return render(request, template_name, data)

@login_required()
def MenuTaller(request, template_name='MenuTaller.html'):
    data = {}
    return render(request, template_name, data)

@login_required()
def MenuMecanico(request, template_name='MenuMecanico.html'):
    data = {}
    return render(request, template_name, data)

@login_required
def ingresausuario(request):
    rutInvalido = False
    correoRegistrado = False
    telefonoInvalido = False
    cargoInvalido = False
    correoVacio = False
    camposVacios = False
    if request.method == 'POST':  
        form = SignUpForm(request.POST)
        formu = EmpleadoForm(request.POST)
        cargo = request.POST['cargo']
        if cargo == '0':
            cargoInvalido = True
        if formu.is_valid():
            rut = formu.cleaned_data['rutEmpleado']
            rut = rut.replace('.','').replace('-','')
            if not rut.isdigit() and rut[-1] != 'K' and rut[-1] != 'k':
                rutInvalido = True
            elif len(rut) < 2 or rut == '':
                rutInvalido = True
            elif rut[len(rut)-1] != validaRut(int(rut[:-1])):
                rutInvalido = True
            telefono = formu.cleaned_data['telefonoEmpleado']
            if len(telefono) <8 or not telefono.isdigit():
                telefonoInvalido = True
        else:
            rutInvalido = True
            telefonoInvalido = True
        while form.is_valid():

            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            email = form.cleaned_data["email"]
            if len(email) == 0:
                correoVacio = True
            usuarios = User.objects.filter(email = email)
            if len(usuarios) > 0:
                correoRegistrado = True                
            first_name = form.cleaned_data["first_name"]
            last_name = form.cleaned_data["last_name"]
            if first_name == '' or last_name == '':
                camposVacios = True
            if camposVacios or correoVacio or correoRegistrado or rutInvalido or telefonoInvalido or cargoInvalido:
                break
            user = User.objects.create_user(username, email, password)
            user.first_name = first_name
            user.last_name = last_name
            user.save()
            empleado = Empleado(rutEmpleado = rut, telefonoEmpleado=telefono)
            empleado.user = user
            empleado.cargoID = Cargo.objects.filter(id=cargo)[0]
            empleado.save()
            return HttpResponseRedirect(reverse('MenuAdmin'))
    else:
        form =SignUpForm()
        formu = EmpleadoForm()
    data = {
        'cargoInvalido': cargoInvalido,
        'telefonoInvalido': telefonoInvalido,
        'correoRegistrado': correoRegistrado,
        'correoVacio': correoVacio,
        'camposVacios': camposVacios,
        'rutInvalido': rutInvalido,
        'form': form,
        'formu': formu,
    }
    return render_to_response('ingresausuario.html', data, context_instance=RequestContext(request))

@login_required()
def modificausuario(request, template_name='modificausuario.html'):
    noexiste = False
    rutInvalido = False
    correoRegistrado = False
    telefonoInvalido = False
    cargoInvalido = False
    correoVacio = False
    camposVacios = False
    muestra = False 
    empleado = EmpleadoForm
    user = SignUpForm
    if request.method == 'POST' and 'guardar' in request.POST:
        ID=request.POST['ID']
        username=request.POST['username']
        email=request.POST['correo']
        rut=request.POST['rut2']
        rut = rut.replace('.','').replace('-','')
        if not rut.isdigit() and rut[-1] != 'K' and rut[-1] != 'k':
            rutInvalido = True
        elif len(rut) < 2 or rut == '':
            rutInvalido = True
        elif rut[len(rut)-1] != validaRut(int(rut[:-1])):
            rutInvalido = True
        nombre=request.POST['nombre']
        apellido=request.POST['apellido']
        telefono=request.POST['telefono']
        if len(telefono) <8 or not telefono.isdigit():
            telefonoInvalido = True
        cargo=request.POST['cargo']
        if len(email) == 0 or not validaEmail(email):
            correoVacio = True                
        if nombre == '' or apellido == '':
            camposVacios = True
        if camposVacios or correoVacio or correoRegistrado or rutInvalido or telefonoInvalido or cargoInvalido:
            pass
        else:
            user = User.objects.filter(id=ID)[0]
            user.first_name = nombre
            user.last_name = apellido
            user.email = email
            user.save()
            empleado = Empleado.objects.filter(user=ID)[0]
            empleado.telefonoEmpleado = telefono
            empleado.rutEmpleado = rut
            empleado.cargoID = Cargo.objects.filter(id=cargo)[0]
            empleado.save()
            return HttpResponseRedirect(reverse('MenuAdmin'))
    elif request.method == 'POST' and request.POST['rut']!='':
        empleado = Empleado.objects.filter(rutEmpleado = request.POST['rut'].replace('.','').replace('-',''))
        print empleado
        if len(empleado)==0:
            noexiste = True
            empleado = EmpleadoForm
            user = SignUpForm
            muestra = True
        else:
            empleado=empleado[0]
            user = empleado.user
            muestra = False
    elif request.method == 'POST' and request.POST['rut']=='':
        empleado = Empleado.objects.filter(rutEmpleado = request.POST['rut'])[0] 
        user = empleado.user
        muestra = False
    else:
        empleado = EmpleadoForm
        user = SignUpForm
        muestra = True
    data = {
        'rutInvalido':  rutInvalido,
        'correoRegistrado': correoRegistrado,
        'telefonoInvalido':telefonoInvalido,
        'cargoInvalido': cargoInvalido,
        'correoVacio': correoVacio,
        'camposVacios':camposVacios,
        'user': user,
        'empleado': empleado,
        'muestra': muestra,
        'noexiste': noexiste,
    }
    return render(request, template_name, data)

@login_required
def ingresamaterial(request):
    proveedores = Proveedor.objects.all()
    tipos = TipoMaterial.objects.all()
    matBuscado = []
    codigoInvalido = False
    precioInvalido = False
    cantInvalida = False
    camposVacios = False
    if request.method == 'POST' and 'buscacodigo' in request.POST:
        codigo = request.POST['codigoMaterial']
        if codigo != '':
            matBuscado = Material.objects.filter(codigoMaterial = codigo)[0]
        else:
            codigoInvalido = True
    elif request.method == 'POST':
        codigo = request.POST['codigoMaterial']
        tipo = request.POST['tipoMaterial']
        nombre = request.POST['nombreMaterial']
        cant = request.POST['cantidadMaterial']
        if not cant.isdigit():
            cantInvalida = True
        elif cant.isdigit() and int(cant) < 0:
            cantInvalida = True
        precio = request.POST['precioMaterial']
        if not precio.isdigit():
            precioInvalido = True
        elif precio.isdigit() and int(precio) < 0:
            precioInvalido = True
        prov = request.POST['proveedor']
        if codigo == '' or tipo == '' or nombre == '' or cant == '' or precio == '' or prov == '':
            camposVacios = True
        nuevoMat = Material.objects.filter(codigoMaterial=codigo)
        if len(nuevoMat)!=0 and not cantInvalida:
            nuevoMat = nuevoMat[0]
            actual = nuevoMat.stockMaterial 
            nuevoMat.stockMaterial = int(actual) + int(cant)
            nuevoMat.save()
            return HttpResponseRedirect(reverse('MenuBodega'))
        elif len(nuevoMat) == 0 and not camposVacios and not cantInvalida and not precioInvalido:
            nuevoMat = Material()
            nuevoMat.nombreMaterial = nombre
            nuevoMat.codigoMaterial = codigo
            nuevoMat.stockMaterial = int(cant)
            nuevoMat.precioMaterial = int(precio)
            nuevoMat.ofertaMaterial = False
            nuevoMat.descuentoOferta = 0
            fecha = date.today()
            fecha = str(fecha.year)+'-'+str(fecha.month)+'-'+str(fecha.day)
            nuevoMat.fechaInicioOferta = fecha
            nuevoMat.fechaTerminoOferta = fecha
            nuevoMat.precioNeto = int(precio)
            if tipo == '0' and len(request.POST['tipoo']) != 0:
                tipo = request.POST['tipoo']
                if len(TipoMaterial.objects.filter(nombreTipo=formatoNombre(tipo))) == 0:
                    nuevoTipo = TipoMaterial(nombreTipo=formatoNombre(tipo))
                    nuevoTipo.save()
                tipo = TipoMaterial.objects.filter(nombreTipo=tipo)
            else:
                tipo = TipoMaterial.objects.filter(id=tipo)
            nuevoMat.tipoID = tipo[0]
            nuevoMat.proveedorID = Proveedor.objects.filter(id=prov)[0]
            nuevoMat.save()
            return HttpResponseRedirect(reverse('MenuBodega'))

    data = {
        'codigoInvalido': codigoInvalido,
        'cantInvalida': cantInvalida,
        'precioInvalido': precioInvalido,
        'camposVacios': camposVacios,
        'matBuscado': matBuscado,
        'tipos': tipos,
        'proveedores': proveedores,
    }
    return render(request, 'ingresamaterial.html', data)

@login_required()
def eliminausuario(request, template_name='eliminausuario.html'):
    noexiste = False
    if request.method == 'POST' and 'bloquear' in request.POST:
        usuario = User.objects.filter(id = request.POST['idusuario'])[0]
        usuario.is_active = False
        usuario.save()
        return HttpResponseRedirect(reverse('MenuAdmin'))
    elif request.method == 'POST' and request.POST['rut']!='':
        empleado = Empleado.objects.filter(rutEmpleado = request.POST['rut'].replace('.','').replace('-',''))
        if len(empleado)==0:
            noexiste = True
            empleado = EmpleadoForm
            user = SignUpForm
            muestra = True
        else:
            empleado=empleado[0]
            user = empleado.user
            muestra = False
    elif request.method == 'POST' and request.POST['rut']=='':
        empleado = Empleado.objects.filter(rutEmpleado = request.POST['rut'])[0] 
        user = empleado.user
        muestra = False
    else:
        empleado = EmpleadoForm
        user = SignUpForm
        muestra = True
    data = {
        'user': user,
        'empleado': empleado,
        'muestra': muestra,
        'noexiste': noexiste,
    }
    return render(request, template_name, data)

@login_required
def informes(request):
    aux = canvas.Canvas("InformeVentas.pdf")
    aux.drawImage("C:/BitNami/djangostack-1.5.5-1/PBD/Gest/static/1.jpg",10,735,100,100)
    #aux.drawImage("C:\\Users\\Guisselle\\Desktop\\2.jpg",120,755,450,50)
    aux.drawImage("C:/BitNami/djangostack-1.5.5-1/PBD/Gest/static/3.jpg",10,200,50,450)
    aux.drawImage("C:/BitNami/djangostack-1.5.5-1/PBD/Gest/static/4.jpg",540,200,50,450)
    aux.drawString(200,800,"Informe de Ventas Serviteca PNEUS")
    aux.showPage()
    aux.save()
    return render(request, 'informes.html',{})

@login_required()
def regicliente(request):
    rutInvalido = False
    telefonoInvalido = False
    comunas = Comuna.objects.all()
    correoInvalido = False
    if request.method == 'POST':  
        form = RegiClienteForm(request.POST )
        while form.is_valid() and request.POST['comuna'] != '':
            rut = form.cleaned_data['rutCliente']
            rut = rut.replace('.','').replace('-','')
            if not rut.isdigit() and rut[-1] != 'K' and rut[-1] != 'k':
                rutInvalido = True
            elif len(rut) < 2:
                rutInvalido = True
            elif rut[len(rut)-1] != validaRut(int(rut[:-1])):
                rutInvalido = True
            telefono = form.cleaned_data['telefonoCliente']
            if len(telefono) <8 or not telefono.isdigit():
                telefonoInvalido = True
            correo = form.cleaned_data['correoCliente']
            if ((validaEmail(correo)) != True ):
                correoInvalido = True
            direccion = form.cleaned_data['direccionCliente']
            nombre = form.cleaned_data['nombreCliente']
            apellido = form.cleaned_data['apellidoCliente']
            comuna = request.POST['comuna']
            if comuna == '0':
                comuna = request.POST['comunaa']
                comuna = formatoNombre(comuna)
                if len(Comuna.objects.filter(nombreComuna=comuna)) == 0:
                    nuevacomuna = Comuna(nombreComuna=comuna)
                    nuevacomuna.save()
            comuna = Comuna.objects.filter(nombreComuna=comuna)
            clientes = Cliente.objects.filter(rutCliente=rut)
            if len(clientes) > 0:
                rutInvalido = True           
            if correoInvalido or rutInvalido or telefonoInvalido:
                break
            clientenuevo = Cliente(rutCliente=rut, nombreCliente=nombre, apellidoCliente=apellido, direccionCliente=direccion, correoCliente=correo, telefonoCliente=telefono) 
            clientenuevo.ComunaCliente=comuna[0]
            clientenuevo.estadoCliente= True
            clientenuevo.save()
            return HttpResponseRedirect(reverse('MenuServicio'))
    else:
        form =RegiClienteForm()
    data = {
        'telefonoInvalido': telefonoInvalido,
        'rutInvalido': rutInvalido,
        'correoInvalido': correoInvalido,
        'form': form,
        'comunas': comunas,
    }
    return render_to_response('regicliente.html', data, context_instance=RequestContext(request))

@login_required()
def regivehiculo(request):
    rutInvalido = False
    telefonoInvalido = False
    correoInvalido = False
    patenteInvalida = False
    clientenuevo = False
    camposVacios = False
    NC = '0'
    modelos = Modelo.objects.all()
    clientes = Cliente.objects.all()
    marcas = Marca.objects.all()
    comunas = Comuna.objects.all()
    if request.method == 'POST' and request.POST['cliente'] == '0' and request.POST['NC']=='0' and ('boton' in request.POST):
        clientenuevo = True
        NC = '1'
        form = RegiVehiculoForm(request.POST)
    elif request.method == 'POST' and request.POST['cliente'] == '0' and request.POST['NC']=='1':
        clientenuevo = True
        form = RegiVehiculoForm(request.POST)
        NC = '1'
        while request.POST['comuna'] != '':
            rut = request.POST['rutCliente']
            if rut == '':
                camposVacios = True
                break
            rut = rut.replace('.','').replace('-','')
            if not rut.isdigit() and rut[-1] != 'K' and rut[-1] != 'k':
                rutInvalido = True
            elif len(rut) < 2:
                rutInvalido = True
            elif rut[len(rut)-1] != validaRut(int(rut[:-1])):
                rutInvalido = True
            telefono = request.POST['telefonoCliente']
            if telefono == '':
                camposVacios = True
                break
            if len(telefono) <8 or not telefono.isdigit():
                telefonoInvalido = True
            correo = request.POST['correoCliente']
            if correo == '':
                camposVacios = True
                break
            if ((validaEmail(correo)) != True ):
                correoInvalido = True
            direccion = request.POST['direccionCliente']
            nombre = request.POST['nombreCliente']
            apellido =request.POST['apellidoCliente']
            if direccion == '' or nombre == '' or apellido == '':
                camposVacios = True
            comuna = request.POST['comuna']
            if comuna == '0':
                comuna = request.POST['comunaa']
                nuevacomuna = Comuna(nombreComuna=comuna)
                nuevacomuna.save()
            else:
                comuna = request.POST['comuna']
            comuna = Comuna.objects.filter(nombreComuna=comuna)
            clientes = Cliente.objects.filter(rutCliente=rut)
            if len(clientes) > 0:
                rutInvalido = True           
            if correoInvalido or rutInvalido or telefonoInvalido:
                break
            clientenuevo = Cliente(rutCliente=rut, nombreCliente=nombre, apellidoCliente=apellido, direccionCliente=direccion, correoCliente=correo, telefonoCliente=telefono) 
            clientenuevo.ComunaCliente=comuna[0]
            clientenuevo.estadoCliente= True
            if request.POST['patenteVehiculo']!='' and request.POST['anioVehiculo']!='' and request.POST['colorVehiculo']!='':
                marcaVehiculo = request.POST['Marca']
                nombreMarcaVehiculo = formatoNombre(marcaVehiculo)
                modeloVehiculo = request.POST['Modelo']
                nombreModeloVehiculo = formatoNombre(modeloVehiculo)
                patente = request.POST['patenteVehiculo']
                patente = patente.upper()
                anio = request.POST['anioVehiculo']
                color = request.POST['colorVehiculo']
                marcaVehiculo = Marca.objects.filter(nombreMarca=nombreMarcaVehiculo)
                if len(marcaVehiculo)==0:
                    nuevaMarca=Marca(nombreMarca=nombreMarcaVehiculo)
                    nuevaMarca.save()
                marcaVehiculo = Marca.objects.filter(nombreMarca=nombreMarcaVehiculo)
                modeloVehiculo = Modelo.objects.filter(nombreModelo=nombreModeloVehiculo)
                if len(modeloVehiculo) == 0:
                    nuevoModelo = Modelo(nombreModelo=nombreModeloVehiculo)
                    nuevoModelo.marcaID = marcaVehiculo[0]
                    nuevoModelo.save()
                modeloVehiculo = Modelo.objects.filter(nombreModelo=nombreModeloVehiculo)
                ListaV = Vehiculo.objects.filter(patenteVehiculo = patente)
                if ((validarPatente(patente)) != True ) or len(ListaV)>0:
                    patenteInvalida = True
                    break
                clientenuevo.save()
                clientenuevo = Cliente.objects.filter(rutCliente=rut)
                vehiculonuevo = Vehiculo(patenteVehiculo=patente, colorVehiculo=color, anioVehiculo=anio)
                vehiculonuevo.clienteRut = clientenuevo[0]
                vehiculonuevo.modeloID = modeloVehiculo[0]
                vehiculonuevo.save()
                return HttpResponseRedirect(reverse('MenuServicio'))
        data = {
            'comunas': comunas,
            'NC': NC,
            'clientenuevo':clientenuevo,
            'marcas': marcas,
            'rutInvalido': rutInvalido,
            'camposVacios':camposVacios,
            'form': form,
            'patenteInvalida': patenteInvalida,
            'modelos': modelos,
            'clientes': clientes,
        }
        return render_to_response('regivehiculo.html', data, context_instance=RequestContext(request))
    elif request.method == 'POST': 
        form = RegiVehiculoForm(request.POST)
        while form.is_valid():
            rut = request.POST['cliente']
            rut = rut.replace('.','').replace('-','')
            if not rut.isdigit() and rut[-1] != 'K' and rut[-1] != 'k':
                rutInvalido = True
            elif rut == '0':
                rutInvalido = True
            elif rut[len(rut)-1] != validaRut(int(rut[:-1])):
                rutInvalido = True   
            clienteRut= Cliente.objects.filter(rutCliente=rut) 
            patente = form.cleaned_data['patenteVehiculo']
            patente = patente.upper()
            ListaV = Vehiculo.objects.filter(patenteVehiculo = patente)
            if ((validarPatente(patente)) != True ) or len(ListaV) > 0:
                patenteInvalida = True
            marcaVehiculo = request.POST['Marca']
            nombreMarcaVehiculo = formatoNombre(marcaVehiculo)
            modeloVehiculo = request.POST['Modelo']
            nombreModeloVehiculo = formatoNombre(modeloVehiculo)
            if marcaVehiculo == '' or modeloVehiculo == '':
                camposVacios = True
            marcaVehiculo = Marca.objects.filter(nombreMarca=nombreMarcaVehiculo)
            if len(marcaVehiculo)==0:
                nuevaMarca=Marca(nombreMarca=nombreMarcaVehiculo)
                nuevaMarca.save()
            marcaVehiculo = Marca.objects.filter(nombreMarca=nombreMarcaVehiculo)
            print marcaVehiculo, nombreMarcaVehiculo, Marca.objects.filter(nombreMarca=nombreMarcaVehiculo)
            modeloVehiculo = Modelo.objects.filter(nombreModelo=nombreModeloVehiculo)
            if len(modeloVehiculo) == 0:
                nuevoModelo = Modelo(nombreModelo=nombreModeloVehiculo)
                nuevoModelo.marcaID = marcaVehiculo[0]
                nuevoModelo.save()
            modeloVehiculo = Modelo.objects.filter(nombreModelo=nombreModeloVehiculo)
            color = form.cleaned_data['colorVehiculo']
            anio = form.cleaned_data['anioVehiculo']
            if patenteInvalida or rutInvalido or camposVacios:
                break
            vehiculonuevo = Vehiculo(colorVehiculo=color, patenteVehiculo=patente, anioVehiculo=anio) 
            vehiculonuevo.modeloID=modeloVehiculo[0]
            vehiculonuevo.clienteRut=clienteRut[0]
            vehiculonuevo.save()
            return HttpResponseRedirect(reverse('MenuServicio'))
    else:
        form =RegiVehiculoForm()
    data = {
        'comunas':comunas,
        'NC': NC,
        'clientenuevo':clientenuevo,
        'marcas': marcas,
        'rutInvalido': rutInvalido,
        'camposVacios': camposVacios,
        'form': form,
        'patenteInvalida': patenteInvalida,
        'modelos': modelos,
        'clientes': clientes,
    }
    return render_to_response('regivehiculo.html', data, context_instance=RequestContext(request))


def validaRut(num):
    ini=num
    conta=2
    suma=0
    while num>0:
        suma= suma + (conta * (num%10))
        conta=conta+1
        if conta==8:
            conta=2     
        num=num/10
    conta=suma%11
    valor=11-conta
    if valor==10:
        valor="K"   
    elif valor==11:
        valor="0"
    else:
        valor = chr(valor+48)
    return valor

def validaEmail(email):
    return True if email_re.match(email) else False

def validarPatente(patente):
    if len(patente) == 0:
        return "A/D"
    patente = patente.replace("-", "")
    patente = patente.replace(" ", "")
    if len(patente) != 6:
        return False
    if (patente[0:2].isalpha() and patente[2:6].isdigit()) or (patente[0:4].isalpha() and patente[4:6].isdigit()):
        return True
    else:
        return False

def formatoNombre(nombre):
    nombreConFormato = ''
    aux = 0
    for l in nombre:
        if aux == 0:
            nombreConFormato+=l.upper()
            aux+=1
        else:
            nombreConFormato+=l.lower()
    return nombreConFormato

