-- ============================================================================
-- seed.sql / Datos de prueba iniciales (Club Deportivo)
-- Totalmente compatible con schema.sql (MySQL 8.0+)
-- ============================================================================

USE digitalsportmanager;

-- Desactivar temporalmente revisión de FK para inserción limpia
SET FOREIGN_KEY_CHECKS = 0;

-- 1. TIPO_MEMBRESIA
INSERT INTO TIPO_MEMBRESIA (claveTipoMembresia, nombreTipo, costo, duracionDias) VALUES
    ('TP-SM', 'Semanal', 500.00, 7),
    ('TP-MS', 'Mensual', 1200.00, 30),
    ('TP-AN', 'Anual', 5250.00, 365);

-- 2. CATEGORIA
INSERT INTO CATEGORIA (claveCategoria, nombreCategoria, edadMinima, edadMaxima) VALUES
    ('PREIN', 'Pre-infantil', 4, 6),
    ('INFAN', 'Infantil', 7, 12),
    ('JUVEN', 'Juvenil', 13, 17),
    ('ADULT', 'Libre', 18, 39);

-- 3. ENTRENADOR
INSERT INTO ENTRENADOR (claveEntrenador, nombre, primerApell, segApell, telefono, correo, especialidad, estatus) VALUES
    (1, 'Ricardo', 'Montes', 'Lara', '(664)312 45 10', 'ricardo.montes@dsm.mx', 'Fútbol', 'activo'),
    (2, 'Adriana', 'Salcedo', 'Vega', '(664)528 90 21', 'adriana.salcedo@dsm.mx', 'Voleibol', 'activo'),
    (3, 'Marcos', 'Tapia', 'Orozco', '(664)701 33 48', 'marcos.tapia@dsm.mx', 'Basquetbol', 'activo'),
    (4, 'Lucía', 'Barraza', 'Núñez', '(664)455 12 76', 'lucia.barraza@dsm.mx', 'Voleibol', 'activo'),
    (5, 'Armando', 'Villaseñor', 'Cruz', '(664)230 87 59', 'armando.villasenor@dsm.mx', 'Fútbol', 'activo'),
    (6, 'Paulina', 'Ibarra', 'Solís', '(664)619 04 82', 'paulina.ibarra@dsm.mx', 'Basquetbol', 'activo'),
    (7, 'Daniela', 'Rojas', 'Ceja', '(664)387 26 15', 'daniela.rojas@dsm.mx', 'Fútbol', 'activo'),
    (8, 'Iván', 'Carrillo', 'Peña', '(664)940 71 03', 'ivan.carrillo@dsm.mx', 'Fútbol', 'inactivo');

-- 4. EQUIPO
INSERT INTO EQUIPO (claveEquipo, nombreEquipo, categoria, entrenador) VALUES
    ('EQU01', 'Halcones Fútbol Infantil', 'INFAN', 1),
    ('EQU02', 'Tormenta Voleibol Juvenil', 'JUVEN', 2),
    ('EQU03', 'Titanes Basquetbol Libre', 'ADULT', 3),
    ('EQU04', 'Águilas Voleibol Juvenil', 'JUVEN', 4),
    ('EQU05', 'Pumas Fútbol Libre', 'ADULT', 1),
    ('EQU06', 'Toros Fútbol Libre', 'ADULT', 5),
    ('EQU07', 'Cachorros Mini Basquetbol', 'PREIN', 6),
    ('EQU08', 'Leones Basquetbol Infantil', 'INFAN', 3);

