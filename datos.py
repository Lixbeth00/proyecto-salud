import os
import django
from datetime import datetime, timedelta
import mercadopago

# Configurar el entorno del proyecto
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SALUD.settings')  # Reemplaza "SALUD" con el nombre de tu proyecto
django.setup()

from Base.models import *
from settings import ACCESS_TOKEN  # Ajusta la importación de ACCESS_TOKEN según tu configuración

# Inicializa el cliente de Mercado Pago
sdk = mercadopago.SDK(ACCESS_TOKEN)

# 1. Agregar valores a la tabla Inventario
for i in range(5):
    Inventario.objects.create(
        nombre=f"Producto {i+1}",
        descripcion=f"Descripción del producto {i+1}",
        categoria="Categoría General",
        precio=100.00 + i * 10,
        stock=50 - i
    )

# 2. Agregar valores a la tabla Envio
for i in range(5):
    envio = Envio.objects.create(
        id_orden=f"ORD-{i+1}",
        fecha_envio=datetime.now(),
        fecha_estimada_llegada=datetime.now() + timedelta(days=5 + i),
        precio_total=500.00 + i * 20,
        estado_entrega="Pendiente",
        direccion_entrega=f"Dirección {i+1}",
        nombre_destinatario=f"Destinatario {i+1}",
        costo_envio=50.00 + i * 5,
        transportista="DHL"
    )
    envio.productos.set(Inventario.objects.all()[:2])  # Asocia dos productos por envío

# 3. Agregar valores a la tabla Usuarios
for i in range(5):
    Usuarios.objects.create_user(
        username=f"usuario{i+1}",
        password="password123",
        email=f"usuario{i+1}@example.com",
        first_name=f"Nombre {i+1}",
        last_name=f"Apellido {i+1}",
        is_active=True
    )

# 4. Agregar valores a la tabla Hospitales
for i in range(5):
    Hospitales.objects.create(
        nombre=f"Hospital {i+1}",
        direccion=f"Dirección {i+1}",
        ciudad=f"Ciudad {i+1}",
        estado=f"Estado {i+1}",
        pais="México",
        telefono=f"123-456-789{i}",
        email=f"hospital{i+1}@example.com"
    )

# 5. Agregar valores a la tabla Categorias
for i in range(5):
    Categorias.objects.create(
        nombre=f"Categoría {i+1}",
        descripcion=f"Descripción de la categoría {i+1}"
    )

# 6. Agregar valores a la tabla Medications
for i in range(5):
    Medications.objects.create(
        nombre=f"Medicamento {i+1}",
        descripcion=f"Descripción del medicamento {i+1}",
        categoria=f"Categoría {i+1}",
        precio=200.00 + i * 15,
        stock=100 - i * 5,
        tiempo_produccion=7 + i
    )

# 7. Agregar valores a la tabla Orders
hospitales = Hospitales.objects.all()[:5]
for i in range(5):
    Orders.objects.create(
        hospital=hospitales[i],
        estado="Pendiente",
        tiempo_estimado_entrega=3 + i,
        total=1000.00 + i * 50,
        prioridad="Alta" if i % 2 == 0 else "Normal"
    )

# 8. Agregar valores a la tabla OrderItems
orders = Orders.objects.all()
medications = Medications.objects.all()
for i, order in enumerate(orders):
    OrderItems.objects.create(
        order=order,
        medication=medications[i],
        cantidad=5 + i,
        precio_unitario=medications[i].precio,
        subtotal=(5 + i) * medications[i].precio
    )

# 9. Procesar pagos con Mercado Pago
for i, order in enumerate(orders):
    payment_data = {
        "transaction_amount": order.total,
        "description": f"Pago por Orden {order.id}",
        "installments": 1,
        "payment_method_id": "visa",  # Cambiar según los métodos soportados
        "payer": {
            "email": f"usuario{i+1}@example.com"  # Usar el email del usuario relacionado
        }
    }

    # Procesa el pago en Mercado Pago
    payment_response = sdk.payment().create(payment_data)
    payment = payment_response.get("response", {})

    Payments.objects.create(
        order=order,
        monto=order.total,
        metodo_pago=payment.get("payment_method_id", "Desconocido"),
        estado_pago=payment.get("status", "Error"),
        referencia_pago=payment.get("id", "Sin Referencia")
    )

    print(f"Orden {order.id} - Estado del Pago: {payment.get('status', 'Error')}")

# 10. Agregar valores a la tabla Shipments
for i, order in enumerate(orders):
    Shipments.objects.create(
        order=order,
        fecha_envio=datetime.now() - timedelta(days=i),
        fecha_estimada_llegada=datetime.now() + timedelta(days=i+3),
        proveedor_envio="FedEx",
        tracking_number=f"TRACK-{i+1}",
        estado="En tránsito",
        costo_envio=50.00 + i * 10
    )

# 11. Agregar valores a las tablas restantes (StockHistory, Discounts, etc.)
for i, medication in enumerate(medications):
    StockHistory.objects.create(
        medication=medication,
        cambio_stock=-5,
        razon=f"Ajuste de stock por pedido {i+1}"
    )

    Discounts.objects.create(
        medication=medication,
        porcentaje_descuento=10.0 + i,
        fecha_inicio=datetime.now(),
        fecha_fin=datetime.now() + timedelta(days=10)
    )

usuarios = Usuarios.objects.all()[:5]
for i, usuario in enumerate(usuarios):
    PurchaseHistory.objects.create(
        usuario=usuario,
        order=orders[i],
        total=orders[i].total,
        estado="Completado"
    )

    Notifications.objects.create(
        usuario=usuario,
        mensaje=f"Notificación {i+1}",
        leido=False
    )
