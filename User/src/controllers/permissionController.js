// ============================================
// ARCHIVO: src/controllers/permissionController.js
// ============================================
// DESCRIPCIÓN:
// Controlador CRUD para la gestión de permisos del sistema.
// Los permisos definen acciones específicas que pueden realizar los usuarios.
//
// RESPONSABILIDADES:
// - Gestionar operaciones CRUD de permisos
// - Listar permisos disponibles para asignar a roles
// - Validar permisos de acceso
// - Formatear respuestas HTTP
//
// ENDPOINTS MANEJADOS:
// - GET    /api/permissions     -> Listar todos los permisos
// - GET    /api/permissions/:id -> Obtener un permiso por ID
// - POST   /api/permissions     -> Crear un nuevo permiso
// - PUT    /api/permissions/:id -> Actualizar un permiso existente
// - DELETE /api/permissions/:id -> Eliminar un permiso
//
// RELACIONES:
// - Un permiso puede estar asignado a múltiples roles (roles_permisos)
// - Un permiso puede estar asignado directamente a usuarios (usuario_permisos)
//
// EJEMPLOS DE PERMISOS:
// - "users.create" - Crear usuarios
// - "users.read" - Ver usuarios
// - "users.update" - Actualizar usuarios
// - "users.delete" - Eliminar usuarios
// - "reports.view" - Ver reportes
// - "attendance.manage" - Gestionar asistencias
//
// SEGURIDAD:
// Todos los endpoints requieren autenticación JWT
// ============================================

const permissionService = require('../services/permissionService.js');

class PermissionController {
    // ============================================
    // MÉTODO: getAll
    // ============================================
    /**
     * Obtiene la lista de todos los permisos del sistema
     * 
     * RUTA: GET /api/permissions
     * ACCESO: Privado (requiere token JWT válido)
     * 
     * RESPUESTA EXITOSA (200):
     * {
     *   "success": true,
     *   "data": [
     *     {
     *       "id": "uuid",
     *       "nombre": "string",          // Ej: "users.create"
     *       "descripcion": "string",     // Ej: "Crear nuevos usuarios"
     *       "creado_en": "timestamp"
     *     },
     *     ...
     *   ]
     * }
     * 
     * USO TÍPICO:
     * - Listar permisos disponibles al crear/editar roles
     * - Mostrar permisos en panel de administración
     * - Asignar permisos directos a usuarios específicos
     */
    async getAll(req, res) {
        try {
            const permissions = await permissionService.getAllPermissions();
            res.status(200).json({ success: true, data: permissions });
        } catch (error) {
            res.status(500).json({ success: false, message: error.message });
        }
    }

    // ============================================
    // MÉTODO: getById
    // ============================================
    /**
     * Obtiene un permiso específico por su ID
     * 
     * RUTA: GET /api/permissions/:id
     * ACCESO: Privado (requiere token JWT válido)
     * 
     * PARÁMETROS URL:
     * - id: UUID del permiso a buscar
     * 
     * RESPUESTA EXITOSA (200):
     * {
     *   "success": true,
     *   "data": {
     *     "id": "uuid",
     *     "nombre": "string",
     *     "descripcion": "string",
     *     "creado_en": "timestamp"
     *   }
     * }
     * 
     * ERRORES POSIBLES:
     * - 404: Permiso no encontrado
     */
    async getById(req, res) {
        try {
            const permission = await permissionService.getPermissionById(req.params.id);
            res.status(200).json({ success: true, data: permission });
        } catch (error) {
            res.status(404).json({ success: false, message: error.message });
        }
    }

