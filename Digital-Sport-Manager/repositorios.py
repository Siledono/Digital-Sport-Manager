"""
repositorios.py
Digital Sport Manager - Club Deportivo

Acceso a datos y consultas SQL centralizadas para todos los módulos (A, B y C).
Utiliza bloques try/except directamente donde se ejecutan las sentencias SQL
para capturar y traducir excepciones de MySQL a excepciones personalizadas.
"""

from datetime import date, timedelta
import mysql.connector
from db.conexion import obtener_cursor
from modelos import (
    Miembro, Entrenador, calcular_edad, Categoria, Equipo,
    Tipo_Membresia, Membresia, Pago, Actividad, Inscripcion,
    Espacio_Deportivo, Material, Horario, Reserva, Asistencia,
    ValidacionError, BaseDatosError,
    ESTATUS_ACTIVO, ESTATUS_VALIDOS,
    ESTADO_MEMB_VIGENTE, ESTADO_MEMB_POR_VENCER, ESTADO_MEMB_VENCIDA, DIAS_POR_VENCER,
    ESTADO_ESPACIO_DISPONIBLE, ESTADOS_ESPACIO,
    DIA_POR_NUMERO
)

MSG_EDAD_FUERA_RANGO = "La edad del miembro no está dentro del rango de la categoría del equipo."
MSG_SIN_CUPO = "La actividad ya alcanzó su cupo máximo."
MSG_TRASLAPE = "El espacio ya está ocupado en esa fecha y horario."


# ===========================================================================
# REPOSITORIOS DEL MÓDULO A: Personas, Equipos y Categorías
# ===========================================================================
class MiembroRepositorio:
    """Consultas SQL para la tabla MIEMBRO."""

    @staticmethod
    def guardar(miembro: Miembro) -> int:
        with obtener_cursor() as cursor:
            if cursor is None:
                raise BaseDatosError("No hay conexión a la base de datos.")

            # Validar correo único
            cursor.execute("SELECT numeroSocio FROM MIEMBRO WHERE correo = %s", (miembro.correo,))
            if cursor.fetchone():
                raise ValidacionError(f"Ya existe un miembro con el correo '{miembro.correo}'.")

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
                raise ValidacionError(f"El equipo '{miembro.equipo}' no existe.")

            edad = miembro.edad
            if not (eq["edadMinima"] <= edad <= eq["edadMaxima"]):
                raise ValidacionError(f"{MSG_EDAD_FUERA_RANGO} (Edad: {edad}, Rango: {eq['edadMinima']}-{eq['edadMaxima']})")

            sql = """
                INSERT INTO MIEMBRO (nombre, primerApell, segApell, telefono, correo,
                                     fechaRegistro, fechaNacimiento, edad, estatus, equipo)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            try:
                cursor.execute(sql, (
                    miembro.nombre, miembro.primer_apell, miembro.seg_apell,
                    miembro.telefono, miembro.correo, miembro.fecha_registro,
                    miembro.fecha_nacimiento, edad, miembro.estatus, miembro.equipo
                ))
                return cursor.lastrowid
            except mysql.connector.Error as e:
                if e.errno == 1062:
                    raise ValidacionError("Ya existe un miembro con ese correo electrónico.")
                elif e.errno == 1452:
                    raise ValidacionError("El equipo especificado no existe.")
                raise BaseDatosError(f"Error al registrar miembro: {e}")

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
            try:
                cursor.execute(sql, tuple(valores))
                return cursor.rowcount > 0
            except mysql.connector.Error as e:
                if e.errno == 1062:
                    raise ValidacionError("Ya existe otro socio registrado con ese correo.")
                raise BaseDatosError(f"Error al actualizar datos del miembro: {e}")

    @staticmethod
    def cambiar_estatus(numero_socio: int, nuevo_estatus: str) -> bool:
        est = nuevo_estatus.strip().lower()
        if est not in ESTATUS_VALIDOS:
            raise ValidacionError(f"Estatus no válido: '{est}'.")
        with obtener_cursor() as cursor:
            if cursor is None:
                return False
            cursor.execute("UPDATE MIEMBRO SET estatus = %s WHERE numeroSocio = %s", (est, numero_socio))
            return cursor.rowcount > 0


class EntrenadorRepositorio:
    """Consultas SQL para la tabla ENTRENADOR."""

    @staticmethod
    def guardar(entrenador: Entrenador) -> int:
        with obtener_cursor() as cursor:
            if cursor is None:
                raise BaseDatosError("No hay conexión a la base de datos.")

            cursor.execute("SELECT claveEntrenador FROM ENTRENADOR WHERE correo = %s", (entrenador.correo,))
            if cursor.fetchone():
                raise ValidacionError(f"Ya existe un entrenador con el correo '{entrenador.correo}'.")

            sql = """
                INSERT INTO ENTRENADOR (nombre, primerApell, segApell, telefono, correo, especialidad, estatus)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            try:
                cursor.execute(sql, (
                    entrenador.nombre, entrenador.primer_apell, entrenador.seg_apell,
                    entrenador.telefono, entrenador.correo, entrenador.especialidad, entrenador.estatus
                ))
                return cursor.lastrowid
            except mysql.connector.Error as e:
                if e.errno == 1062:
                    raise ValidacionError("Ya existe un entrenador con ese correo electrónico.")
                raise BaseDatosError(f"Error al registrar entrenador: {e}")

    @staticmethod
    def obtener(clave_entrenador: int) -> dict:
        with obtener_cursor() as cursor:
            if cursor is None:
                return None
            cursor.execute("SELECT * FROM ENTRENADOR WHERE claveEntrenador = %s", (clave_entrenador,))
            return cursor.fetchone()

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
            try:
                cursor.execute(sql, tuple(valores))
                return cursor.rowcount > 0
            except mysql.connector.Error as e:
                if e.errno == 1062:
                    raise ValidacionError("Ya existe otro entrenador con ese correo.")
                raise BaseDatosError(f"Error al actualizar entrenador: {e}")

    @staticmethod
    def cambiar_estatus(clave_entrenador: int, nuevo_estatus: str) -> bool:
        est = nuevo_estatus.strip().lower()
        if est not in ESTATUS_VALIDOS:
            raise ValidacionError(f"Estatus no válido: '{est}'.")
        with obtener_cursor() as cursor:
            if cursor is None:
                return False
            cursor.execute("UPDATE ENTRENADOR SET estatus = %s WHERE claveEntrenador = %s", (est, clave_entrenador))
            return cursor.rowcount > 0


