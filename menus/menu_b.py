"""
menus/menu_b.py
Digital Sport Manager - Club Deportivo

Menú del Módulo B: Membresías, Pagos e Inscripciones (RF-04, RF-06, RF-07).
Estructurado por espacios independientes: Membresías, Pagos, Actividades e Inscripciones.
"""

from datetime import date
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import constantes as c
from modelos.membresias import Membresia, Pago
from repositorios.repositorio_b import (
    TipoMembresiaRepositorio, MembresiaRepositorio,
    PagoRepositorio, ActividadRepositorio, InscripcionRepositorio
)


# ===========================================================================
# 1. ESPACIO DE MEMBRESÍAS
# ===========================================================================
def submenu_membresias():
    MembresiaRepositorio.actualizar_estados()
    while True:
        print("\n" + "-" * 50)
        print("            GESTIÓN DE MEMBRESÍAS")
        print("-" * 50)
        print("  1. Registrar nueva membresía")
        print("  2. Listar membresías")
        print("  3. Alertas: Membresías por vencer (<= 7 días)")
        print("  4. Renovar membresía")
        print("  0. Volver")
        print("-" * 50)

        op = input("Elige una opción: ").strip()

        try:
            if op == "1":
                print("\n--- Registrar Membresía ---")
                print("Tipos de membresía disponibles:")
                for t in TipoMembresiaRepositorio.listar():
                    print(f"  [{t['claveTipoMembresia']}] {t['nombreTipo']:<10} | Costo: ${t['costo']:.2f} | Duración: {t['duracionDias']} días")
                socio = int(input("Número de socio: "))
                tipo_clave = input("Clave de tipo de membresía: ").strip().upper()
                finicio = input(f"Fecha de inicio (Enter hoy {date.today()}): ").strip() or str(date.today())

                m = Membresia(fecha_inicio=finicio, tipo_membresia=tipo_clave, miembro=socio)
                folio = MembresiaRepositorio.guardar(m)
                print(f"[OK] Membresía registrada con Folio #{folio}.")

                if input("¿Deseas registrar el pago de esta membresía ahora? (s/n): ").strip().lower() in c.CONFIRMAR_SI:
                    tipo_info = TipoMembresiaRepositorio.obtener(tipo_clave)
                    monto = float(input(f"Monto a pagar (Sugerido ${tipo_info['costo']:.2f}): ") or tipo_info["costo"])
                    metodo = input("Método de pago (efectivo/tarjeta/transferencia): ")
                    p = Pago(fecha_pago=date.today(), monto=monto, metodo_pago=metodo, membresia=folio)
                    folio_pago = PagoRepositorio.registrar_pago(p)
                    p.folio_pago = folio_pago
                    print("[OK] Pago registrado.")
                    print(p.generarComprobante())

            elif op == "2":
                vig = input("¿Solo vigentes o por vencer? (s/n): ").strip().lower() in c.CONFIRMAR_SI
                filas = MembresiaRepositorio.listar(solo_vigentes=vig)
                print(f"\n--- Listado de Membresías ({len(filas)}) ---")
                for f in filas:
                    print(f"  Folio #{f['folioMembresia']:<3} | Socio #{f['miembro']} ({f['miembroNombre']}) | {f['nombreTipo']:<8} | {f['fechaInicio']} al {f['fechaFin']} | [{f['estado'].upper()}]")

            elif op == "3":
                filas = MembresiaRepositorio.listar_por_vencer()
                print(f"\n--- [ALERTA RF-06] Membresías Próximas a Vencer ({len(filas)}) ---")
                if not filas:
                    print("  No hay membresías por vencer en los próximos 7 días.")
                for f in filas:
                    print(f"  [!] Folio #{f['folioMembresia']:<3} | Socio #{f['miembro']} ({f['miembroNombre']}) | Vence en: {f['diasRestantes']} días ({f['fechaFin']}) | Tel: {f['telefono']}")

            elif op == "4":
                folio = int(input("Folio de la membresía a renovar: "))
                if MembresiaRepositorio.renovar(folio):
                    print(f"[OK] Membresía #{folio} renovada exitosamente.")
                else:
                    print("[!] No se pudo renovar la membresía.")

            elif op == "0":
                break
            else:
                print(c.MSG_OPCION_INVALIDA)

        except ValueError as err:
            print(f"[!] Validación: {err}")
        except Exception as err:
            print(f"[!] Error: {err}")


