const { verifyToken } = require('../utils/jwt');
const prisma = require('../config/database');

/**
 * Middleware para verificar JWT en las peticiones
 */
const authenticate = async (req, res, next) => {
  try {
    // Obtener token del header
    const authHeader = req.headers.authorization;
    
    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      return res.status(401).json({
        success: false,
        message: 'Token no proporcionado'
      });
    }

    const token = authHeader.substring(7); // Remover 'Bearer '

    // Verificar token
    const decoded = verifyToken(token);

    // Verificar si el token existe en sesiones activas
    const session = await prisma.sesiones_usuario.findFirst({
      where: {
        token,
        usuario_id: decoded.userId,
        expira_en: {
          gt: new Date()
        }
      }
    });

    if (!session) {
      return res.status(401).json({
        success: false,
        message: 'Sesión inválida o expirada'
      });
    }

    // Verificar si el usuario está activo
    const user = await prisma.usuarios.findUnique({
      where: { id: decoded.userId },
      select: {
        id: true,
        usuario: true,
        correo_electronico: true,
        esta_activo: true,
        rol_id: true,
        rol: {
          select: {
            id: true,
            nombre: true
          }
        }
      }
    });

    if (!user || !user.esta_activo) {
      return res.status(401).json({
        success: false,
        message: 'Usuario inactivo o no encontrado'
      });
    }

    // Agregar usuario al request
    req.user = user;
    req.token = token;
    
    next();
  } catch (error) {
    return res.status(401).json({
      success: false,
      message: 'Token inválido',
      error: error.message
    });
  }
};

/**
 * Middleware para verificar roles
 * @param {Array<String>} allowedRoles - Roles permitidos
 */
const authorize = (...allowedRoles) => {
  return async (req, res, next) => {
    try {
      if (!req.user) {
        return res.status(401).json({
          success: false,
          message: 'Usuario no autenticado'
        });
      }

      const userRole = req.user.rol.nombre;

      if (!allowedRoles.includes(userRole)) {
        return res.status(403).json({
          success: false,
          message: 'No tienes permisos para acceder a este recurso'
        });
      }

      next();
    } catch (error) {
      return res.status(500).json({
        success: false,
        message: 'Error al verificar permisos',
        error: error.message
      });
    }
  };
};

/**
 * Middleware para verificar permisos específicos
 * @param {String} permissionName - Nombre del permiso requerido
 */
const checkPermission = (permissionName) => {
  return async (req, res, next) => {
    try {
      if (!req.user) {
        return res.status(401).json({
          success: false,
          message: 'Usuario no autenticado'
        });
      }

      // Obtener permisos del rol del usuario
      const rolePermissions = await prisma.roles_permisos.findMany({
        where: {
          rol_id: req.user.rol_id
        },
        include: {
          permiso: true
        }
      });

      // Obtener permisos directos del usuario
      const userPermissions = await prisma.usuario_permisos.findMany({
        where: {
          usuario_id: req.user.id
        },
        include: {
          permiso: true
        }
      });

      const allPermissions = [
        ...rolePermissions.map(rp => rp.permiso.nombre),
        ...userPermissions.map(up => up.permiso.nombre)
      ];

      if (!allPermissions.includes(permissionName)) {
        return res.status(403).json({
          success: false,
          message: `Requiere el permiso: ${permissionName}`
        });
      }

      next();
    } catch (error) {
      return res.status(500).json({
        success: false,
        message: 'Error al verificar permisos',
        error: error.message
      });
    }
  };
};

module.exports = {
  authenticate,
  authorize,
  checkPermission
};