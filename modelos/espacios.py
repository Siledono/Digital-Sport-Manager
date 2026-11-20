"""
modelos/espacios.py
Digital Sport Manager - Club Deportivo

Clases: Espacio_Deportivo, Material, Necesita.
RF-02: Gestión de espacios deportivos y verificación de material requerido.
"""

import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import constantes as c


class Espacio_Deportivo:
    """Instalación deportiva (cancha de fútbol, duela, voleibol, etc.)."""

    def __init__(self, codigo_espacio: str, nombre_espacio: str, tipo: str,
                 capacidad: int, estado: str = c.ESTADO_ESPACIO_DISPONIBLE):
        self.codigo_espacio = (codigo_espacio or "").strip().upper()
        self.nombre_espacio = (nombre_espacio or "").strip()
        self.tipo = (tipo or "").strip()
        self.capacidad = int(capacidad)
        self.estado = (estado or c.ESTADO_ESPACIO_DISPONIBLE).strip().lower()

        if self.capacidad <= 0:
            raise ValueError("La capacidad debe ser mayor a 0.")
        if self.estado not in c.ESTADOS_ESPACIO:
            raise ValueError(f"Estado de espacio inválido: '{self.estado}'. Válidos: {c.ESTADOS_ESPACIO}")

    def __str__(self):
        return f"[{self.codigo_espacio}] {self.nombre_espacio} ({self.tipo}, Cap: {self.capacidad}) - {self.estado.upper()}"

    @classmethod
    def desde_dict(cls, d: dict):
        return cls(
            codigo_espacio=d["codigoEspacio"],
            nombre_espacio=d["nombreEspacio"],
            tipo=d["tipo"],
            capacidad=int(d["capacidad"]),
            estado=d.get("estado", c.ESTADO_ESPACIO_DISPONIBLE)
        )


class Material:
    """Material o equipo deportivo utilizado en las actividades."""

    def __init__(self, codigo_material: str, nombre_material: str,
                 cantidad_total: int, estado: str = c.ESTADO_MATERIAL_BUENO):
        self.codigo_material = (codigo_material or "").strip().upper()
        self.nombre_material = (nombre_material or "").strip()
        self.cantidad_total = int(cantidad_total)
        self.estado = (estado or c.ESTADO_MATERIAL_BUENO).strip().lower()

        if self.cantidad_total < 0:
            raise ValueError("La cantidad total no puede ser negativa.")
        if self.estado not in c.ESTADOS_MATERIAL:
            raise ValueError(f"Estado de material inválido: '{self.estado}'. Válidos: {c.ESTADOS_MATERIAL}")

    def hayStock(self, cantidad: int) -> bool:
        return cantidad > 0 and self.cantidad_total >= cantidad

    def retirar(self, cantidad: int):
        if not self.hayStock(cantidad):
            raise ValueError("No hay material suficiente en stock.")
        self.cantidad_total -= cantidad

    def __str__(self):
        return f"[{self.codigo_material}] {self.nombre_material} (Stock: {self.cantidad_total}, Estado: {self.estado})"

    @classmethod
    def desde_dict(cls, d: dict):
        return cls(
            codigo_material=d["codigoMaterial"],
            nombre_material=d["nombreMaterial"],
            cantidad_total=int(d["cantidadTotal"]),
            estado=d.get("estado", c.ESTADO_MATERIAL_BUENO)
        )


class Necesita:
    """Relación M:M entre Espacio Deportivo y Material (ESPACIO_MATERIAL)."""

    def __init__(self, espacio: str, material: str, cantidad_requerida: int):
        self.espacio = (espacio or "").strip().upper()
        self.material = (material or "").strip().upper()
        self.cantidad_requerida = int(cantidad_requerida)

        if self.cantidad_requerida <= 0:
            raise ValueError("La cantidad requerida debe ser mayor a 0.")

    def __str__(self):
        return f"Espacio {self.espacio} requiere {self.cantidad_requerida} de {self.material}"

    @classmethod
    def desde_dict(cls, d: dict):
        return cls(
            espacio=d["espacio"],
            material=d["material"],
            cantidad_requerida=int(d["cantidadRequerida"])
        )
