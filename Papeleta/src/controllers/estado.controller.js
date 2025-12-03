import prisma from '../config/database.js';
import { AppError } from '../middleware/error.middleware.js';
import { ERROR_MESSAGES } from '../utils/constants.js';

/**
 * Obtener todos los estados
 */
export const obtenerEstados = async (req, res, next) => {
  try {
    const estados = await prisma.estado.findMany({
      orderBy: { nombre: 'asc' }
    });

    res.json({
      success: true,
      data: estados,
      total: estados.length
    });
  } catch (error) {
    next(error);
  }
};

/**
 * Obtener un estado por ID
 */
export const obtenerEstadoPorId = async (req, res, next) => {
  try {
    const { id } = req.params;

    const estado = await prisma.estado.findUnique({
      where: { id },
      include: {
        _count: {
          select: { permisos: true }
        }
      }
    });

    if (!estado) {
      throw new AppError(ERROR_MESSAGES.ESTADO_NOT_FOUND, 404);
    }

    res.json({
      success: true,
      data: estado
    });
  } catch (error) {
    next(error);
  }
};

/**
 * Crear un nuevo estado
 */
export const crearEstado = async (req, res, next) => {
  try {
    const { nombre, codigo, descripcion } = req.body;

    const estado = await prisma.estado.create({
      data: {
        nombre,
        codigo,
        descripcion
      }
    });

    res.status(201).json({
      success: true,
      message: 'Estado creado exitosamente',
      data: estado
    });
  } catch (error) {
    next(error);
  }
};

/**
 * Actualizar un estado
 */
export const actualizarEstado = async (req, res, next) => {
  try {
    const { id } = req.params;
    const { nombre, codigo, descripcion } = req.body;

    const estado = await prisma.estado.update({
      where: { id },
      data: {
        ...(nombre && { nombre }),
        ...(codigo && { codigo }),
        ...(descripcion !== undefined && { descripcion })
      }
    });

    res.json({
      success: true,
      message: 'Estado actualizado exitosamente',
      data: estado
    });
  } catch (error) {
    next(error);
  }
};

/**
 * Eliminar un estado
 */
export const eliminarEstado = async (req, res, next) => {
  try {
    const { id } = req.params;

    // Verificar si tiene permisos asociados
    const count = await prisma.permiso.count({
      where: { estado_id: id }
    });

    if (count > 0) {
      throw new AppError(
        `No se puede eliminar. Hay ${count} permiso(s) en este estado`,
        400
      );
    }

    await prisma.estado.delete({
      where: { id }
    });

    res.json({
      success: true,
      message: 'Estado eliminado exitosamente'
    });
  } catch (error) {
    next(error);
  }
};
