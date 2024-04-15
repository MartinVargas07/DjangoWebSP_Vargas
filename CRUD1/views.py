import csv
import json

import pandas as pd
import statsmodels.api as sm

from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from .models import Usuario, Vendedor, Producto, Venta, DatosVentaUsuario, PrediccionVenta
from .form import UsuarioForm, UserRegisterForm, UserLoginForm, VendedorForm, ProductoForm, VentaForm, DateFilterForm, DatosVentaUsuarioForm, PrediccionVentaForm
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import logout, authenticate, login

from django.http import HttpResponse
from django.contrib.auth.models import User

from pyecharts import options as opts
from pyecharts.charts import Line

from django.contrib import messages


def can_edit_user(user):
    return user.has_perm('CRUD1.can_edit_user')

# Create your views here.

# CRUD y algunas cosas del login
##########################################################################################


def index(request):
    usuarios = Usuario.objects.all()
    campo = usuarios.model._meta.fields
    return render(request, "usuarios/index.html", {"usuarios": usuarios, "campo": campo, "request": request})


@login_required
def usercreate(request):
    formulario = UsuarioForm(request.POST or None, request.FILES or None)
    if formulario.is_valid():
        formulario.save()
        return redirect('index')
    return render(request, "usuarios/create.html", {"formulario": formulario})


def userdetails(request, id):
    usuario = Usuario.objects.get(id=id)
    return render(request, "usuarios/details.html", {"usuario": usuario})

# @permission_required('CRUD1.can_edit_user')


@user_passes_test(can_edit_user, login_url='index')
@login_required
def useredit(request, id):
    usuario = Usuario.objects.get(id=id)
    formulario = UsuarioForm(request.POST or None,
                             request.FILES or None, instance=usuario)
    if formulario.is_valid() and request.POST:
        formulario.save()
        return redirect('index')
    return render(request, "usuarios/edit.html", {"formulario": formulario})


@login_required
def userdelete(request, id):
    usuario = Usuario.objects.get(id=id)
    if usuario:
        usuario.delete()
    return redirect('index')
##########################################################################################

# Login, logout and register
##########################################################################################
# Login and register


def login_or_register(request):
    login_form = UserLoginForm(request.POST or None)
    register_form = UserRegisterForm(request.POST or None)
    if request.method == 'POST':

        # Registrar usuario
        if 'register' in request.POST:
            form = UserRegisterForm(request.POST)
            if form.is_valid():
                form.save()
                # Autenticar al usuario recién registrado
                username = form.cleaned_data.get('username')
                raw_password = form.cleaned_data.get('password1')
                user = authenticate(username=username, password=raw_password)
                login(request, user)
                return redirect('index')
        # Iniciar sesión
        elif 'login' in request.POST:
            form = UserLoginForm(request, data=request.POST)
            if form.is_valid():
                username = form.cleaned_data.get('username')
                raw_password = form.cleaned_data.get('password')
                user = authenticate(username=username, password=raw_password)
                login(request, user)
                return redirect('index')
    context = {'login_form': login_form, 'register_form': register_form}
    return render(request, 'registration/login.html', context)


# Logout
def exit(request):
    logout(request)
    return redirect('index')
##########################################################################################


# Mini core
##########################################################################################
def indexvendedor(request):
    vendedores = Vendedor.objects.all()
    campo = vendedores.model._meta.fields
    return render(request, "MiniCore/vendedores/index.html", {"vendedores": vendedores, "campo": campo})

def vendedorescreate(request):
    formulario = VendedorForm(request.POST or None, request.FILES or None)
    if formulario.is_valid():
        formulario.save()
        return redirect('vendedores')
    return render(request, "MiniCore/vendedores/create.html", {"formulario": formulario})

def indexproducto(request):
    productos = Producto.objects.all()
    campo = productos.model._meta.fields
    return render(request, "MiniCore/producto/index.html", {"productos": productos, "campo": campo})

def productoscreate(request):
    formulario = ProductoForm(request.POST or None, request.FILES or None)
    if formulario.is_valid():
        formulario.save()
        return redirect('productos')
    return render(request, "MiniCore/producto/create.html", {"formulario": formulario})

def indexventas(request):
    ventas = Venta.objects.all()
    campo = ventas.model._meta.fields
    return render(request, "MiniCore/ventas/index.html", {"ventas": ventas, "campo": campo})


