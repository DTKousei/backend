// ============================================
// ARCHIVO: src/controllers/roleController.js
// ============================================
// DESCRIPCIÓN:
// Controlador CRUD para la gestión de roles del sistema.
// Los roles definen conjuntos de permisos que se asignan a los usuarios.
//
// RESPONSABILIDADES:
// - Gestionar operaciones CRUD de roles
// - Manejar asignación de permisos a roles (tabla roles_permisos)
// - Validar permisos de acceso
// - Formatear respuestas HTTP
//
// ENDPOINTS MANEJADOS:
// - GET    /api/roles     -> Listar todos los roles
// - GET    /api/roles/:id -> Obtener un rol por ID
// - POST   /api/roles     -> Crear un nuevo rol
// - PUT    /api/roles/:id -> Actualizar un rol existente
// - DELETE /api/roles/:id -> Eliminar un rol
//
// RELACIONES:
// - Un rol puede tener múltiples permisos (roles_permisos)
// - Un rol puede ser asignado a múltiples usuarios (usuarios.rol_id)
//
// SEGURIDAD:
// Todos los endpoints requieren autenticación JWT
// ============================================

const roleService = require('../services/roleService.js');

class RoleController {
    // ============================================
    // MÉTODO: getAll
    // ============================================
    /**
     * Obtiene la lista de todos los roles con sus permisos
     * 
     * RUTA: GET /api/roles
     * ACCESO: Privado (requiere token JWT válido)
     * 
     * RESPUESTA EXITOSA (200):
     * {
     *   "success": true,
     *   "data": [
     *     {
     *       "id": "uuid",
     *       "nombre": "string",
     *       "descripcion": "string",
     *       "roles_permisos": [
     *         {
     *           "permiso": {
     *             "id": "uuid",
     *             "nombre": "string",
     *             "descripcion": "string"
     *           }
     *         },
     *         ...
     *       ]
     *     },
     *     ...
     *   ]
     * }
     * 
     * USO TÍPICO:
     * - Listar roles disponibles al crear/editar usuarios
     * - Mostrar roles y sus permisos en panel de administración
     */
    async getAll(req, res) {
        try {
            const roles = await roleService.getAllRoles();
            res.status(200).json({ success: true, data: roles });
        } catch (error) {
            res.status(500).json({ success: false, message: error.message });
        }
    }

    // ============================================
    // MÉTODO: getById
    // ============================================
    /**
     * Obtiene un rol específico con sus permisos asociados
     * 
     * RUTA: GET /api/roles/:id
     * ACCESO: Privado (requiere token JWT válido)
     * 
     * PARÁMETROS URL:
     * - id: UUID del rol a buscar
     * 
     * RESPUESTA EXITOSA (200):
     * {
     *   "success": true,
     *   "data": {
     *     "id": "uuid",
     *     "nombre": "string",
     *     "descripcion": "string",
     *     "roles_permisos": [
     *       {
     *         "permiso": {
     *           "id": "uuid",
     *           "nombre": "string",
     *           "descripcion": "string",
     *           "creado_en": "timestamp"
     *         }
     *       }
     *     ]
     *   }
     * }
     * 
     * ERRORES POSIBLES:
     * - 404: Rol no encontrado
     */
    async getById(req, res) {
        try {
            const role = await roleService.getRoleById(req.params.id);
            res.status(200).json({ success: true, data: role });
        } catch (error) {
            res.status(404).json({ success: false, message: error.message });
        }
    }

