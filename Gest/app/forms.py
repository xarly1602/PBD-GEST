from django import forms
from django.contrib.auth.models import User
from django.forms import ModelForm
from app.models import *
 
class SignUpForm(ModelForm):
    class Meta:
        model = User
        fields = ['username', 'password', 'email', 'first_name', 'last_name']
        widgets = {
            'password': forms.PasswordInput(),
        }

class EmpleadoForm(ModelForm):
    class Meta:
        model = Empleado
        fields = ['rutEmpleado', 'telefonoEmpleado']
        
class RegiClienteForm(ModelForm):
    class Meta:
        model = Cliente
        fields = ['nombreCliente', 'apellidoCliente', 'rutCliente', 'correoCliente', 'direccionCliente', 'telefonoCliente']

class RegiVehiculoForm(ModelForm):
    class Meta:
        model = Vehiculo
        fields = ['patenteVehiculo', 'colorVehiculo', 'anioVehiculo']

class FormOT(ModelForm):
    class Meta:
        model = OrdenDeTrabajo
        fields = ['kmVehiculo']

class RegiProveedorForm(ModelForm):
    class Meta:
        model = Proveedor 
        fields =['rutProveedor', 'nombreProveedor', 'telefonoProveedor', 'correoProveedor']