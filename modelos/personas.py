"""
modelos/personas.py
Digital Sport Manager - Club Deportivo

Clases: Persona (abstracta), Miembro, Entrenador.
RF-01: Control de alumnos y entrenadores, baja lógica con confirmación.
"""

from abc import ABC, abstractmethod
from datetime import date, datetime
import re
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import constantes as c


def calcular_edad(fecha_nacimiento: date, hoy: date = None) -> int:
    """Calcula la edad cumplida en años."""
    hoy = hoy or date.today()
    return hoy.year - fecha_nacimiento.year - (
        (hoy.month, hoy.day) < (fecha_nacimiento.month, fecha_nacimiento.day)
    )


class Persona(ABC):
    """Clase abstracta base para Miembro y Entrenador."""

    def __init__(self, nombre: str, primer_apell: str, seg_apell: str = None,
                 telefono: str = "", correo: str = "", estatus: str = c.ESTATUS_ACTIVO):
        self.nombre = (nombre or "").strip()
        self.primer_apell = (primer_apell or "").strip()
        self.seg_apell = (seg_apell or "").strip() if seg_apell else None
        self.telefono = re.sub(r"[\s\-()]", "", (telefono or "").strip())
        self.correo = (correo or "").strip().lower()
        self.estatus = (estatus or c.ESTATUS_ACTIVO).strip().lower()

        if self.estatus not in c.ESTATUS_VALIDOS:
            raise ValueError(f"Estatus inválido: '{self.estatus}'. Valores válidos: {c.ESTATUS_VALIDOS}")

    def obtenerNombreCompleto(self) -> str:
        partes = [self.nombre, self.primer_apell, self.seg_apell]
        return " ".join(p for p in partes if p)

    @abstractmethod
    def mostrarInformacion(self) -> str:
        pass


class Miembro(Persona):
    """Representa a un socio/alumno del club."""

    def __init__(self, nombre: str, primer_apell: str, seg_apell: str = None,
                 telefono: str = "", correo: str = "", fecha_nacimiento: str = "",
                 equipo: str = "", estatus: str = c.ESTATUS_ACTIVO,
                 numero_socio: int = None, fecha_registro: str = None, edad: int = None):
        super().__init__(nombre, primer_apell, seg_apell, telefono, correo, estatus)
        self.numero_socio = int(numero_socio) if numero_socio is not None else None

        if isinstance(fecha_nacimiento, (date, datetime)):
            self.fecha_nacimiento = fecha_nacimiento if isinstance(fecha_nacimiento, date) else fecha_nacimiento.date()
        else:
            self.fecha_nacimiento = datetime.strptime(str(fecha_nacimiento).strip(), c.FORMATO_FECHA).date()

        if fecha_registro:
            if isinstance(fecha_registro, (date, datetime)):
                self.fecha_registro = fecha_registro if isinstance(fecha_registro, date) else fecha_registro.date()
            else:
                self.fecha_registro = datetime.strptime(str(fecha_registro).strip(), c.FORMATO_FECHA).date()
        else:
            self.fecha_registro = date.today()

        self.equipo = (equipo or "").strip().upper()
        self._edad_almacenada = edad

    @property
    def edad(self) -> int:
        return calcular_edad(self.fecha_nacimiento)

    def calcularEdad(self) -> int:
        return self.edad

    def mostrarInformacion(self) -> str:
        return (f"Miembro #{self.numero_socio or 'Nuevo'}: {self.obtenerNombreCompleto()}\n"
                f"Edad: {self.edad} años\n"
                f"Teléfono: {self.telefono}\n"
                f"Correo: {self.correo}\n"
                f"Equipo: {self.equipo}\n"
                f"Estatus: {self.estatus.capitalize()}")

    @classmethod
    def desde_dict(cls, d: dict):
        return cls(
            nombre=d["nombre"],
            primer_apell=d["primerApell"],
            seg_apell=d.get("segApell"),
            telefono=d["telefono"],
            correo=d["correo"],
            fecha_nacimiento=d["fechaNacimiento"],
            equipo=d["equipo"],
            estatus=d.get("estatus", c.ESTATUS_ACTIVO),
            numero_socio=d.get("numeroSocio"),
            fecha_registro=d.get("fechaRegistro"),
            edad=d.get("edad")
        )


class Entrenador(Persona):
    """Representa a un entrenador o preparador físico."""

    def __init__(self, nombre: str, primer_apell: str, seg_apell: str = None,
                 telefono: str = "", correo: str = "", especialidad: str = "",
                 estatus: str = c.ESTATUS_ACTIVO, clave_entrenador: int = None):
        super().__init__(nombre, primer_apell, seg_apell, telefono, correo, estatus)
        self.clave_entrenador = int(clave_entrenador) if clave_entrenador is not None else None
        self.especialidad = (especialidad or "").strip()

    def mostrarInformacion(self) -> str:
        return (f"Entrenador #{self.clave_entrenador or 'Nuevo'}: {self.obtenerNombreCompleto()}\n"
                f"Especialidad: {self.especialidad}\n"
                f"Teléfono: {self.telefono}\n"
                f"Correo: {self.correo}\n"
                f"Estatus: {self.estatus.capitalize()}")

    @classmethod
    def desde_dict(cls, d: dict):
        return cls(
            nombre=d["nombre"],
            primer_apell=d["primerApell"],
            seg_apell=d.get("segApell"),
            telefono=d["telefono"],
            correo=d["correo"],
            especialidad=d["especialidad"],
            estatus=d.get("estatus", c.ESTATUS_ACTIVO),
            clave_entrenador=d.get("claveEntrenador")
        )
