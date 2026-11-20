"""
modelos.py
Digital Sport Manager - Club Deportivo

Definición de Clases y Entidades del Sistema según los fundamentos de POO:
- Abstracción y Encapsulamiento
- Herencia (Persona -> Miembro, Entrenador)
- Polimorfismo (mostrarInformacion)
- Excepciones personalizadas
"""

from datetime import date, datetime, time, timedelta

# Formatos y valores válidos
FORMATO_FECHA = "%Y-%m-%d"
FORMATO_HORA = "%H:%M"
FORMATO_HORA_BD = "%H:%M:%S"

ESTATUS_ACTIVO = "activo"
ESTATUS_INACTIVO = "inactivo"
ESTATUS_VALIDOS = (ESTATUS_ACTIVO, ESTATUS_INACTIVO)

ESTADO_MEMB_VIGENTE = "vigente"
ESTADO_MEMB_POR_VENCER = "por vencer"
ESTADO_MEMB_VENCIDA = "vencida"
DIAS_POR_VENCER = 7

ESTADO_PAGO_PAGADO = "pagado"
ESTADO_PAGO_PENDIENTE = "pendiente"
ESTADOS_PAGO = (ESTADO_PAGO_PAGADO, ESTADO_PAGO_PENDIENTE)
METODO_PAGO_EFECTIVO = "efectivo"
METODOS_PAGO = ("efectivo", "tarjeta", "transferencia")

ESTADO_INSCR_ACTIVA = "activa"
ESTADO_INSCR_FINALIZADA = "finalizada"
ESTADOS_INSCRIPCION = (ESTADO_INSCR_ACTIVA, ESTADO_INSCR_FINALIZADA)

ESTADO_ESPACIO_DISPONIBLE = "disponible"
ESTADO_ESPACIO_MANTENIMIENTO = "mantenimiento"
ESTADOS_ESPACIO = (ESTADO_ESPACIO_DISPONIBLE, ESTADO_ESPACIO_MANTENIMIENTO)

ESTADO_MATERIAL_BUENO = "bueno"
ESTADOS_MATERIAL = ("bueno", "regular", "dañado")

ASIST_PRESENTE = "presente"
ESTADOS_ASISTENCIA = (ASIST_PRESENTE, "ausente")

DIAS_SEMANA = (
    "lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"
)
DIA_POR_NUMERO = {i: dia for i, dia in enumerate(DIAS_SEMANA)}


# ===========================================================================
# Excepciones personalizadas (Control de Excepciones visto en clase)
# ===========================================================================
class ClubDeportivoError(Exception):
    """Clase base de excepciones del sistema."""
    pass


class ValidacionError(ClubDeportivoError):
    """Lanzada cuando un dato de entrada no cumple con las reglas."""
    pass


class BaseDatosError(ClubDeportivoError):
    """Lanzada para fallas relacionadas con la base de datos."""
    pass


# ===========================================================================
# Funciones auxiliares simples
# ===========================================================================
def calcular_edad(fecha_nacimiento, hoy: date = None) -> int:
    """Calcula la edad cumplida en años a partir de una fecha de nacimiento."""
    if not isinstance(fecha_nacimiento, (date, datetime)):
        fecha_nacimiento = datetime.strptime(str(fecha_nacimiento).strip(), FORMATO_FECHA).date()
    elif isinstance(fecha_nacimiento, datetime):
        fecha_nacimiento = fecha_nacimiento.date()

    hoy = hoy or date.today()
    return hoy.year - fecha_nacimiento.year - (
        (hoy.month, hoy.day) < (fecha_nacimiento.month, fecha_nacimiento.day)
    )


def parsear_hora(valor) -> time:
    """Convierte una cadena a objeto time."""
    if isinstance(valor, time):
        return valor
    cadena = str(valor).strip()
    for fmt in (FORMATO_HORA, FORMATO_HORA_BD):
        try:
            return datetime.strptime(cadena, fmt).time()
        except ValueError:
            pass
    raise ValidacionError(f"Hora no válida: '{valor}'. Usa formato HH:MM o HH:MM:SS.")