-- 5. MIEMBRO
INSERT INTO MIEMBRO (numeroSocio, nombre, primerApell, segApell, telefono, correo, fechaRegistro, fechaNacimiento, edad, estatus, equipo) VALUES
    (1, 'Sofía', 'Ramírez', 'Cota', '(664)210 33 41', 'sofia.ramirez@mail.com', '2025-02-10', '2016-03-14', 10, 'activo', 'EQU01'),
    (2, 'Diego', 'Herrera', 'Lugo', '(664)210 33 41', 'diego.herrera@mail.com', '2025-02-10', '2015-08-22', 11, 'activo', 'EQU01'),
    (3, 'Valeria', 'Núñez', 'Ibarra', '(664)455 90 12', 'valeria.nunez@mail.com', '2025-06-03', '2010-05-09', 16, 'activo', 'EQU02'),
    (4, 'Mateo', 'Cisneros', 'Peña', '(664)378 21 64', 'mateo.cisneros@mail.com', '2025-09-12', '2009-11-30', 16, 'activo', 'EQU04'),
    (5, 'Camila', 'Ortiz', 'Salas', '(664)902 15 37', 'camila.ortiz@mail.com', '2025-11-20', '2008-12-02', 17, 'inactivo', 'EQU04'),
    (6, 'Luis Fernando', 'Aguirre', 'Mora', '(664)611 48 20', 'luis.aguirre@mail.com', '2025-01-15', '1995-07-04', 31, 'activo', 'EQU03'),
    (7, 'Andrea', 'Beltrán', 'Quiroz', '(664)287 56 03', 'andrea.beltran@mail.com', '2025-05-05', '1998-02-19', 28, 'activo', 'EQU03'),
    (8, 'Jorge Alberto', 'Soto', 'Meza', '(664)530 77 18', 'jorge.soto@mail.com', '2026-01-08', '1990-10-10', 36, 'activo', 'EQU05'),
    (9, 'Karla Patricia', 'Domínguez', 'Rey', '(664)124 89 52', 'karla.dominguez@mail.com', '2025-08-18', '1988-12-25', 37, 'inactivo', 'EQU05'),
    (10, 'Ernesto', 'Valdez', 'Cano', '(664)849 36 70', 'ernesto.valdez@mail.com', '2025-01-07', '1992-06-30', 34, 'activo', 'EQU06'),
    (11, 'Rosa María', 'Estrada', 'Vidal', '(664)395 02 84', 'rosa.estrada@mail.com', '2025-03-22', '1989-09-12', 37, 'activo', 'EQU06'),
    (12, 'Emiliano', 'Torres', 'Ruiz', '(664)716 24 95', 'emiliano.torres@mail.com', '2026-03-01', '2021-04-05', 5, 'activo', 'EQU07'),
    (13, 'Renata', 'Guerrero', 'Plascencia', '(664)716 24 95', 'renata.guerrero@mail.com', '2026-03-01', '2020-09-18', 6, 'activo', 'EQU07'),
    (14, 'Santiago', 'Medina', 'Bravo', '(664)483 61 07', 'santiago.medina@mail.com', '2025-07-14', '2014-02-27', 12, 'activo', 'EQU08'),
    (15, 'Isabella', 'Acosta', 'Lomelí', '(664)259 18 43', 'isabella.acosta@mail.com', '2026-04-19', '2013-10-08', 13, 'activo', 'EQU02'),
    (16, 'Gabriel', 'Esquivel', 'Duarte', '(664)672 30 59', 'gabriel.esquivel@mail.com', '2025-10-02', '1991-03-03', 35, 'activo', 'EQU06'),
    (17, 'Fernanda', 'Lara', 'Ochoa', '(664)340 75 26', 'fernanda.lara@mail.com', '2025-12-12', '2001-08-16', 25, 'activo', 'EQU03'),
    (18, 'Pablo', 'Cervantes', 'Ibarra', '(664)598 12 80', 'pablo.cervantes@mail.com', '2026-02-14', '1993-01-21', 33, 'activo', 'EQU05'),
    (19, 'Ximena', 'Robles', 'Fuentes', '(664)807 45 31', 'ximena.robles@mail.com', '2025-04-25', '2012-06-11', 14, 'activo', 'EQU04'),
    (20, 'Héctor', 'Mendívil', 'Sandoval', '(664)163 92 74', 'hector.mendivil@mail.com', '2025-11-10', '1994-11-02', 32, 'activo', 'EQU06');

