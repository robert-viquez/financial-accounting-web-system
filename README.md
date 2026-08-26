# Sistema Web Financiero-Contable — Queso Los Santos

## Base de datos para la demostración

El comando destructivo de demostración solo funciona con `DEBUG=True` y la
autorización explícita `ALLOW_DEMO_SEED=true`. La contraseña se recibe por el
entorno y nunca se almacena en el repositorio:

```bash
cd backend
export ALLOW_DEMO_SEED=true
export DEMO_USER_PASSWORD='una-clave-temporal-segura'
python manage.py seed_demo --reset --seed 20260828
```

El comando conserva catálogos estructurales, roles, medios de pago y
configuración; reconstruye los datos operativos dentro de una transacción
atómica. Genera 15 productos terminados, 15 clientes individuales ficticios,
6 proveedores, 66 ventas, 18 compras y sus movimientos, cuentas, pagos y
asientos a través de los flujos normales del sistema. Al final valida totales,
saldos, inventario, relaciones y partida doble. Los costos son supuestos de
demostración modelados y no precios históricos de la empresa.

Los usuarios creados son `rsantos` (administrador) y `cajero` (rol
`Operaciones`). `rviquez` conserva su contraseña actual y privilegios totales.
