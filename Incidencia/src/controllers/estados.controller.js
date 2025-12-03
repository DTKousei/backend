const prisma = require('../utils/prisma');

/**
 * Crear nuevo estado
 */
const createEstado = async (req, res, next) => {
  try {
    const { nombre, descripcion } = req.body;

    const estado = await prisma.estado.create({
      data: {
        nombre,
        descripcion,
      },
    });

    res.status(201).json({
      message: 'Estado creado exitosamente',
      data: estado,
    });
  } catch (error) {
    next(error);
  }
};

/**
 * Obtener todos los estados
 */
const getAllEstados = async (req, res, next) => {
  try {
    const estados = await prisma.estado.findMany({
      orderBy: {
        nombre: 'asc',
      },
    });

    res.json({ data: estados });
  } catch (error) {
    next(error);
  }
};

/**
 * Obtener estado por ID
 */
const getEstadoById = async (req, res, next) => {
  try {
    const { id } = req.params;

    const estado = await prisma.estado.findUnique({
      where: { id },
      include: {
        incidencias: {
          take: 10,
          orderBy: {
            creado_en: 'desc',
          },
        },
      },
    });

    if (!estado) {
      return res.status(404).json({
        error: 'No encontrado',
        message: 'El estado no existe',
      });
    }

    res.json({ data: estado });
  } catch (error) {
    next(error);
  }
};

/**
 * Actualizar estado
 */
const updateEstado = async (req, res, next) => {
  try {
    const { id } = req.params;
    const { nombre, descripcion } = req.body;

    const updateData = {};
    if (nombre !== undefined) updateData.nombre = nombre;
    if (descripcion !== undefined) updateData.descripcion = descripcion;

    const estado = await prisma.estado.update({
      where: { id },
      data: updateData,
    });

    res.json({
      message: 'Estado actualizado exitosamente',
      data: estado,
    });
  } catch (error) {
    next(error);
  }
};

/**
 * Eliminar estado
 */
const deleteEstado = async (req, res, next) => {
  try {
    const { id } = req.params;

    // Verificar si hay incidencias asociadas
    const incidenciasCount = await prisma.incidencia.count({
      where: { estado_id: id },
    });

    if (incidenciasCount > 0) {
      return res.status(400).json({
        error: 'No se puede eliminar',
        message: `Existen ${incidenciasCount} incidencia(s) con este estado. Cámbielas primero a otro estado.`,
      });
    }

    await prisma.estado.delete({
      where: { id },
    });

    res.json({
      message: 'Estado eliminado exitosamente',
    });
  } catch (error) {
    next(error);
  }
};

module.exports = {
  createEstado,
  getAllEstados,
  getEstadoById,
  updateEstado,
  deleteEstado,
};
