"""
repositorios/repositorio_a.py
Digital Sport Manager - Club Deportivo

Consultas SQL del Módulo A:
- Miembros, Entrenadores, Categorías y Equipos (RF-01, RF-05).
"""

import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import constantes as c
from db.conexion import obtener_cursor
from modelos.personas import Miembro, Entrenador, calcular_edad
from modelos.organizacion import Categoria, Equipo


class MiembroRepositorio:
    """Acceso a datos para la tabla MIEMBRO."""

    @staticmethod
    def guardar(miembro: Miembro) -> int:
        with obtener_cursor() as cursor:
            if cursor is None:
                raise ConnectionError("No hay conexión a la base de datos.")

            # Validar correo único
            cursor.execute("SELECT numeroSocio FROM MIEMBRO WHERE correo = %s", (miembro.correo,))
            if cursor.fetchone():
                raise ValueError(f"Ya existe un miembro con el correo '{miembro.correo}'.")

            # Validar equipo y rango de edad
            cursor.execute(
                """
                SELECT e.claveEquipo, cat.edadMinima, cat.edadMaxima
                FROM EQUIPO e
                JOIN CATEGORIA cat ON cat.claveCategoria = e.categoria
                WHERE e.claveEquipo = %s
                """,
                (miembro.equipo,)
            )
            eq = cursor.fetchone()
            if not eq:
                raise ValueError(f"El equipo '{miembro.equipo}' no existe.")

            edad = miembro.edad
            if not (eq["edadMinima"] <= edad <= eq["edadMaxima"]):
                raise ValueError(f"{c.MSG_EDAD_FUERA_RANGO} (Edad: {edad}, Rango: {eq['edadMinima']}-{eq['edadMaxima']})")

            sql = """
                INSERT INTO MIEMBRO (nombre, primerApell, segApell, telefono, correo,
                                     fechaRegistro, fechaNacimiento, edad, estatus, equipo)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (
                miembro.nombre, miembro.primerApell, miembro.segApell,
                miembro.telefono, miembro.correo, miembro.fecha_registro,
                miembro.fecha_nacimiento, edad, miembro.estatus, miembro.equipo
            ))
            return cursor.lastrowid

    @staticmethod
    def obtener(numero_socio: int) -> dict:
        with obtener_cursor() as cursor:
            if cursor is None:
                return None
            cursor.execute("SELECT * FROM MIEMBRO WHERE numeroSocio = %s", (numero_socio,))
            return cursor.fetchone()

    @staticmethod
    def listar(solo_activos: bool = False) -> list:
        with obtener_cursor() as cursor:
            if cursor is None:
                return []
            filtro = "WHERE m.estatus = 'activo'" if solo_activos else ""
            sql = f"""
                SELECT m.*, e.nombreEquipo,
                       CONCAT(m.nombre, ' ', m.primerApell, IFNULL(CONCAT(' ', m.segApell), '')) AS nombreCompleto
                FROM MIEMBRO m
                LEFT JOIN EQUIPO e ON e.claveEquipo = m.equipo
                {filtro}
                ORDER BY m.numeroSocio
            """
            cursor.execute(sql)
            return cursor.fetchall()

    @staticmethod
    def buscar(termino: str) -> list:
        with obtener_cursor() as cursor:
            if cursor is None:
                return []
            like = f"%{termino.strip()}%"
            sql = """
                SELECT m.*, e.nombreEquipo,
                       CONCAT(m.nombre, ' ', m.primerApell, IFNULL(CONCAT(' ', m.segApell), '')) AS nombreCompleto
                FROM MIEMBRO m
                LEFT JOIN EQUIPO e ON e.claveEquipo = m.equipo
                WHERE m.nombre LIKE %s OR m.primerApell LIKE %s OR m.correo LIKE %s
                ORDER BY m.numeroSocio
            """
            cursor.execute(sql, (like, like, like))
            return cursor.fetchall()

    @staticmethod
    def actualizar(numero_socio: int, datos: dict) -> bool:
        if not datos:
            return False
        with obtener_cursor() as cursor:
            if cursor is None:
                return False
            set_clauses = [f"{col} = %s" for col in datos.keys()]
            valores = list(datos.values())
            valores.append(numero_socio)
            sql = f"UPDATE MIEMBRO SET {', '.join(set_clauses)} WHERE numeroSocio = %s"
            cursor.execute(sql, tuple(valores))
            return cursor.rowcount > 0

    @staticmethod
    def cambiar_estatus(numero_socio: int, nuevo_estatus: str) -> bool:
        est = nuevo_estatus.strip().lower()
        if est not in c.ESTATUS_VALIDOS:
            raise ValueError(f"Estatus no válido: {est}")
        with obtener_cursor() as cursor:
            if cursor is None:
                return False
            cursor.execute("UPDATE MIEMBRO SET estatus = %s WHERE numeroSocio = %s", (est, numero_socio))
            return cursor.rowcount > 0


class EntrenadorRepositorio:
    """Acceso a datos para la tabla ENTRENADOR."""

    @staticmethod
    def guardar(entrenador: Entrenador) -> int:
        with obtener_cursor() as cursor:
            if cursor is None:
                raise ConnectionError("No hay conexión a la base de datos.")

            cursor.execute("SELECT claveEntrenador FROM ENTRENADOR WHERE correo = %s", (entrenador.correo,))
            if cursor.fetchone():
                raise ValueError(f"Ya existe un entrenador con el correo '{entrenador.correo}'.")

            sql = """
                INSERT INTO ENTRENADOR (nombre, primerApell, segApell, telefono, correo, especialidad, estatus)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (
                entrenador.nombre, entrenador.primerApell, entrenador.segApell,
                entrenador.telefono, entrenador.correo, entrenador.especialidad, entrenador.estatus
            ))
            return cursor.lastrowid

    @staticmethod
    def listar(solo_activos: bool = False) -> list:
        with obtener_cursor() as cursor:
            if cursor is None:
                return []
            filtro = "WHERE t.estatus = 'activo'" if solo_activos else ""
            sql = f"""
                SELECT t.*,
                       CONCAT(t.nombre, ' ', t.primerApell, IFNULL(CONCAT(' ', t.segApell), '')) AS nombreCompleto,
                       COUNT(e.claveEquipo) AS equipos
                FROM ENTRENADOR t
                LEFT JOIN EQUIPO e ON e.entrenador = t.claveEntrenador
                {filtro}
                GROUP BY t.claveEntrenador
                ORDER BY t.claveEntrenador
            """
            cursor.execute(sql)
            return cursor.fetchall()

    @staticmethod
    def actualizar(clave_entrenador: int, datos: dict) -> bool:
        if not datos:
            return False
        with obtener_cursor() as cursor:
            if cursor is None:
                return False
            set_clauses = [f"{col} = %s" for col in datos.keys()]
            valores = list(datos.values())
            valores.append(clave_entrenador)
            sql = f"UPDATE ENTRENADOR SET {', '.join(set_clauses)} WHERE claveEntrenador = %s"
            cursor.execute(sql, tuple(valores))
            return cursor.rowcount > 0

    @staticmethod
    def cambiar_estatus(clave_entrenador: int, nuevo_estatus: str) -> bool:
        est = nuevo_estatus.strip().lower()
        if est not in c.ESTATUS_VALIDOS:
            raise ValueError(f"Estatus no válido: {est}")
        with obtener_cursor() as cursor:
            if cursor is None:
                return False
            cursor.execute("UPDATE ENTRENADOR SET estatus = %s WHERE claveEntrenador = %s", (est, clave_entrenador))
            return cursor.rowcount > 0


