"""
main.py
Digital Sport Manager - Club Deportivo

Menú Principal de Integración del Sistema.
Conecta los Módulos A, B y C con la base de datos MySQL.
"""

import os
from db.conexion import probar_conexion, ejecutar_script_sql, obtener_cursor
from menus import menu_modulo_a, menu_modulo_b, menu_modulo_c


def resetear_base_de_datos():
    """Ejecuta schema.sql y seed.sql para inicializar o restaurar la base de datos."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    schema_path = os.path.join(base_dir, "db", "schema.sql")
    seed_path = os.path.join(base_dir, "db", "seed.sql")

    print("\n[!] Se reconstruirán las tablas y se sembrarán los datos iniciales.")
    confirm = input("¿Estás seguro de continuar? (s/n): ").strip().lower()
    if confirm not in ("s", "si", "sí"):
        print("Operación cancelada.")
        return

    print("-> Ejecutando schema.sql...")
    if ejecutar_script_sql(schema_path):
        print("[OK] Esquema de tablas creado con éxito.")
    else:
        print("[X] Falló la creación del esquema.")
        return

    print("-> Ejecutando seed.sql (datos iniciales corregidos)...")
    if ejecutar_script_sql(seed_path):
        print("[OK] Datos iniciales sembrados con éxito en las 16 tablas.")
    else:
        print("[X] Falló la inserción de datos iniciales.")


def ver_resumen_sistema():
    """Muestra un resumen estadístico de la base de datos."""
    with obtener_cursor() as cursor:
        if cursor is None:
            print("[X] No hay conexión con la base de datos.")
            return

        print("\n" + "=" * 50)
        print("           RESUMEN DEL CLUB DEPORTIVO            ")
        print("=" * 50)
        consultas = [
            ("Miembros registrados", "SELECT COUNT(*) AS total FROM MIEMBRO"),
            ("Miembros activos", "SELECT COUNT(*) AS total FROM MIEMBRO WHERE estatus = 'activo'"),
            ("Entrenadores activos", "SELECT COUNT(*) AS total FROM ENTRENADOR WHERE estatus = 'activo'"),
            ("Equipos formados", "SELECT COUNT(*) AS total FROM EQUIPO"),
            ("Membresías vigentes", "SELECT COUNT(*) AS total FROM MEMBRESIA WHERE estado = 'vigente'"),
            ("Membresías por vencer (<= 7 días)", "SELECT COUNT(*) AS total FROM MEMBRESIA WHERE estado = 'por vencer'"),
            ("Espacios disponibles", "SELECT COUNT(*) AS total FROM ESPACIO_DEPORTIVO WHERE estado = 'disponible'"),
            ("Inscripciones activas", "SELECT COUNT(*) AS total FROM INSCRIPCION WHERE estado = 'activa'"),
            ("Reservas programadas", "SELECT COUNT(*) AS total FROM RESERVA WHERE fecha >= CURDATE()"),
        ]

        for etiqueta, sql in consultas:
            try:
                cursor.execute(sql)
                total = cursor.fetchone()["total"]
                print(f"  • {etiqueta:<36}: {total}")
            except Exception as e:
                print(f"  • {etiqueta:<36}: Error ({e})")
        print("=" * 50)


def main():
    while True:
        print("\n" + "=" * 55)
        print("          DIGITAL SPORT MANAGER (DSM)")
        print("                Club Deportivo                ")
        print("=" * 55)
        print("  1: Personas y Equipos")
        print("  2: Membresías, Pagos e Inscripciones")
        print("  3: Espacios, Horarios y Asistencias")
        print("  4: Resumen del sistema")
        print("  0. Salir")
        print("=" * 55)

        opcion = input("Selecciona una opción: ").strip()

        if opcion == "1":
            menu_modulo_a()
        elif opcion == "2":
            menu_modulo_b()
        elif opcion == "3":
            menu_modulo_c()
        elif opcion == "4":
            ver_resumen_sistema()
        elif opcion == "0":
            print("\n¡Gracias por utilizar Digital Sport Manager!")
            break
        else:
            print("\nOpción inválida. Intenta nuevamente.")
if __name__ == "__main__":
    main()