# ===========================================================================
# MÓDULO A: Personas, Equipos y Categorías
# ===========================================================================
class Persona:
    """
    Clase base que modela a cualquier persona del club.
    Aplica Abstracción y Encapsulamiento con propiedades (getters y setters).
    """

    def __init__(self, nombre: str, primer_apell: str, seg_apell: str = None,
                 telefono: str = "", correo: str = "", estatus: str = ESTATUS_ACTIVO):
        self._nombre = (nombre or "").strip()
        self._primer_apell = (primer_apell or "").strip()
        self._seg_apell = (seg_apell or "").strip() if seg_apell else None
        self._telefono = (telefono or "").strip().replace(" ", "").replace("-", "")
        self._correo = (correo or "").strip().lower()
        self._estatus = (estatus or ESTATUS_ACTIVO).strip().lower()

        if not self._nombre:
            raise ValidacionError("El nombre no puede estar vacío.")
        if not self._primer_apell:
            raise ValidacionError("El primer apellido no puede estar vacío.")
        if self._estatus not in ESTATUS_VALIDOS:
            raise ValidacionError(f"Estatus inválido: '{self._estatus}'. Válidos: {ESTATUS_VALIDOS}")

    # Encapsulamiento con propiedades
    @property
    def nombre(self) -> str:
        return self._nombre

    @nombre.setter
    def nombre(self, valor: str):
        self._nombre = (valor or "").strip()

    @property
    def primer_apell(self) -> str:
        return self._primer_apell

    @primer_apell.setter
    def primer_apell(self, valor: str):
        self._primer_apell = (valor or "").strip()

    # Compatibilidad camelCase
    @property
    def primerApell(self) -> str:
        return self.primer_apell

    @primerApell.setter
    def primerApell(self, valor: str):
        self.primer_apell = valor

    @property
    def seg_apell(self):
        return self._seg_apell

    @seg_apell.setter
    def seg_apell(self, valor):
        self._seg_apell = (valor or "").strip() if valor else None

    @property
    def segApell(self):
        return self.seg_apell

    @segApell.setter
    def segApell(self, valor):
        self.seg_apell = valor

    @property
    def telefono(self) -> str:
        return self._telefono

    @telefono.setter
    def telefono(self, valor: str):
        self._telefono = (valor or "").strip()

    @property
    def correo(self) -> str:
        return self._correo

    @correo.setter
    def correo(self, valor: str):
        self._correo = (valor or "").strip().lower()

    @property
    def estatus(self) -> str:
        return self._estatus

    @estatus.setter
    def estatus(self, valor: str):
        val = (valor or "").strip().lower()
        if val not in ESTATUS_VALIDOS:
            raise ValidacionError(f"Estatus inválido: '{val}'.")
        self._estatus = val

    def obtenerNombreCompleto(self) -> str:
        """Devuelve el nombre completo concatenado."""
        partes = [self._nombre, self._primer_apell, self._seg_apell]
        return " ".join(p for p in partes if p)

    def mostrarInformacion(self) -> str:
        """Método polimórfico base a sobreescribir por las clases hijas."""
        return f"Persona: {self.obtenerNombreCompleto()}"


class Miembro(Persona):
    """
    Representa a un socio/alumno del club deportivo.
    Hereda atributos y métodos de Persona (Herencia).
    """

    def __init__(self, nombre: str, primer_apell: str, seg_apell: str = None,
                 telefono: str = "", correo: str = "", fecha_nacimiento: str = "",
                 equipo: str = "", estatus: str = ESTATUS_ACTIVO,
                 numero_socio: int = None, fecha_registro: str = None, edad: int = None):
        super().__init__(nombre, primer_apell, seg_apell, telefono, correo, estatus)
        self.numero_socio = int(numero_socio) if numero_socio is not None else None

        if isinstance(fecha_nacimiento, (date, datetime)):
            self.fecha_nacimiento = fecha_nacimiento if isinstance(fecha_nacimiento, date) else fecha_nacimiento.date()
        else:
            self.fecha_nacimiento = datetime.strptime(str(fecha_nacimiento).strip(), FORMATO_FECHA).date()

        if fecha_registro:
            if isinstance(fecha_registro, (date, datetime)):
                self.fecha_registro = fecha_registro if isinstance(fecha_registro, date) else fecha_registro.date()
            else:
                self.fecha_registro = datetime.strptime(str(fecha_registro).strip(), FORMATO_FECHA).date()
        else:
            self.fecha_registro = date.today()

        self.equipo = (equipo or "").strip().upper()

    @property
    def edad(self) -> int:
        """Calcula la edad dinámica según la fecha de nacimiento."""
        return calcular_edad(self.fecha_nacimiento)

    def calcularEdad(self) -> int:
        return self.edad

    # Polimorfismo: implementa su propia versión de mostrarInformacion
    def mostrarInformacion(self) -> str:
        return (f"Miembro #{self.numero_socio or 'Nuevo'}: {self.obtenerNombreCompleto()}\n"
                f"Edad: {self.edad} años\n"
                f"Teléfono: {self.telefono}\n"
                f"Correo: {self.correo}\n"
                f"Equipo: {self.equipo}\n"
                f"Estatus: {self.estatus.capitalize()}")


