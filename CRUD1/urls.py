from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),

    # CRUD1
    path('usercreate', views.usercreate, name='usercreate'),
    path('userdetails/<int:id>', views.userdetails, name='userdetails'),
    path('useredit/<int:id>', views.useredit, name='useredit'),
    path('userdelete/<int:id>', views.userdelete, name='userdelete'),

    # Login, logout and register
    path('logout/', views.exit, name='exit'),
    path('iniciarsesion/', views.login_or_register, name='login_or_register'),

    # Mini core
    path('vendedores/', views.indexvendedor, name='vendedores'),
    path('vendedores/create/', views.vendedorescreate, name='vendedorescreate'),

    path('productos/', views.indexproducto, name='productos'),
    path('productos/create/', views.productoscreate, name='productoscreate'),

    path('ventas/', views.indexventas, name='ventas'),
    path('ventas/create/', views.ventascreate, name='ventascreate'),

    path('reporte/', views.report, name='reporte'),
    
    # Test
    # path('mostrar_user_id/', views.mostrar_user_id, name='mostrar_user_id'),
    
    # Core
    path('indexCore/<int:id>/', views.tabla_datos_venta, name='indexCore'),
    path('crear-datos-venta/', views.datos_venta_usuario_create, name='crear_datos_venta'),
    path('realizar_prediccion/', views.realizar_prediccion, name='realizar_prediccion'),
    path('grafica_ventas/<str:id>/', views.grafica_datos_venta, name='grafica_ventas'),
    path('grafica_pronostico/<int:id>/', views.grafica_datos_prediccion, name='grafica_pronostico'),
    path('calculo', views.calculo, name='calculo'),
]
