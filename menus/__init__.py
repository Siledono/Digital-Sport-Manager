"""
menus/__init__.py
Exportación de los menús de consola para cada módulo.
"""

from .menu_a import menu_modulo_a
from .menu_b import menu_modulo_b
from .menu_c import menu_modulo_c

__all__ = ["menu_modulo_a", "menu_modulo_b", "menu_modulo_c"]
