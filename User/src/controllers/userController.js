// ============================================
// ARCHIVO: src/controllers/userController.js
// ============================================
// DESCRIPCIÓN:
// Controlador CRUD para la gestión de usuarios del sistema.
// Maneja todas las operaciones de creación, lectura, actualización y eliminación
// de usuarios, excluyendo las operaciones de autenticación (login/register).
//
// RESPONSABILIDADES:
// - Procesar peticiones HTTP para operaciones CRUD de usuarios
// - Validar permisos de acceso (todos los endpoints requieren autenticación)
// - Llamar a los servicios correspondientes (userService)
// - Formatear y enviar respuestas HTTP
// - Manejar errores y códigos de estado apropiados
//
// ENDPOINTS MANEJADOS:
// - GET    /api/users     -> Listar todos los usuarios
// - GET    /api/users/:id -> Obtener un usuario por ID
// - POST   /api/users     -> Crear un nuevo usuario
// - PUT    /api/users/:id -> Actualizar un usuario existente
// - DELETE /api/users/:id -> Eliminar un usuario
//
// SEGURIDAD:
// Todos los endpoints requieren autenticación JWT (middleware authenticate)
// ============================================

const userService = require('../services/userService.js');

class UserController {
    // ============================================
    // MÉTODO: getAll
    // ============================================
    /**
     * Obtiene la lista de todos los usuarios del sistema
     * 
     * RUTA: GET /api/users
     * ACCESO: Privado (requiere token JWT válido)
     * 
     * RESPUESTA EXITOSA (200):
     * {
     *   "success": true,
     *   "data": [
     *     {
     *       "id": "uuid",
     *       "usuario": "string",
     *       "correo_electronico": "string",
     *       "esta_activo": boolean,
     *       "creado_en": "timestamp",
     *       "rol": { id, nombre }
     *     },
     *     ...
     *   ]
     * }
     * 
     * NOTA: No incluye contraseñas por seguridad
     */
    async getAll(req, res) {
        try {
            const users = await userService.getAllUsers();
            res.status(200).json({ success: true, data: users });
        } catch (error) {
            res.status(500).json({ success: false, message: error.message });
        }
    }

    // ============================================
    // MÉTODO: getById
    // ============================================
    /**
     * Obtiene un usuario específico por su ID
     * 
     * RUTA: GET /api/users/:id
     * ACCESO: Privado (requiere token JWT válido)
     * 
     * PARÁMETROS URL:
     * - id: UUID del usuario a buscar
     * 
     * RESPUESTA EXITOSA (200):
     * {
     *   "success": true,
     *   "data": {
     *     "id": "uuid",
     *     "usuario": "string",
     *     "correo_electronico": "string",
     *     "esta_activo": boolean,
     *     "creado_en": "timestamp",
     *     "rol": { id, nombre, descripcion },
     *     "usuario_permisos": [ { permiso: {...} }, ... ]
     *   }
     * }
     * 
     * ERRORES POSIBLES:
     * - 404: Usuario no encontrado
     */
    async getById(req, res) {
        try {
            const user = await userService.getUserById(req.params.id);
            res.status(200).json({ success: true, data: user });
        } catch (error) {
            res.status(404).json({ success: false, message: error.message });
        }
    }

    // ============================================
    // MÉTODO: create
    // ============================================
    /**
     * Crea un nuevo usuario en el sistema
     * 
     * RUTA: POST /api/users
     * ACCESO: Privado (requiere token JWT válido)
     * 
     * BODY ESPERADO:
     * {
     *   "usuario": "string",           // Nombre de usuario único
     *   "correo_electronico": "string", // Email único
     *   "contrasena": "string",        // Contraseña (será hasheada automáticamente)
     *   "rol_id": "uuid"               // ID del rol a asignar
     * }
     * 
     * PROCESO:
     * 1. Valida que usuario y correo sean únicos
     * 2. Hashea la contraseña con bcrypt
     * 3. Crea el usuario en la base de datos
     * 4. Retorna el usuario creado (sin contraseña)
     * 
     * RESPUESTA EXITOSA (201):
     * {
     *   "success": true,
     *   "data": { id, usuario, correo_electronico, rol_id, ... }
     * }
     * 
     * ERRORES POSIBLES:
     * - 400: Usuario o correo ya existe
     * - 400: Datos inválidos
     */
    // ============================================
    // MÉTODO: getByUsername
    // ============================================
    /**
     * Obtiene un usuario específico por su nombre de usuario
     * 
     * RUTA: GET /api/users/usuario/:usuario
     * ACCESO: Privado (requiere token JWT válido)
     * 
     * PARÁMETROS URL:
     * - usuario: nombre de usuario a buscar
     * 
     * RESPUESTA EXITOSA (200):
     * {
     *   "success": true,
     *   "data": { ... }
     * }
     * 
     * ERRORES POSIBLES:
     * - 404: Usuario no encontrado
     */
    async getByUsername(req, res) {
        try {
            const user = await userService.getUserByUsername(req.params.usuario);
            res.status(200).json({ success: true, data: user });
        } catch (error) {
            res.status(404).json({ success: false, message: error.message });
        }
    }