class CategoriaRepositorio:
    """Consultas SQL para la tabla CATEGORIA."""

    @staticmethod
    def guardar(categoria: Categoria) -> bool:
        with obtener_cursor() as cursor:
            if cursor is None:
                raise BaseDatosError("No hay conexión a la base de datos.")
            sql = """
                INSERT INTO CATEGORIA (claveCategoria, nombreCategoria, edadMinima, edadMaxima)
                VALUES (%s, %s, %s, %s)
            """
            try:
                cursor.execute(sql, (
                    categoria.clave_categoria, categoria.nombre_categoria,
                    categoria.edad_minima, categoria.edad_maxima
                ))
                return True
            except mysql.connector.Error as e:
                if e.errno == 1062:
                    if "nombreCategoria" in str(e):
                        raise ValidacionError("Ya existe una categoría con ese nombre.")
                    raise ValidacionError("Ya existe una categoría con esa clave.")
                elif e.errno == 3819:
                    raise ValidacionError("La edad máxima debe ser mayor o igual a la edad mínima.")
                raise BaseDatosError(f"Error al guardar la categoría: {e}")

    @staticmethod
    def listar() -> list:
        with obtener_cursor() as cursor:
            if cursor is None:
                return []
            cursor.execute("SELECT * FROM CATEGORIA ORDER BY edadMinima")
            return cursor.fetchall()