-- 6. MEMBRESIA
INSERT INTO MEMBRESIA (folioMembresia, fechaInicio, fechaFin, estado, tipoMembresia, miembro) VALUES
    (1, '2026-11-01', '2026-12-01', 'vigente', 'TP-MS', 1),
    (2, '2026-11-01', '2026-12-01', 'vigente', 'TP-MS', 2),
    (3, '2026-11-15', '2026-11-22', 'por vencer', 'TP-SM', 3),
    (4, '2026-07-01', '2027-07-01', 'vigente', 'TP-AN', 4),
    (5, '2026-09-05', '2026-10-05', 'vencida', 'TP-MS', 5),
    (6, '2026-03-10', '2027-03-10', 'vigente', 'TP-AN', 6),
    (7, '2026-11-12', '2026-12-12', 'vigente', 'TP-MS', 7),
    (8, '2026-11-17', '2026-11-24', 'por vencer', 'TP-SM', 8),
    (9, '2026-11-10', '2026-12-10', 'vigente', 'TP-MS', 9),
    (10, '2026-01-15', '2027-01-15', 'vigente', 'TP-AN', 10),
    (11, '2026-10-22', '2026-10-29', 'vencida', 'TP-SM', 11),
    (12, '2026-11-05', '2026-12-05', 'vigente', 'TP-MS', 12),
    (13, '2026-11-05', '2026-12-05', 'vigente', 'TP-MS', 13),
    (14, '2026-09-20', '2026-10-20', 'vencida', 'TP-MS', 14),
    (15, '2026-11-13', '2026-11-20', 'por vencer', 'TP-SM', 15),
    (16, '2026-10-25', '2026-11-24', 'por vencer', 'TP-MS', 16),
    (17, '2026-02-01', '2027-02-01', 'vigente', 'TP-AN', 17),
    (18, '2026-11-18', '2026-11-25', 'por vencer', 'TP-SM', 18),
    (19, '2026-10-01', '2026-10-31', 'vencida', 'TP-MS', 19),
    (20, '2025-12-01', '2026-12-01', 'vigente', 'TP-AN', 20);

-- 7. PAGO
INSERT INTO PAGO (folioPago, fechaPago, monto, metodoPago, estadoPago, membresia) VALUES
    (1, '2026-11-01', 1200.00, 'efectivo', 'pagado', 1),
    (2, '2026-11-01', 1200.00, 'tarjeta', 'pagado', 2),
    (3, '2026-11-15', 500.00, 'transferencia', 'pagado', 3),
    (4, '2026-07-01', 5250.00, 'tarjeta', 'pagado', 4),
    (5, '2026-09-05', 1200.00, 'efectivo', 'pendiente', 5),
    (6, '2026-03-10', 5250.00, 'tarjeta', 'pagado', 6),
    (7, '2026-11-12', 1200.00, 'transferencia', 'pagado', 7),
    (8, '2026-11-17', 500.00, 'tarjeta', 'pagado', 8),
    (9, '2026-11-10', 1200.00, 'efectivo', 'pendiente', 9),
    (10, '2026-01-15', 5250.00, 'tarjeta', 'pagado', 10),
    (11, '2026-10-22', 500.00, 'transferencia', 'pagado', 11),
    (12, '2026-11-05', 1200.00, 'tarjeta', 'pagado', 12),
    (13, '2026-11-05', 1200.00, 'efectivo', 'pagado', 13),
    (14, '2026-09-20', 1200.00, 'tarjeta', 'pagado', 14),
    (15, '2026-11-13', 500.00, 'transferencia', 'pagado', 15),
    (16, '2026-10-25', 1200.00, 'tarjeta', 'pagado', 16),
    (17, '2026-02-01', 5250.00, 'efectivo', 'pagado', 17),
    (18, '2026-11-18', 500.00, 'tarjeta', 'pagado', 18),
    (19, '2026-10-01', 1200.00, 'transferencia', 'pagado', 19),
    (20, '2025-12-01', 5250.00, 'tarjeta', 'pagado', 20);

-- 8. ACTIVIDAD
INSERT INTO ACTIVIDAD (codigoActividad, nombre, descripcion, cupoMaximo) VALUES
    ('FUTBO', 'Fútbol', 'Entrenamiento y partidos de fútbol', 22),
    ('BASQU', 'Basquetbol', 'Práctica de basquetbol por categorías', 20),
    ('VOLEI', 'Voleibol', 'Práctica de voleibol de sala', 16);

