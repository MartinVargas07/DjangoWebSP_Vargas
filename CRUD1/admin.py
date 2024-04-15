from django.contrib import admin
from django.contrib.auth.models import Permission 
from CRUD1.models import Usuario
# Register your models here.

class UsuarioAdmin(admin.ModelAdmin):
    list_display=("nombre","apellido","nombre_usuario","email","tfno")

admin.site.register(Usuario,UsuarioAdmin)
admin.site.register(Permission)
