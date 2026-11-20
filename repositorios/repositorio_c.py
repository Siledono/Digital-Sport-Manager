"""
repositorios/repositorio_c.py
Digital Sport Manager - Club Deportivo

Consultas SQL del Módulo C:
- Espacios, Materiales, Horarios, Reservas y Asistencias (RF-02, RF-03, RF-08).
"""

from datetime import date
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import constantes as c
from db.conexion import obtener_cursor
from modelos.espacios import Espacio_Deportivo, Material, Necesita
from modelos.agenda import Horario, Reserva, Asistencia


class EspacioRepositorio:
    """Acceso a datos para la tabla ESPACIO_DEPORTIVO."""

    @staticmethod
    def guardar(espacio: Espacio_Deportivo) -> bool:
        with obtener_cursor() as cursor:
            if cursor is None:
                return False
            sql = """
                INSERT INTO ESPACIO_DEPORTIVO (codigoEspacio, nombreEspacio, tipo, capacidad, estado)
                VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (
                espacio.codigo_espacio, espacio.nombre_espacio,
                espacio.tipo, espacio.capacidad, espacio.estado
            ))
            return True

    @staticmethod
    def listar() -> list:
        with obtener_cursor() as cursor:
            if cursor is None:
                return []
            cursor.execute("SELECT * FROM ESPACIO_DEPORTIVO ORDER BY codigoEspacio")
            return cursor.fetchall()

    @staticmethod
    def cambiar_estado(codigo_espacio: str, nuevo_estado: str) -> bool:
        est = nuevo_estado.strip().lower()
        if est not in c.ESTADOS_ESPACIO:
            raise ValueError(f"Estado de espacio no válido: {est}")
        with obtener_cursor() as cursor:
            if cursor is None:
                return False
            cursor.execute(
                "UPDATE ESPACIO_DEPORTIVO SET estado = %s WHERE codigoEspacio = %s",
                (est, codigo_espacio.strip().upper())
            )
            return cursor.rowcount > 0


class MaterialRepositorio:
    """Acceso a datos para la tabla MATERIAL."""

    @staticmethod
    def guardar(material: Material) -> bool:
        with obtener_cursor() as cursor:
            if cursor is None:
                return False
            sql = """
                INSERT INTO MATERIAL (codigoMaterial, nombreMaterial, cantidadTotal, estado)
                VALUES (%s, %s, %s, %s)
            """
            cursor.execute(sql, (
                material.codigo_material, material.nombre_material,
                material.cantidad_total, material.estado
            ))
            return True

    @staticmethod
    def listar() -> list:
        with obtener_cursor() as cursor:
            if cursor is None:
                return []
            cursor.execute("SELECT * FROM MATERIAL ORDER BY codigoMaterial")
            return cursor.fetchall()


class EspacioMaterialRepositorio:
    """Acceso a datos para la tabla ESPACIO_MATERIAL (Necesita)."""

    @staticmethod
    def asignar(espacio: str, material: str, cantidad: int) -> bool:
        with obtener_cursor() as cursor:
            if cursor is None:
                return False
            sql = """
                INSERT INTO ESPACIO_MATERIAL (espacio, material, cantidadRequerida)
                VALUES (%s, %s, %s)
                ON DUPLICATE KEY UPDATE cantidadRequerida = VALUES(cantidadRequerida)
            """
            cursor.execute(sql, (espacio.strip().upper(), material.strip().upper(), cantidad))
            return True

    @staticmethod
    def listar_por_espacio(codigo_espacio: str) -> list:
        with obtener_cursor() as cursor:
            if cursor is None:
                return []
            sql = """
                SELECT em.*, m.nombreMaterial, m.cantidadTotal, m.estado
                FROM ESPACIO_MATERIAL em
                JOIN MATERIAL m ON m.codigoMaterial = em.material
                WHERE em.espacio = %s
            """
            cursor.execute(sql, (codigo_espacio.strip().upper(),))
            return cursor.fetchall()


class HorarioRepositorio:
    """Acceso a datos para la tabla HORARIO y EQUIPO_HORARIO (RF-03)."""

    @staticmethod
    def guardar(horario: Horario) -> int:
        with obtener_cursor() as cursor:
            if cursor is None:
                raise ConnectionError("No hay conexión a la base de datos.")

            # Validación de traslape con otros horarios en el mismo espacio y día
            cursor.execute(
                """
                SELECT codigoHorario, horaInicio, horaFin
                FROM HORARIO
                WHERE espacio = %s AND diaSemana = %s
                  AND %s < horaFin AND horaInicio < %s
                """,
                (horario.espacio, horario.dia_semana, horario.hora_inicio, horario.hora_fin)
            )
            if cursor.fetchone():
                raise ValueError(f"{c.MSG_TRASLAPE} (Conflicto con horario de entrenamiento)")

            sql = """
                INSERT INTO HORARIO (diaSemana, horaInicio, horaFin, actividad, espacio)
                VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (
                horario.dia_semana, horario.hora_inicio, horario.hora_fin,
                horario.actividad, horario.espacio
            ))
            return cursor.lastrowid

    @staticmethod
    def listar() -> list:
        with obtener_cursor() as cursor:
            if cursor is None:
                return []
            sql = """
                SELECT h.*, a.nombre AS actividadNombre, ed.nombreEspacio
                FROM HORARIO h
                JOIN ACTIVIDAD a ON a.codigoActividad = h.actividad
                JOIN ESPACIO_DEPORTIVO ed ON ed.codigoEspacio = h.espacio
                ORDER BY FIELD(h.diaSemana, 'lunes','martes','miércoles','jueves','viernes','sábado','domingo'), h.horaInicio
            """
            cursor.execute(sql)
            return cursor.fetchall()

    @staticmethod
    def asignar_equipo(clave_equipo: str, codigo_horario: int) -> bool:
        with obtener_cursor() as cursor:
            if cursor is None:
                return False
            cursor.execute(
                """
                INSERT IGNORE INTO EQUIPO_HORARIO (equipo, horario)
                VALUES (%s, %s)
                """,
                (clave_equipo.strip().upper(), codigo_horario)
            )
            return cursor.rowcount > 0

    @staticmethod
    def listar_por_equipo(nombre_o_clave: str) -> list:
        """Consulta 2 del entregable: horarios en los que entrena un equipo."""
        with obtener_cursor() as cursor:
            if cursor is None:
                return []
            sql = """
                SELECT e.nombreEquipo, h.codigoHorario, h.diaSemana, h.horaInicio, h.horaFin,
                       ed.nombreEspacio, a.nombre AS actividadNombre
                FROM EQUIPO e
                JOIN EQUIPO_HORARIO eh ON eh.equipo = e.claveEquipo
                JOIN HORARIO h ON h.codigoHorario = eh.horario
                JOIN ESPACIO_DEPORTIVO ed ON ed.codigoEspacio = h.espacio
                JOIN ACTIVIDAD a ON a.codigoActividad = h.actividad
                WHERE e.claveEquipo = %s OR e.nombreEquipo LIKE %s
                ORDER BY FIELD(h.diaSemana, 'lunes','martes','miércoles','jueves','viernes','sábado','domingo'), h.horaInicio
            """
            cursor.execute(sql, (nombre_o_clave, f"%{nombre_o_clave}%"))
            return cursor.fetchall()


