"""
menus/menu_c.py
Digital Sport Manager - Club Deportivo

Menú del Módulo C: Espacios Deportivos, Horarios, Reservas y Asistencias (RF-02, RF-03, RF-08).
Estructurado por espacios independientes: Espacios y Materiales, Horarios, Reservas, y Asistencias.
"""

from datetime import date
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import constantes as c
from modelos.espacios import Espacio_Deportivo, Material
from modelos.agenda import Horario, Reserva, Asistencia
from repositorios.repositorio_c import (
    EspacioRepositorio, MaterialRepositorio, EspacioMaterialRepositorio,
    HorarioRepositorio, ReservaRepositorio, AsistenciaRepositorio
)


# ===========================================================================
# 1. ESPACIO DE ESPACIOS DEPORTIVOS Y MATERIALES
# ===========================================================================
def submenu_espacios_materiales():
    while True:
        print("\n" + "-" * 50)
        print("      GESTIÓN DE ESPACIOS Y MATERIALES (RF-02)")
        print("-" * 50)
        print("  1. Registrar espacio deportivo")
        print("  2. Listar espacios deportivos")
        print("  3. Cambiar estado de espacio (disponible/mantenimiento)")
        print("  4. Registrar material deportivo")
        print("  5. Listar inventario de materiales")
        print("  6. Asignar material requerido a un espacio")
        print("  0. Volver")
        print("-" * 50)

        op = input("Elige una opción: ").strip()

        try:
            if op == "1":
                codigo = input("Código espacio (máx 5, ej. CAN05): ")
                nombre = input("Nombre (ej. Cancha de Pádel): ")
                tipo = input("Tipo (Exterior/Interior/Duela): ")
                cap = int(input("Capacidad de personas: "))
                esp = Espacio_Deportivo(codigo, nombre, tipo, cap)
                if EspacioRepositorio.guardar(esp):
                    print(f"[OK] Espacio '{nombre}' registrado exitosamente.")

            elif op == "2":
                filas = EspacioRepositorio.listar()
                print(f"\n--- Espacios Deportivos ({len(filas)}) ---")
                for e in filas:
                    print(f"  [{e['codigoEspacio']}] {e['nombreEspacio']:<28} | {e['tipo']:<10} | Cap: {e['capacidad']:<3} | [{e['estado'].upper()}]")

            elif op == "3":
                cod = input("Código del espacio a modificar: ")
                nest = input("Nuevo estado (disponible/mantenimiento): ")
                if EspacioRepositorio.cambiar_estado(cod, nest):
                    print("[OK] Estado del espacio actualizado.")

            elif op == "4":
                codigo = input("Código material (máx 5, ej. RED02): ")
                nombre = input("Nombre del material: ")
                cant = int(input("Cantidad total de piezas: "))
                est = input("Estado (bueno/regular/dañado): ")
                mat = Material(codigo, nombre, cant, est)
                if MaterialRepositorio.guardar(mat):
                    print(f"[OK] Material '{nombre}' registrado.")

            elif op == "5":
                filas = MaterialRepositorio.listar()
                print(f"\n--- Inventario de Materiales ({len(filas)}) ---")
                for m in filas:
                    print(f"  [{m['codigoMaterial']}] {m['nombreMaterial']:<25} | Total: {m['cantidadTotal']:<4} | [{m['estado'].upper()}]")

            elif op == "6":
                esp = input("Código del espacio (ej. CAN01): ")
                mat = input("Código del material (ej. BALFU): ")
                cant = int(input("Cantidad requerida por el espacio: "))
                if EspacioMaterialRepositorio.asignar(esp, mat, cant):
                    print("[OK] Requerimiento de material asignado al espacio.")

            elif op == "0":
                break
            else:
                print(c.MSG_OPCION_INVALIDA)

        except ValueError as err:
            print(f"[!] Validación: {err}")
        except Exception as err:
            print(f"[!] Error: {err}")