def ventascreate(request):
    formulario = VentaForm(request.POST or None, request.FILES or None)
    if formulario.is_valid():
        formulario.save()
        return redirect('ventas')
    return render(request, "MiniCore/ventas/create.html", {"formulario": formulario})


def report(request):
    form = DateFilterForm(request.GET)
    if not form.data:
        form.errors.clear()
        return render(request, 'MiniCore/filtrofechas.html', {'form': form})
    if not form.is_valid():
        return render(request, 'MiniCore/filtrofechas.html', {'form': form})

    fecha_inicio = form.cleaned_data['fecha_inicio']
    fecha_fin = form.cleaned_data['fecha_fin']

    ventas = Venta.objects.all()
    results = []
    for venta in ventas:
        # Filter by creation date
        rango = venta.fecha_creacion >= fecha_inicio and venta.fecha_creacion <= fecha_fin
        if not rango:
            continue
        vendedor = venta.vendedor
        # Find the client in the results and update it
        vendedor_found = False
        for result in results:
            if result['vendedor'] == vendedor:
                vendedor_found = True
                result['ventas'] += 1
                result['total_monto'] += venta.monto
                break
        # If the client is not in the results, add it
        if not vendedor_found:
            results.append({
                'vendedor': vendedor,
                'ventas': 1,
                'total_monto': venta.monto
            })
    # Sort the results by total price
    results.sort(key=lambda result: result['total_monto'], reverse=True)
    return render(request, 'MiniCore/filtrofechas.html', {
        'form': form,
        'results': results,
        'summary': {
            'ventas': sum(result['ventas'] for result in results),
            'total_monto': sum(result['total_monto'] for result in results),
            'vendedores': len(results)
        }
    })


##########################################################################################

# CORE
##########################################################################################

@login_required
def tabla_datos_venta(request, id):
    datos_venta = DatosVentaUsuario.objects.filter(cod_usuario_id=id)
    context = {
        'datos_venta': datos_venta,
    }
    return render(request, 'CORE/indexCore.html', context)


