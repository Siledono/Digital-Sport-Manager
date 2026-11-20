"""
modelos/organizacion.py
Digital Sport Manager - Club Deportivo

Clases: Categoria, Equipo.
RF-05: Asignación de miembros a equipos según rango de edad de la categoría.
"""

import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import constantes as c


class Categoria:
    """Categoría deportiva clasificada por rango de edades."""

    def __init__(self, clave_categoria: str, nombre_categoria: str, edad_minima: int, edad_maxima: int):
        self.clave_categoria = (clave_categoria or "").strip().upper()
        self.nombre_categoria = (nombre_categoria or "").strip()
        self.edad_minima = int(edad_minima)
        self.edad_maxima = int(edad_maxima)

        if self.edad_maxima < self.edad_minima:
            raise ValueError("La edad máxima no puede ser menor a la edad mínima.")

    def esEdadValida(self, edad: int) -> bool:
        """Verifica si una edad cae dentro del rango de la categoría."""
        return self.edad_minima <= edad <= self.edad_maxima

    def __str__(self):
        return f"{self.nombre_categoria} ({self.edad_minima}-{self.edad_maxima} años)"

    @classmethod
    def desde_dict(cls, d: dict):
        return cls(
            clave_categoria=d["claveCategoria"],
            nombre_categoria=d["nombreCategoria"],
            edad_minima=d["edadMinima"],
            edad_maxima=d["edadMaxima"]
        )


class Equipo:
    """Equipo deportivo vinculado a una categoría y a un entrenador."""

    def __init__(self, clave_equipo: str, nombre_equipo: str, categoria: str, entrenador: int):
        self.clave_equipo = (clave_equipo or "").strip().upper()
        self.nombre_equipo = (nombre_equipo or "").strip()
        self.categoria = (categoria or "").strip().upper()
        self.entrenador = int(entrenador)

    def __str__(self):
        return f"[{self.clave_equipo}] {self.nombre_equipo} (Cat: {self.categoria})"

    @classmethod
    def desde_dict(cls, d: dict):
        return cls(
            clave_equipo=d["claveEquipo"],
            nombre_equipo=d["nombreEquipo"],
            categoria=d["categoria"],
            entrenador=d["entrenador"]
        )
