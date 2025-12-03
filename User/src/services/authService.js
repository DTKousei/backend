const prisma = require('../config/database.js');
const { hashPassword, comparePassword } = require('../utils/password.js');
const { generateToken } = require('../utils/jwt.js');
const jwtConfig = require('../config/jwt.js');

class AuthService {
  /**
   * Registrar un nuevo usuario
   */
  async register(userData) {
    try {
      const { usuario, correo_electronico, contrasena, rol_id } = userData;

      // Verificar si el usuario ya existe
      const existingUser = await prisma.usuarios.findFirst({
        where: {
          OR: [
            { usuario },
            { correo_electronico }
          ]
        }
      });

      if (existingUser) {
        throw new Error('El usuario o correo electrónico ya está registrado');
      }

      // Si no se proporciona rol_id, asignar rol por defecto (ej: "usuario")
      let finalRolId = rol_id;
      if (!finalRolId) {
        const defaultRole = await prisma.roles.findFirst({
          where: { id: 'rol-1' }
        });

        if (!defaultRole) {
          throw new Error('No se encontró un rol por defecto');
        }

        finalRolId = defaultRole.id;
      }

      // Hashear contraseña
      const contrasena_hash = await hashPassword(contrasena);

      // Crear usuario
      const newUser = await prisma.usuarios.create({
        data: {
          usuario,
          correo_electronico,
          contrasena_hash,
          rol_id: finalRolId,
          esta_activo: true
        },
        select: {
          id: true,
          usuario: true,
          correo_electronico: true,
          esta_activo: true,
          creado_en: true,
          rol: {
            select: {
              id: true,
              nombre: true
            }
          }
        }
      });

      return {
        success: true,
        message: 'Usuario registrado exitosamente',
        user: newUser
      };
    } catch (error) {
      throw error;
    }
  }

  /**
   * Iniciar sesión
   */
  async login(correo_electronico, contrasena) {
    try {
      // Buscar usuario
      const user = await prisma.usuarios.findFirst({
        where: { correo_electronico },
        include: {
          rol: {
            select: {
              id: true,
              nombre: true
            }
          }
        }
      });

      if (!user) {
        throw new Error('Credenciales inválidas');
      }

      // Verificar si está activo
      if (!user.esta_activo) {
        throw new Error('Usuario inactivo');
      }

      // Verificar contraseña
      const isPasswordValid = await comparePassword(contrasena, user.contrasena_hash);

      if (!isPasswordValid) {
        throw new Error('Credenciales inválidas');
      }

      // Generar token
      const token = generateToken({
        userId: user.id,
        usuario: user.usuario,
        rol: user.rol.nombre
      });

      // Calcular fecha de expiración
      const expiresIn = jwtConfig.expiresIn;
      let expirationDate = new Date();

      // Parsear el tiempo de expiración
      if (expiresIn.endsWith('h')) {
        expirationDate.setHours(expirationDate.getHours() + parseInt(expiresIn));
      } else if (expiresIn.endsWith('d')) {
        expirationDate.setDate(expirationDate.getDate() + parseInt(expiresIn));
      } else if (expiresIn.endsWith('m')) {
        expirationDate.setMinutes(expirationDate.getMinutes() + parseInt(expiresIn));
      }

      // Guardar sesión
      await prisma.sesiones_usuario.create({
        data: {
          usuario_id: user.id,
          token,
          expira_en: expirationDate
        }
      });

      // Limpiar sesiones expiradas del usuario
      await this.cleanExpiredSessions(user.id);

      return {
        success: true,
        message: 'Login exitoso',
        token,
        user: {
          id: user.id,
          usuario: user.usuario,
          correo_electronico: user.correo_electronico,
          esta_activo: user.esta_activo,
          rol: user.rol
        }
      };
    } catch (error) {
      throw error;
    }
  }

  /**
   * Cerrar sesión
   */
  async logout(token, userId) {
    try {
      // Eliminar sesión específica
      await prisma.sesiones_usuario.deleteMany({
        where: {
          token,
          usuario_id: userId
        }
      });

      return {
        success: true,
        message: 'Sesión cerrada exitosamente'
      };
    } catch (error) {
      throw error;
    }
  }

  /**
   * Cambiar contraseña
   */
  async changePassword(userId, contrasenaActual, contrasenaNueva) {
    try {
      // Obtener usuario
      const user = await prisma.usuarios.findUnique({
        where: { id: userId }
      });

      if (!user) {
        throw new Error('Usuario no encontrado');
      }

      // Verificar contraseña actual
      const isPasswordValid = await comparePassword(contrasenaActual, user.contrasena_hash);

      if (!isPasswordValid) {
        throw new Error('Contraseña actual incorrecta');
      }

      // Hashear nueva contraseña
      const nuevaContrasenaHash = await hashPassword(contrasenaNueva);

      // Actualizar contraseña
      await prisma.usuarios.update({
        where: { id: userId },
        data: {
          contrasena_hash: nuevaContrasenaHash,
          actualizado_en: new Date()
        }
      });

      // Cerrar todas las sesiones del usuario (seguridad)
      await prisma.sesiones_usuario.deleteMany({
        where: { usuario_id: userId }
      });

      return {
        success: true,
        message: 'Contraseña cambiada exitosamente. Por favor, inicia sesión nuevamente.'
      };
    } catch (error) {
      throw error;
    }
  }

  /**
   * Limpiar sesiones expiradas
   */
  async cleanExpiredSessions(userId) {
    try {
      await prisma.sesiones_usuario.deleteMany({
        where: {
          usuario_id: userId,
          expira_en: {
            lt: new Date()
          }
        }
      });
    } catch (error) {
      console.error('Error al limpiar sesiones:', error);
    }
  }

  /**
   * Obtener perfil del usuario
   */
  async getUserProfile(userId) {
    try {
      const user = await prisma.usuarios.findUnique({
        where: { id: userId },
        select: {
          id: true,
          usuario: true,
          correo_electronico: true,
          esta_activo: true,
          creado_en: true,
          actualizado_en: true,
          rol: {
            select: {
              id: true,
              nombre: true,
              descripcion: true
            }
          }
        }
      });

      if (!user) {
        throw new Error('Usuario no encontrado');
      }

      return {
        success: true,
        user
      };
    } catch (error) {
      throw error;
    }
  }
}

module.exports = new AuthService();