def decimal_default(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError


@login_required
def datos_venta_usuario_create(request):
    if request.method == 'POST':
        formulario = DatosVentaUsuarioForm(request.POST, request.FILES)
        if formulario.is_valid():
            cod_usuario_id = request.user.id
            conjunto_id = formulario.cleaned_data['conjunto_id']
            datos_file = formulario.cleaned_data['datos_file']

            # Obtener la instancia de User correspondiente al ID del usuario actual
            cod_usuario = User.objects.get(id=cod_usuario_id)

            # Leer los datos del archivo CSV y realizar el procesamiento necesario
            # Leer los datos del archivo CSV y calcular la ganancia
            datos = []
            csv_reader = csv.DictReader(datos_file.read().decode('utf-8').splitlines())
            fecha = []
            ventas = []
            valor_unitario = []
            # csv_reader = csv.DictReader(datos_file)
            for row in csv_reader:
                fecha = row['Fecha']
                ventas = int(row['Ventas Producto A'])
                valor_unitario = Decimal(row['Valor Unitario'])
                ganancia = ventas * valor_unitario

                # Crear el diccionario con los datos
                datos.append({
                    'Fecha': fecha,
                    'Ventas Producto A': ventas,
                    'Valor Unitario': float(valor_unitario),
                    'Ganancia': float(ganancia)
                })

            # Convertir la lista de datos a formato JSON
            datos_json = json.dumps(datos, default=decimal_default)

            # Crear un nuevo registro en DatosVentaUsuario
            datos_venta_usuario = DatosVentaUsuario(
                cod_usuario=cod_usuario,
                conjunto_id=conjunto_id,
                datos=datos_json
            )
            datos_venta_usuario.save()

            # Redireccionar a una página de éxito o cualquier otra ruta deseada
            return redirect('index')
    else:
        formulario = DatosVentaUsuarioForm()

    return render(request, 'CORE/datosVentas/create.html', {'formulario': formulario})


@login_required
def realizar_prediccion(request):
    if request.method == 'POST':
        formulario = PrediccionVentaForm(request.POST)
        if formulario.is_valid():
            cod_usuario_id = request.user.id
            conjunto_id = formulario.cleaned_data['conjunto_id']
            modelo_usado = formulario.cleaned_data['modelo_usado']
            fecha_inicio = formulario.cleaned_data['fecha_inicio']
            fecha_fin = formulario.cleaned_data['fecha_fin']

            # Obtener la instancia de User correspondiente al ID del usuario actual
            cod_usuario = User.objects.get(id=cod_usuario_id)

            # Obtener el objeto DatosVentaUsuario correspondiente al conjunto_id
            datos_venta_usuario = DatosVentaUsuario.objects.get(
                conjunto_id=conjunto_id)

            # Obtener el JSON de datos de la tabla DatosVentaUsuario
            datos_json = datos_venta_usuario.datos

            # Cargar los datos en un DataFrame de Pandas
            datos_df = pd.DataFrame(json.loads(datos_json))

            # Obtener el precio unitario antes de eliminar la columna
            precio_unitario = datos_df['Valor Unitario'].values[0]

            # Eliminar las columnas de Precio Unitario y Ganancias
            datos_df = datos_df.drop(
                ['Ventas Producto A', 'Valor Unitario'], axis=1)

            # Cambiar el formato de la fecha al formato "%d/%m/%Y"
            datos_df['Fecha'] = pd.to_datetime(
                datos_df['Fecha'], format="%d/%m/%Y")

            # Convertir la columna de fechas en el índice
            datos_df = datos_df.set_index('Fecha')

            # Realizar las transformaciones de fechas
            fecha_inicio = pd.to_datetime(fecha_inicio)
            fecha_fin = pd.to_datetime(fecha_fin)

            # Generar el rango de fechas para el pronóstico
            fechas = pd.date_range(start=fecha_inicio, end=fecha_fin, freq='D')

            if modelo_usado == 'sarima':
                # Realizar el entrenamiento del modelo SARIMA
                P, D, Q, S = 1, 1, 1, 12
                p, d, q = 2, 1, 2
                modelo_sarima = sm.tsa.SARIMAX(datos_df, order=(
                    p, d, q), seasonal_order=(P, D, Q, S))
                resultados_sarima = modelo_sarima.fit()

                # Realizar la predicción de ventas para el rango de fechas dado
                pronostico = resultados_sarima.predict(
                    start=fecha_inicio, end=fecha_fin)

            else:
                modelo_ols = sm.OLS(
                    datos_df, sm.add_constant(range(len(datos_df))))
                resultados_ols = modelo_ols.fit()

                pronostico = resultados_ols.predict(sm.add_constant(
                    range(len(datos_df), len(datos_df) + len(fechas))))

            # Calcular la cantidad de productos vendidos dividiendo el pronóstico por el valor unitario
            productos_vendidos = (pronostico / precio_unitario).astype(int)

            # Reducir el pronóstico a dos decimales
            pronostico = pronostico.round(2)

            # Crear un DataFrame con los datos requeridos
            datos_prediccion_df = pd.DataFrame({
                'Fecha': fechas.strftime("%d/%m/%Y"),
                'Productos Vendidos': productos_vendidos,
                'Valor Unitario': precio_unitario,
                'Pronostico': pronostico
            })
            pronostico_json = datos_prediccion_df.to_json(orient='records')

            # Crear un nuevo registro en PrediccionVenta
            prediccion_venta = PrediccionVenta(
                cod_usuario=cod_usuario,
                cod_entrenamiento_usuario=datos_venta_usuario,
                modelo_usado=modelo_usado,
                datos=pronostico_json
            )
            prediccion_venta.save()

            # Redireccionar a una página de éxito o cualquier otra ruta deseada
            return redirect('index')
    else:
        formulario = PrediccionVentaForm()

    return render(request, 'CORE/datosPrediccion/prediccion.html', {'formulario': formulario})

@login_required
def grafica_datos_venta(request, id):
    datos_venta = DatosVentaUsuario.objects.get(conjunto_id=id)
    datos_prediccion = PrediccionVenta.objects.filter(cod_entrenamiento_usuario=id, cod_usuario=request.user.id)

    # Obtener los datos del JSON
    json_data = json.loads(datos_venta.datos)
    # Obtener el valor unitario de cualquier elemento del JSON
    valor_unitario = json_data[0]['Valor Unitario']
    # Extraer las fechas y ganancias del JSON
    fechas = [data['Fecha'] for data in json_data]
    ganancias = [data['Ganancia'] for data in json_data]
    ventas_producto_a = [data['Ventas Producto A'] for data in json_data]

    # Crear una lista de etiquetas de datos con la información de ventas producto A
    data_labels = [f"Ventas: {venta}" for venta in ventas_producto_a]

    # Crear el gráfico de línea con ECharts
    line_chart = (
        Line()
        .add_xaxis(fechas)
        .add_yaxis("Ganancia", ganancias, label_opts=opts.LabelOpts("data_labels", data_labels))
        .set_global_opts(title_opts=opts.TitleOpts(title="Gráfico de Ganancias"), xaxis_opts=opts.AxisOpts(name="Fecha"),
                         yaxis_opts=opts.AxisOpts(name="Dinero"))
    )

    # Renderizar el gráfico en el template
    chart_options = line_chart.dump_options_with_quotes()
    context = {
        'valor_unitario': valor_unitario,
        "chart_options": chart_options,
        "datos_venta": datos_venta,
        "datos_prediccion": datos_prediccion,
        "data_labels": data_labels,
    }
    return render(request, 'CORE/datosVentas/graficodetails.html', context)

@login_required
def grafica_datos_prediccion(request, id):
    datos_prediccion = PrediccionVenta.objects.get(id=id)

    # Obtener los datos del JSON
    json_data = json.loads(datos_prediccion.datos)
    # Obtener el valor unitario de cualquier elemento del JSON
    valor_unitario = json_data[0]['Valor Unitario']
    # Extraer las fechas y ganancias del JSON
    fechas = [data['Fecha'] for data in json_data]
    pronostico = [data['Pronostico'] for data in json_data]
    ventas_producto = [data['Productos Vendidos'] for data in json_data]

    # Crear una lista de etiquetas de datos con la información de ventas producto A
    data_labels = [f"Ventas: {venta}" for venta in ventas_producto]

    # Crear el gráfico de línea con ECharts
    line_chart = (
        Line()
        .add_xaxis(fechas)
        .add_yaxis("Pronostico", pronostico, label_opts=opts.LabelOpts("data_labels", data_labels))
        .set_global_opts(title_opts=opts.TitleOpts(title="Gráfico de Prediccion"), xaxis_opts=opts.AxisOpts(name="Fecha"),
                         yaxis_opts=opts.AxisOpts(name="Dinero"))
    )

    # Renderizar el gráfico en el template
    chart_options = line_chart.dump_options_with_quotes()
    context = {
        'valor_unitario': valor_unitario,
        "chart_options": chart_options,
        "datos_prediccion": datos_prediccion,
        "data_labels": data_labels,
    }
    return render(request, 'CORE/datosPrediccion/graficodetails.html', context)

def calculo(request):
    # Obtener las últimas dos instancias de PrediccionVenta
    ultimas_predicciones = PrediccionVenta.objects.order_by('-id')[:2]
    
    # Obtener los datos de la primera predicción
    datos_prediccion_1 = json.loads(ultimas_predicciones[0].datos)
    fechas1 = [data['Fecha'] for data in datos_prediccion_1]
    valor_unitario1 = [data['Valor Unitario'] for data in datos_prediccion_1]
    ventas_producto1 = [data['Productos Vendidos'] for data in datos_prediccion_1]
    pronostico1 = [data['Pronostico'] for data in datos_prediccion_1]

    # Obtener los datos de la segunda predicción
    datos_prediccion_2 = json.loads(ultimas_predicciones[1].datos)
    fechas2 = [data['Fecha'] for data in datos_prediccion_2]
    valor_unitario2 = [data['Valor Unitario'] for data in datos_prediccion_2]
    ventas_producto2 = [data['Productos Vendidos'] for data in datos_prediccion_2]
    pronostico2 = [data['Pronostico'] for data in datos_prediccion_2]

    
    diferenciaproductos = [p1 - p2 for p1, p2 in zip(ventas_producto1, ventas_producto2)]

    # Realizar el cálculo utilizando los datos obtenidos
    diferenciaganancia = [round(p1 - p2, 2) for p1, p2 in zip(pronostico1, pronostico2)]
    
    diferenciaganancia_porcentaje = [round(((p1 - p2) / p2) * 100, 2) for p1, p2 in zip(pronostico1, pronostico2)]
    
    datos1 = zip(fechas1, valor_unitario1, ventas_producto1, pronostico1)
    datos2 = zip(fechas2, valor_unitario2, ventas_producto2, pronostico2)
    diferencia = zip(diferenciaproductos, diferenciaganancia, diferenciaganancia_porcentaje)
    # Agregar los datos, la diferencia y cualquier otro valor necesario al contexto
    context = {
        "datos1": datos1,
        "datos2": datos2,
        "diferencia": diferencia,
    }
    return render(request, 'CORE/calculo.html', context)