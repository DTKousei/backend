// ============================================
// ARCHIVO: src/routes/index.js
// ============================================
// DESCRIPCIÓN:
// Este archivo es el enrutador principal del API REST.
// Centraliza todas las rutas y las organiza por módulos.
// Cada módulo (auth, users, roles, permissions) tiene su propio archivo de rutas.
//
// FUNCIÓN:
// - Importa todos los enrutadores de módulos específicos
// - Los registra con sus prefijos correspondientes (/auth, /users, etc.)
// - Exporta el enrutador principal para ser usado en app.js
//
// ENDPOINTS DISPONIBLES:
// - /api/auth/*        -> Autenticación (login, register, logout, etc.)
// - /api/users/*       -> CRUD de usuarios
// - /api/roles/*       -> CRUD de roles
// - /api/permissions/* -> CRUD de permisos
// ============================================

const { Router } = require('express');
const authRoutes = require('./authRoutes.js');

const router = Router();

// ============================================
// REGISTRO DE RUTAS PRINCIPALES
// ============================================

// RUTAS DE AUTENTICACIÓN (/api/auth/*)
// Maneja: login, register, logout, cambio de contraseña, perfil
// Acceso: Público (login, register) y Privado (resto)
router.use('/auth', authRoutes);

// RUTAS DE USUARIOS (/api/users/*)
// Maneja: CRUD completo de usuarios (Create, Read, Update, Delete)
// Acceso: Privado (requiere autenticación con JWT)
// Endpoints: GET /, GET /:id, POST /, PUT /:id, DELETE /:id
router.use('/users', require('./userRoutes.js'));

// RUTAS DE ROLES (/api/roles/*)
// Maneja: CRUD completo de roles y asignación de permisos
// Acceso: Privado (requiere autenticación con JWT)
// Endpoints: GET /, GET /:id, POST /, PUT /:id, DELETE /:id
router.use('/roles', require('./roleRoutes.js'));

// RUTAS DE PERMISOS (/api/permissions/*)
// Maneja: CRUD completo de permisos del sistema
// Acceso: Privado (requiere autenticación con JWT)
// Endpoints: GET /, GET /:id, POST /, PUT /:id, DELETE /:id
router.use('/permissions', require('./permissionRoutes.js'));

// ============================================
// CÓMO AGREGAR NUEVAS RUTAS
// ============================================
// 1. Crear archivo en src/routes/nombreRoutes.js
// 2. Definir las rutas en ese archivo
// 3. Registrar aquí: router.use('/nombre', require('./nombreRoutes.js'));
//
// Ejemplo para módulo de asistencias:
// router.use('/attendance', require('./attendanceRoutes.js'));
// ============================================

module.exports = router;