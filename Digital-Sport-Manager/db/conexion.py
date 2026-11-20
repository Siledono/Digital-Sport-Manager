"""
db/conexion.py
Digital Sport Manager - Club Deportivo

Gestor centralizado de conexiones y transacciones con MySQL.
"""

import os
from contextlib import contextmanager
import mysql.connector
from mysql.connector import Error

# Configuración de conexión a MySQL
DB_CONFIG = {
    "host": os.getenv("DSM_DB_HOST", "localhost"),
    "port": int(os.getenv("DSM_DB_PORT", "3306")),
    "user": os.getenv("DSM_DB_USER", "root"),
    "password": os.getenv("DSM_DB_PASSWORD", ""),
    "database": os.getenv("DSM_DB_NAME", "digitalsportmanager"),
}


def conectar(base_datos: str = None):
    """Crea y devuelve una conexión activa a MySQL."""
    config = dict(DB_CONFIG)
    if base_datos is not None:
        config["database"] = base_datos
    try:
        conexion = mysql.connector.connect(**config)
        return conexion
    except Error as e:
        print(f"\n[Error de Conexión a MySQL]: {e}")
        print("Verifica que MySQL esté encendido (ej. XAMPP) y la BD 'digitalsportmanager' exista.")
        return None


@contextmanager
def obtener_cursor(diccionario=True, auto_commit=True):
    """
    Gestor de contexto seguro para transacciones SQL.
    Abre conexión, entrega cursor y cierra adecuadamente con commit/rollback.
    """
    conexion = conectar()
    if conexion is None:
        yield None
        return

    cursor = conexion.cursor(dictionary=diccionario)
    try:
        yield cursor
        if auto_commit:
            conexion.commit()
    except Error as e:
        conexion.rollback()
        raise
    finally:
        cursor.close()
        conexion.close()


def probar_conexion():
    """Verifica si la base de datos responde y muestra el conteo de tablas."""
    with obtener_cursor() as cursor:
        if cursor is None:
            return False
        cursor.execute("SHOW TABLES;")
        tablas = cursor.fetchall()
        print(f"[OK] Conexión exitosa a '{DB_CONFIG['database']}'. Tablas detectadas: {len(tablas)}")
        return True


def ejecutar_script_sql(ruta_archivo: str):
    """Ejecuta un archivo de sentencias SQL (como schema.sql o seed.sql)."""
    if not os.path.exists(ruta_archivo):
        raise FileNotFoundError(f"No se encontró el archivo: {ruta_archivo}")

    with open(ruta_archivo, "r", encoding="utf-8") as f:
        contenido = f.read()

    conexion = conectar()
    if conexion is None:
        return False

    cursor = conexion.cursor()
    try:
        # mysql.connector permite multi=True
        for statement in cursor.execute(contenido, multi=True):
            pass
        conexion.commit()
        return True
    except Error as e:
        conexion.rollback()
        print(f"Error al ejecutar script SQL {ruta_archivo}: {e}")
        return False
    finally:
        cursor.close()
        conexion.close()


if __name__ == "__main__":
    probar_conexion()