-- 9. INSCRIPCION
INSERT INTO INSCRIPCION (folioInscripcion, fechaInscripcion, fechaBaja, estado, miembro, actividad) VALUES
    (1, '2025-02-17', NULL, 'activa', 1, 'FUTBO'),
    (2, '2025-02-17', NULL, 'activa', 2, 'FUTBO'),
    (3, '2025-06-10', NULL, 'activa', 3, 'VOLEI'),
    (4, '2025-09-19', NULL, 'activa', 4, 'VOLEI'),
    (5, '2025-11-27', '2026-10-15', 'finalizada', 5, 'VOLEI'),
    (6, '2025-01-22', NULL, 'activa', 6, 'BASQU'),
    (7, '2025-05-12', NULL, 'activa', 7, 'BASQU'),
    (8, '2026-01-15', NULL, 'activa', 8, 'FUTBO'),
    (9, '2025-08-25', NULL, 'activa', 9, 'FUTBO'),
    (10, '2025-01-14', NULL, 'activa', 10, 'FUTBO'),
    (11, '2025-03-29', NULL, 'activa', 11, 'FUTBO'),
    (12, '2026-03-08', NULL, 'activa', 12, 'BASQU'),
    (13, '2026-03-08', NULL, 'activa', 13, 'BASQU'),
    (14, '2025-07-21', NULL, 'activa', 14, 'BASQU'),
    (15, '2026-04-26', NULL, 'activa', 15, 'VOLEI'),
    (16, '2025-10-09', NULL, 'activa', 16, 'FUTBO'),
    (17, '2025-12-19', NULL, 'activa', 17, 'BASQU'),
    (18, '2026-02-21', NULL, 'activa', 18, 'FUTBO'),
    (19, '2025-05-02', NULL, 'activa', 19, 'VOLEI'),
    (20, '2025-11-17', NULL, 'activa', 20, 'FUTBO'),
    (21, '2026-08-01', NULL, 'activa', 3, 'BASQU'),
    (22, '2026-09-01', NULL, 'activa', 7, 'VOLEI');

-- 10. ESPACIO_DEPORTIVO
INSERT INTO ESPACIO_DEPORTIVO (codigoEspacio, nombreEspacio, tipo, capacidad, estado) VALUES
    ('CAN01', 'Cancha de Fútbol 1', 'Exterior', 22, 'disponible'),
    ('CAN02', 'Cancha de Basquetbol 1', 'Duela', 20, 'disponible'),
    ('CVO01', 'Cancha de Voleibol de Sala', 'Interior', 16, 'disponible'),
    ('CAN03', 'Cancha de Fútbol Rápido', 'Exterior', 14, 'mantenimiento'),
    ('CAN04', 'Cancha de Basquetbol 2', 'Exterior', 20, 'disponible'),
    ('CVO02', 'Cancha de Voleibol de Playa', 'Exterior', 12, 'disponible');

-- 11. MATERIAL
INSERT INTO MATERIAL (codigoMaterial, nombreMaterial, cantidadTotal, estado) VALUES
    ('BALFU', 'Balón de fútbol', 30, 'bueno'),
    ('BALBA', 'Balón de basquetbol', 25, 'bueno'),
    ('BALVO', 'Balón de voleibol', 20, 'regular'),
    ('REDVO', 'Red de voleibol', 4, 'bueno'),
    ('CONOS', 'Conos de entrenamiento', 60, 'bueno'),
    ('PORFU', 'Portería de fútbol', 6, 'bueno'),
    ('CHALE', 'Chalecos de entrenamiento', 40, 'regular');

-- 12. ESPACIO_MATERIAL
INSERT INTO ESPACIO_MATERIAL (espacio, material, cantidadRequerida) VALUES
    ('CAN01', 'BALFU', 10),
    ('CAN01', 'PORFU', 2),
    ('CAN01', 'CONOS', 20),
    ('CAN02', 'BALBA', 10),
    ('CAN02', 'CHALE', 10),
    ('CVO01', 'BALVO', 8),
    ('CVO01', 'REDVO', 1),
    ('CAN03', 'BALFU', 6),
    ('CAN03', 'PORFU', 2),
    ('CAN04', 'BALBA', 8),
    ('CVO02', 'BALVO', 6),
    ('CVO02', 'REDVO', 1);

