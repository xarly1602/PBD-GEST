# -*- encoding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import User
# Create your models here.
class Cargo(models.Model):
	id = models.AutoField('ID', primary_key=True)
	nombreCargo = models.CharField(max_length=20)

	def __unicode__(self):
		return u'%s' % (self.nombreCargo)

class CargoOT(models.Model):
	id = models.AutoField('ID', primary_key=True)
	nombreCargoOT = models.CharField(max_length=20)

	def __unicode__(self):
		return u'%s' % (self.nombreCargoOT)

class Comuna(models.Model):
	nombreComuna = models.CharField(max_length=30)

	def __unicode__(self):
		return u'%s' % (self.nombreComuna)

class Cliente(models.Model):
	id = models.AutoField(primary_key=True)
	rutCliente = models.CharField(max_length=12)
	nombreCliente = models.CharField(max_length=30)
	apellidoCliente = models.CharField(max_length=30)
	direccionCliente = models.CharField(max_length=50)
	correoCliente = models.CharField(max_length=50)
	telefonoCliente = models.CharField(max_length=10)
	estadoCliente = models.BooleanField()

	#Llaves foráneas
	ComunaCliente = models.ForeignKey(Comuna)

	def __unicode__(self):
		return u'%s' % (self.rutCliente)

class Marca(models.Model):
	nombreMarca = models.CharField(max_length=30)

	def __unicode__(self):
		return u'%s' % (self.nombreMarca)

class Modelo(models.Model):
	nombreModelo = models.CharField(max_length=30)

	#Llave foránea
	marcaID = models.ForeignKey(Marca)

	def __unicode__(self):
		return u'%s' % (self.nombreModelo)

class FormaPago(models.Model):
	tipoPago = models.CharField(max_length=20)

	def __unicode__(self):
		return u'%s' % (self.tipoPago)

class Empleado(models.Model):
	user = models.OneToOneField(User)
	rutEmpleado = models.CharField(max_length=12)
	telefonoEmpleado = models.CharField(max_length=10)

	#Llaves foráneas
	cargoID = models.ForeignKey(Cargo)

	def __unicode__(self):
		return u'%s' % (self.user.first_name)

class Venta(models.Model):
	numeroVenta = models.AutoField('ID', primary_key=True)
	precioVenta = models.IntegerField()
	horaVenta = models.DateTimeField(auto_now_add=True)

	#Llaves foráneas
	empleadoID = models.ForeignKey(Empleado)
	pagoID = models.ForeignKey(FormaPago)
	clienteRut = models.ForeignKey(Cliente, null=True)
	#numeroOrden = models.ForeignKey(OrdenDeTrabajo, null=True)

	def __unicode__(self):
		return u'%s' % (self.numeroVenta)

class EstadoOT(models.Model):
	nombreEstado = models.CharField(max_length=20)

	def __unicode__(self):
		return u'%s' % (self.nombreEstado)

class Vehiculo(models.Model):
	patenteVehiculo = models.CharField(max_length=10, primary_key=True)
	colorVehiculo = models.CharField(max_length=20)
	anioVehiculo = models.IntegerField()
	estadoVehiculo = models.BooleanField()

	#Llaves foráneas
	modeloID = models.ForeignKey(Modelo)
	clienteRut = models.ForeignKey(Cliente)

	def __unicode__(self):
		return u'%s' % (self.patenteVehiculo)

class OrdenDeTrabajo(models.Model):
	numeroOrden = models.AutoField('ID', primary_key=True)
	observaciones = models.TextField()
	fechaInicio = models.DateField(auto_now_add=True)
	fechaTermino = models.DateField(null=True)
	kmVehiculo = models.IntegerField()
	combustibleVehiculo = models.CharField(max_length=1)

	#Llaves foráneas
	pagoID = models.ForeignKey(FormaPago)
	estadoID = models.ForeignKey(EstadoOT)
	clienteRut = models.ForeignKey(Cliente)
	numeroVenta = models.OneToOneField(Venta, null=True, blank=True)
	patenteVehiculo = models.ForeignKey(Vehiculo)

	def __unicode__(self):
		return u'%s' % (self.numeroOrden)