# ===========================================================================
# 2. ESPACIO DE HORARIOS DE ENTRENAMIENTO
# ===========================================================================
def submenu_horarios():
    while True:
        print("\n" + "-" * 50)
        print("    GESTIÓN DE HORARIOS DE ENTRENAMIENTO (RF-03)")
        print("-" * 50)
        print("  1. Crear horario semanal (valida traslapes)")
        print("  2. Listar horarios semanales")
        print("  3. Asignar equipo a un horario")
        print("  4. Consultar horarios de un equipo")
        print("  0. Volver")
        print("-" * 50)

        op = input("Elige una opción: ").strip()

        try:
            if op == "1":
                print("\n--- Crear Horario Semanal ---")
                dia = input(f"Día de la semana ({', '.join(c.DIAS_SEMANA)}): ")
                hini = input("Hora inicio (HH:MM): ")
                hfin = input("Hora fin (HH:MM): ")
                act = input("Código de actividad (FUTBO/BASQU/VOLEI): ")
                esp = input("Código de espacio (ej. CAN01): ")

                h = Horario(dia, hini, hfin, act, esp)
                codigo_h = HorarioRepositorio.guardar(h)
                print(f"[OK] Horario #{codigo_h} programado exitosamente sin traslapes.")

            elif op == "2":
                filas = HorarioRepositorio.listar()
                print(f"\n--- Horarios Semanales ({len(filas)}) ---")
                for h in filas:
                    print(f"  Horario #{h['codigoHorario']:<2} | {h['diaSemana'].capitalize():<10} | {h['horaInicio']} - {h['horaFin']} | Act: {h['actividadNombre']:<12} | Esp: {h['nombreEspacio']}")

            elif op == "3":
                eq = input("Clave del equipo: ")
                h_id = int(input("Código del horario: "))
                if HorarioRepositorio.asignar_equipo(eq, h_id):
                    print(f"[OK] Equipo {eq} asignado al horario #{h_id}.")
                else:
                    print("[i] La asignación ya existía o el equipo no existe.")

            elif op == "4":
                busq = input("Nombre o clave del equipo: ")
                filas = HorarioRepositorio.listar_por_equipo(busq)
                print(f"\n--- Horarios de entrenamiento ({len(filas)}) ---")
                for f in filas:
                    print(f"  [{f['codigoHorario']}] {f['diaSemana'].capitalize():<10} | {f['horaInicio']} a {f['horaFin']} | {f['nombreEspacio']} | {f['actividadNombre']}")

            elif op == "0":
                break
            else:
                print(c.MSG_OPCION_INVALIDA)

        except ValueError as err:
            print(f"[!] Validación: {err}")
        except Exception as err:
            print(f"[!] Error: {err}")


# ===========================================================================
# 3. ESPACIO DE RESERVAS DE ESPACIOS
# ===========================================================================
def submenu_reservas():
    while True:
        print("\n" + "-" * 50)
        print("        GESTIÓN DE RESERVAS DE ESPACIOS")
        print("-" * 50)
        print("  1. Registrar reserva (con validación anti-traslape)")
        print("  2. Consultar reservas por fecha")
        print("  3. Cancelar reserva por nombre del socio")
        print("  0. Volver")
        print("-" * 50)

        op = input("Elige una opción: ").strip()

        try:
            if op == "1":
                print("\n--- Registrar Reserva ---")
                fecha_res = input(f"Fecha de reserva (AAAA-MM-DD, Enter hoy {date.today()}): ").strip() or str(date.today())
                hini = input("Hora inicio (HH:MM): ")
                hfin = input("Hora fin (HH:MM): ")
                socio = int(input("Número de socio: "))
                esp = input("Código del espacio a reservar (ej. CAN01): ")

                r = Reserva(fecha_res, hini, hfin, socio, esp)
                num = ReservaRepositorio.crear_reserva(r)
                print(f"[OK] ¡Reserva confirmada con éxito! Folio #{num}.")

            elif op == "2":
                fecha_busq = input(f"Fecha a consultar (AAAA-MM-DD, Enter hoy {date.today()}): ").strip() or str(date.today())
                filas = ReservaRepositorio.listar_por_fecha(fecha_busq)
                print(f"\n--- Reservas del día {fecha_busq} ({len(filas)}) ---")
                if not filas:
                    print("  No hay reservas para esta fecha.")
                for r in filas:
                    print(f"  Reserva #{r['numReserva']:<2} | {r['horaInicio']} - {r['horaFin']} | {r['nombreEspacio']:<25} | Socio: {r['miembro']}")

            elif op == "3":
                nombre = input("Nombre o apellido del socio: ")
                if ReservaRepositorio.cancelar_por_nombre(nombre):
                    print(f"[OK] Reservas asociadas a '{nombre}' canceladas exitosamente.")
                else:
                    print("[i] No se encontraron reservas para ese socio.")

            elif op == "0":
                break
            else:
                print(c.MSG_OPCION_INVALIDA)

        except ValueError as err:
            print(f"[!] Validación: {err}")
        except Exception as err:
            print(f"[!] Error: {err}")


