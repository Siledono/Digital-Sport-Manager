"""
constantes.py
Digital Sport Manager - Club Deportivo

Valores fijos compartidos por los tres módulos (A, B y C).
Si un valor cambia aquí, cambia en todo el sistema.
Los valores de texto coinciden EXACTAMENTE con los de seed.sql / schema.sql.
"""

import os

# ---------------------------------------------------------------------------
# Conexión a MySQL (se puede sobreescribir con variables de entorno)
# ---------------------------------------------------------------------------
DB_CONFIG = {
    "host": os.getenv("DSM_DB_HOST", "localhost"),
    "port": int(os.getenv("DSM_DB_PORT", "3306")),
    "user": os.getenv("DSM_DB_USER", "root"),
    "password": os.getenv("DSM_DB_PASSWORD", ""),
    "database": os.getenv("DSM_DB_NAME", "digitalsportmanager"),
}

# ---------------------------------------------------------------------------
# Nombres de las tablas (16, según el modelo relacional)
# ---------------------------------------------------------------------------
# Nivel 1 (sin FK)
TABLA_CATEGORIA = "CATEGORIA"
TABLA_TIPO_MEMBRESIA = "TIPO_MEMBRESIA"
TABLA_ACTIVIDAD = "ACTIVIDAD"
TABLA_ESPACIO_DEPORTIVO = "ESPACIO_DEPORTIVO"
TABLA_MATERIAL = "MATERIAL"
TABLA_ENTRENADOR = "ENTRENADOR"
# Nivel 2
TABLA_EQUIPO = "EQUIPO"
# Nivel 3
TABLA_MIEMBRO = "MIEMBRO"
# Nivel 4
TABLA_MEMBRESIA = "MEMBRESIA"
TABLA_HORARIO = "HORARIO"
TABLA_ESPACIO_MATERIAL = "ESPACIO_MATERIAL"
# Nivel 5
TABLA_PAGO = "PAGO"
TABLA_INSCRIPCION = "INSCRIPCION"
TABLA_RESERVA = "RESERVA"
TABLA_ASISTENCIA = "ASISTENCIA"
TABLA_EQUIPO_HORARIO = "EQUIPO_HORARIO"

# Orden de creación (respeta las llaves foráneas)
TABLAS_ORDEN_CREACION = (
    TABLA_CATEGORIA,
    TABLA_TIPO_MEMBRESIA,
    TABLA_ACTIVIDAD,
    TABLA_ESPACIO_DEPORTIVO,
    TABLA_MATERIAL,
    TABLA_ENTRENADOR,
    TABLA_EQUIPO,
    TABLA_MIEMBRO,
    TABLA_MEMBRESIA,
    TABLA_HORARIO,
    TABLA_ESPACIO_MATERIAL,
    TABLA_PAGO,
    TABLA_INSCRIPCION,
    TABLA_RESERVA,
    TABLA_ASISTENCIA,
    TABLA_EQUIPO_HORARIO,
)

# Orden para borrar / vaciar tablas (inverso al de creación)
TABLAS_ORDEN_BORRADO = tuple(reversed(TABLAS_ORDEN_CREACION))

# ---------------------------------------------------------------------------
# Estatus de miembros y entrenadores (RF-01: baja lógica, no se elimina)
# ---------------------------------------------------------------------------
ESTATUS_ACTIVO = "activo"
ESTATUS_INACTIVO = "inactivo"
ESTATUS_VALIDOS = (ESTATUS_ACTIVO, ESTATUS_INACTIVO)

# ---------------------------------------------------------------------------
# Membresías (RF-04 y RF-06)
# ---------------------------------------------------------------------------
ESTADO_MEMB_VIGENTE = "vigente"
ESTADO_MEMB_POR_VENCER = "por vencer"
ESTADO_MEMB_VENCIDA = "vencida"
ESTADOS_MEMBRESIA = (
    ESTADO_MEMB_VIGENTE,
    ESTADO_MEMB_POR_VENCER,
    ESTADO_MEMB_VENCIDA,
)

