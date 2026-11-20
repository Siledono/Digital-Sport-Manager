"""
repositorios/repositorio_b.py
Digital Sport Manager - Club Deportivo

Consultas SQL del Módulo B:
- Membresías, Pagos, Actividades e Inscripciones (RF-04, RF-06, RF-07).
"""

from datetime import date, timedelta
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import constantes as c
from db.conexion import obtener_cursor
from modelos.membresias import Tipo_Membresia, Membresia, Pago
from modelos.actividades import Actividad, Inscripcion


class TipoMembresiaRepositorio:
    """Acceso a datos para la tabla TIPO_MEMBRESIA."""

    @staticmethod
    def listar() -> list:
        with obtener_cursor() as cursor:
            if cursor is None:
                return []
            cursor.execute("SELECT * FROM TIPO_MEMBRESIA ORDER BY costo")
            return cursor.fetchall()

    @staticmethod
    def obtener(clave: str) -> dict:
        with obtener_cursor() as cursor:
            if cursor is None:
                return None
            cursor.execute("SELECT * FROM TIPO_MEMBRESIA WHERE claveTipoMembresia = %s", (clave.strip().upper(),))
            return cursor.fetchone()


class MembresiaRepositorio:
    """Acceso a datos para la tabla MEMBRESIA."""

    @staticmethod
    def guardar(membresia: Membresia) -> int:
        with obtener_cursor() as cursor:
            if cursor is None:
                raise ConnectionError("No hay conexión a la base de datos.")

            # Obtener duración del tipo de membresía si no se calculó
            cursor.execute("SELECT duracionDias FROM TIPO_MEMBRESIA WHERE claveTipoMembresia = %s",
                           (membresia.tipo_membresia,))
            tipo = cursor.fetchone()
            if not tipo:
                raise ValueError(f"El tipo de membresía '{membresia.tipo_membresia}' no existe.")

            fecha_fin = membresia.fecha_inicio + timedelta(days=tipo["duracionDias"])
            dias_restantes = (fecha_fin - date.today()).days
            if dias_restantes < 0:
                estado = c.ESTADO_MEMB_VENCIDA
            elif dias_restantes <= c.DIAS_POR_VENCER:
                estado = c.ESTADO_MEMB_POR_VENCER
            else:
                estado = c.ESTADO_MEMB_VIGENTE

            sql = """
                INSERT INTO MEMBRESIA (fechaInicio, fechaFin, estado, tipoMembresia, miembro)
                VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (
                membresia.fecha_inicio, fecha_fin, estado,
                membresia.tipo_membresia, membresia.miembro
            ))
            return cursor.lastrowid

    @staticmethod
    def listar(solo_vigentes: bool = False) -> list:
        with obtener_cursor() as cursor:
            if cursor is None:
                return []
            filtro = "WHERE mem.estado IN ('vigente', 'por vencer')" if solo_vigentes else ""
            sql = f"""
                SELECT mem.*, tm.nombreTipo, tm.costo,
                       CONCAT(m.nombre, ' ', m.primerApell) AS miembroNombre
                FROM MEMBRESIA mem
                JOIN TIPO_MEMBRESIA tm ON tm.claveTipoMembresia = mem.tipoMembresia
                JOIN MIEMBRO m ON m.numeroSocio = mem.miembro
                {filtro}
                ORDER BY mem.fechaFin ASC
            """
            cursor.execute(sql)
            return cursor.fetchall()

    @staticmethod
    def listar_por_vencer() -> list:
        """RF-06: Notificaciones de membresías próximas a vencer."""
        with obtener_cursor() as cursor:
            if cursor is None:
                return []
            sql = """
                SELECT mem.*, tm.nombreTipo, tm.costo,
                       CONCAT(m.nombre, ' ', m.primerApell) AS miembroNombre,
                       m.telefono, m.correo,
                       DATEDIFF(mem.fechaFin, CURDATE()) AS diasRestantes
                FROM MEMBRESIA mem
                JOIN TIPO_MEMBRESIA tm ON tm.claveTipoMembresia = mem.tipoMembresia
                JOIN MIEMBRO m ON m.numeroSocio = mem.miembro
                WHERE mem.fechaFin >= CURDATE()
                  AND DATEDIFF(mem.fechaFin, CURDATE()) <= %s
                ORDER BY mem.fechaFin ASC
            """
            cursor.execute(sql, (c.DIAS_POR_VENCER,))
            return cursor.fetchall()

    @staticmethod
    def actualizar_estados():
        """Actualiza el campo 'estado' de todas las membresías con la fecha actual."""
        with obtener_cursor() as cursor:
            if cursor is None:
                return 0
            sql = """
                UPDATE MEMBRESIA
                SET estado = CASE
                    WHEN fechaFin < CURDATE() THEN 'vencida'
                    WHEN DATEDIFF(fechaFin, CURDATE()) <= 7 THEN 'por vencer'
                    ELSE 'vigente'
                END
            """
            cursor.execute(sql)
            return cursor.rowcount

    @staticmethod
    def renovar(folio_membresia: int) -> bool:
        with obtener_cursor() as cursor:
            if cursor is None:
                return False
            cursor.execute(
                """
                SELECT mem.*, tm.duracionDias
                FROM MEMBRESIA mem
                JOIN TIPO_MEMBRESIA tm ON tm.claveTipoMembresia = mem.tipoMembresia
                WHERE mem.folioMembresia = %s
                """,
                (folio_membresia,)
            )
            fila = cursor.fetchone()
            if not fila:
                raise ValueError("La membresía no existe.")

            hoy = date.today()
            # Si aún está vigente, se suma a fechaFin existente; si venció, parte de hoy
            if fila["fechaFin"] >= hoy:
                nueva_fin = fila["fechaFin"] + timedelta(days=fila["duracionDias"])
            else:
                nueva_fin = hoy + timedelta(days=fila["duracionDias"])

            cursor.execute(
                """
                UPDATE MEMBRESIA
                SET fechaFin = %s,
                    estado = CASE
                        WHEN DATEDIFF(%s, CURDATE()) <= 7 THEN 'por vencer'
                        ELSE 'vigente'
                    END
                WHERE folioMembresia = %s
                """,
                (nueva_fin, nueva_fin, folio_membresia)
            )
            return cursor.rowcount > 0


class PagoRepositorio:
    """Acceso a datos para la tabla PAGO."""

    @staticmethod
    def registrar_pago(pago: Pago) -> int:
        with obtener_cursor() as cursor:
            if cursor is None:
                raise ConnectionError("No hay conexión a la base de datos.")

            # Validar que exista la membresía
            cursor.execute("SELECT folioMembresia FROM MEMBRESIA WHERE folioMembresia = %s", (pago.membresia,))
            if not cursor.fetchone():
                raise ValueError(f"La membresía #{pago.membresia} no existe.")

            sql = """
                INSERT INTO PAGO (fechaPago, monto, metodoPago, estadoPago, membresia)
                VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (
                pago.fecha_pago, pago.monto, pago.metodo_pago,
                pago.estado_pago, pago.membresia
            ))
            return cursor.lastrowid

    @staticmethod
    def listar_por_membresia(folio_membresia: int) -> list:
        with obtener_cursor() as cursor:
            if cursor is None:
                return []
            sql = "SELECT * FROM PAGO WHERE membresia = %s ORDER BY fechaPago DESC"
            cursor.execute(sql, (folio_membresia,))
            return cursor.fetchall()

    @staticmethod
    def historial() -> list:
        with obtener_cursor() as cursor:
            if cursor is None:
                return []
            sql = """
                SELECT p.*, mem.miembro,
                       CONCAT(m.nombre, ' ', m.primerApell) AS miembroNombre
                FROM PAGO p
                JOIN MEMBRESIA mem ON mem.folioMembresia = p.membresia
                JOIN MIEMBRO m ON m.numeroSocio = mem.miembro
                ORDER BY p.folioPago DESC
            """
            cursor.execute(sql)
            return cursor.fetchall()


