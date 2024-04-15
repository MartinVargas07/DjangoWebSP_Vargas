from django.db import models
from django.contrib.auth.models import User
# Create your models here.

# Esto era para el CRUD de los usuarios
class Usuario(models.Model):
    nombre = models.CharField(max_length=50)
    apellido = models.CharField(max_length=50)
    nombre_usuario = models.CharField(max_length=50, verbose_name="Nombre del Usuario")
    email = models.EmailField(verbose_name="Correo electronico")
    tfno = models.CharField(max_length=10, verbose_name="Telefono")

# El mini core
class Vendedor(models.Model):
    nombre = models.CharField(max_length=50)
    def __str__(self):
        return self.nombre

class Producto(models.Model):
    nombre = models.CharField(max_length=50)
    precioUnitario = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Precio")
    def __str__(self):
        return self.nombre
    
class Venta(models.Model):
    vendedor = models.ForeignKey(Vendedor, on_delete=models.CASCADE, verbose_name="Vendedor")
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, verbose_name="Producto")
    cantidad = models.IntegerField(verbose_name="Cantidad Vendida", default=0)
    monto = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Monto Vendido", default=0)
    fecha_creacion = models.DateField(auto_now_add=True, verbose_name="Fecha de creacion", editable=False)
    fecha_edicion = models.DateTimeField(auto_now=True, verbose_name="Fecha de edicion")
    
# El Core
class DatosVentaUsuario(models.Model):
    cod_usuario = models.ForeignKey(User, null=False, on_delete=models.CASCADE, verbose_name="Usuario")
    conjunto_id = models.CharField(primary_key=True, max_length=10, verbose_name="Identificador de datos", unique=True)
    datos = models.JSONField(verbose_name="Datos de venta", default=dict)

class PrediccionVenta(models.Model):
    OPCIONES_MODELO = [
        ('sarima', 'Sarima'),
        ('ols', 'Ordinary Least Squares (OLS)'),
    ]
    cod_usuario = models.ForeignKey(User, null=False, on_delete=models.CASCADE, verbose_name="Usuario")
    modelo_usado = models.CharField(choices=OPCIONES_MODELO, max_length=50, verbose_name="Modelo usado", default="Sarima")
    cod_entrenamiento_usuario = models.ForeignKey(DatosVentaUsuario, to_field='conjunto_id', null=True, on_delete=models.CASCADE, verbose_name="Conjunto de datos de entrenamiento del Usuario")
    datos = models.JSONField(verbose_name="Datos de la predicción", default=dict)
    