const prisma = require('../utils/prisma');

/**
 * Crear nuevo tipo de incidencia
 */
const createTipoIncidencia = async (req, res, next) => {
  try {
    const { nombre, codigo, requiere_aprobacion, requiere_documento, descuenta_salario, esta_activo } = req.body;

    const tipoIncidencia = await prisma.tipoIncidencia.create({
      data: {
        nombre,
        codigo,
        requiere_aprobacion,
        requiere_documento,
        descuenta_salario,
        esta_activo,
        creado_en: new Date(),
      },
    });

    res.status(201).json({
      message: 'Tipo de incidencia creado exitosamente',
      data: tipoIncidencia,
    });
  } catch (error) {
    next(error);
  }
};

/**
 * Obtener todos los tipos de incidencia
 */
const getAllTiposIncidencia = async (req, res, next) => {
  try {
    const { esta_activo } = req.query;

    const where = {};
    if (esta_activo !== undefined) {
      where.esta_activo = esta_activo === 'true';
    }

    const tiposIncidencia = await prisma.tipoIncidencia.findMany({
      where,
      orderBy: {
        nombre: 'asc',
      },
    });

    res.json({ data: tiposIncidencia });
  } catch (error) {
    next(error);
  }
};

/**
 * Obtener tipo de incidencia por ID
 */
const getTipoIncidenciaById = async (req, res, next) => {
  try {
    const { id } = req.params;

    const tipoIncidencia = await prisma.tipoIncidencia.findUnique({
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

    if (!tipoIncidencia) {
      return res.status(404).json({
        error: 'No encontrado',
        message: 'El tipo de incidencia no existe',
      });
    }

    res.json({ data: tipoIncidencia });
  } catch (error) {
    next(error);
  }
};

/**
 * Actualizar tipo de incidencia
 */
const updateTipoIncidencia = async (req, res, next) => {
  try {
    const { id } = req.params;
    const { nombre, codigo, requiere_aprobacion, requiere_documento, descuenta_salario, esta_activo } = req.body;

    const updateData = {};
    if (nombre !== undefined) updateData.nombre = nombre;
    if (codigo !== undefined) updateData.codigo = codigo;
    if (requiere_aprobacion !== undefined) updateData.requiere_aprobacion = requiere_aprobacion;
    if (requiere_documento !== undefined) updateData.requiere_documento = requiere_documento;
    if (descuenta_salario !== undefined) updateData.descuenta_salario = descuenta_salario;
    if (esta_activo !== undefined) updateData.esta_activo = esta_activo;

    const tipoIncidencia = await prisma.tipoIncidencia.update({
      where: { id },
      data: updateData,
    });

    res.json({
      message: 'Tipo de incidencia actualizado exitosamente',
      data: tipoIncidencia,
    });
  } catch (error) {
    next(error);
  }
};

/**
 * Eliminar tipo de incidencia
 */
const deleteTipoIncidencia = async (req, res, next) => {
  try {
    const { id } = req.params;

    // Verificar si hay incidencias asociadas
    const incidenciasCount = await prisma.incidencia.count({
      where: { tipo_incidencia_id: id },
    });

    if (incidenciasCount > 0) {
      return res.status(400).json({
        error: 'No se puede eliminar',
        message: `Existen ${incidenciasCount} incidencia(s) asociadas a este tipo. Elimínelas primero o desactive el tipo.`,
      });
    }

    await prisma.tipoIncidencia.delete({
      where: { id },
    });

    res.json({
      message: 'Tipo de incidencia eliminado exitosamente',
    });
  } catch (error) {
    next(error);
  }
};

module.exports = {
  createTipoIncidencia,
  getAllTiposIncidencia,
  getTipoIncidenciaById,
  updateTipoIncidencia,
  deleteTipoIncidencia,
};