# Una membresía está "por vencer" si faltan este número de días o menos
DIAS_POR_VENCER = 7

# ---------------------------------------------------------------------------
# Pagos (RF-04)
# ---------------------------------------------------------------------------
ESTADO_PAGO_PAGADO = "pagado"
ESTADO_PAGO_PENDIENTE = "pendiente"
ESTADOS_PAGO = (ESTADO_PAGO_PAGADO, ESTADO_PAGO_PENDIENTE)

METODO_PAGO_EFECTIVO = "efectivo"
METODO_PAGO_TARJETA = "tarjeta"
METODO_PAGO_TRANSFERENCIA = "transferencia"
METODOS_PAGO = (METODO_PAGO_EFECTIVO, METODO_PAGO_TARJETA, METODO_PAGO_TRANSFERENCIA)

# ---------------------------------------------------------------------------
# Inscripciones (RF-07): solo una activa por alumno, la anterior pasa a finalizada
# ---------------------------------------------------------------------------
ESTADO_INSCR_ACTIVA = "activa"
ESTADO_INSCR_FINALIZADA = "finalizada"
ESTADOS_INSCRIPCION = (ESTADO_INSCR_ACTIVA, ESTADO_INSCR_FINALIZADA)

# ---------------------------------------------------------------------------
# Asistencias (RF-08)
# ---------------------------------------------------------------------------
ASIST_PRESENTE = "presente"
ASIST_AUSENTE = "ausente"
ESTADOS_ASISTENCIA = (ASIST_PRESENTE, ASIST_AUSENTE)

# ---------------------------------------------------------------------------
# Espacios deportivos y material (RF-02)
# ---------------------------------------------------------------------------
ESTADO_ESPACIO_DISPONIBLE = "disponible"
ESTADO_ESPACIO_MANTENIMIENTO = "mantenimiento"
ESTADOS_ESPACIO = (
    ESTADO_ESPACIO_DISPONIBLE,
    ESTADO_ESPACIO_MANTENIMIENTO,
)

ESTADO_MATERIAL_BUENO = "bueno"
ESTADO_MATERIAL_REGULAR = "regular"
ESTADO_MATERIAL_DANADO = "dañado"
ESTADOS_MATERIAL = (ESTADO_MATERIAL_BUENO, ESTADO_MATERIAL_REGULAR, ESTADO_MATERIAL_DANADO)

# ---------------------------------------------------------------------------
# Horarios (RF-03)
# ---------------------------------------------------------------------------
DIAS_SEMANA = (
    "lunes",
    "martes",
    "miércoles",
    "jueves",
    "viernes",
    "sábado",
    "domingo",
)

# Equivalencia con datetime.weekday() (lunes = 0 ... domingo = 6)
DIA_POR_NUMERO = {i: dia for i, dia in enumerate(DIAS_SEMANA)}

# ---------------------------------------------------------------------------
# Formatos de fecha y hora
# ---------------------------------------------------------------------------
FORMATO_FECHA = "%Y-%m-%d"        # como lo guarda MySQL (DATE)
FORMATO_HORA = "%H:%M"            # lo que captura el usuario
FORMATO_HORA_BD = "%H:%M:%S"      # como lo guarda MySQL (TIME)

# ---------------------------------------------------------------------------
# Mensajes y confirmaciones (RF-01: confirmar antes de dar de baja)
# ---------------------------------------------------------------------------
CONFIRMAR_SI = ("s", "si", "sí")
CONFIRMAR_NO = ("n", "no")
MSG_CONFIRMAR_BAJA = "¿Seguro que deseas dar de baja este registro? (s/n): "
MSG_OPCION_INVALIDA = "Opción no válida, intenta de nuevo."
MSG_TRASLAPE = "El espacio ya está ocupado en esa fecha y horario."
MSG_SIN_CUPO = "La actividad ya alcanzó su cupo máximo."
MSG_EDAD_FUERA_RANGO = "La edad del miembro no está dentro del rango de la categoría del equipo."
