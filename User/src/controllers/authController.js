// ============================================
// ARCHIVO: src/controllers/authController.js
// ============================================
// DESCRIPCIÓN:
// Controlador de autenticación que maneja todas las operaciones relacionadas
// con el inicio de sesión, registro, cierre de sesión y gestión de usuarios.
//
// RESPONSABILIDADES:
// - Procesar peticiones HTTP relacionadas con autenticación
// - Validar datos de entrada (ya validados por middleware)
// - Llamar a los servicios correspondientes (authService)
// - Formatear y enviar respuestas HTTP al cliente
// - Manejar errores y enviar códigos de estado apropiados
//
// ENDPOINTS MANEJADOS:
// - POST /api/auth/register      -> Registrar nuevo usuario
// - POST /api/auth/login         -> Iniciar sesión (obtener token JWT)
// - POST /api/auth/logout        -> Cerrar sesión (invalidar token)
// - POST /api/auth/change-password -> Cambiar contraseña del usuario
// - GET  /api/auth/profile       -> Obtener perfil del usuario autenticado
// - GET  /api/auth/verify        -> Verificar validez del token JWT
// ============================================

const authService = require('../services/authService.js');
const userService = require('../services/userService.js');

class AuthController {
  // ============================================
  // MÉTODO: register
  // ============================================
  /**
   * Registra un nuevo usuario en el sistema
   * 
   * RUTA: POST /api/auth/register
   * ACCESO: Público (no requiere autenticación)
   * 
   * BODY ESPERADO:
   * {
   *   "usuario": "string",           // Nombre de usuario único
   *   "correo_electronico": "string", // Email único
   *   "contrasena": "string",        // Contraseña (será hasheada)
   *   "rol_id": "uuid"               // ID del rol a asignar
   * }
   * 
   * RESPUESTA EXITOSA (201):
   * {
   *   "success": true,
   *   "message": "Usuario registrado exitosamente",
   *   "user": { usuario, correo_electronico, rol, ... }
   * }
   * 
   * ERRORES POSIBLES:
   * - 400: Usuario o correo ya existe
   * - 400: Datos de entrada inválidos
   */
  async register(req, res) {
    try {
      const result = await authService.register(req.body);

      res.status(201).json(result);
    } catch (error) {
      res.status(400).json({
        success: false,
        message: error.message || 'Error al registrar usuario'
      });
    }
  }

  // ============================================
  // MÉTODO: login
  // ============================================
  /**
   * Autentica un usuario y genera un token JWT
   * 
   * RUTA: POST /api/auth/login
   * ACCESO: Público (no requiere autenticación)
   * SEGURIDAD: Protegido con rate limiting (loginLimiter)
   * 
   * BODY ESPERADO:
   * {
   *   "correo_electronico": "string", // Email del usuario
   *   "contrasena": "string"          // Contraseña sin hashear
   * }
   * 
   * RESPUESTA EXITOSA (200):
   * {
   *   "success": true,
   *   "message": "Login exitoso",
   *   "token": "jwt_token_string",    // Token JWT para autenticación
   *   "user": { id, usuario, correo, rol, ... }
   * }
   * 
   * ERRORES POSIBLES:
   * - 401: Credenciales inválidas
   * - 401: Usuario inactivo
   * - 429: Demasiados intentos de login (rate limit)
   */
  async login(req, res) {
    try {
      const { correo_electronico, contrasena } = req.body;

      const result = await authService.login(correo_electronico, contrasena);

      res.status(200).json(result);
    } catch (error) {
      res.status(401).json({
        success: false,
        message: error.message || 'Error al iniciar sesión'
      });
    }
  }

  // ============================================
  // MÉTODO: logout
  // ============================================
  /**
   * Cierra la sesión del usuario invalidando su token JWT
   * 
   * RUTA: POST /api/auth/logout
   * ACCESO: Privado (requiere token JWT válido)
   * 
   * HEADERS REQUERIDOS:
   * Authorization: Bearer {token}
   * 
   * PROCESO:
   * 1. Obtiene el token del header (ya validado por middleware authenticate)
   * 2. Elimina la sesión de la base de datos
   * 3. El token queda invalidado y no puede usarse más
   * 
   * RESPUESTA EXITOSA (200):
   * {
   *   "success": true,
   *   "message": "Sesión cerrada exitosamente"
   * }
   */
  async logout(req, res) {
    try {
      const result = await authService.logout(req.token, req.user.id);

      res.status(200).json(result);
    } catch (error) {
      res.status(400).json({
        success: false,
        message: error.message || 'Error al cerrar sesión'
      });
    }
  }

