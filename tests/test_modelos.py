"""
tests/test_modelos.py
Pruebas unitarias de las clases del modelo de datos y reglas de negocio.
"""

import unittest
from datetime import date, time, timedelta
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import constantes as c
from modelos.personas import Miembro, Entrenador, calcular_edad
from modelos.organizacion import Categoria, Equipo
from modelos.membresias import Tipo_Membresia, Membresia, Pago
from modelos.actividades import Actividad, Inscripcion
from modelos.espacios import Espacio_Deportivo, Material, Necesita
from modelos.agenda import Horario, Reserva, Asistencia


class TestReglasDeNegocio(unittest.TestCase):

    def test_calculo_edad(self):
        # Nacido hace 15 años exactos
        hoy = date(2026, 11, 19)
        fnac = date(2011, 11, 19)
        self.assertEqual(calcular_edad(fnac, hoy), 15)

        # Nacido mañana cumple años, hoy tiene 14
        fnac_manana = date(2011, 11, 20)
        self.assertEqual(calcular_edad(fnac_manana, hoy), 14)

    def test_categoria_edad_valida(self):
        cat_infantil = Categoria("INFAN", "Infantil", 7, 12)
        self.assertTrue(cat_infantil.esEdadValida(7))
        self.assertTrue(cat_infantil.esEdadValida(10))
        self.assertTrue(cat_infantil.esEdadValida(12))
        self.assertFalse(cat_infantil.esEdadValida(6))
        self.assertFalse(cat_infantil.esEdadValida(13))

    def test_estados_membresia(self):
        hoy = date(2026, 11, 19)
        tipo = Tipo_Membresia("TP-MS", "Mensual", 1200.0, 30)

        # Vigente (faltan más de 7 días, ej. vence en 15 días)
        m_vigente = Membresia(fecha_inicio=hoy, fecha_fin=hoy + timedelta(days=15), tipo_membresia="TP-MS", miembro=1)
        self.assertEqual(m_vigente.calcularEstado(hoy), c.ESTADO_MEMB_VIGENTE)

        # Por vencer (faltan 5 días)
        m_por_vencer = Membresia(fecha_inicio=hoy - timedelta(days=25), fecha_fin=hoy + timedelta(days=5), tipo_membresia="TP-MS", miembro=1)
        self.assertEqual(m_por_vencer.calcularEstado(hoy), c.ESTADO_MEMB_POR_VENCER)

        # Vencida (venció ayer)
        m_vencida = Membresia(fecha_inicio=hoy - timedelta(days=40), fecha_fin=hoy - timedelta(days=1), tipo_membresia="TP-MS", miembro=1)
        self.assertEqual(m_vencida.calcularEstado(hoy), c.ESTADO_MEMB_VENCIDA)

    def test_traslape_horario(self):
        h1 = Horario("lunes", time(16, 0), time(18, 0), "FUTBO", "CAN01")

        # Mismo día, traslape parcial (17:00 a 19:00)
        self.assertTrue(h1.hayTraslape("lunes", time(17, 0), time(19, 0)))

        # Mismo día, sin traslape (18:00 a 20:00)
        self.assertFalse(h1.hayTraslape("lunes", time(18, 0), time(20, 0)))

        # Distinto día
        self.assertFalse(h1.hayTraslape("martes", time(16, 30), time(17, 30)))

    def test_stock_material(self):
        balones = Material("BALFU", "Balón de fútbol", 10, "bueno")
        self.assertTrue(balones.hayStock(5))
        self.assertTrue(balones.hayStock(10))
        self.assertFalse(balones.hayStock(11))

        balones.retirar(4)
        self.assertEqual(balones.cantidad_total, 6)
        with self.assertRaises(ValueError):
            balones.retirar(7)

    def test_comprobante_pago(self):
        pago = Pago(date(2026, 11, 1), 1200.0, "efectivo", 1, folio_pago=101)
        self.assertIn("COMPROBANTE", pago.generarComprobante())
        self.assertIn("1200.00", pago.generarComprobante())


if __name__ == "__main__":
    unittest.main()