    // ============================================
    // MÉTODO: create
    // ============================================
    /**
     * Crea un nuevo rol en el sistema
     * 
     * RUTA: POST /api/roles
     * ACCESO: Privado (requiere token JWT válido)
     * 
     * BODY ESPERADO:
     * {
     *   "nombre": "string",           // Nombre del rol (ej: "Administrador", "Usuario")
     *   "descripcion": "string",      // Descripción opcional del rol
     *   "permisos": ["uuid1", "uuid2", ...] // Array de IDs de permisos (opcional)
     * }
     * 
     * PROCESO:
     * 1. Crea el rol en la tabla 'roles'
     * 2. Si se proporcionan permisos, crea las relaciones en 'roles_permisos'
     * 3. Retorna el rol creado
     * 
     * RESPUESTA EXITOSA (201):
     * {
     *   "success": true,
     *   "data": {
     *     "id": "uuid",
     *     "nombre": "string",
     *     "descripcion": "string"
     *   }
     * }
     * 
     * ERRORES POSIBLES:
     * - 400: Nombre de rol ya existe
     * - 400: IDs de permisos inválidos
     * 
     * EJEMPLO DE USO:
     * POST /api/roles
     * {
     *   "nombre": "Supervisor",
     *   "descripcion": "Supervisor de área",
     *   "permisos": ["permiso-1", "permiso-2"]
     * }
     */
    async create(req, res) {
        try {
            const role = await roleService.createRole(req.body);
            res.status(201).json({ success: true, data: role });
        } catch (error) {
            res.status(400).json({ success: false, message: error.message });
        }
    }

    // ============================================
    // MÉTODO: update
    // ============================================
    /**
     * Actualiza un rol existente
     * 
     * RUTA: PUT /api/roles/:id
     * ACCESO: Privado (requiere token JWT válido)
     * 
     * PARÁMETROS URL:
     * - id: UUID del rol a actualizar
     * 
     * BODY ESPERADO (todos los campos son opcionales):
     * {
     *   "nombre": "string",
     *   "descripcion": "string",
     *   "permisos": ["uuid1", "uuid2", ...] // Reemplaza todos los permisos
     * }
     * 
     * PROCESO:
     * 1. Verifica que el rol exista
     * 2. Si se incluyen permisos:
     *    - Elimina todas las relaciones existentes en 'roles_permisos'
     *    - Crea nuevas relaciones con los permisos proporcionados
     * 3. Actualiza nombre y descripción si se proporcionan
     * 4. Retorna el rol actualizado
     * 
     * RESPUESTA EXITOSA (200):
     * {
     *   "success": true,
     *   "data": { id, nombre, descripcion, ... }
     * }
     * 
     * ERRORES POSIBLES:
     * - 400: Rol no encontrado
     * - 400: IDs de permisos inválidos
     * 
     * NOTA IMPORTANTE:
     * Si se envía el array "permisos", se REEMPLAZAN todos los permisos
     * existentes. No es una operación de agregar/quitar individual.
     */
    async update(req, res) {
        try {
            const role = await roleService.updateRole(req.params.id, req.body);
            res.status(200).json({ success: true, data: role });
        } catch (error) {
            res.status(400).json({ success: false, message: error.message });
        }
    }

    // ============================================
    // MÉTODO: delete
    // ============================================
    /**
     * Elimina un rol del sistema
     * 
     * RUTA: DELETE /api/roles/:id
     * ACCESO: Privado (requiere token JWT válido)
     * 
     * PARÁMETROS URL:
     * - id: UUID del rol a eliminar
     * 
     * PROCESO:
     * 1. Verifica que el rol exista
     * 2. Elimina el rol de la base de datos
     * 3. Por CASCADE, también elimina:
     *    - Relaciones en 'roles_permisos'
     * 
     * RESPUESTA EXITOSA (200):
     * {
     *   "success": true,
     *   "message": "Rol eliminado"
     * }
     * 
     * ERRORES POSIBLES:
     * - 400: Rol no encontrado
     * - 400: No se puede eliminar porque hay usuarios con este rol
     * 
     * ADVERTENCIA:
     * No se puede eliminar un rol si hay usuarios asignados a él.
     * Primero se debe reasignar esos usuarios a otro rol.
     * 
     * RECOMENDACIÓN:
     * Considerar implementar roles del sistema que no puedan eliminarse
     * (ej: "Administrador", "Usuario") para evitar problemas.
     */
    async delete(req, res) {
        try {
            await roleService.deleteRole(req.params.id);
            res.status(200).json({ success: true, message: 'Rol eliminado' });
        } catch (error) {
            res.status(400).json({ success: false, message: error.message });
        }
    }
}

module.exports = new RoleController();