class ActividadRepositorio:
    """Acceso a datos para la tabla ACTIVIDAD."""

    @staticmethod
    def listar() -> list:
        with obtener_cursor() as cursor:
            if cursor is None:
                return []
            sql = """
                SELECT a.*,
                       COUNT(CASE WHEN i.estado = 'activa' THEN 1 END) AS inscritosActivos
                FROM ACTIVIDAD a
                LEFT JOIN INSCRIPCION i ON i.actividad = a.codigoActividad
                GROUP BY a.codigoActividad
                ORDER BY a.codigoActividad
            """
            cursor.execute(sql)
            return cursor.fetchall()

    @staticmethod
    def obtener(codigo: str) -> dict:
        with obtener_cursor() as cursor:
            if cursor is None:
                return None
            cursor.execute("SELECT * FROM ACTIVIDAD WHERE codigoActividad = %s", (codigo.strip().upper(),))
            return cursor.fetchone()


class InscripcionRepositorio:
    """Acceso a datos para la tabla INSCRIPCION (RF-07)."""

    @staticmethod
    def inscribir(numero_socio: int, codigo_actividad: str) -> int:
        """
        Inscribe a un socio en una actividad:
        1. Verifica cupo máximo de la actividad.
        2. Si el miembro tiene una inscripción 'activa' previa, la finaliza automáticamente (historial).
        3. Inserta la nueva inscripción.
        """
        codigo_actividad = codigo_actividad.strip().upper()
        with obtener_cursor() as cursor:
            if cursor is None:
                raise ConnectionError("No hay conexión a la base de datos.")

            # Validar existencia de socio y actividad
            cursor.execute("SELECT numeroSocio, estatus FROM MIEMBRO WHERE numeroSocio = %s", (numero_socio,))
            m = cursor.fetchone()
            if not m:
                raise ValueError("El miembro no existe.")
            if m["estatus"] != c.ESTATUS_ACTIVO:
                raise ValueError("El miembro está inactivo. Debe estar activo para inscribirse.")

            cursor.execute("SELECT codigoActividad, cupoMaximo FROM ACTIVIDAD WHERE codigoActividad = %s", (codigo_actividad,))
            act = cursor.fetchone()
            if not act:
                raise ValueError("La actividad no existe.")

            # Validar cupo
            cursor.execute("SELECT COUNT(*) AS total FROM INSCRIPCION WHERE actividad = %s AND estado = 'activa'", (codigo_actividad,))
            cupo_ocupado = cursor.fetchone()["total"]
            if cupo_ocupado >= act["cupoMaximo"]:
                raise ValueError(f"{c.MSG_SIN_CUPO} (Inscritos: {cupo_ocupado}/{act['cupoMaximo']})")

            # Finalizar inscripción activa anterior (RF-07)
            cursor.execute(
                """
                UPDATE INSCRIPCION
                SET estado = 'finalizada', fechaBaja = CURDATE()
                WHERE miembro = %s AND estado = 'activa'
                """,
                (numero_socio,)
            )

            # Insertar nueva inscripción
            cursor.execute(
                """
                INSERT INTO INSCRIPCION (fechaInscripcion, fechaBaja, estado, miembro, actividad)
                VALUES (CURDATE(), NULL, 'activa', %s, %s)
                """,
                (numero_socio, codigo_actividad)
            )
            return cursor.lastrowid

    @staticmethod
    def dar_de_baja(numero_socio: int) -> bool:
        with obtener_cursor() as cursor:
            if cursor is None:
                return False
            cursor.execute(
                """
                UPDATE INSCRIPCION
                SET estado = 'finalizada', fechaBaja = CURDATE()
                WHERE miembro = %s AND estado = 'activa'
                """,
                (numero_socio,)
            )
            return cursor.rowcount > 0

    @staticmethod
    def miembros_por_actividad(nombre_o_codigo: str) -> list:
        """Consulta 4 del entregable: miembros inscritos a una actividad."""
        with obtener_cursor() as cursor:
            if cursor is None:
                return []
            sql = """
                SELECT a.nombre AS actividad,
                       m.numeroSocio,
                       CONCAT(m.nombre, ' ', m.primerApell, IFNULL(CONCAT(' ', m.segApell), '')) AS miembro,
                       i.fechaInscripcion, i.estado
                FROM INSCRIPCION i
                JOIN ACTIVIDAD a ON a.codigoActividad = i.actividad
                JOIN MIEMBRO m ON m.numeroSocio = i.miembro
                WHERE a.codigoActividad = %s OR a.nombre LIKE %s
                ORDER BY i.fechaInscripcion DESC
            """
            cursor.execute(sql, (nombre_o_codigo, f"%{nombre_o_codigo}%"))
            return cursor.fetchall()

    @staticmethod
    def historial_socio(numero_socio: int) -> list:
        with obtener_cursor() as cursor:
            if cursor is None:
                return []
            sql = """
                SELECT i.*, a.nombre AS actividadNombre
                FROM INSCRIPCION i
                JOIN ACTIVIDAD a ON a.codigoActividad = i.actividad
                WHERE i.miembro = %s
                ORDER BY i.fechaInscripcion DESC
            """
            cursor.execute(sql, (numero_socio,))
            return cursor.fetchall()
