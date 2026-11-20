"""
menus/menu_a.py
Digital Sport Manager - Club Deportivo

Menú del Módulo A: Gestión de Personas y Equipos (RF-01, RF-05).
Estructurado por espacios independientes: Miembros, Entrenadores, Equipos y Categorías.
"""

import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import constantes as c
from modelos.personas import Miembro, Entrenador
from modelos.organizacion import Categoria, Equipo
from repositorios.repositorio_a import (
    MiembroRepositorio, EntrenadorRepositorio,
    CategoriaRepositorio, EquipoRepositorio
)


# ===========================================================================
# 1. ESPACIO DE MIEMBROS (ALUMNOS)
# ===========================================================================
def submenu_miembros():
    while True:
        print("\n" + "-" * 50)
        print("         GESTIÓN DE MIEMBROS (ALUMNOS)")
        print("-" * 50)
        print("  1. Registrar nuevo miembro")
        print("  2. Listar miembros")
        print("  3. Buscar miembro (por nombre o correo)")
        print("  4. Modificar datos de miembro")
        print("  5. Dar de baja miembro (inactivo)")
        print("  6. Reactivar miembro")
        print("  0. Volver")
        print("-" * 50)

        op = input("Elige una opción: ").strip()

        try:
            if op == "1":
                print("\n--- Registro de Nuevo Miembro ---")
                print("Equipos disponibles:")
                for eq in EquipoRepositorio.listar():
                    print(f"  [{eq['claveEquipo']}] {eq['nombreEquipo']} ({eq['nombreCategoria']}, {eq['edadMinima']}-{eq['edadMaxima']} años)")
                nombre = input("Nombre: ")
                p_apell = input("Primer apellido: ")
                s_apell = input("Segundo apellido (Enter si no tiene): ")
                tel = input("Teléfono: ")
                correo = input("Correo: ")
                fnac = input("Fecha nacimiento (AAAA-MM-DD): ")
                equipo = input("Clave de equipo: ")

                m = Miembro(nombre, p_apell, s_apell, tel, correo, fnac, equipo)
                nuevo_id = MiembroRepositorio.guardar(m)
                print(f"[OK] Miembro registrado con número de socio #{nuevo_id} (Edad calculada: {m.edad} años).")

            elif op == "2":
                activos = input("¿Solo socios activos? (s/n): ").strip().lower() in c.CONFIRMAR_SI
                filas = MiembroRepositorio.listar(solo_activos=activos)
                print(f"\n--- Listado de Miembros ({len(filas)}) ---")
                for m in filas:
                    print(f"  #{m['numeroSocio']:<3} | {m['nombreCompleto']:<25} | {m['edad']} años | Eq: {m['equipo']} | [{m['estatus'].upper()}]")

            elif op == "3":
                termino = input("Ingresa nombre, apellido o correo: ")
                filas = MiembroRepositorio.buscar(termino)
                print(f"\n--- Resultados ({len(filas)}) ---")
                for m in filas:
                    print(f"  #{m['numeroSocio']:<3} | {m['nombreCompleto']:<25} | {m['correo']} | Tel: {m['telefono']} | [{m['estatus'].upper()}]")

            elif op == "4":
                socio = int(input("Número de socio a modificar: "))
                m = MiembroRepositorio.obtener(socio)
                if not m:
                    print("[!] Miembro no encontrado.")
                    continue
                print(f"Modificando a: {m['nombre']} {m['primerApell']}")
                nombre = input(f"Nombre [{m['nombre']}]: ").strip()
                p_apell = input(f"Primer apellido [{m['primerApell']}]: ").strip()
                s_apell = input(f"Segundo apellido [{m['segApell'] or ''}]: ").strip()
                tel = input(f"Teléfono [{m['telefono']}]: ").strip()
                correo = input(f"Correo [{m['correo']}]: ").strip()

                datos = {}
                if nombre: datos["nombre"] = nombre
                if p_apell: datos["primerApell"] = p_apell
                if s_apell: datos["segApell"] = s_apell
                if tel: datos["telefono"] = tel
                if correo: datos["correo"] = correo

                if MiembroRepositorio.actualizar(socio, datos):
                    print("[OK] Datos actualizados.")
                else:
                    print("[i] Sin cambios.")

            elif op == "5":
                socio = int(input("Número de socio a dar de baja: "))
                if input(c.MSG_CONFIRMAR_BAJA).strip().lower() in c.CONFIRMAR_SI:
                    if MiembroRepositorio.cambiar_estatus(socio, c.ESTATUS_INACTIVO):
                        print("[OK] Miembro dado de baja (registro conservado como inactivo).")
                    else:
                        print("[!] No se encontró el socio.")

            elif op == "6":
                socio = int(input("Número de socio a reactivar: "))
                if MiembroRepositorio.cambiar_estatus(socio, c.ESTATUS_ACTIVO):
                    print("[OK] Miembro reactivado.")
                else:
                    print("[!] No se encontró el socio.")

            elif op == "0":
                break
            else:
                print(c.MSG_OPCION_INVALIDA)

        except ValueError as err:
            print(f"[!] Validación: {err}")
        except Exception as err:
            print(f"[!] Error: {err}")