class CategoriaRepositorio:
    """Acceso a datos para la tabla CATEGORIA."""

    @staticmethod
    def guardar(categoria: Categoria) -> bool:
        with obtener_cursor() as cursor:
            if cursor is None:
                return False
            sql = """
                INSERT INTO CATEGORIA (claveCategoria, nombreCategoria, edadMinima, edadMaxima)
                VALUES (%s, %s, %s, %s)
            """
            cursor.execute(sql, (
                categoria.clave_categoria, categoria.nombre_categoria,
                categoria.edad_minima, categoria.edad_maxima
            ))
            return True

    @staticmethod
    def listar() -> list:
        with obtener_cursor() as cursor:
            if cursor is None:
                return []
            cursor.execute("SELECT * FROM CATEGORIA ORDER BY edadMinima")
            return cursor.fetchall()


class EquipoRepositorio:
    """Acceso a datos para la tabla EQUIPO."""

    @staticmethod
    def guardar(equipo: Equipo) -> bool:
        with obtener_cursor() as cursor:
            if cursor is None:
                return False
            sql = """
                INSERT INTO EQUIPO (claveEquipo, nombreEquipo, categoria, entrenador)
                VALUES (%s, %s, %s, %s)
            """
            cursor.execute(sql, (
                equipo.clave_equipo, equipo.nombre_equipo,
                equipo.categoria, equipo.entrenador
            ))
            return True

    @staticmethod
    def listar() -> list:
        with obtener_cursor() as cursor:
            if cursor is None:
                return []
            sql = """
                SELECT e.*, c.nombreCategoria, c.edadMinima, c.edadMaxima,
                       CONCAT(t.nombre, ' ', t.primerApell) AS entrenadorNombre,
                       t.estatus AS estatusEntrenador,
                       COUNT(m.numeroSocio) AS miembrosActivos
                FROM EQUIPO e
                JOIN CATEGORIA c ON c.claveCategoria = e.categoria
                JOIN ENTRENADOR t ON t.claveEntrenador = e.entrenador
                LEFT JOIN MIEMBRO m ON m.equipo = e.claveEquipo AND m.estatus = 'activo'
                GROUP BY e.claveEquipo
                ORDER BY e.claveEquipo
            """
            cursor.execute(sql)
            return cursor.fetchall()

    @staticmethod
    def equipos_para_edad(edad: int) -> list:
        with obtener_cursor() as cursor:
            if cursor is None:
                return []
            sql = """
                SELECT e.claveEquipo, e.nombreEquipo, c.nombreCategoria, c.edadMinima, c.edadMaxima
                FROM EQUIPO e
                JOIN CATEGORIA c ON c.claveCategoria = e.categoria
                WHERE %s BETWEEN c.edadMinima AND c.edadMaxima
                ORDER BY e.claveEquipo
            """
            cursor.execute(sql, (edad,))
            return cursor.fetchall()

    @staticmethod
    def asignar_miembro(numero_socio: int, clave_equipo: str) -> bool:
        with obtener_cursor() as cursor:
            if cursor is None:
                return False
            # Validar edad del socio contra equipo
            cursor.execute("SELECT fechaNacimiento FROM MIEMBRO WHERE numeroSocio = %s", (numero_socio,))
            m = cursor.fetchone()
            if not m:
                raise ValueError("El miembro no existe.")
            edad = calcular_edad(m["fechaNacimiento"])

            cursor.execute(
                """
                SELECT c.edadMinima, c.edadMaxima
                FROM EQUIPO e
                JOIN CATEGORIA c ON c.claveCategoria = e.categoria
                WHERE e.claveEquipo = %s
                """,
                (clave_equipo.strip().upper(),)
            )
            eq = cursor.fetchone()
            if not eq:
                raise ValueError("El equipo no existe.")
            if not (eq["edadMinima"] <= edad <= eq["edadMaxima"]):
                raise ValueError(f"{c.MSG_EDAD_FUERA_RANGO} (Edad: {edad}, Categoría: {eq['edadMinima']}-{eq['edadMaxima']})")

            cursor.execute("UPDATE MIEMBRO SET equipo = %s WHERE numeroSocio = %s", (clave_equipo.strip().upper(), numero_socio))
            return cursor.rowcount > 0

    @staticmethod
    def cambiar_entrenador(clave_equipo: str, clave_entrenador: int) -> bool:
        with obtener_cursor() as cursor:
            if cursor is None:
                return False
            cursor.execute("UPDATE EQUIPO SET entrenador = %s WHERE claveEquipo = %s", (clave_entrenador, clave_equipo.strip().upper()))
            return cursor.rowcount > 0

    @staticmethod
    def miembros_de(nombre_o_clave_equipo: str) -> list:
        """Consulta 1 del entregable: miembros de un equipo."""
        with obtener_cursor() as cursor:
            if cursor is None:
                return []
            sql = """
                SELECT e.nombreEquipo,
                       CONCAT(t.nombre, ' ', t.primerApell) AS entrenador,
                       m.numeroSocio,
                       CONCAT(m.nombre, ' ', m.primerApell, IFNULL(CONCAT(' ', m.segApell), '')) AS miembro,
                       m.edad, m.estatus
                FROM EQUIPO e
                JOIN ENTRENADOR t ON t.claveEntrenador = e.entrenador
                JOIN MIEMBRO m ON m.equipo = e.claveEquipo
                WHERE e.claveEquipo = %s OR e.nombreEquipo LIKE %s
                ORDER BY m.numeroSocio
            """
            cursor.execute(sql, (nombre_o_clave_equipo, f"%{nombre_o_clave_equipo}%"))
            return cursor.fetchall()
