"""
repositorios/__init__.py
Exportación de los repositorios de datos de Digital Sport Manager.
"""

from .repositorio_a import MiembroRepositorio, EntrenadorRepositorio, CategoriaRepositorio, EquipoRepositorio
from .repositorio_b import TipoMembresiaRepositorio, MembresiaRepositorio, PagoRepositorio, ActividadRepositorio, InscripcionRepositorio
from .repositorio_c import EspacioRepositorio, MaterialRepositorio, EspacioMaterialRepositorio, HorarioRepositorio, ReservaRepositorio, AsistenciaRepositorio

__all__ = [
    "MiembroRepositorio", "EntrenadorRepositorio", "CategoriaRepositorio", "EquipoRepositorio",
    "TipoMembresiaRepositorio", "MembresiaRepositorio", "PagoRepositorio", "ActividadRepositorio", "InscripcionRepositorio",
    "EspacioRepositorio", "MaterialRepositorio", "EspacioMaterialRepositorio", "HorarioRepositorio", "ReservaRepositorio", "AsistenciaRepositorio",
]
