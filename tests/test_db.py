"""
tests/test_db.py
Pruebas de integración con la base de datos MySQL (digitalsportmanager).
"""

import unittest
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import constantes as c
from db.conexion import obtener_cursor, probar_conexion
from repositorios.repositorio_a import MiembroRepositorio, EquipoRepositorio
from repositorios.repositorio_b import MembresiaRepositorio, InscripcionRepositorio
from repositorios.repositorio_c import EspacioRepositorio, ReservaRepositorio


class TestBaseDeDatos(unittest.TestCase):

    def test_01_conexion(self):
        self.assertTrue(probar_conexion(), "No se pudo conectar a la base de datos.")

    def test_02_conteo_tablas(self):
        with obtener_cursor() as cursor:
            self.assertIsNotNone(cursor)
            cursor.execute("SHOW TABLES;")
            tablas = cursor.fetchall()
            self.assertEqual(len(tablas), 16, "Debe haber exactamente 16 tablas en la base de datos.")

    def test_03_datos_sembrados(self):
        with obtener_cursor() as cursor:
            cursor.execute("SELECT COUNT(*) AS total FROM CATEGORIA")
            self.assertGreater(cursor.fetchone()["total"], 0)

            cursor.execute("SELECT COUNT(*) AS total FROM MIEMBRO")
            self.assertGreater(cursor.fetchone()["total"], 0)

            cursor.execute("SELECT COUNT(*) AS total FROM EQUIPO")
            self.assertGreater(cursor.fetchone()["total"], 0)

            cursor.execute("SELECT COUNT(*) AS total FROM MEMBRESIA")
            self.assertGreater(cursor.fetchone()["total"], 0)

    def test_04_consulta_miembros_equipo(self):
        # Consulta 1: Miembros de Halcones
        miembros = EquipoRepositorio.miembros_de("Halcones")
        self.assertIsInstance(miembros, list)
        self.assertGreater(len(miembros), 0)

    def test_05_consulta_reservas(self):
        # Consulta 3: Reservas existentes
        reservas = ReservaRepositorio.listar_por_fecha("2026-11-14")
        self.assertIsInstance(reservas, list)


if __name__ == "__main__":
    unittest.main()