class EquipoRepositorio:
    """Consultas SQL para la tabla EQUIPO."""

    @staticmethod
    def guardar(equipo: Equipo) -> bool:
        with obtener_cursor() as cursor:
            if cursor is None:
                raise BaseDatosError("No hay conexión a la base de datos.")
            sql = """
                INSERT INTO EQUIPO (claveEquipo, nombreEquipo, categoria, entrenador)
                VALUES (%s, %s, %s, %s)
            """
            try:
                cursor.execute(sql, (
                    equipo.clave_equipo, equipo.nombre_equipo,
                    equipo.categoria, equipo.entrenador
                ))
                return True
            except mysql.connector.Error as e:
                if e.errno == 1062:
                    if "nombreEquipo" in str(e):
                        raise ValidacionError("Ya existe un equipo con ese nombre.")
                    raise ValidacionError("Ya existe un equipo con esa clave.")
                elif e.errno == 1452:
                    raise ValidacionError("La categoría o el entrenador especificado no existe.")
                raise BaseDatosError(f"Error al guardar el equipo: {e}")

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
            cursor.execute("SELECT fechaNacimiento FROM MIEMBRO WHERE numeroSocio = %s", (numero_socio,))
            m = cursor.fetchone()
            if not m:
                raise ValidacionError("El miembro no existe.")
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
                raise ValidacionError("El equipo no existe.")
            if not (eq["edadMinima"] <= edad <= eq["edadMaxima"]):
                raise ValidacionError(f"{MSG_EDAD_FUERA_RANGO} (Edad: {edad}, Categoría: {eq['edadMinima']}-{eq['edadMaxima']})")

            try:
                cursor.execute("UPDATE MIEMBRO SET equipo = %s WHERE numeroSocio = %s", (clave_equipo.strip().upper(), numero_socio))
                return cursor.rowcount > 0
            except mysql.connector.Error as e:
                if e.errno == 1452:
                    raise ValidacionError("El equipo especificado no existe.")
                raise BaseDatosError(f"Error al asignar miembro: {e}")

    @staticmethod
    def cambiar_entrenador(clave_equipo: str, clave_entrenador: int) -> bool:
        with obtener_cursor() as cursor:
            if cursor is None:
                return False
            try:
                cursor.execute("UPDATE EQUIPO SET entrenador = %s WHERE claveEquipo = %s", (clave_entrenador, clave_equipo.strip().upper()))
                return cursor.rowcount > 0
            except mysql.connector.Error as e:
                if e.errno == 1452:
                    raise ValidacionError("El entrenador especificado no existe.")
                raise BaseDatosError(f"Error al cambiar entrenador: {e}")

    @staticmethod
    def miembros_de(nombre_o_clave_equipo: str) -> list:
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


# ===========================================================================
# REPOSITORIOS DEL MÓDULO B: Membresías, Pagos e Inscripciones
# ===========================================================================
class TipoMembresiaRepositorio:
    """Consultas SQL para la tabla TIPO_MEMBRESIA."""

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
    """Consultas SQL para la tabla MEMBRESIA."""

    @staticmethod
    def guardar(membresia: Membresia) -> int:
        with obtener_cursor() as cursor:
            if cursor is None:
                raise BaseDatosError("No hay conexión a la base de datos.")

            cursor.execute("SELECT duracionDias FROM TIPO_MEMBRESIA WHERE claveTipoMembresia = %s",
                           (membresia.tipo_membresia,))
            tipo = cursor.fetchone()
            if not tipo:
                raise ValidacionError(f"El tipo de membresía '{membresia.tipo_membresia}' no existe.")

            fecha_fin = membresia.fecha_inicio + timedelta(days=tipo["duracionDias"])
            dias_restantes = (fecha_fin - date.today()).days
            if dias_restantes < 0:
                estado = ESTADO_MEMB_VENCIDA
            elif dias_restantes <= DIAS_POR_VENCER:
                estado = ESTADO_MEMB_POR_VENCER
            else:
                estado = ESTADO_MEMB_VIGENTE

            sql = """
                INSERT INTO MEMBRESIA (fechaInicio, fechaFin, estado, tipoMembresia, miembro)
                VALUES (%s, %s, %s, %s, %s)
            """
            try:
                cursor.execute(sql, (
                    membresia.fecha_inicio, fecha_fin, estado,
                    membresia.tipo_membresia, membresia.miembro
                ))
                return cursor.lastrowid
            except mysql.connector.Error as e:
                if e.errno == 1452:
                    raise ValidacionError("El socio o tipo de membresía no existe.")
                raise BaseDatosError(f"Error al registrar membresía: {e}")

    @staticmethod
    def obtener(folio_membresia: int) -> dict:
        with obtener_cursor() as cursor:
            if cursor is None:
                return None
            sql = """
                SELECT mem.*, tm.nombreTipo, tm.costo, tm.duracionDias,
                       CONCAT(m.nombre, ' ', m.primerApell) AS miembroNombre
                FROM MEMBRESIA mem
                JOIN TIPO_MEMBRESIA tm ON tm.claveTipoMembresia = mem.tipoMembresia
                JOIN MIEMBRO m ON m.numeroSocio = mem.miembro
                WHERE mem.folioMembresia = %s
            """
            cursor.execute(sql, (folio_membresia,))
            return cursor.fetchone()

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
            cursor.execute(sql, (DIAS_POR_VENCER,))
            return cursor.fetchall()

    @staticmethod
    def actualizar_estados():
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
                raise ValidacionError("La membresía no existe.")

            hoy = date.today()
            if fila["fechaFin"] >= hoy:
                nueva_fin = fila["fechaFin"] + timedelta(days=fila["duracionDias"])
            else:
                nueva_fin = hoy + timedelta(days=fila["duracionDias"])

            try:
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
            except mysql.connector.Error as e:
                raise BaseDatosError(f"Error al renovar membresía: {e}")


