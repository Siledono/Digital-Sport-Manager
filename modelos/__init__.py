"""
modelos/__init__.py
Exportación unificada de todas las clases del modelo de datos de Digital Sport Manager.
"""

from .personas import Persona, Miembro, Entrenador, calcular_edad
from .organizacion import Categoria, Equipo
from .membresias import Tipo_Membresia, Membresia, Pago
from .actividades import Actividad, Inscripcion
from .espacios import Espacio_Deportivo, Material, Necesita
from .agenda import Horario, Reserva, Asistencia

__all__ = [
    "Persona", "Miembro", "Entrenador", "calcular_edad",
    "Categoria", "Equipo",
    "Tipo_Membresia", "Membresia", "Pago",
    "Actividad", "Inscripcion",
    "Espacio_Deportivo", "Material", "Necesita",
    "Horario", "Reserva", "Asistencia",
]
