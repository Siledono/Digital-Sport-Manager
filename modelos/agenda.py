"""
modelos/agenda.py
Digital Sport Manager - Club Deportivo

Clases: Horario, Reserva, Asistencia.
RF-03: Control de traslapes y horarios en espacios deportivos.
RF-08: Control y registro de asistencias a entrenamientos.
"""

from datetime import date, datetime, time
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import constantes as c


def parsear_hora(valor) -> time:
    if isinstance(valor, time):
        return valor
    cadena = str(valor).strip()
    for fmt in (c.FORMATO_HORA, c.FORMATO_HORA_BD):
        try:
            return datetime.strptime(cadena, fmt).time()
        except ValueError:
            pass
    raise ValueError(f"Hora no válida: '{valor}'. Usa formato HH:MM o HH:MM:SS.")


class Horario:
    """Horario semanal de entrenamiento programado para una actividad y espacio."""

    def __init__(self, dia_semana: str, hora_inicio, hora_fin,
                 actividad: str, espacio: str, codigo_horario: int = None):
        self.codigo_horario = int(codigo_horario) if codigo_horario is not None else None
        self.dia_semana = (dia_semana or "").strip().lower()

        if self.dia_semana not in c.DIAS_SEMANA:
            raise ValueError(f"Día no válido: '{self.dia_semana}'. Válidos: {c.DIAS_SEMANA}")

        self.hora_inicio = parsear_hora(hora_inicio)
        self.hora_fin = parsear_hora(hora_fin)

        if self.hora_inicio >= self.hora_fin:
            raise ValueError("La hora de inicio debe ser anterior a la hora final.")

        self.actividad = (actividad or "").strip().upper()
        self.espacio = (espacio or "").strip().upper()

    def hayTraslape(self, otro_dia: str, otra_inicio: time, otra_fin: time) -> bool:
        if self.dia_semana != (otro_dia or "").strip().lower():
            return False
        return self.hora_inicio < otra_fin and otra_inicio < self.hora_fin

    def __str__(self):
        return (f"Horario #{self.codigo_horario or 'Nuevo'} | {self.dia_semana.capitalize()} "
                f"{self.hora_inicio.strftime('%H:%M')}-{self.hora_fin.strftime('%H:%M')} | "
                f"Actividad: {self.actividad} | Espacio: {self.espacio}")

    @classmethod
    def desde_dict(cls, d: dict):
        return cls(
            codigo_horario=d.get("codigoHorario"),
            dia_semana=d["diaSemana"],
            hora_inicio=str(d["horaInicio"]),
            hora_fin=str(d["horaFin"]),
            actividad=d["actividad"],
            espacio=d["espacio"]
        )


class Reserva:
    """Reserva de un espacio deportivo realizada por un miembro."""

    def __init__(self, fecha, hora_inicio, hora_fin, miembro: int,
                 espacio: str, num_reserva: int = None):
        self.num_reserva = int(num_reserva) if num_reserva is not None else None

        if isinstance(fecha, (date, datetime)):
            self.fecha = fecha if isinstance(fecha, date) else fecha.date()
        else:
            self.fecha = datetime.strptime(str(fecha).strip(), c.FORMATO_FECHA).date()

        self.hora_inicio = parsear_hora(hora_inicio)
        self.hora_fin = parsear_hora(hora_fin)

        if self.hora_inicio >= self.hora_fin:
            raise ValueError("La hora de inicio debe ser anterior a la hora de fin.")

        self.miembro = int(miembro)
        self.espacio = (espacio or "").strip().upper()

    def __str__(self):
        return (f"Reserva #{self.num_reserva or 'Nueva'} | Fecha: {self.fecha} | "
                f"{self.hora_inicio.strftime('%H:%M')}-{self.hora_fin.strftime('%H:%M')} | "
                f"Socio: #{self.miembro} | Espacio: {self.espacio}")

    @classmethod
    def desde_dict(cls, d: dict):
        return cls(
            num_reserva=d.get("numReserva"),
            fecha=d["fecha"],
            hora_inicio=str(d["horaInicio"]),
            hora_fin=str(d["horaFin"]),
            miembro=d["miembro"],
            espacio=d["espacio"]
        )


class Asistencia:
    """Registro de asistencia de un miembro a un horario de entrenamiento."""

    def __init__(self, miembro: int, horario: int,
                 estado_asistencia: str = c.ASIST_PRESENTE,
                 fecha=None, folio_asistencia: int = None):
        self.folio_asistencia = int(folio_asistencia) if folio_asistencia is not None else None
        self.miembro = int(miembro)
        self.horario = int(horario)

        if fecha:
            if isinstance(fecha, (date, datetime)):
                self.fecha = fecha if isinstance(fecha, date) else fecha.date()
            else:
                self.fecha = datetime.strptime(str(fecha).strip(), c.FORMATO_FECHA).date()
        else:
            self.fecha = date.today()

        self.estado_asistencia = (estado_asistencia or c.ASIST_PRESENTE).strip().lower()
        if self.estado_asistencia not in c.ESTADOS_ASISTENCIA:
            raise ValueError(f"Estado de asistencia inválido: '{self.estado_asistencia}'. Válidos: {c.ESTADOS_ASISTENCIA}")

    def __str__(self):
        return (f"Asistencia #{self.folio_asistencia or 'Nueva'} | Fecha: {self.fecha} | "
                f"Socio #{self.miembro} | Horario #{self.horario} | Estado: {self.estado_asistencia.upper()}")

    @classmethod
    def desde_dict(cls, d: dict):
        return cls(
            folio_asistencia=d.get("folioAsistencia"),
            fecha=d["fecha"],
            estado_asistencia=d["estadoAsistencia"],
            miembro=d["miembro"],
            horario=d["horario"]
        )