class PagoRepositorio:
    """Consultas SQL para la tabla PAGO."""

    @staticmethod
    def registrar_pago(pago: Pago) -> int:
        with obtener_cursor() as cursor:
            if cursor is None:
                raise BaseDatosError("No hay conexión a la base de datos.")

            cursor.execute("SELECT folioMembresia FROM MEMBRESIA WHERE folioMembresia = %s", (pago.membresia,))
            if not cursor.fetchone():
                raise ValidacionError(f"La membresía #{pago.membresia} no existe.")

            sql = """
                INSERT INTO PAGO (fechaPago, monto, metodoPago, estadoPago, membresia)
                VALUES (%s, %s, %s, %s, %s)
            """
            try:
                cursor.execute(sql, (
                    pago.fecha_pago, pago.monto, pago.metodo_pago,
                    pago.estado_pago, pago.membresia
                ))
                return cursor.lastrowid
            except mysql.connector.Error as e:
                if e.errno == 1452:
                    raise ValidacionError("La membresía indicada no existe.")
                raise BaseDatosError(f"Error al registrar pago: {e}")

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
    """Consultas SQL para la tabla ACTIVIDAD."""

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
    """Consultas SQL para la tabla INSCRIPCION."""

    @staticmethod
    def inscribir(numero_socio: int, codigo_actividad: str) -> int:
        codigo_actividad = codigo_actividad.strip().upper()
        with obtener_cursor() as cursor:
            if cursor is None:
                raise BaseDatosError("No hay conexión a la base de datos.")

            cursor.execute("SELECT numeroSocio, estatus FROM MIEMBRO WHERE numeroSocio = %s", (numero_socio,))
            m = cursor.fetchone()
            if not m:
                raise ValidacionError("El miembro no existe.")
            if m["estatus"] != ESTATUS_ACTIVO:
                raise ValidacionError("El miembro está inactivo. Debe estar activo para inscribirse.")

            cursor.execute("SELECT codigoActividad, cupoMaximo FROM ACTIVIDAD WHERE codigoActividad = %s", (codigo_actividad,))
            act = cursor.fetchone()
            if not act:
                raise ValidacionError("La actividad no existe.")

            cursor.execute("SELECT COUNT(*) AS total FROM INSCRIPCION WHERE actividad = %s AND estado = 'activa'", (codigo_actividad,))
            cupo_ocupado = cursor.fetchone()["total"]
            if cupo_ocupado >= act["cupoMaximo"]:
                raise ValidacionError(f"{MSG_SIN_CUPO} (Inscritos: {cupo_ocupado}/{act['cupoMaximo']})")

            # Finalizar inscripción activa previa
            cursor.execute(
                """
                UPDATE INSCRIPCION
                SET estado = 'finalizada', fechaBaja = CURDATE()
                WHERE miembro = %s AND estado = 'activa'
                """,
                (numero_socio,)
            )

            try:
                cursor.execute(
                    """
                    INSERT INTO INSCRIPCION (fechaInscripcion, fechaBaja, estado, miembro, actividad)
                    VALUES (CURDATE(), NULL, 'activa', %s, %s)
                    """,
                    (numero_socio, codigo_actividad)
                )
                return cursor.lastrowid
            except mysql.connector.Error as e:
                if e.errno == 1452:
                    raise ValidacionError("El miembro o la actividad no existe.")
                raise BaseDatosError(f"Error al registrar inscripción: {e}")

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