class Entrenador(Persona):
    """
    Representa a un entrenador deportivo.
    Hereda de Persona (Herencia).
    """

    def __init__(self, nombre: str, primer_apell: str, seg_apell: str = None,
                 telefono: str = "", correo: str = "", especialidad: str = "",
                 estatus: str = ESTATUS_ACTIVO, clave_entrenador: int = None):
        super().__init__(nombre, primer_apell, seg_apell, telefono, correo, estatus)
        self.clave_entrenador = int(clave_entrenador) if clave_entrenador is not None else None
        self.especialidad = (especialidad or "").strip()

    # Polimorfismo: implementa su propia versión de mostrarInformacion
    def mostrarInformacion(self) -> str:
        return (f"Entrenador #{self.clave_entrenador or 'Nuevo'}: {self.obtenerNombreCompleto()}\n"
                f"Especialidad: {self.especialidad}\n"
                f"Teléfono: {self.telefono}\n"
                f"Correo: {self.correo}\n"
                f"Estatus: {self.estatus.capitalize()}")


class Categoria:
    """Clasificación por edades para los equipos."""

    def __init__(self, clave_categoria: str, nombre_categoria: str, edad_minima: int, edad_maxima: int):
        self.clave_categoria = (clave_categoria or "").strip().upper()
        self.nombre_categoria = (nombre_categoria or "").strip()
        self.edad_minima = int(edad_minima)
        self.edad_maxima = int(edad_maxima)

        if not self.clave_categoria:
            raise ValidacionError("La clave de categoría no puede estar vacía.")
        if not self.nombre_categoria:
            raise ValidacionError("El nombre de la categoría no puede estar vacío.")
        if self.edad_maxima < self.edad_minima:
            raise ValidacionError("La edad máxima no puede ser menor a la edad mínima.")

    def esEdadValida(self, edad: int) -> bool:
        """Determina si la edad indicada entra dentro del rango."""
        return self.edad_minima <= edad <= self.edad_maxima

    def __str__(self):
        return f"{self.nombre_categoria} ({self.edad_minima}-{self.edad_maxima} años)"


class Equipo:
    """Equipo deportivo asignado a una categoría y a un entrenador."""

    def __init__(self, clave_equipo: str, nombre_equipo: str, categoria: str, entrenador: int):
        self.clave_equipo = (clave_equipo or "").strip().upper()
        self.nombre_equipo = (nombre_equipo or "").strip()
        self.categoria = (categoria or "").strip().upper()
        self.entrenador = int(entrenador)

        if not self.clave_equipo:
            raise ValidacionError("La clave del equipo no puede estar vacía.")
        if not self.nombre_equipo:
            raise ValidacionError("El nombre del equipo no puede estar vacío.")

    def agregarMiembro(self, miembro):
        """Agrega un miembro al equipo asignándole la clave del equipo."""
        miembro.equipo = self.clave_equipo

    def quitarMiembro(self, miembro):
        """Quita un miembro del equipo desasignándolo."""
        if miembro.equipo == self.clave_equipo:
            miembro.equipo = ""

    def __str__(self):
        return f"[{self.clave_equipo}] {self.nombre_equipo} (Cat: {self.categoria})"


