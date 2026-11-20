"""
modelos/membresias.py
Digital Sport Manager - Club Deportivo

Clases: Tipo_Membresia, Membresia, Pago.
RF-04: Control de membresías y pagos.
RF-06: Notificación preventiva de membresías por vencer (umbral 7 días).
"""

from datetime import date, datetime, timedelta
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import constantes as c


class Tipo_Membresia:
    """Catálogo de tipos de membresía (duración en días y costo)."""

    def __init__(self, clave_tipo_membresia: str, nombre_tipo: str, costo: float, duracion_dias: int):
        self.clave_tipo_membresia = (clave_tipo_membresia or "").strip().upper()
        self.nombre_tipo = (nombre_tipo or "").strip()
        self.costo = float(costo)
        self.duracion_dias = int(duracion_dias)

        if self.costo <= 0:
            raise ValueError("El costo debe ser mayor a 0.")
        if self.duracion_dias <= 0:
            raise ValueError("La duración en días debe ser mayor a 0.")

    def calcularFin(self, inicio: date) -> date:
        return inicio + timedelta(days=self.duracion_dias)

    def __str__(self):
        return f"[{self.clave_tipo_membresia}] {self.nombre_tipo} (${self.costo:.2f}, {self.duracion_dias} días)"

    @classmethod
    def desde_dict(cls, d: dict):
        return cls(
            clave_tipo_membresia=d["claveTipoMembresia"],
            nombre_tipo=d["nombreTipo"],
            costo=float(d["costo"]),
            duracion_dias=int(d["duracionDias"])
        )


class Membresia:
    """Membresía adquirida por un miembro."""

    def __init__(self, fecha_inicio, tipo_membresia: str, miembro: int,
                 fecha_fin=None, estado: str = None, folio_membresia: int = None,
                 duracion_dias: int = None):
        self.folio_membresia = int(folio_membresia) if folio_membresia is not None else None
        self.tipo_membresia = (tipo_membresia or "").strip().upper()
        self.miembro = int(miembro)

        if isinstance(fecha_inicio, (date, datetime)):
            self.fecha_inicio = fecha_inicio if isinstance(fecha_inicio, date) else fecha_inicio.date()
        else:
            self.fecha_inicio = datetime.strptime(str(fecha_inicio).strip(), c.FORMATO_FECHA).date()

        if fecha_fin:
            if isinstance(fecha_fin, (date, datetime)):
                self.fecha_fin = fecha_fin if isinstance(fecha_fin, date) else fecha_fin.date()
            else:
                self.fecha_fin = datetime.strptime(str(fecha_fin).strip(), c.FORMATO_FECHA).date()
        elif duracion_dias:
            self.fecha_fin = self.fecha_inicio + timedelta(days=int(duracion_dias))
        else:
            self.fecha_fin = self.fecha_inicio + timedelta(days=30)

        self._estado = estado.strip().lower() if estado else self.calcularEstado()

    @property
    def estado(self) -> str:
        return self.calcularEstado()

    def calcularEstado(self, hoy: date = None) -> str:
        """
        Regla de negocio RF-04 / RF-06:
        - Si hoy > fecha_fin: 'vencida'
        - Si 0 <= (fecha_fin - hoy).days <= 7: 'por vencer'
        - Si (fecha_fin - hoy).days > 7: 'vigente'
        """
        hoy = hoy or date.today()
        dias_restantes = (self.fecha_fin - hoy).days
        if dias_restantes < 0:
            return c.ESTADO_MEMB_VENCIDA
        elif dias_restantes <= c.DIAS_POR_VENCER:
            return c.ESTADO_MEMB_POR_VENCER
        return c.ESTADO_MEMB_VIGENTE

    def renovar(self, duracion_dias: int, hoy: date = None):
        """Renueva la membresía extendiendo la vigencia."""
        hoy = hoy or date.today()
        if self.calcularEstado(hoy) == c.ESTADO_MEMB_VIGENTE:
            self.fecha_fin += timedelta(days=duracion_dias)
        else:
            self.fecha_inicio = hoy
            self.fecha_fin = hoy + timedelta(days=duracion_dias)

    def __str__(self):
        return (f"Membresía #{self.folio_membresia or 'Nueva'} | Socio #{self.miembro} | "
                f"Tipo: {self.tipo_membresia} | Vigencia: {self.fecha_inicio} al {self.fecha_fin} | "
                f"Estado: {self.estado.upper()}")

    @classmethod
    def desde_dict(cls, d: dict):
        return cls(
            folio_membresia=d.get("folioMembresia"),
            fecha_inicio=d["fechaInicio"],
            fecha_fin=d["fechaFin"],
            estado=d.get("estado"),
            tipo_membresia=d["tipoMembresia"],
            miembro=d["miembro"]
        )


class Pago:
    """Comprobante y registro de pago de una membresía."""

    def __init__(self, fecha_pago, monto: float, metodo_pago: str, membresia: int,
                 estado_pago: str = c.ESTADO_PAGO_PAGADO, folio_pago: int = None):
        self.folio_pago = int(folio_pago) if folio_pago is not None else None

        if isinstance(fecha_pago, (date, datetime)):
            self.fecha_pago = fecha_pago if isinstance(fecha_pago, date) else fecha_pago.date()
        else:
            self.fecha_pago = datetime.strptime(str(fecha_pago).strip(), c.FORMATO_FECHA).date()

        self.monto = float(monto)
        self.metodo_pago = (metodo_pago or "").strip().lower()
        self.estado_pago = (estado_pago or c.ESTADO_PAGO_PAGADO).strip().lower()
        self.membresia = int(membresia)

        if self.monto <= 0:
            raise ValueError("El monto del pago debe ser mayor que cero.")
        if self.metodo_pago not in c.METODOS_PAGO:
            raise ValueError(f"Método de pago inválido: '{self.metodo_pago}'. Válidos: {c.METODOS_PAGO}")
        if self.estado_pago not in c.ESTADOS_PAGO:
            raise ValueError(f"Estado de pago inválido: '{self.estado_pago}'. Válidos: {c.ESTADOS_PAGO}")

    def procesarPago(self):
        self.estado_pago = c.ESTADO_PAGO_PAGADO
        return True

    def generarComprobante(self) -> str:
        return (f"========================================\n"
                f"          COMPROBANTE DE PAGO           \n"
                f"========================================\n"
                f"Folio de pago : #{self.folio_pago or 'S/F'}\n"
                f"Membresía     : #{self.membresia}\n"
                f"Fecha         : {self.fecha_pago}\n"
                f"Monto         : ${self.monto:.2f} MXN\n"
                f"Método        : {self.metodo_pago.capitalize()}\n"
                f"Estado        : {self.estado_pago.upper()}\n"
                f"========================================")

    @classmethod
    def desde_dict(cls, d: dict):
        return cls(
            folio_pago=d.get("folioPago"),
            fecha_pago=d["fechaPago"],
            monto=float(d["monto"]),
            metodo_pago=d["metodoPago"],
            estado_pago=d.get("estadoPago", c.ESTADO_PAGO_PAGADO),
            membresia=d["membresia"]
        )