# ===========================================================================
# REPOSITORIOS DEL MÓDULO C: Espacios, Horarios, Reservas y Asistencias
# ===========================================================================
class EspacioRepositorio:
    """Consultas SQL para la tabla ESPACIO_DEPORTIVO."""

    @staticmethod
    def guardar(espacio: Espacio_Deportivo) -> bool:
        with obtener_cursor() as cursor:
            if cursor is None:
                raise BaseDatosError("No hay conexión a la base de datos.")
            sql = """
                INSERT INTO ESPACIO_DEPORTIVO (codigoEspacio, nombreEspacio, tipo, capacidad, estado)
                VALUES (%s, %s, %s, %s, %s)
            """
            try:
                cursor.execute(sql, (
                    espacio.codigo_espacio, espacio.nombre_espacio,
                    espacio.tipo, espacio.capacidad, espacio.estado
                ))
                return True
            except mysql.connector.Error as e:
                if e.errno == 1062:
                    if "nombreEspacio" in str(e):
                        raise ValidacionError("Ya existe un espacio deportivo con ese nombre.")
                    raise ValidacionError("Ya existe un espacio deportivo con ese código.")
                raise BaseDatosError(f"Error al registrar espacio deportivo: {e}")

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
        if est not in ESTADOS_ESPACIO:
            raise ValidacionError(f"Estado de espacio no válido: '{est}'.")
        with obtener_cursor() as cursor:
            if cursor is None:
                return False
            cursor.execute(
                "UPDATE ESPACIO_DEPORTIVO SET estado = %s WHERE codigoEspacio = %s",
                (est, codigo_espacio.strip().upper())
            )
            return cursor.rowcount > 0


class MaterialRepositorio:
    """Consultas SQL para la tabla MATERIAL."""

    @staticmethod
    def guardar(material: Material) -> bool:
        with obtener_cursor() as cursor:
            if cursor is None:
                raise BaseDatosError("No hay conexión a la base de datos.")
            sql = """
                INSERT INTO MATERIAL (codigoMaterial, nombreMaterial, cantidadTotal, estado)
                VALUES (%s, %s, %s, %s)
            """
            try:
                cursor.execute(sql, (
                    material.codigo_material, material.nombre_material,
                    material.cantidad_total, material.estado
                ))
                return True
            except mysql.connector.Error as e:
                if e.errno == 1062:
                    if "nombreMaterial" in str(e):
                        raise ValidacionError("Ya existe un material deportivo con ese nombre.")
                    raise ValidacionError("Ya existe un material deportivo con ese código.")
                raise BaseDatosError(f"Error al registrar material: {e}")

    @staticmethod
    def listar() -> list:
        with obtener_cursor() as cursor:
            if cursor is None:
                return []
            cursor.execute("SELECT * FROM MATERIAL ORDER BY codigoMaterial")
            return cursor.fetchall()