# ===========================================================================
# 2. ESPACIO DE ENTRENADORES
# ===========================================================================
def submenu_entrenadores():
    while True:
        print("\n" + "-" * 50)
        print("         GESTIÓN DE ENTRENADORES")
        print("-" * 50)
        print("  1. Registrar nuevo entrenador")
        print("  2. Listar entrenadores")
        print("  3. Modificar datos de entrenador")
        print("  4. Dar de baja entrenador (inactivo)")
        print("  5. Reactivar entrenador")
        print("  0. Volver")
        print("-" * 50)

        op = input("Elige una opción: ").strip()

        try:
            if op == "1":
                print("\n--- Registro de Entrenador ---")
                nombre = input("Nombre: ")
                p_apell = input("Primer apellido: ")
                s_apell = input("Segundo apellido (Enter si no tiene): ")
                tel = input("Teléfono: ")
                correo = input("Correo: ")
                esp = input("Especialidad (Fútbol/Voleibol/Basquetbol): ")

                t = Entrenador(nombre, p_apell, s_apell, tel, correo, esp)
                clave = EntrenadorRepositorio.guardar(t)
                print(f"[OK] Entrenador registrado con clave #{clave}.")

            elif op == "2":
                activos = input("¿Solo entrenadores activos? (s/n): ").strip().lower() in c.CONFIRMAR_SI
                filas = EntrenadorRepositorio.listar(solo_activos=activos)
                print(f"\n--- Listado de Entrenadores ({len(filas)}) ---")
                for t in filas:
                    print(f"  #{t['claveEntrenador']:<3} | {t['nombreCompleto']:<25} | Esp: {t['especialidad']:<12} | Equipos: {t['equipos']} | [{t['estatus'].upper()}]")

            elif op == "3":
                clave = int(input("Clave del entrenador a modificar: "))
                nombre = input("Nuevo nombre (Enter dejar igual): ").strip()
                p_apell = input("Nuevo primer apellido (Enter dejar igual): ").strip()
                tel = input("Nuevo teléfono (Enter dejar igual): ").strip()
                esp = input("Nueva especialidad (Enter dejar igual): ").strip()

                datos = {}
                if nombre: datos["nombre"] = nombre
                if p_apell: datos["primerApell"] = p_apell
                if tel: datos["telefono"] = tel
                if esp: datos["especialidad"] = esp

                if EntrenadorRepositorio.actualizar(clave, datos):
                    print("[OK] Entrenador actualizado.")

            elif op == "4":
                clave = int(input("Clave del entrenador a dar de baja: "))
                if input(c.MSG_CONFIRMAR_BAJA).strip().lower() in c.CONFIRMAR_SI:
                    if EntrenadorRepositorio.cambiar_estatus(clave, c.ESTATUS_INACTIVO):
                        print("[OK] Entrenador marcado como inactivo.")

            elif op == "5":
                clave = int(input("Clave del entrenador a reactivar: "))
                if EntrenadorRepositorio.cambiar_estatus(clave, c.ESTATUS_ACTIVO):
                    print("[OK] Entrenador reactivado.")

            elif op == "0":
                break
            else:
                print(c.MSG_OPCION_INVALIDA)

        except ValueError as err:
            print(f"[!] Validación: {err}")
        except Exception as err:
            print(f"[!] Error: {err}")