class Servicio(models.Model):
	nombreServicio = models.CharField(max_length=40)
	precioServicio = models.IntegerField()
	def __unicode__(self):
		return u'%s' % (self.nombreServicio)

class Proveedor(models.Model):
	nombreProveedor = models.CharField(max_length=30)
	telefonoProveedor = models.CharField(max_length=10)
	correoProveedor = models.CharField(max_length=50)
	estadoProveedor = models.BooleanField()
	rutProveedor = models.CharField(max_length=12)
	def __unicode__(self):
		return u'%s' % (self.nombreProveedor)

class TipoMaterial(models.Model):
	nombreTipo = models.CharField(max_length=30)

	def __unicode__(self):
		return u'%s' % (self.nombreTipo)

class Material(models.Model):
	nombreMaterial = models.CharField(max_length=30)
	codigoMaterial = models.CharField(max_length=10)
	stockMaterial = models.IntegerField()
	precioMaterial = models.IntegerField()
	ofertaMaterial = models.BooleanField()
	descuentoOferta = models.IntegerField()
	fechaInicioOferta = models.DateField()
	fechaTerminoOferta = models.DateField()
	precioNeto = models.IntegerField()

	#Llaves foráneas
	proveedorID = models.ForeignKey(Proveedor)
	tipoID = models.ForeignKey(TipoMaterial)

	def __unicode__(self):
		return u'%s' % (self.nombreMaterial)

class DetalleOT(models.Model):
	numeroOrden = models.ForeignKey(OrdenDeTrabajo)
	sevicioID = models.ForeignKey(Servicio)

	def __unicode__(self):
		return u'%s' % (self.numeroOrden)

class DetalleVenta(models.Model):
	cantidadMaterial = models.IntegerField()

	#Llaves foráneas
	numeroVenta = models.ForeignKey(Venta)
	codigoMaterial = models.ForeignKey(Material)

	def __unicode__(self):
		return u'%s' % (self.numeroVenta)

class EmpleadoOT(models.Model):
	#Llaves foráneas
	numeroOrden = models.ForeignKey(OrdenDeTrabajo)
	cargoOTID = models.ForeignKey(CargoOT)
	rutEmpleado = models.ForeignKey(Empleado)

	def __unicode__(self):
		return u'%s' % (self.numeroOrden)

class Herramienta(models.Model):
	nombreHerramienta = models.CharField(max_length=30)

	def __unicode__(self):
		return u'%s' % (self.nombreHerramienta)

class LogSistema(models.Model):
	timestamp = models.DateTimeField(auto_now_add=True)
	usuarioID = models.IntegerField()
	tabla = models.CharField(max_length=20)
	accion = models.CharField(max_length=10)

	def __unicode__(self):
		return u'%s' % (self.timestamp)

class Propiedad(models.Model):
	nombrePropiedad = models.CharField(max_length=30)
	unidadMedida = models.CharField(max_length=10)

	def __unicode__(self):
		return u'%s' % (self.nombrePropiedad)

class TMProp(models.Model):
	#Llaves foráneas
	propiedadID = models.ForeignKey(Propiedad)
	tipoID = models.ForeignKey(TipoMaterial)

	def __unicode__(self):
		return u'%s %s' % (self.propiedadID, self.tipoID)

class MaterialProp(models.Model):
	valorEntero = models.IntegerField(null=True)
	valorChar = models.CharField(max_length=20, null=True)

	#Llaves foráneas
	codigoMaterial = models.ForeignKey(Material)
	propiedadID = models.ForeignKey(TMProp)

	def __unicode__(self):
		return u'%s %s %s %s' % (self.valorEntero, self.valorChar, self.codigoMaterial, self.propiedadID)

class ServicioHerramienta(models.Model):
	cantidadHerramienta = models.IntegerField()

	#Llaves foráneas
	servicioID = models.ForeignKey(Servicio)
	herramientaID = models.ForeignKey(Herramienta)

	def __unicode__(self):
		return u'%s' % (self.servicioID)

class ServicioMaterial(models.Model):
	cantidadMaterial = models.IntegerField()

	#Llaves foráneas
	servicioID = models.ForeignKey(Servicio)
	materialID = models.ForeignKey(Material)

	def __unicode__(self):
		return u'%s' % (self.servicioID)