# ===========================================================================
# 2. ESPACIO DE PAGOS
# ===========================================================================
def submenu_pagos():
    while True:
        print("\n" + "-" * 50)
        print("               GESTIÓN DE PAGOS")
        print("-" * 50)
        print("  1. Registrar pago de membresía")
        print("  2. Historial de pagos")
        print("  0. Volver")
        print("-" * 50)

        op = input("Elige una opción: ").strip()

        try:
            if op == "1":
                print("\n--- Registrar Pago ---")
                folio_m = int(input("Folio de membresía a pagar: "))
                monto = float(input("Monto pagado ($): "))
                metodo = input("Método de pago (efectivo/tarjeta/transferencia): ")
                p = Pago(fecha_pago=date.today(), monto=monto, metodo_pago=metodo, membresia=folio_m)
                fol_p = PagoRepositorio.registrar_pago(p)
                p.folio_pago = fol_p
                print("[OK] Pago procesado exitosamente.")
                print(p.generarComprobante())

            elif op == "2":
                filas = PagoRepositorio.historial()
                print(f"\n--- Historial de Pagos ({len(filas)}) ---")
                for f in filas:
                    print(f"  Pago #{f['folioPago']:<3} | Membresía #{f['membresia']:<3} ({f['miembroNombre']}) | Fecha: {f['fechaPago']} | ${f['monto']:<8.2f} | {f['metodoPago'].capitalize()} | [{f['estadoPago'].upper()}]")

            elif op == "0":
                break
            else:
                print(c.MSG_OPCION_INVALIDA)

        except ValueError as err:
            print(f"[!] Validación: {err}")
        except Exception as err:
            print(f"[!] Error: {err}")


# ===========================================================================
# 3. ESPACIO DE ACTIVIDADES E INSCRIPCIONES
# ===========================================================================
def submenu_inscripciones():
    while True:
        print("\n" + "-" * 50)
        print("     GESTIÓN DE ACTIVIDADES E INSCRIPCIONES")
        print("-" * 50)
        print("  1. Consultar actividades y cupos")
        print("  2. Inscribir miembro a actividad (RF-07)")
        print("  3. Dar de baja inscripción activa")
        print("  4. Consultar miembros por actividad")
        print("  5. Ver historial de inscripciones de un miembro")
        print("  0. Volver")
        print("-" * 50)

        op = input("Elige una opción: ").strip()

        try:
            if op == "1":
                filas = ActividadRepositorio.listar()
                print("\n--- Actividades Deportivas y Cupo ---")
                for a in filas:
                    disp = a["cupoMaximo"] - (a["inscritosActivos"] or 0)
                    print(f"  [{a['codigoActividad']}] {a['nombre']:<15} | Inscritos: {a['inscritosActivos']}/{a['cupoMaximo']} | Cupo libre: {disp}")

            elif op == "2":
                print("\n--- Inscribir a Actividad ---")
                socio = int(input("Número de socio: "))
                act = input("Código de actividad (FUTBO/BASQU/VOLEI): ")
                folio_i = InscripcionRepositorio.inscribir(socio, act)
                print(f"[OK] Miembro #{socio} inscrito exitosamente en {act.upper()} (Folio #{folio_i}).")

            elif op == "3":
                socio = int(input("Número de socio para dar de baja: "))
                if InscripcionRepositorio.dar_de_baja(socio):
                    print(f"[OK] Inscripción activa del socio #{socio} dada de baja.")
                else:
                    print("[!] No se encontró ninguna inscripción activa para este socio.")

            elif op == "4":
                busq = input("Código o nombre de actividad: ")
                filas = InscripcionRepositorio.miembros_por_actividad(busq)
                print(f"\n--- Miembros inscritos ({len(filas)}) ---")
                for f in filas:
                    print(f"  Socio #{f['numeroSocio']:<3} | {f['miembro']:<25} | Desde: {f['fechaInscripcion']} | [{f['estado'].upper()}]")

            elif op == "5":
                socio = int(input("Número de socio: "))
                filas = InscripcionRepositorio.historial_socio(socio)
                print(f"\n--- Historial de Inscripciones del Socio #{socio} ({len(filas)}) ---")
                for f in filas:
                    fb = f" - Baja: {f['fechaBaja']}" if f['fechaBaja'] else ""
                    print(f"  Folio #{f['folioInscripcion']:<3} | {f['actividadNombre']:<15} | Fecha: {f['fechaInscripcion']}{fb} | [{f['estado'].upper()}]")

            elif op == "0":
                break
            else:
                print(c.MSG_OPCION_INVALIDA)

        except ValueError as err:
            print(f"[!] Validación: {err}")
        except Exception as err:
            print(f"[!] Error: {err}")


# ===========================================================================
# MENÚ PRINCIPAL DEL MÓDULO B
# ===========================================================================
def menu_modulo_b():
    while True:
        print("\n" + "=" * 55)
        print("  MÓDULO B: MEMBRESÍAS, PAGOS E INSCRIPCIONES")
        print("=" * 55)
        print("  1. Gestión de Membresías")
        print("  2. Gestión de Pagos")
        print("  3. Gestión de Actividades e Inscripciones")
        print("  0. Volver al menú principal")
        print("=" * 55)

        op = input("Elige un espacio de gestión: ").strip()

        if op == "1":
            submenu_membresias()
        elif op == "2":
            submenu_pagos()
        elif op == "3":
            submenu_inscripciones()
        elif op == "0":
            break
        else:
            print(c.MSG_OPCION_INVALIDA)


if __name__ == "__main__":
    menu_modulo_b()