class ReservaRepositorio:
    """Acceso a datos para la tabla RESERVA (RF-03 anti-traslapes)."""

    @staticmethod
    def crear_reserva(reserva: Reserva) -> int:
        with obtener_cursor() as cursor:
            if cursor is None:
                raise ConnectionError("No hay conexión a la base de datos.")

            # 1. Validar estado del espacio
            cursor.execute("SELECT estado FROM ESPACIO_DEPORTIVO WHERE codigoEspacio = %s", (reserva.espacio,))
            esp = cursor.fetchone()
            if not esp:
                raise ValueError("El espacio deportivo no existe.")
            if esp["estado"] != c.ESTADO_ESPACIO_DISPONIBLE:
                raise ValueError(f"El espacio no está disponible (estado actual: {esp['estado']}).")

            # 2. Validar traslape con otras reservas en la misma fecha y espacio
            cursor.execute(
                """
                SELECT numReserva FROM RESERVA
                WHERE espacio = %s AND fecha = %s
                  AND %s < horaFin AND horaInicio < %s
                """,
                (reserva.espacio, reserva.fecha, reserva.hora_inicio, reserva.hora_fin)
            )
            if cursor.fetchone():
                raise ValueError(f"{c.MSG_TRASLAPE} (Conflicto con otra reserva existente)")

            # 3. Validar traslape con horarios de entrenamiento en ese día de la semana
            dia_semana_nombre = c.DIA_POR_NUMERO[reserva.fecha.weekday()]
            cursor.execute(
                """
                SELECT codigoHorario FROM HORARIO
                WHERE espacio = %s AND diaSemana = %s
                  AND %s < horaFin AND horaInicio < %s
                """,
                (reserva.espacio, dia_semana_nombre, reserva.hora_inicio, reserva.hora_fin)
            )
            if cursor.fetchone():
                raise ValueError(f"{c.MSG_TRASLAPE} (Conflicto con horario fijo de entrenamiento del día {dia_semana_nombre})")

            sql = """
                INSERT INTO RESERVA (fecha, horaInicio, horaFin, miembro, espacio)
                VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (
                reserva.fecha, reserva.hora_inicio, reserva.hora_fin,
                reserva.miembro, reserva.espacio
            ))
            return cursor.lastrowid

    @staticmethod
    def listar_por_fecha(fecha_str: str) -> list:
        """Consulta 3 del entregable: reservas de una fecha."""
        with obtener_cursor() as cursor:
            if cursor is None:
                return []
            sql = """
                SELECT r.numReserva, r.fecha, r.horaInicio, r.horaFin,
                       r.miembro AS numeroSocio,
                       CONCAT(m.nombre, ' ', m.primerApell, IFNULL(CONCAT(' ', m.segApell), '')) AS miembro,
                       ed.nombreEspacio, ed.codigoEspacio
                FROM RESERVA r
                JOIN MIEMBRO m ON m.numeroSocio = r.miembro
                JOIN ESPACIO_DEPORTIVO ed ON ed.codigoEspacio = r.espacio
                WHERE r.fecha = %s
                ORDER BY r.horaInicio
            """
            cursor.execute(sql, (fecha_str,))
            return cursor.fetchall()

    @staticmethod
    def cancelar_por_nombre(nombre_miembro: str) -> bool:
        with obtener_cursor() as cursor:
            if cursor is None:
                return False
            sql = """
                DELETE r FROM RESERVA r
                JOIN MIEMBRO m ON m.numeroSocio = r.miembro
                WHERE m.nombre LIKE %s OR m.primerApell LIKE %s
            """
            like = f"%{nombre_miembro.strip()}%"
            cursor.execute(sql, (like, like))
            return cursor.rowcount > 0


class AsistenciaRepositorio:
    """Acceso a datos para la tabla ASISTENCIA (RF-08)."""

    @staticmethod
    def registrar(asistencia: Asistencia) -> int:
        with obtener_cursor() as cursor:
            if cursor is None:
                raise ConnectionError("No hay conexión a la base de datos.")

            sql = """
                INSERT INTO ASISTENCIA (fecha, estadoAsistencia, miembro, horario)
                VALUES (%s, %s, %s, %s)
            """
            cursor.execute(sql, (
                asistencia.fecha, asistencia.estado_asistencia,
                asistencia.miembro, asistencia.horario
            ))
            return cursor.lastrowid

    @staticmethod
    def historial_miembro(numero_socio: int) -> list:
        with obtener_cursor() as cursor:
            if cursor is None:
                return []
            sql = """
                SELECT a.folioAsistencia, a.fecha, a.estadoAsistencia,
                       h.diaSemana, h.horaInicio, h.horaFin,
                       act.nombre AS actividadNombre, ed.nombreEspacio
                FROM ASISTENCIA a
                JOIN HORARIO h ON h.codigoHorario = a.horario
                JOIN ACTIVIDAD act ON act.codigoActividad = h.actividad
                JOIN ESPACIO_DEPORTIVO ed ON ed.codigoEspacio = h.espacio
                WHERE a.miembro = %s
                ORDER BY a.fecha DESC
            """
            cursor.execute(sql, (numero_socio,))
            return cursor.fetchall()