-- 13. HORARIO
INSERT INTO HORARIO (codigoHorario, diaSemana, horaInicio, horaFin, actividad, espacio) VALUES
    (1, 'lunes', '16:00:00', '17:30:00', 'FUTBO', 'CAN01'),
    (2, 'martes', '17:00:00', '18:30:00', 'BASQU', 'CAN02'),
    (3, 'miércoles', '18:00:00', '19:30:00', 'VOLEI', 'CVO01'),
    (4, 'jueves', '18:00:00', '19:30:00', 'VOLEI', 'CVO01'),
    (5, 'viernes', '19:00:00', '20:30:00', 'FUTBO', 'CAN01'),
    (6, 'sábado', '09:00:00', '10:30:00', 'VOLEI', 'CVO02'),
    (7, 'lunes', '18:00:00', '19:30:00', 'BASQU', 'CAN04'),
    (8, 'martes', '19:00:00', '20:30:00', 'FUTBO', 'CAN01'),
    (9, 'sábado', '10:00:00', '12:00:00', 'FUTBO', 'CAN01'),
    (10, 'jueves', '17:00:00', '18:00:00', 'BASQU', 'CAN02'),
    (11, 'miércoles', '20:00:00', '21:30:00', 'FUTBO', 'CAN01'),
    (12, 'domingo', '09:00:00', '10:30:00', 'BASQU', 'CAN02'),
    (13, 'viernes', '16:00:00', '17:00:00', 'BASQU', 'CAN02');

-- 14. EQUIPO_HORARIO
INSERT INTO EQUIPO_HORARIO (equipo, horario) VALUES
    ('EQU01', 1),
    ('EQU01', 9),
    ('EQU02', 3),
    ('EQU02', 6),
    ('EQU03', 2),
    ('EQU03', 7),
    ('EQU03', 10),
    ('EQU04', 4),
    ('EQU05', 8),
    ('EQU05', 11),
    ('EQU06', 5),
    ('EQU07', 12),
    ('EQU08', 13);

-- 15. ASISTENCIA
INSERT INTO ASISTENCIA (folioAsistencia, fecha, estadoAsistencia, miembro, horario) VALUES
    (1, '2026-11-02', 'presente', 1, 1),
    (2, '2026-11-09', 'presente', 2, 1),
    (3, '2026-11-04', 'presente', 3, 3),
    (4, '2026-11-12', 'presente', 4, 4),
    (5, '2026-11-05', 'ausente', 5, 4),
    (6, '2026-11-10', 'presente', 6, 2),
    (7, '2026-11-05', 'ausente', 7, 10),
    (8, '2026-11-11', 'presente', 8, 11),
    (9, '2026-11-06', 'presente', 10, 5),
    (10, '2026-11-13', 'presente', 11, 5),
    (11, '2026-11-08', 'presente', 12, 12),
    (12, '2026-11-15', 'presente', 13, 12),
    (13, '2026-11-06', 'ausente', 14, 13),
    (14, '2026-11-11', 'presente', 15, 3),
    (15, '2026-11-06', 'ausente', 16, 5),
    (16, '2026-11-10', 'presente', 17, 2),
    (17, '2026-11-03', 'presente', 18, 8),
    (18, '2026-11-12', 'presente', 19, 4),
    (19, '2026-11-06', 'presente', 20, 5),
    (20, '2026-11-10', 'presente', 9, 8),
    (21, '2026-11-07', 'ausente', 7, 6),
    (22, '2026-11-09', 'presente', 3, 7),
    (23, '2026-11-07', 'ausente', 1, 9),
    (24, '2026-11-14', 'presente', 2, 9),
    (25, '2026-11-05', 'presente', 6, 10);

-- 16. RESERVA
INSERT INTO RESERVA (numReserva, fecha, horaInicio, horaFin, miembro, espacio) VALUES
    (1, '2026-11-14', '10:00:00', '11:00:00', 6, 'CAN02'),
    (2, '2026-11-15', '12:00:00', '14:00:00', 8, 'CAN01'),
    (3, '2026-11-16', '18:00:00', '19:00:00', 10, 'CVO01'),
    (4, '2026-11-18', '07:00:00', '08:00:00', 17, 'CAN02'),
    (5, '2026-11-21', '16:00:00', '17:00:00', 3, 'CVO02'),
    (6, '2026-11-22', '09:00:00', '10:30:00', 18, 'CAN01'),
    (7, '2026-11-24', '19:00:00', '20:00:00', 20, 'CVO01'),
    (8, '2026-11-25', '20:00:00', '21:00:00', 9, 'CAN01'),
    (9, '2026-11-28', '11:00:00', '12:00:00', 4, 'CAN04'),
    (10, '2026-11-29', '17:00:00', '18:30:00', 7, 'CAN02'),
    (11, '2026-12-02', '18:00:00', '19:00:00', 11, 'CVO02'),
    (12, '2026-12-05', '10:00:00', '12:00:00', 16, 'CVO01');

SET FOREIGN_KEY_CHECKS = 1;