    // ============================================
    // MÉTODO: create
    // ============================================
    /**
     * Crea un nuevo permiso en el sistema
     * 
     * RUTA: POST /api/permissions
     * ACCESO: Privado (requiere token JWT válido)
     * 
     * BODY ESPERADO:
     * {
     *   "nombre": "string",           // Nombre único del permiso (ej: "users.delete")
     *   "descripcion": "string"       // Descripción del permiso (ej: "Eliminar usuarios")
     * }
     * 
     * CONVENCIÓN DE NOMBRES:
     * Se recomienda usar el formato: "recurso.accion"
     * Ejemplos:
     * - "users.create", "users.read", "users.update", "users.delete"
     * - "roles.manage"
     * - "reports.view", "reports.export"
     * - "attendance.register", "attendance.approve"
     * 
     * PROCESO:
     * 1. Valida que el nombre sea único
     * 2. Crea el permiso en la tabla 'permisos'
     * 3. Retorna el permiso creado
     * 
     * RESPUESTA EXITOSA (201):
     * {
     *   "success": true,
     *   "data": {
     *     "id": "uuid",
     *     "nombre": "string",
     *     "descripcion": "string",
     *     "creado_en": "timestamp"
     *   }
     * }
     * 
     * ERRORES POSIBLES:
     * - 400: Nombre de permiso ya existe
     * - 400: Datos inválidos
     * 
     * EJEMPLO DE USO:
     * POST /api/permissions
     * {
     *   "nombre": "attendance.manage",
     *   "descripcion": "Gestionar registros de asistencia"
     * }
     */
    async create(req, res) {
        try {
            const permission = await permissionService.createPermission(req.body);
            res.status(201).json({ success: true, data: permission });
        } catch (error) {
            res.status(400).json({ success: false, message: error.message });
        }
    }

    // ============================================
    // MÉTODO: update
    // ============================================
    /**
     * Actualiza un permiso existente
     * 
     * RUTA: PUT /api/permissions/:id
     * ACCESO: Privado (requiere token JWT válido)
     * 
     * PARÁMETROS URL:
     * - id: UUID del permiso a actualizar
     * 
     * BODY ESPERADO (todos los campos son opcionales):
     * {
     *   "nombre": "string",
     *   "descripcion": "string"
     * }
     * 
     * PROCESO:
     * 1. Verifica que el permiso exista
     * 2. Si se cambia el nombre, valida que sea único
     * 3. Actualiza los campos proporcionados
     * 4. Retorna el permiso actualizado
     * 
     * RESPUESTA EXITOSA (200):
     * {
     *   "success": true,
     *   "data": {
     *     "id": "uuid",
     *     "nombre": "string",
     *     "descripcion": "string",
     *     "creado_en": "timestamp"
     *   }
     * }
     * 
     * ERRORES POSIBLES:
     * - 400: Permiso no encontrado
     * - 400: Nombre ya existe
     * 
     * ADVERTENCIA:
     * Cambiar el nombre de un permiso puede afectar la lógica de
     * autorización si se usa el nombre del permiso en el código.
     * Considerar usar IDs en lugar de nombres para verificaciones.
     */
    async update(req, res) {
        try {
            const permission = await permissionService.updatePermission(req.params.id, req.body);
            res.status(200).json({ success: true, data: permission });
        } catch (error) {
            res.status(400).json({ success: false, message: error.message });
        }
    }

    // ============================================
    // MÉTODO: delete
    // ============================================
    /**
     * Elimina un permiso del sistema
     * 
     * RUTA: DELETE /api/permissions/:id
     * ACCESO: Privado (requiere token JWT válido)
     * 
     * PARÁMETROS URL:
     * - id: UUID del permiso a eliminar
     * 
     * PROCESO:
     * 1. Verifica que el permiso exista
     * 2. Elimina el permiso de la base de datos
     * 3. Por CASCADE, también elimina:
     *    - Relaciones en 'roles_permisos'
     *    - Relaciones en 'usuario_permisos'
     * 
     * RESPUESTA EXITOSA (200):
     * {
     *   "success": true,
     *   "message": "Permiso eliminado"
     * }
     * 
     * ERRORES POSIBLES:
     * - 400: Permiso no encontrado
     * 
     * ADVERTENCIA:
     * Eliminar un permiso afectará a todos los roles y usuarios que
     * lo tengan asignado. Las relaciones se eliminarán automáticamente
     * por CASCADE, pero esto puede causar que usuarios pierdan acceso
     * a ciertas funcionalidades.
     * 
     * RECOMENDACIÓN:
     * Antes de eliminar un permiso, verificar:
     * 1. Qué roles lo tienen asignado
     * 2. Qué usuarios lo tienen directamente asignado
     * 3. Qué funcionalidades del sistema dependen de este permiso
     * 
     * Considerar implementar permisos del sistema que no puedan
     * eliminarse para evitar problemas de seguridad.
     */
    async delete(req, res) {
        try {
            await permissionService.deletePermission(req.params.id);
            res.status(200).json({ success: true, message: 'Permiso eliminado' });
        } catch (error) {
            res.status(400).json({ success: false, message: error.message });
        }
    }
}

module.exports = new PermissionController();
