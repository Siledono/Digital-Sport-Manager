-- ============================================================================
-- Base de datos: digitalsportmanager
-- Digital Sport Manager - Club Deportivo
-- DDL para MySQL 8.0+
-- ============================================================================

DROP DATABASE IF EXISTS digitalsportmanager;
CREATE DATABASE digitalsportmanager CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
USE digitalsportmanager;

-- ----------------------------------------------------------------------------
-- 1. Tablas independientes (Nivel 1 - sin llaves foráneas)
-- ----------------------------------------------------------------------------

CREATE TABLE CATEGORIA (
    claveCategoria VARCHAR(5) NOT NULL,
    nombreCategoria VARCHAR(20) NOT NULL,
    edadMinima INT NOT NULL,
    edadMaxima INT NOT NULL,
    PRIMARY KEY (claveCategoria),
    UNIQUE (nombreCategoria),
    CHECK (edadMaxima >= edadMinima)
);

CREATE TABLE TIPO_MEMBRESIA (
    claveTipoMembresia VARCHAR(5) NOT NULL,
    nombreTipo VARCHAR(20) NOT NULL,
    costo DECIMAL(8,2) NOT NULL,
    duracionDias INT NOT NULL,
    PRIMARY KEY (claveTipoMembresia),
    UNIQUE (nombreTipo)
);

CREATE TABLE ACTIVIDAD (
    codigoActividad VARCHAR(5) NOT NULL,
    nombre VARCHAR(30) NOT NULL,
    descripcion VARCHAR(90) NOT NULL,
    cupoMaximo INT NOT NULL,
    PRIMARY KEY (codigoActividad),
    UNIQUE (nombre)
);

CREATE TABLE ESPACIO_DEPORTIVO (
    codigoEspacio VARCHAR(5) NOT NULL,
    nombreEspacio VARCHAR(30) NOT NULL,
    tipo VARCHAR(20) NOT NULL,
    capacidad INT NOT NULL,
    estado VARCHAR(15) NOT NULL,
    PRIMARY KEY (codigoEspacio),
    UNIQUE (nombreEspacio),
    CHECK (estado IN ('disponible', 'mantenimiento'))
);

CREATE TABLE MATERIAL (
    codigoMaterial VARCHAR(5) NOT NULL,
    nombreMaterial VARCHAR(30) NOT NULL,
    cantidadTotal INT NOT NULL,
    estado VARCHAR(15) NOT NULL,
    PRIMARY KEY (codigoMaterial),
    UNIQUE (nombreMaterial),
    CHECK (estado IN ('bueno', 'regular', 'dañado'))
);

CREATE TABLE ENTRENADOR (
    claveEntrenador INT NOT NULL AUTO_INCREMENT,
    nombre VARCHAR(30) NOT NULL,
    primerApell VARCHAR(30) NOT NULL,
    segApell VARCHAR(30),
    telefono VARCHAR(15) NOT NULL,
    correo VARCHAR(50) NOT NULL,
    especialidad VARCHAR(30) NOT NULL,
    estatus VARCHAR(8) NOT NULL,
    PRIMARY KEY (claveEntrenador),
    UNIQUE (correo),
    CHECK (estatus IN ('activo', 'inactivo'))
);

-- ----------------------------------------------------------------------------
-- 2. Tablas dependientes (Nivel 2 en adelante - con llaves foráneas)
-- ----------------------------------------------------------------------------

CREATE TABLE EQUIPO (
    claveEquipo VARCHAR(5) NOT NULL,
    nombreEquipo VARCHAR(30) NOT NULL,
    categoria VARCHAR(5) NOT NULL,
    entrenador INT NOT NULL,
    PRIMARY KEY (claveEquipo),
    UNIQUE (nombreEquipo),
    FOREIGN KEY (categoria) REFERENCES CATEGORIA (claveCategoria),
    FOREIGN KEY (entrenador) REFERENCES ENTRENADOR (claveEntrenador)
);

CREATE TABLE MIEMBRO (
    numeroSocio INT NOT NULL AUTO_INCREMENT,
    nombre VARCHAR(30) NOT NULL,
    primerApell VARCHAR(30) NOT NULL,
    segApell VARCHAR(30),
    telefono VARCHAR(15) NOT NULL,
    correo VARCHAR(50) NOT NULL,
    fechaRegistro DATE NOT NULL,
    fechaNacimiento DATE NOT NULL,
    edad INT,
    estatus VARCHAR(8) NOT NULL,
    equipo VARCHAR(5) NOT NULL,
    PRIMARY KEY (numeroSocio),
    UNIQUE (correo),
    CHECK (estatus IN ('activo', 'inactivo')),
    FOREIGN KEY (equipo) REFERENCES EQUIPO (claveEquipo)
);

