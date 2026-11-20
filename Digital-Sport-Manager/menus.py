"""
menus.py
Digital Sport Manager - Club Deportivo

Menús unificados de los 3 módulos del sistema:
  Módulo A: Personas y Equipos (RF-01, RF-05)
  Módulo B: Membresías, Pagos e Inscripciones (RF-04, RF-06, RF-07)
  Módulo C: Espacios, Horarios, Reservas y Asistencias (RF-02, RF-03, RF-08)
"""

from datetime import date
from modelos import (
    Miembro, Entrenador, Categoria, Equipo, calcular_edad,
    Membresia, Pago,
    Espacio_Deportivo, Material, Horario, Reserva, Asistencia,
    ValidacionError, BaseDatosError
)
from repositorios import (
    MiembroRepositorio, EntrenadorRepositorio,
    CategoriaRepositorio, EquipoRepositorio,
    TipoMembresiaRepositorio, MembresiaRepositorio,
    PagoRepositorio, ActividadRepositorio, InscripcionRepositorio,
    EspacioRepositorio, MaterialRepositorio, EspacioMaterialRepositorio,
    HorarioRepositorio, ReservaRepositorio, AsistenciaRepositorio
)

# Constantes locales
CONFIRMAR_SI = ("s", "si", "sí")
MSG_CONFIRMAR_BAJA = "¿Seguro que deseas dar de baja este registro? (s/n): "
MSG_OPCION_INVALIDA = "Opción no válida, intenta de nuevo."
METODOS_PAGO = ("efectivo", "tarjeta", "transferencia")
METODO_PAGO_EFECTIVO = "efectivo"
DIAS_SEMANA = ("lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo")
ASIST_PRESENTE = "presente"


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
                filas = MiembroRepositorio.listar()
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
                m = MiembroRepositorio.obtener(socio)
                if not m:
                    print("[!] No se encontró el socio.")
                elif m["estatus"] == "inactivo":
                    print("[!] Este miembro ya está inactivo (dado de baja).")
                else:
                    if input(MSG_CONFIRMAR_BAJA).strip().lower() in CONFIRMAR_SI:
                        if MiembroRepositorio.cambiar_estatus(socio, "inactivo"):
                            print("[OK] Miembro dado de baja (registro conservado como inactivo).")
                        else:
                            print("[!] No se pudo dar de baja al socio.")
                    else:
                        print("Operación cancelada.")

            elif op == "6":
                socio = int(input("Número de socio a reactivar: "))
                m = MiembroRepositorio.obtener(socio)
                if not m:
                    print("[!] No se encontró el socio.")
                elif m["estatus"] == "activo":
                    print("[!] Este miembro ya está activo.")
                else:
                    if MiembroRepositorio.cambiar_estatus(socio, "activo"):
                        print("[OK] Miembro reactivado.")
                    else:
                        print("[!] No se pudo reactivar al socio.")

            elif op == "0":
                break
            else:
                print(MSG_OPCION_INVALIDA)

        except ValidacionError as err:
            print(f"[!] Validación: {err}")
        except BaseDatosError as err:
            print(f"[!] Error de BD: {err}")
        except ValueError:
            print("[!] Validación: Debes ingresar un número válido (no puede estar vacío ni contener letras).")
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
                activos = input("¿Solo entrenadores activos? (s/n): ").strip().lower() in CONFIRMAR_SI
                filas = EntrenadorRepositorio.listar(solo_activos=activos)
                print(f"\n--- Listado de Entrenadores ({len(filas)}) ---")
                for t in filas:
                    print(f"  #{t['claveEntrenador']:<3} | {t['nombreCompleto']:<25} | Esp: {t['especialidad']:<12} | Equipos: {t['equipos']} | [{t['estatus'].upper()}]")

            elif op == "3":
                clave = int(input("Clave del entrenador a modificar: "))
                t = EntrenadorRepositorio.obtener(clave)
                if not t:
                    print("[!] Entrenador no encontrado.")
                    continue
                print(f"Modificando a: {t['nombre']} {t['primerApell']}")
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
                else:
                    print("[i] Sin cambios.")

            elif op == "4":
                clave = int(input("Clave del entrenador a dar de baja: "))
                t = EntrenadorRepositorio.obtener(clave)
                if not t:
                    print("[!] No se encontró el entrenador.")
                elif t["estatus"] == "inactivo":
                    print("[!] Este entrenador ya está inactivo (dado de baja).")
                else:
                    if input(MSG_CONFIRMAR_BAJA).strip().lower() in CONFIRMAR_SI:
                        if EntrenadorRepositorio.cambiar_estatus(clave, "inactivo"):
                            print("[OK] Entrenador marcado como inactivo.")
                        else:
                            print("[!] No se pudo dar de baja al entrenador.")
                    else:
                        print("Operación cancelada.")

            elif op == "5":
                clave = int(input("Clave del entrenador a reactivar: "))
                t = EntrenadorRepositorio.obtener(clave)
                if not t:
                    print("[!] No se encontró el entrenador.")
                elif t["estatus"] == "activo":
                    print("[!] Este entrenador ya está activo.")
                else:
                    if EntrenadorRepositorio.cambiar_estatus(clave, "activo"):
                        print("[OK] Entrenador reactivado.")
                    else:
                        print("[!] No se pudo reactivar al entrenador.")

            elif op == "0":
                break
            else:
                print(MSG_OPCION_INVALIDA)

        except ValidacionError as err:
            print(f"[!] Validación: {err}")
        except BaseDatosError as err:
            print(f"[!] Error de BD: {err}")
        except ValueError:
            print("[!] Validación: Debes ingresar un número válido (no puede estar vacío ni contener letras).")
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
                clave = input("Clave categoría (máx 5 letras, ej. JUVEN): ").strip().upper()
                nombre = input("Nombre categoría (ej. Juvenil): ").strip()
                if not clave:
                    raise ValueError("La clave de categoría no puede estar vacía.")
                if not nombre:
                    raise ValueError("El nombre de la categoría no puede estar vacío.")
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
                clave = input("Clave del equipo (máx 5 letras, ej. EQU09): ").strip().upper()
                nombre = input("Nombre del equipo: ").strip()
                cat = input("Clave de categoría: ").strip().upper()
                if not clave:
                    raise ValueError("La clave del equipo no puede estar vacía.")
                if not nombre:
                    raise ValueError("El nombre del equipo no puede estar vacío.")
                if not cat:
                    raise ValueError("La clave de categoría no puede estar vacía.")
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
                edad = calcular_edad(m["fechaNacimiento"])
                print(f"Edad del socio: {edad} años. Equipos disponibles para su rango de edad:")
                equipos_disp = EquipoRepositorio.equipos_para_edad(edad)
                if not equipos_disp:
                    print("  No hay equipos disponibles para este rango de edad.")
                    continue
                for eq in equipos_disp:
                    print(f"  [{eq['claveEquipo']}] {eq['nombreEquipo']} ({eq['nombreCategoria']})")
                nueva_clave = input("Clave del equipo a asignar: ").strip().upper()
                if not nueva_clave:
                    print("[!] Clave de equipo no puede estar vacía.")
                    continue
                if m.get("equipo") == nueva_clave:
                    print(f"[i] El socio ya pertenece al equipo '{nueva_clave}'.")
                    continue
                confirm = input(f"¿Confirmas asignar al socio #{socio} ({m['nombre']} {m['primerApell']}) al equipo '{nueva_clave}'? (s/n): ").strip().lower()
                if confirm not in CONFIRMAR_SI:
                    print("Asignación cancelada.")
                    continue
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
                print(MSG_OPCION_INVALIDA)

        except ValidacionError as err:
            print(f"[!] Validación: {err}")
        except BaseDatosError as err:
            print(f"[!] Error de BD: {err}")
        except ValueError:
            print("[!] Validación: Debes ingresar un número válido (no puede estar vacío ni contener letras).")
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
            print(MSG_OPCION_INVALIDA)


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

                if input("¿Deseas registrar el pago de esta membresía ahora? (s/n): ").strip().lower() in CONFIRMAR_SI:
                    tipo_info = TipoMembresiaRepositorio.obtener(tipo_clave)
                    costo = float(tipo_info["costo"])
                    print(f"Costo de la membresía: ${costo:.2f}")
                    metodo = input("Método de pago (efectivo/tarjeta/transferencia, Enter efectivo): ").strip().lower() or METODO_PAGO_EFECTIVO
                    if metodo not in METODOS_PAGO:
                        raise ValueError(f"Método de pago inválido: '{metodo}'. Válidos: {', '.join(METODOS_PAGO)}")

                    if metodo == METODO_PAGO_EFECTIVO:
                        recibido_str = input(f"Efectivo recibido (Total ${costo:.2f}): ").strip()
                        recibido = float(recibido_str) if recibido_str else costo
                        if recibido < costo:
                            raise ValueError(f"Monto insuficiente. El costo es ${costo:.2f} y se entregó ${recibido:.2f}.")
                        cambio = recibido - costo
                        print(f"Cambio: ${cambio:.2f}")
                    else:
                        recibido = costo
                        cambio = 0.0

                    p = Pago(fecha_pago=date.today(), monto=costo, metodo_pago=metodo, membresia=folio,
                             recibido=recibido, cambio=cambio)
                    folio_pago = PagoRepositorio.registrar_pago(p)
                    p.folio_pago = folio_pago
                    print("[OK] Pago registrado.")
                    print(p.generarComprobante())

            elif op == "2":
                filas = MembresiaRepositorio.listar()
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
                print(MSG_OPCION_INVALIDA)

        except ValidacionError as err:
            print(f"[!] Validación: {err}")
        except BaseDatosError as err:
            print(f"[!] Error de BD: {err}")
        except ValueError:
            print("[!] Validación: Debes ingresar un número válido (no puede estar vacío ni contener letras).")
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
                mem_info = MembresiaRepositorio.obtener(folio_m)
                if not mem_info:
                    print(f"[!] La membresía #{folio_m} no fue encontrada.")
                    continue

                costo = float(mem_info["costo"])
                print(f"Socio: #{mem_info['miembro']} - {mem_info['miembroNombre']}")
                print(f"Tipo: {mem_info['nombreTipo']} | Monto a pagar: ${costo:.2f}")

                metodo = input("Método de pago (efectivo/tarjeta/transferencia, Enter efectivo): ").strip().lower() or METODO_PAGO_EFECTIVO
                if metodo not in METODOS_PAGO:
                    raise ValueError(f"Método de pago inválido: '{metodo}'. Válidos: {', '.join(METODOS_PAGO)}")

                if metodo == METODO_PAGO_EFECTIVO:
                    recibido_str = input(f"Efectivo recibido (Total ${costo:.2f}): ").strip()
                    recibido = float(recibido_str) if recibido_str else costo
                    if recibido < costo:
                        raise ValueError(f"Monto insuficiente. El costo es ${costo:.2f} y se entregó ${recibido:.2f}.")
                    cambio = recibido - costo
                    print(f"Cambio: ${cambio:.2f}")
                else:
                    recibido = costo
                    cambio = 0.0

                p = Pago(fecha_pago=date.today(), monto=costo, metodo_pago=metodo, membresia=folio_m,
                         recibido=recibido, cambio=cambio)
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
                print(MSG_OPCION_INVALIDA)

        except ValidacionError as err:
            print(f"[!] Validación: {err}")
        except BaseDatosError as err:
            print(f"[!] Error de BD: {err}")
        except ValueError:
            print("[!] Validación: Debes ingresar un número válido (no puede estar vacío ni contener letras).")
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
                print(MSG_OPCION_INVALIDA)

        except ValidacionError as err:
            print(f"[!] Validación: {err}")
        except BaseDatosError as err:
            print(f"[!] Error de BD: {err}")
        except ValueError:
            print("[!] Validación: Debes ingresar un número válido (no puede estar vacío ni contener letras).")
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
            print(MSG_OPCION_INVALIDA)


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
                print(MSG_OPCION_INVALIDA)

        except ValidacionError as err:
            print(f"[!] Validación: {err}")
        except BaseDatosError as err:
            print(f"[!] Error de BD: {err}")
        except ValueError:
            print("[!] Validación: Debes ingresar un número válido (no puede estar vacío ni contener letras).")
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
                dia = input(f"Día de la semana ({', '.join(DIAS_SEMANA)}): ")
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
                print(MSG_OPCION_INVALIDA)

        except ValidacionError as err:
            print(f"[!] Validación: {err}")
        except BaseDatosError as err:
            print(f"[!] Error de BD: {err}")
        except ValueError:
            print("[!] Validación: Debes ingresar un número válido (no puede estar vacío ni contener letras).")
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
                print(MSG_OPCION_INVALIDA)

        except ValidacionError as err:
            print(f"[!] Validación: {err}")
        except BaseDatosError as err:
            print(f"[!] Error de BD: {err}")
        except ValueError:
            print("[!] Validación: Debes ingresar un número válido (no puede estar vacío ni contener letras).")
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
                estado_asist = input("Estado (presente/ausente, Enter presente): ").strip().lower() or ASIST_PRESENTE
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
                print(MSG_OPCION_INVALIDA)

        except ValidacionError as err:
            print(f"[!] Validación: {err}")
        except BaseDatosError as err:
            print(f"[!] Error de BD: {err}")
        except ValueError:
            print("[!] Validación: Debes ingresar un número válido (no puede estar vacío ni contener letras).")
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
            print(MSG_OPCION_INVALIDA)