# ===========================================================================
# MÓDULO B: Membresías, Pagos, Actividades e Inscripciones
# ===========================================================================
class Tipo_Membresia:
    """Catálogo de tipos de membresías y sus costos."""

    def __init__(self, clave_tipo_membresia: str, nombre_tipo: str, costo: float, duracion_dias: int):
        self.clave_tipo_membresia = (clave_tipo_membresia or "").strip().upper()
        self.nombre_tipo = (nombre_tipo or "").strip()
        self.costo = float(costo)
        self.duracion_dias = int(duracion_dias)

        if self.costo <= 0:
            raise ValidacionError("El costo debe ser mayor a 0.")
        if self.duracion_dias <= 0:
            raise ValidacionError("La duración en días debe ser mayor a 0.")

    def calcularFin(self, inicio):
        """Calcula la fecha de fin sumando la duración en días a la fecha de inicio."""
        if not isinstance(inicio, date):
            inicio = datetime.strptime(str(inicio).strip(), FORMATO_FECHA).date()
        return inicio + timedelta(days=self.duracion_dias)

    def __str__(self):
        return f"[{self.clave_tipo_membresia}] {self.nombre_tipo} (${self.costo:.2f}, {self.duracion_dias} días)"


TipoMembresia = Tipo_Membresia


class Membresia:
    """Membresía adquirida por un socio."""

    def __init__(self, fecha_inicio, tipo_membresia: str, miembro: int,
                 fecha_fin=None, estado: str = None, folio_membresia: int = None,
                 duracion_dias: int = None):
        self.folio_membresia = int(folio_membresia) if folio_membresia is not None else None
        self.tipo_membresia = (tipo_membresia or "").strip().upper()
        self.miembro = int(miembro)

        if isinstance(fecha_inicio, (date, datetime)):
            self.fecha_inicio = fecha_inicio if isinstance(fecha_inicio, date) else fecha_inicio.date()
        else:
            self.fecha_inicio = datetime.strptime(str(fecha_inicio).strip(), FORMATO_FECHA).date()

        if fecha_fin:
            if isinstance(fecha_fin, (date, datetime)):
                self.fecha_fin = fecha_fin if isinstance(fecha_fin, date) else fecha_fin.date()
            else:
                self.fecha_fin = datetime.strptime(str(fecha_fin).strip(), FORMATO_FECHA).date()
        elif duracion_dias:
            self.fecha_fin = self.fecha_inicio + timedelta(days=int(duracion_dias))
        else:
            self.fecha_fin = self.fecha_inicio + timedelta(days=30)

        self._estado = estado.strip().lower() if estado else self.calcularEstado()

    @property
    def estado(self) -> str:
        return self.calcularEstado()

    def calcularEstado(self, hoy: date = None) -> str:
        """Determina si la membresía está vigente, por vencer (<= 7 días) o vencida."""
        hoy = hoy or date.today()
        dias_restantes = (self.fecha_fin - hoy).days
        if dias_restantes < 0:
            return ESTADO_MEMB_VENCIDA
        elif dias_restantes <= DIAS_POR_VENCER:
            return ESTADO_MEMB_POR_VENCER
        return ESTADO_MEMB_VIGENTE

    def renovar(self, duracion_dias: int, hoy: date = None):
        """Extiende la vigencia sumando días a la fecha correspondiente."""
        hoy = hoy or date.today()
        if self.calcularEstado(hoy) == ESTADO_MEMB_VIGENTE:
            self.fecha_fin += timedelta(days=duracion_dias)
        else:
            self.fecha_inicio = hoy
            self.fecha_fin = hoy + timedelta(days=duracion_dias)

    def __str__(self):
        return (f"Membresía #{self.folio_membresia or 'Nueva'} | Socio #{self.miembro} | "
                f"Tipo: {self.tipo_membresia} | Vigencia: {self.fecha_inicio} al {self.fecha_fin} | "
                f"Estado: {self.estado.upper()}")