# ===========================================================================
# 4. ESPACIO DE ASISTENCIAS
# ===========================================================================
def submenu_asistencias():
    while True:
        print("\n" + "-" * 50)
        print("        CONTROL DE ASISTENCIAS (RF-08)")
        print("-" * 50)
        print("  1. Registrar asistencia a entrenamiento")
        print("  2. Consultar historial de asistencia de un socio")
        print("  0. Volver")
        print("-" * 50)

        op = input("Elige una opción: ").strip()

        try:
            if op == "1":
                print("\n--- Registrar Asistencia ---")
                socio = int(input("Número de socio: "))
                horario_id = int(input("Código de horario de entrenamiento: "))
                estado_asist = input("Estado (presente/ausente, Enter presente): ").strip().lower() or c.ASIST_PRESENTE
                fecha_asist = input(f"Fecha (AAAA-MM-DD, Enter hoy {date.today()}): ").strip() or str(date.today())

                a = Asistencia(socio, horario_id, estado_asist, fecha_asist)
                folio_a = AsistenciaRepositorio.registrar(a)
                print(f"[OK] Asistencia registrada con Folio #{folio_a}.")

            elif op == "2":
                socio = int(input("Número de socio: "))
                filas = AsistenciaRepositorio.historial_miembro(socio)
                print(f"\n--- Historial de Asistencia del Socio #{socio} ({len(filas)}) ---")
                if not filas:
                    print("  Sin registros de asistencia.")
                for a in filas:
                    print(f"  Folio #{a['folioAsistencia']:<2} | {a['fecha']} ({a['diaSemana'].capitalize()}) | {a['horaInicio']}-{a['horaFin']} | {a['actividadNombre']:<12} | [{a['estadoAsistencia'].upper()}]")

            elif op == "0":
                break
            else:
                print(c.MSG_OPCION_INVALIDA)

        except ValueError as err:
            print(f"[!] Validación: {err}")
        except Exception as err:
            print(f"[!] Error: {err}")


# ===========================================================================
# MENÚ PRINCIPAL DEL MÓDULO C
# ===========================================================================
def menu_modulo_c():
    while True:
        print("\n" + "=" * 55)
        print("  MÓDULO C: ESPACIOS, HORARIOS Y ASISTENCIAS")
        print("=" * 55)
        print("  1. Espacios Deportivos y Materiales")
        print("  2. Horarios de Entrenamiento")
        print("  3. Reservas de Espacios")
        print("  4. Control de Asistencias")
        print("  0. Volver al menú principal")
        print("=" * 55)

        op = input("Elige un espacio de gestión: ").strip()

        if op == "1":
            submenu_espacios_materiales()
        elif op == "2":
            submenu_horarios()
        elif op == "3":
            submenu_reservas()
        elif op == "4":
            submenu_asistencias()
        elif op == "0":
            break
        else:
            print(c.MSG_OPCION_INVALIDA)


if __name__ == "__main__":
    menu_modulo_c()