CREATE TABLE MEMBRESIA (
    folioMembresia INT NOT NULL AUTO_INCREMENT,
    fechaInicio DATE NOT NULL,
    fechaFin DATE NOT NULL,
    estado VARCHAR(12),
    tipoMembresia VARCHAR(5) NOT NULL,
    miembro INT NOT NULL,
    PRIMARY KEY (folioMembresia),
    CHECK (estado IN ('vigente', 'por vencer', 'vencida')),
    FOREIGN KEY (tipoMembresia) REFERENCES TIPO_MEMBRESIA (claveTipoMembresia),
    FOREIGN KEY (miembro) REFERENCES MIEMBRO (numeroSocio)
);

CREATE TABLE PAGO (
    folioPago INT NOT NULL AUTO_INCREMENT,
    fechaPago DATE NOT NULL,
    monto DECIMAL(8,2) NOT NULL,
    metodoPago VARCHAR(15) NOT NULL,
    estadoPago VARCHAR(12) NOT NULL,
    membresia INT NOT NULL,
    PRIMARY KEY (folioPago),
    CHECK (metodoPago IN ('efectivo', 'tarjeta', 'transferencia')),
    CHECK (estadoPago IN ('pagado', 'pendiente')),
    FOREIGN KEY (membresia) REFERENCES MEMBRESIA (folioMembresia)
);

CREATE TABLE INSCRIPCION (
    folioInscripcion INT NOT NULL AUTO_INCREMENT,
    fechaInscripcion DATE NOT NULL,
    fechaBaja DATE,
    estado VARCHAR(10) NOT NULL,
    miembro INT NOT NULL,
    actividad VARCHAR(5) NOT NULL,
    PRIMARY KEY (folioInscripcion),
    CHECK (estado IN ('activa', 'finalizada')),
    FOREIGN KEY (miembro) REFERENCES MIEMBRO (numeroSocio),
    FOREIGN KEY (actividad) REFERENCES ACTIVIDAD (codigoActividad)
);

CREATE TABLE HORARIO (
    codigoHorario INT NOT NULL AUTO_INCREMENT,
    diaSemana VARCHAR(10) NOT NULL,
    horaInicio TIME NOT NULL,
    horaFin TIME NOT NULL,
    actividad VARCHAR(5) NOT NULL,
    espacio VARCHAR(5) NOT NULL,
    PRIMARY KEY (codigoHorario),
    CHECK (diaSemana IN ('lunes', 'martes', 'miércoles', 'jueves', 'viernes', 'sábado', 'domingo')),
    CHECK (horaFin > horaInicio),
    FOREIGN KEY (actividad) REFERENCES ACTIVIDAD (codigoActividad),
    FOREIGN KEY (espacio) REFERENCES ESPACIO_DEPORTIVO (codigoEspacio)
);

CREATE TABLE EQUIPO_HORARIO (
    equipo VARCHAR(5) NOT NULL,
    horario INT NOT NULL,
    PRIMARY KEY (equipo, horario),
    FOREIGN KEY (equipo) REFERENCES EQUIPO (claveEquipo),
    FOREIGN KEY (horario) REFERENCES HORARIO (codigoHorario)
);

CREATE TABLE ESPACIO_MATERIAL (
    espacio VARCHAR(5) NOT NULL,
    material VARCHAR(5) NOT NULL,
    cantidadRequerida INT NOT NULL,
    PRIMARY KEY (espacio, material),
    FOREIGN KEY (espacio) REFERENCES ESPACIO_DEPORTIVO (codigoEspacio),
    FOREIGN KEY (material) REFERENCES MATERIAL (codigoMaterial)
);

CREATE TABLE ASISTENCIA (
    folioAsistencia INT NOT NULL AUTO_INCREMENT,
    fecha DATE NOT NULL,
    estadoAsistencia VARCHAR(10) NOT NULL,
    miembro INT NOT NULL,
    horario INT NOT NULL,
    PRIMARY KEY (folioAsistencia),
    CHECK (estadoAsistencia IN ('presente', 'ausente')),
    FOREIGN KEY (miembro) REFERENCES MIEMBRO (numeroSocio),
    FOREIGN KEY (horario) REFERENCES HORARIO (codigoHorario)
);

CREATE TABLE RESERVA (
    numReserva INT NOT NULL AUTO_INCREMENT,
    fecha DATE NOT NULL,
    horaInicio TIME NOT NULL,
    horaFin TIME NOT NULL,
    miembro INT NOT NULL,
    espacio VARCHAR(5) NOT NULL,
    PRIMARY KEY (numReserva),
    CHECK (horaFin > horaInicio),
    FOREIGN KEY (miembro) REFERENCES MIEMBRO (numeroSocio),
    FOREIGN KEY (espacio) REFERENCES ESPACIO_DEPORTIVO (codigoEspacio)
);