class Pago:
    """Registro y comprobante del pago de una membresía."""

    def __init__(self, fecha_pago, monto: float, metodo_pago: str, membresia: int,
                 estado_pago: str = ESTADO_PAGO_PAGADO, folio_pago: int = None,
                 recibido: float = None, cambio: float = None):
        self.folio_pago = int(folio_pago) if folio_pago is not None else None

        if isinstance(fecha_pago, (date, datetime)):
            self.fecha_pago = fecha_pago if isinstance(fecha_pago, date) else fecha_pago.date()
        else:
            self.fecha_pago = datetime.strptime(str(fecha_pago).strip(), FORMATO_FECHA).date()

        self.monto = float(monto)
        self.metodo_pago = (metodo_pago or "").strip().lower()
        self.estado_pago = (estado_pago or ESTADO_PAGO_PAGADO).strip().lower()
        self.membresia = int(membresia)
        self.recibido = float(recibido) if recibido is not None else None
        self.cambio = float(cambio) if cambio is not None else None

        if self.monto <= 0:
            raise ValidacionError("El monto del pago debe ser mayor que cero.")
        if self.metodo_pago not in METODOS_PAGO:
            raise ValidacionError(f"Método de pago inválido: '{self.metodo_pago}'. Válidos: {METODOS_PAGO}")
        if self.estado_pago not in ESTADOS_PAGO:
            raise ValidacionError(f"Estado de pago inválido: '{self.estado_pago}'. Válidos: {ESTADOS_PAGO}")

    def procesarPago(self):
        self.estado_pago = ESTADO_PAGO_PAGADO
        return True

    def generarComprobante(self) -> str:
        lineas_cambio = ""
        if self.metodo_pago == METODO_PAGO_EFECTIVO and self.cambio is not None:
            recibido_val = self.recibido if self.recibido is not None else self.monto
            lineas_cambio = (f"Efectivo re : ${recibido_val:.2f} MXN\n"
                             f"Cambio        : ${self.cambio:.2f} MXN\n")
        return (f"========================================\n"
                f"          COMPROBANTE DE PAGO           \n"
                f"========================================\n"
                f"Folio de pago : #{self.folio_pago or 'S/F'}\n"
                f"Membresía     : #{self.membresia}\n"
                f"Fecha         : {self.fecha_pago}\n"
                f"Monto         : ${self.monto:.2f} MXN\n"
                f"Método        : {self.metodo_pago.capitalize()}\n"
                f"{lineas_cambio}"
                f"Estado        : {self.estado_pago.upper()}\n"
                f"========================================")

    def reembolsarPago(self):
        """Cambia el estado del pago a pendiente (reembolso)."""
        self.estado_pago = ESTADO_PAGO_PENDIENTE
        return True


class Actividad:
    """Actividad deportiva (fútbol, basquetbol, voleibol, et)."""

    def __init__(self, codigo_actividad: str, nombre: str, descripcion: str, cupo_maximo: int):
        self.codigo_actividad = (codigo_actividad or "").strip().upper()
        self.nombre = (nombre or "").strip()
        self.descripcion = (descripcion or "").strip()
        self.cupo_maximo = int(cupo_maximo)

        if self.cupo_maximo <= 0:
            raise ValidacionError("El cupo máximo debe ser mayor a 0.")

    def hayCupo(self, inscritos_actuales=0):
        """Verifica si aún hay cupo disponible en la actividad."""
        return inscritos_actuales < self.cupo_maximo

    def __str__(self):
        return f"[{self.codigo_actividad}] {self.nombre} (Cupo máx: {self.cupo_maximo})"


class Inscripcion:
    """Inscripción de un miembro a una actividad deportiva."""

    def __init__(self, miembro: int, actividad: str, fecha_inscripcion=None,
                 fecha_baja=None, estado: str = ESTADO_INSCR_ACTIVA, folio_inscripcion: int = None):
        self.folio_inscripcion = int(folio_inscripcion) if folio_inscripcion is not None else None
        self.miembro = int(miembro)
        self.actividad = (actividad or "").strip().upper()

        if fecha_inscripcion:
            if isinstance(fecha_inscripcion, (date, datetime)):
                self.fecha_inscripcion = fecha_inscripcion if isinstance(fecha_inscripcion, date) else fecha_inscripcion.date()
            else:
                self.fecha_inscripcion = datetime.strptime(str(fecha_inscripcion).strip(), FORMATO_FECHA).date()
        else:
            self.fecha_inscripcion = date.today()

        if fecha_baja:
            if isinstance(fecha_baja, (date, datetime)):
                self.fecha_baja = fecha_baja if isinstance(fecha_baja, date) else fecha_baja.date()
            else:
                self.fecha_baja = datetime.strptime(str(fecha_baja).strip(), FORMATO_FECHA).date()
        else:
            self.fecha_baja = None

        self.estado = (estado or ESTADO_INSCR_ACTIVA).strip().lower()
        if self.estado not in ESTADOS_INSCRIPCION:
            raise ValidacionError(f"Estado de inscripción inválido: '{self.estado}'. Válidos: {ESTADOS_INSCRIPCION}")

    def inscribir(self):
        """Activa la inscripción con la fecha actual."""
        self.estado = ESTADO_INSCR_ACTIVA
        self.fecha_inscripcion = date.today()

    def darDeBaja(self, fecha: date = None):
        self.estado = ESTADO_INSCR_FINALIZADA
        self.fecha_baja = fecha or date.today()

    def __str__(self):
        baja_str = f" | Baja: {self.fecha_baja}" if self.fecha_baja else ""
        return (f"Inscripción #{self.folio_inscripcion or 'Nueva'} | Socio #{self.miembro} | "
                f"Actividad: {self.actividad} | Fecha: {self.fecha_inscripcion} | "
                f"Estado: {self.estado.upper()}{baja_str}")


