import prisma from '../config/database.js';
import { AppError } from '../middleware/error.middleware.js';
import { ERROR_MESSAGES, SUCCESS_MESSAGES } from '../utils/constants.js';

/**
 * Obtener todos los tipos de permisos
 */
export const obtenerTiposPermisos = async (req, res, next) => {
  try {
    const { activo } = req.query;

    const where = {};
    if (activo !== undefined) {
      where.esta_activo = activo === 'true';
    }

    const tiposPermisos = await prisma.permisoTipo.findMany({
      where,
      orderBy: { nombre: 'asc' }
    });

    res.json({
      success: true,
      data: tiposPermisos,
      total: tiposPermisos.length
    });
  } catch (error) {
    next(error);
  }
};

/**
 * Obtener un tipo de permiso por ID
 */
export const obtenerTipoPermisoPorId = async (req, res, next) => {
  try {
    const { id } = req.params;

    const tipoPermiso = await prisma.permisoTipo.findUnique({
      where: { id },
      include: {
        _count: {
          select: { permisos: true }
        }
      }
    });

    if (!tipoPermiso) {
      throw new AppError(ERROR_MESSAGES.TIPO_PERMISO_NOT_FOUND, 404);
    }

    res.json({
      success: true,
      data: tipoPermiso
    });
  } catch (error) {
    next(error);
  }
};

/**
 * Crear un nuevo tipo de permiso
 */
export const crearTipoPermiso = async (req, res, next) => {
  try {
    const {
      nombre,
      codigo,
      descripcion,
      requiere_firma_institucion,
      tiempo_maximo_horas,
      esta_activo
    } = req.body;

    const tipoPermiso = await prisma.permisoTipo.create({
      data: {
        nombre,
        codigo,
        descripcion,
        requiere_firma_institucion: requiere_firma_institucion || false,
        tiempo_maximo_horas,
        esta_activo: esta_activo !== undefined ? esta_activo : true
      }
    });

    res.status(201).json({
      success: true,
      message: 'Tipo de permiso creado exitosamente',
      data: tipoPermiso
    });
  } catch (error) {
    next(error);
  }
};

/**
 * Actualizar un tipo de permiso
 */
export const actualizarTipoPermiso = async (req, res, next) => {
  try {
    const { id } = req.params;
    const {
      nombre,
      codigo,
      descripcion,
      requiere_firma_institucion,
      tiempo_maximo_horas,
      esta_activo
    } = req.body;

    const tipoPermiso = await prisma.permisoTipo.update({
      where: { id },
      data: {
        ...(nombre && { nombre }),
        ...(codigo && { codigo }),
        ...(descripcion !== undefined && { descripcion }),
        ...(requiere_firma_institucion !== undefined && { requiere_firma_institucion }),
        ...(tiempo_maximo_horas !== undefined && { tiempo_maximo_horas }),
        ...(esta_activo !== undefined && { esta_activo })
      }
    });

    res.json({
      success: true,
      message: 'Tipo de permiso actualizado exitosamente',
      data: tipoPermiso
    });
  } catch (error) {
    next(error);
  }
};

/**
 * Eliminar un tipo de permiso
 */
export const eliminarTipoPermiso = async (req, res, next) => {
  try {
    const { id } = req.params;

    // Verificar si tiene permisos asociados
    const count = await prisma.permiso.count({
      where: { tipo_permiso_id: id }
    });

    if (count > 0) {
      throw new AppError(
        `No se puede eliminar. Hay ${count} permiso(s) asociado(s) a este tipo`,
        400
      );
    }

    await prisma.permisoTipo.delete({
      where: { id }
    });

    res.json({
      success: true,
      message: 'Tipo de permiso eliminado exitosamente'
    });
  } catch (error) {
    next(error);
  }
};