# ===========================================================================
# 3. ESPACIO DE CATEGORÍAS Y EQUIPOS
# ===========================================================================
def submenu_equipos():
    while True:
        print("\n" + "-" * 50)
        print("      GESTIÓN DE CATEGORÍAS Y EQUIPOS")
        print("-" * 50)
        print("  1. Registrar categoría")
        print("  2. Listar categorías")
        print("  3. Registrar equipo")
        print("  4. Listar equipos")
        print("  5. Asignar miembro a un equipo (según edad)")
        print("  6. Cambiar entrenador de un equipo")
        print("  7. Consultar miembros de un equipo")
        print("  0. Volver")
        print("-" * 50)

        op = input("Elige una opción: ").strip()

        try:
            if op == "1":
                clave = input("Clave categoría (máx 5 letras, ej. JUVEN): ")
                nombre = input("Nombre categoría (ej. Juvenil): ")
                emin = int(input("Edad mínima: "))
                emax = int(input("Edad máxima: "))
                cat = Categoria(clave, nombre, emin, emax)
                if CategoriaRepositorio.guardar(cat):
                    print("[OK] Categoría creada con éxito.")

            elif op == "2":
                print("\n--- Categorías Registradas ---")
                for cat in CategoriaRepositorio.listar():
                    print(f"  [{cat['claveCategoria']}] {cat['nombreCategoria']:<15} ({cat['edadMinima']} a {cat['edadMaxima']} años)")

            elif op == "3":
                clave = input("Clave del equipo (máx 5 letras, ej. EQU09): ")
                nombre = input("Nombre del equipo: ")
                cat = input("Clave de categoría: ")
                ent = int(input("Clave de entrenador: "))
                eq = Equipo(clave, nombre, cat, ent)
                if EquipoRepositorio.guardar(eq):
                    print("[OK] Equipo registrado con éxito.")

            elif op == "4":
                print("\n--- Equipos Registrados ---")
                for eq in EquipoRepositorio.listar():
                    print(f"  [{eq['claveEquipo']}] {eq['nombreEquipo']:<28} | Cat: {eq['nombreCategoria']} ({eq['edadMinima']}-{eq['edadMaxima']}) | Ent: {eq['entrenadorNombre']} | Miembros: {eq['miembrosActivos']}")

            elif op == "5":
                socio = int(input("Número de socio: "))
                m = MiembroRepositorio.obtener(socio)
                if not m:
                    print("[!] Socio no encontrado.")
                    continue
                edad = Miembro.desde_dict(m).edad
                print(f"Edad del socio: {edad} años. Equipos disponibles para su rango de edad:")
                for eq in EquipoRepositorio.equipos_para_edad(edad):
                    print(f"  [{eq['claveEquipo']}] {eq['nombreEquipo']} ({eq['nombreCategoria']})")
                nueva_clave = input("Clave del equipo a asignar: ")
                if EquipoRepositorio.asignar_miembro(socio, nueva_clave):
                    print("[OK] Socio asignado exitosamente al equipo.")

            elif op == "6":
                eq_clave = input("Clave del equipo: ")
                ent_clave = int(input("Clave del nuevo entrenador: "))
                if EquipoRepositorio.cambiar_entrenador(eq_clave, ent_clave):
                    print("[OK] Entrenador del equipo actualizado.")

            elif op == "7":
                busq = input("Nombre o clave del equipo: ")
                filas = EquipoRepositorio.miembros_de(busq)
                print(f"\n--- Miembros del equipo ({len(filas)}) ---")
                for f in filas:
                    print(f"  #{f['numeroSocio']:<3} | {f['miembro']:<25} | {f['edad']} años | [{f['estatus'].upper()}]")

            elif op == "0":
                break
            else:
                print(c.MSG_OPCION_INVALIDA)

        except ValueError as err:
            print(f"[!] Validación: {err}")
        except Exception as err:
            print(f"[!] Error: {err}")


# ===========================================================================
# MENÚ PRINCIPAL DEL MÓDULO A
# ===========================================================================
def menu_modulo_a():
    while True:
        print("\n" + "=" * 55)
        print("          MÓDULO A: PERSONAS Y EQUIPOS")
        print("=" * 55)
        print("  1. Gestión de Miembros (Alumnos)")
        print("  2. Gestión de Entrenadores")
        print("  3. Gestión de Categorías y Equipos")
        print("  0. Volver al menú principal")
        print("=" * 55)

        op = input("Elige un espacio de gestión: ").strip()

        if op == "1":
            submenu_miembros()
        elif op == "2":
            submenu_entrenadores()
        elif op == "3":
            submenu_equipos()
        elif op == "0":
            break
        else:
            print(c.MSG_OPCION_INVALIDA)


if __name__ == "__main__":
    menu_modulo_a()
