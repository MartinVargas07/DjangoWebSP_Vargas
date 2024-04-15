# Esto era para el form de las tablas usuario del propio Django
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User

# Esto era para el form de las tablas creadas
from django.forms import ModelForm
from .models import Usuario, Vendedor, Producto, Venta

# CRUD
##########################################################################################
class UsuarioForm(ModelForm):
    class Meta:
        model = Usuario
        fields = '__all__'
##########################################################################################

# Login, logout and register
##########################################################################################
class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()
    # contraseña1 = forms.CharField(label='Contraseña', widget=forms.PasswordInput)
    # contraseña2 = forms.CharField(label='Confirma Contraseña', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
        # help_texts = {k:"" for k in fields }


class UserLoginForm(AuthenticationForm):
    class Meta:
        model = User
        fields = ['username', 'password']
##########################################################################################


# Mini core
##########################################################################################
class VendedorForm(ModelForm):
    class Meta:
        model = Vendedor
        fields = '__all__'

class ProductoForm(ModelForm):
    class Meta:
        model = Producto
        fields = '__all__'


class VentaForm(ModelForm):
    vendedor = forms.ModelChoiceField(
        queryset=Vendedor.objects.all(),
        label='Vendedor',
        to_field_name='nombre',  # aquí especificamos el campo 'nombre' en lugar del campo 'id'
        widget=forms.Select(attrs={'class': 'form-control'}),
    )
    producto = forms.ModelChoiceField(
        queryset=Producto.objects.all(),
        label='Producto',
        to_field_name='nombre',  # aquí especificamos el campo 'nombre' en lugar del campo 'id'
        widget=forms.Select(attrs={'class': 'form-control'}),
    )
    class Meta:
        model = Venta
        fields = ['vendedor', 'producto', 'cantidad']
  
    def save(self, commit=True):
        venta = super().save(commit=False)

        cantidad = self.cleaned_data['cantidad']
        producto = self.cleaned_data['producto']
        venta.monto = cantidad * producto.precioUnitario

        if commit:
            venta.save()

        return venta

class DateFilterForm(forms.Form):
    fecha_inicio = forms.DateField(
        label='Fecha de inicio',
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    fecha_fin = forms.DateField(
        label='Fecha de fin',
        widget=forms.DateInput(attrs={'type': 'date'})
    )

    def __init__(self, *args, **kwargs):
        super(DateFilterForm, self).__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super(DateFilterForm, self).clean()
        fecha_inico = cleaned_data.get('fecha_inicio')
        fecha_fin = cleaned_data.get('fecha_fin')
        if fecha_inico and fecha_fin:
            if fecha_inico > fecha_fin:
                raise forms.ValidationError(
                    'La fecha de inicio no debe ser mayor que la fecha de fin')
        return cleaned_data
##########################################################################################

# CORE
##########################################################################################
class DatosVentaUsuarioForm(forms.Form):
    conjunto_id = forms.CharField(max_length=10)
    datos_file = forms.FileField()
    
class PrediccionVentaForm(forms.Form):
    OPCIONES_MODELO = [
        ('sarima', 'Sarima'),
        ('ols', 'Ordinary Least Squares (OLS)'),
    ]
        
    conjunto_id = forms.CharField(max_length=10)
    fecha_inicio = forms.DateField(widget=forms.DateInput(attrs={'class': 'datepicker', 'type': 'date'}))
    fecha_fin = forms.DateField(widget=forms.DateInput(attrs={'class': 'datepicker', 'type': 'date'}))
    modelo_usado = forms.ChoiceField(choices=OPCIONES_MODELO, label="Modelo usado")
    
    class Meta:
        labels = {
            'conjunto_id': 'Identificador de datos',
            'fecha_inicio': 'Fecha de inicio',
            'fecha_fin': 'Fecha de fin',
            'modelo_usado':'Modelo usado',
        }

##########################################################################################