  // ============================================
  // MÉTODO: changePassword
  // ============================================
  /**
   * Permite al usuario cambiar su contraseña
   * 
   * RUTA: POST /api/auth/change-password
   * ACCESO: Privado (requiere token JWT válido)
   * 
   * BODY ESPERADO:
   * {
   *   "contrasena_actual": "string",  // Contraseña actual para verificación
   *   "contrasena_nueva": "string"    // Nueva contraseña (será hasheada)
   * }
   * 
   * PROCESO:
   * 1. Verifica que la contraseña actual sea correcta
   * 2. Hashea la nueva contraseña con bcrypt
   * 3. Actualiza la contraseña en la base de datos
   * 4. Invalida todas las sesiones activas del usuario (seguridad)
   * 
   * RESPUESTA EXITOSA (200):
   * {
   *   "success": true,
   *   "message": "Contraseña cambiada exitosamente. Por favor, inicia sesión nuevamente."
   * }
   * 
   * ERRORES POSIBLES:
   * - 400: Contraseña actual incorrecta
   * - 400: Nueva contraseña no cumple requisitos
   */
  async changePassword(req, res) {
    try {
      const { contrasena_actual, contrasena_nueva } = req.body;

      const result = await authService.changePassword(
        req.user.id,
        contrasena_actual,
        contrasena_nueva
      );

      res.status(200).json(result);
    } catch (error) {
      res.status(400).json({
        success: false,
        message: error.message || 'Error al cambiar contraseña'
      });
    }
  }

  // ============================================
  // MÉTODO: resetPasswordByUsername
  // ============================================
  /**
   * Restablece la contraseña de un usuario a un valor por defecto (Ugel + usuario + @)
   * 
   * RUTA: POST /api/auth/change-pass/:usuario
   * ACCESO: Privado (requiere token JWT válido)
   * 
   * PARÁMETROS URL:
   * - usuario: nombre de usuario (DNI) al que se le reseteará la contraseña
   * 
   * PROCESO:
   * 1. Genera la nueva contraseña con el patrón: Ugel{usuario}@
   *    Ejemplo: Si usuario=75143365 -> Pass=Ugel75143365@
   * 2. Actualiza la contraseña en la base de datos usando userService
   * 
   * RESPUESTA EXITOSA (200):
   * {
   *   "success": true,
   *   "message": "Contraseña restablecida exitosamente",
   *   "data": { ... }
   * }
   * 
   * ERRORES POSIBLES:
   * - 400: Error al actualizar (ej: usuario no encontrado)
   */
  async resetPasswordByUsername(req, res) {
    try {
      const { usuario } = req.params;
      const nuevaContrasena = `Ugel${usuario}@`;

      const result = await userService.updateUserByUsername(usuario, {
        contrasena: nuevaContrasena
      });

      res.status(200).json({
        success: true,
        message: `Contraseña restablecida exitosamente a: ${nuevaContrasena}`,
        data: result
      });
    } catch (error) {
      res.status(400).json({
        success: false,
        message: error.message || 'Error al restablecer contraseña'
      });
    }
  }

  // ============================================
  // MÉTODO: getProfile
  // ============================================
  /**
   * Obtiene el perfil completo del usuario autenticado
   * 
   * RUTA: GET /api/auth/profile
   * ACCESO: Privado (requiere token JWT válido)
   * 
   * RESPUESTA EXITOSA (200):
   * {
   *   "success": true,
   *   "user": {
   *     "id": "uuid",
   *     "usuario": "string",
   *     "correo_electronico": "string",
   *     "esta_activo": boolean,
   *     "creado_en": "timestamp",
   *     "actualizado_en": "timestamp",
   *     "rol": { id, nombre, descripcion }
   *   }
   * }
   * 
   * NOTA: La contraseña hasheada NO se incluye en la respuesta por seguridad
   */
  async getProfile(req, res) {
    try {
      const result = await authService.getUserProfile(req.user.id);

      res.status(200).json(result);
    } catch (error) {
      res.status(400).json({
        success: false,
        message: error.message || 'Error al obtener perfil'
      });
    }
  }

  // ============================================
  // MÉTODO: verifyToken
  // ============================================
  /**
   * Verifica si el token JWT proporcionado es válido
   * 
   * RUTA: GET /api/auth/verify
   * ACCESO: Privado (requiere token JWT válido)
   * 
   * PROPÓSITO:
   * - Útil para verificar si una sesión sigue activa
   * - Frontend puede usar esto para validar tokens antes de hacer peticiones
   * - Si el token es inválido o expiró, el middleware authenticate rechazará la petición
   * 
   * RESPUESTA EXITOSA (200):
   * {
   *   "success": true,
   *   "message": "Token válido",
   *   "user": {
   *     "id": "uuid",
   *     "usuario": "string",
   *     "correo_electronico": "string",
   *     "rol": { id, nombre }
   *   }
   * }
   * 
   * NOTA: Si llega aquí, el middleware authenticate ya validó:
   * - Formato del token
   * - Firma del token
   * - Fecha de expiración
   * - Existencia de sesión en BD
   * - Usuario activo
   */
  async verifyToken(req, res) {
    // Si llega aquí, el middleware authenticate ya validó el token
    res.status(200).json({
      success: true,
      message: 'Token válido',
      user: {
        id: req.user.id,
        usuario: req.user.usuario,
        correo_electronico: req.user.correo_electronico,
        rol: req.user.rol
      }
    });
  }
}

module.exports = new AuthController();