# ===========================================================================
# MÓDULO C: Espacios, Horarios, Reservas y Asistencias
# ===========================================================================
class Espacio_Deportivo:
    """Instalación o espacio deportivo del club."""

    def __init__(self, codigo_espacio: str, nombre_espacio: str, tipo: str,
                 capacidad: int, estado: str = ESTADO_ESPACIO_DISPONIBLE):
        self.codigo_espacio = (codigo_espacio or "").strip().upper()
        self.nombre_espacio = (nombre_espacio or "").strip()
        self.tipo = (tipo or "").strip()
        self.capacidad = int(capacidad)
        self.estado = (estado or ESTADO_ESPACIO_DISPONIBLE).strip().lower()

        if self.capacidad <= 0:
            raise ValidacionError("La capacidad debe ser mayor a 0.")
        if self.estado not in ESTADOS_ESPACIO:
            raise ValidacionError(f"Estado de espacio inválido: '{self.estado}'. Válidos: {ESTADOS_ESPACIO}")

    def estaDisponible(self, reserva=None):
        """Verifica si el espacio deportivo está disponible."""
        return self.estado == ESTADO_ESPACIO_DISPONIBLE

    def __str__(self):
        return f"[{self.codigo_espacio}] {self.nombre_espacio} ({self.tipo}, Cap: {self.capacidad}) - {self.estado.upper()}"


EspacioDeportivo = Espacio_Deportivo


class Material:
    """Material deportivo inventariado."""

    def __init__(self, codigo_material: str, nombre_material: str,
                 cantidad_total: int, estado: str = ESTADO_MATERIAL_BUENO):
        self.codigo_material = (codigo_material or "").strip().upper()
        self.nombre_material = (nombre_material or "").strip()
        self.cantidad_total = int(cantidad_total)
        self.estado = (estado or ESTADO_MATERIAL_BUENO).strip().lower()

        if self.cantidad_total < 0:
            raise ValidacionError("La cantidad total no puede ser negativa.")
        if self.estado not in ESTADOS_MATERIAL:
            raise ValidacionError(f"Estado de material inválido: '{self.estado}'. Válidos: {ESTADOS_MATERIAL}")

    def hayStock(self, cantidad: int) -> bool:
        return cantidad > 0 and self.cantidad_total >= cantidad

    def retirar(self, cantidad: int):
        if not self.hayStock(cantidad):
            raise ValidacionError("No hay material suficiente en inventario.")
        self.cantidad_total -= cantidad

    def __str__(self):
        return f"[{self.codigo_material}] {self.nombre_material} (Stock: {self.cantidad_total}, Estado: {self.estado})"


class Necesita:
    """Relación entre espacio deportivo y requerimientos de material."""

    def __init__(self, espacio: str, material: str, cantidad_requerida: int):
        self.espacio = (espacio or "").strip().upper()
        self.material = (material or "").strip().upper()
        self.cantidad_requerida = int(cantidad_requerida)

        if self.cantidad_requerida <= 0:
            raise ValidacionError("La cantidad requerida debe ser mayor a 0.")

    def __str__(self):
        return f"Espacio {self.espacio} requiere {self.cantidad_requerida} de {self.material}"