    async create(req, res) {
        try {
            const user = await userService.createUser(req.body);
            res.status(201).json({ success: true, data: user });
        } catch (error) {
            res.status(400).json({ success: false, message: error.message });
        }
    }

    // ============================================
    // MÉTODO: update
    // ============================================
    /**
     * Actualiza un usuario existente
     * 
     * RUTA: PUT /api/users/:id
     * ACCESO: Privado (requiere token JWT válido)
     * 
     * PARÁMETROS URL:
     * - id: UUID del usuario a actualizar
     * 
     * BODY ESPERADO (todos los campos son opcionales):
     * {
     *   "usuario": "string",
     *   "correo_electronico": "string",
     *   "contrasena": "string",        // Si se envía, será hasheada
     *   "rol_id": "uuid",
     *   "esta_activo": boolean
     * }
     * 
     * PROCESO:
     * 1. Verifica que el usuario exista
     * 2. Si se incluye contraseña, la hashea
     * 3. Actualiza solo los campos proporcionados
     * 4. Retorna el usuario actualizado
     * 
     * RESPUESTA EXITOSA (200):
     * {
     *   "success": true,
     *   "data": { id, usuario, correo_electronico, ... }
     * }
     * 
     * ERRORES POSIBLES:
     * - 400: Usuario no encontrado
     * - 400: Datos inválidos
     */
    async update(req, res) {
        try {
            const user = await userService.updateUser(req.params.id, req.body);
            res.status(200).json({ success: true, data: user });
        } catch (error) {
            res.status(400).json({ success: false, message: error.message });
        }
    }

    // ============================================
    // MÉTODO: updateByUsername
    // ============================================
    /**
     * Actualiza un usuario existente buscando por nombre de usuario
     * 
     * RUTA: PUT /api/users/usuario/:usuario
     * ACCESO: Privado (requiere token JWT válido)
     * 
     * PARÁMETROS URL:
     * - usuario: nombre de usuario a buscar
     * 
     * BODY ESPERADO: Ver update()
     */
    async updateByUsername(req, res) {
        try {
            const user = await userService.updateUserByUsername(req.params.usuario, req.body);
            res.status(200).json({ success: true, data: user });
        } catch (error) {
            res.status(400).json({ success: false, message: error.message });
        }
    }

    // ============================================
    // MÉTODO: delete
    // ============================================
    /**
     * Elimina un usuario del sistema
     * 
     * RUTA: DELETE /api/users/:id
     * ACCESO: Privado (requiere token JWT válido)
     * 
     * PARÁMETROS URL:
     * - id: UUID del usuario a eliminar
     * 
     * PROCESO:
     * 1. Verifica que el usuario exista
     * 2. Elimina el usuario de la base de datos
     * 3. Por CASCADE, también elimina:
     *    - Sesiones del usuario (sesiones_usuario)
     *    - Permisos directos del usuario (usuario_permisos)
     * 
     * RESPUESTA EXITOSA (200):
     * {
     *   "success": true,
     *   "message": "Usuario eliminado"
     * }
     * 
     * ERRORES POSIBLES:
     * - 400: Usuario no encontrado
     * - 400: No se puede eliminar (ej: referencias en otras tablas)
     * 
     * ADVERTENCIA:
     * Esta operación es irreversible. Considerar implementar
     * "soft delete" (esta_activo = false) en lugar de eliminación física.
     */
    async delete(req, res) {
        try {
            await userService.deleteUser(req.params.id);
            res.status(200).json({ success: true, message: 'Usuario eliminado' });
        } catch (error) {
            res.status(400).json({ success: false, message: error.message });
        }
    }
}

module.exports = new UserController();