class EspacioMaterialRepositorio:
    """Consultas SQL para la tabla ESPACIO_MATERIAL."""

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
            try:
                cursor.execute(sql, (espacio.strip().upper(), material.strip().upper(), cantidad))
                return True
            except mysql.connector.Error as e:
                if e.errno == 1452:
                    raise ValidacionError("El espacio o el material especificado no existe.")
                raise BaseDatosError(f"Error al asignar material al espacio: {e}")

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
    """Consultas SQL para la tabla HORARIO y EQUIPO_HORARIO."""

    @staticmethod
    def guardar(horario: Horario) -> int:
        with obtener_cursor() as cursor:
            if cursor is None:
                raise BaseDatosError("No hay conexión a la base de datos.")

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
                raise ValidacionError(f"{MSG_TRASLAPE} (Conflicto con horario de entrenamiento)")

            sql = """
                INSERT INTO HORARIO (diaSemana, horaInicio, horaFin, actividad, espacio)
                VALUES (%s, %s, %s, %s, %s)
            """
            try:
                cursor.execute(sql, (
                    horario.dia_semana, horario.hora_inicio, horario.hora_fin,
                    horario.actividad, horario.espacio
                ))
                return cursor.lastrowid
            except mysql.connector.Error as e:
                if e.errno == 1452:
                    raise ValidacionError("La actividad o el espacio deportivo no existe.")
                raise BaseDatosError(f"Error al programar horario: {e}")

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
            try:
                cursor.execute(
                    """
                    INSERT IGNORE INTO EQUIPO_HORARIO (equipo, horario)
                    VALUES (%s, %s)
                    """,
                    (clave_equipo.strip().upper(), codigo_horario)
                )
                return cursor.rowcount > 0
            except mysql.connector.Error as e:
                if e.errno == 1452:
                    raise ValidacionError("El equipo o el horario no existe.")
                raise BaseDatosError(f"Error al asignar equipo al horario: {e}")

    @staticmethod
    def listar_por_equipo(nombre_o_clave: str) -> list:
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
    """Consultas SQL para la tabla RESERVA."""

    @staticmethod
    def crear_reserva(reserva: Reserva) -> int:
        with obtener_cursor() as cursor:
            if cursor is None:
                raise BaseDatosError("No hay conexión a la base de datos.")

            # 1. Validar estado del espacio
            cursor.execute("SELECT estado FROM ESPACIO_DEPORTIVO WHERE codigoEspacio = %s", (reserva.espacio,))
            esp = cursor.fetchone()
            if not esp:
                raise ValidacionError("El espacio deportivo no existe.")
            if esp["estado"] != ESTADO_ESPACIO_DISPONIBLE:
                raise ValidacionError(f"El espacio no está disponible (estado actual: {esp['estado']}).")

            # 2. Validar traslape con otras reservas
            cursor.execute(
                """
                SELECT numReserva FROM RESERVA
                WHERE espacio = %s AND fecha = %s
                  AND %s < horaFin AND horaInicio < %s
                """,
                (reserva.espacio, reserva.fecha, reserva.hora_inicio, reserva.hora_fin)
            )
            if cursor.fetchone():
                raise ValidacionError(f"{MSG_TRASLAPE} (Conflicto con otra reserva existente)")

            # 3. Validar traslape con horarios de entrenamiento fijos
            dia_semana_nombre = DIA_POR_NUMERO[reserva.fecha.weekday()]
            cursor.execute(
                """
                SELECT codigoHorario FROM HORARIO
                WHERE espacio = %s AND diaSemana = %s
                  AND %s < horaFin AND horaInicio < %s
                """,
                (reserva.espacio, dia_semana_nombre, reserva.hora_inicio, reserva.hora_fin)
            )
            if cursor.fetchone():
                raise ValidacionError(f"{MSG_TRASLAPE} (Conflicto con horario fijo de entrenamiento del día {dia_semana_nombre})")

            sql = """
                INSERT INTO RESERVA (fecha, horaInicio, horaFin, miembro, espacio)
                VALUES (%s, %s, %s, %s, %s)
            """
            try:
                cursor.execute(sql, (
                    reserva.fecha, reserva.hora_inicio, reserva.hora_fin,
                    reserva.miembro, reserva.espacio
                ))
                return cursor.lastrowid
            except mysql.connector.Error as e:
                if e.errno == 1452:
                    raise ValidacionError("El socio o espacio deportivo no existe.")
                raise BaseDatosError(f"Error al registrar reserva: {e}")

    @staticmethod
    def listar_por_fecha(fecha_str: str) -> list:
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
    """Consultas SQL para la tabla ASISTENCIA."""

    @staticmethod
    def registrar(asistencia: Asistencia) -> int:
        with obtener_cursor() as cursor:
            if cursor is None:
                raise BaseDatosError("No hay conexión a la base de datos.")

            sql = """
                INSERT INTO ASISTENCIA (fecha, estadoAsistencia, miembro, horario)
                VALUES (%s, %s, %s, %s)
            """
            try:
                cursor.execute(sql, (
                    asistencia.fecha, asistencia.estado_asistencia,
                    asistencia.miembro, asistencia.horario
                ))
                return cursor.lastrowid
            except mysql.connector.Error as e:
                if e.errno == 1452:
                    raise ValidacionError("El socio o el horario de entrenamiento no existe.")
                raise BaseDatosError(f"Error al registrar asistencia: {e}")

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
