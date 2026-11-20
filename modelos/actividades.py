"""
modelos/actividades.py
Digital Sport Manager - Club Deportivo

Clases: Actividad, Inscripcion.
RF-07: Inscripción a actividades respetando cupo máximo.
      Solo una inscripción activa por alumno; al cambiar, la anterior pasa a 'finalizada'.
"""

from datetime import date, datetime
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import constantes as c


class Actividad:
    """Actividad deportiva (Fútbol, Basquetbol, Voleibol)."""

    def __init__(self, codigo_actividad: str, nombre: str, descripcion: str, cupo_maximo: int):
        self.codigo_actividad = (codigo_actividad or "").strip().upper()
        self.nombre = (nombre or "").strip()
        self.descripcion = (descripcion or "").strip()
        self.cupo_maximo = int(cupo_maximo)

        if self.cupo_maximo <= 0:
            raise ValueError("El cupo máximo debe ser mayor a 0.")

    def __str__(self):
        return f"[{self.codigo_actividad}] {self.nombre} (Cupo máx: {self.cupo_maximo})"

    @classmethod
    def desde_dict(cls, d: dict):
        return cls(
            codigo_actividad=d["codigoActividad"],
            nombre=d["nombre"],
            descripcion=d["descripcion"],
            cupo_maximo=int(d["cupoMaximo"])
        )


class Inscripcion:
    """Inscripción de un miembro a una actividad."""

    def __init__(self, miembro: int, actividad: str, fecha_inscripcion=None,
                 fecha_baja=None, estado: str = c.ESTADO_INSCR_ACTIVA, folio_inscripcion: int = None):
        self.folio_inscripcion = int(folio_inscripcion) if folio_inscripcion is not None else None
        self.miembro = int(miembro)
        self.actividad = (actividad or "").strip().upper()

        if fecha_inscripcion:
            if isinstance(fecha_inscripcion, (date, datetime)):
                self.fecha_inscripcion = fecha_inscripcion if isinstance(fecha_inscripcion, date) else fecha_inscripcion.date()
            else:
                self.fecha_inscripcion = datetime.strptime(str(fecha_inscripcion).strip(), c.FORMATO_FECHA).date()
        else:
            self.fecha_inscripcion = date.today()

        if fecha_baja:
            if isinstance(fecha_baja, (date, datetime)):
                self.fecha_baja = fecha_baja if isinstance(fecha_baja, date) else fecha_baja.date()
            else:
                self.fecha_baja = datetime.strptime(str(fecha_baja).strip(), c.FORMATO_FECHA).date()
        else:
            self.fecha_baja = None

        self.estado = (estado or c.ESTADO_INSCR_ACTIVA).strip().lower()
        if self.estado not in c.ESTADOS_INSCRIPCION:
            raise ValueError(f"Estado de inscripción inválido: '{self.estado}'. Válidos: {c.ESTADOS_INSCRIPCION}")

    def darDeBaja(self, fecha: date = None):
        self.estado = c.ESTADO_INSCR_FINALIZADA
        self.fecha_baja = fecha or date.today()

    def __str__(self):
        baja_str = f" | Baja: {self.fecha_baja}" if self.fecha_baja else ""
        return (f"Inscripción #{self.folio_inscripcion or 'Nueva'} | Socio #{self.miembro} | "
                f"Actividad: {self.actividad} | Fecha: {self.fecha_inscripcion} | "
                f"Estado: {self.estado.upper()}{baja_str}")

    @classmethod
    def desde_dict(cls, d: dict):
        return cls(
            folio_inscripcion=d.get("folioInscripcion"),
            miembro=d["miembro"],
            actividad=d["actividad"],
            fecha_inscripcion=d["fechaInscripcion"],
            fecha_baja=d.get("fechaBaja"),
            estado=d.get("estado", c.ESTADO_INSCR_ACTIVA)
        )