class Horario:
    """Horario semanal de entrenamiento."""

    def __init__(self, dia_semana: str, hora_inicio, hora_fin,
                 actividad: str, espacio: str, codigo_horario: int = None):
        self.codigo_horario = int(codigo_horario) if codigo_horario is not None else None
        self.dia_semana = (dia_semana or "").strip().lower()

        if self.dia_semana not in DIAS_SEMANA:
            raise ValidacionError(f"Día no válido: '{self.dia_semana}'. Válidos: {DIAS_SEMANA}")

        self.hora_inicio = parsear_hora(hora_inicio)
        self.hora_fin = parsear_hora(hora_fin)

        if self.hora_inicio >= self.hora_fin:
            raise ValidacionError("La hora de inicio debe ser anterior a la hora final.")

        self.actividad = (actividad or "").strip().upper()
        self.espacio = (espacio or "").strip().upper()

    def hayTraslape(self, otro_dia: str, otra_inicio: time, otra_fin: time) -> bool:
        if self.dia_semana != (otro_dia or "").strip().lower():
            return False
        return self.hora_inicio < otra_fin and otra_inicio < self.hora_fin

    def __str__(self):
        return (f"Horario #{self.codigo_horario or 'Nuevo'} | {self.dia_semana.capitalize()} "
                f"{self.hora_inicio.strftime('%H:%M')}-{self.hora_fin.strftime('%H:%M')} | "
                f"Actividad: {self.actividad} | Espacio: {self.espacio}")


class Reserva:
    """Reserva de un espacio realizada por un miembro."""

    def __init__(self, fecha, hora_inicio, hora_fin, miembro: int,
                 espacio: str, num_reserva: int = None):
        self.num_reserva = int(num_reserva) if num_reserva is not None else None

        if isinstance(fecha, (date, datetime)):
            self.fecha = fecha if isinstance(fecha, date) else fecha.date()
        else:
            self.fecha = datetime.strptime(str(fecha).strip(), FORMATO_FECHA).date()

        self.hora_inicio = parsear_hora(hora_inicio)
        self.hora_fin = parsear_hora(hora_fin)

        if self.hora_inicio >= self.hora_fin:
            raise ValidacionError("La hora de inicio debe ser anterior a la hora de fin.")

        self.miembro = int(miembro)
        self.espacio = (espacio or "").strip().upper()

    def crearReserva(self):
        """Valida que los datos de la reserva sean correctos."""
        if self.hora_inicio >= self.hora_fin:
            raise ValidacionError("La hora de inicio debe ser anterior a la hora de fin.")
        return True

    def verificarDisponibilidad(self, reservas_existentes):
        """Verifica que no haya traslape con otras reservas del mismo espacio y fecha."""
        for otra in reservas_existentes:
            otra_inicio = parsear_hora(otra["horaInicio"])
            otra_fin = parsear_hora(otra["horaFin"])
            if self.hora_inicio < otra_fin and otra_inicio < self.hora_fin:
                return False
        return True

    def cancelarReserva(self):
        """Marca la reserva como cancelada."""
        self.num_reserva = None
        return True

    def __str__(self):
        return (f"Reserva #{self.num_reserva or 'Nueva'} | Fecha: {self.fecha} | "
                f"{self.hora_inicio.strftime('%H:%M')}-{self.hora_fin.strftime('%H:%M')} | "
                f"Socio: #{self.miembro} | Espacio: {self.espacio}")


class Asistencia:
    """Registro de asistencia de un socio a un horario."""

    def __init__(self, miembro: int, horario: int,
                 estado_asistencia: str = ASIST_PRESENTE,
                 fecha=None, folio_asistencia: int = None):
        self.folio_asistencia = int(folio_asistencia) if folio_asistencia is not None else None
        self.miembro = int(miembro)
        self.horario = int(horario)

        if fecha:
            if isinstance(fecha, (date, datetime)):
                self.fecha = fecha if isinstance(fecha, date) else fecha.date()
            else:
                self.fecha = datetime.strptime(str(fecha).strip(), FORMATO_FECHA).date()
        else:
            self.fecha = date.today()

        self.estado_asistencia = (estado_asistencia or ASIST_PRESENTE).strip().lower()
        if self.estado_asistencia not in ESTADOS_ASISTENCIA:
            raise ValidacionError(f"Estado de asistencia inválido: '{self.estado_asistencia}'.")

    def registrarAsistencia(self):
        """Confirma y valida el registro de asistencia."""
        if self.estado_asistencia not in ESTADOS_ASISTENCIA:
            raise ValidacionError(f"Estado de asistencia inválido: '{self.estado_asistencia}'.")
        return True

    def __str__(self):
        return (f"Asistencia #{self.folio_asistencia or 'Nueva'} | Fecha: {self.fecha} | "
                f"Socio #{self.miembro} | Horario #{self.horario} | Estado: {self.estado_asistencia.upper()}")
