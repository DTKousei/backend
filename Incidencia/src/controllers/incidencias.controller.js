const prisma = require('../utils/prisma');
const { deleteFile, getFileUrl } = require('../utils/fileManager');

/**
 * Crear nueva incidencia
 */
const createIncidencia = async (req, res, next) => {
  try {
    const { empleado_id, tipo_incidencia_id, fecha_inicio, fecha_fin, descripcion, estado_id } = req.body;

    // Verificar que se haya subido un archivo
    if (!req.file) {
      return res.status(400).json({
        error: 'Documento requerido',
        message: 'Debe cargar un documento PDF como justificante',
      });
    }

    // Crear la incidencia
    const incidencia = await prisma.incidencia.create({
      data: {
        empleado_id,
        tipo_incidencia_id,
        fecha_inicio: new Date(fecha_inicio),
        fecha_fin: new Date(fecha_fin),
        descripcion,
        url_documento: getFileUrl(req.file.filename),
        estado_id,
        creado_en: new Date(),
      },
      include: {
        tipo_incidencia: true,
        estado: true,
      },
    });

    res.status(201).json({
      message: 'Incidencia creada exitosamente',
      data: incidencia,
    });
  } catch (error) {
    // Si hay error, eliminar el archivo subido
    if (req.file) {
      deleteFile(getFileUrl(req.file.filename));
    }
    next(error);
  }
};

/**
 * Obtener todas las incidencias
 */
const getAllIncidencias = async (req, res, next) => {
  try {
    const { page = 1, limit = 10, empleado_id, estado_id, tipo_incidencia_id } = req.query;

    const skip = (parseInt(page) - 1) * parseInt(limit);
    const take = parseInt(limit);

    // Construir filtros
    const where = {};
    if (empleado_id) where.empleado_id = empleado_id;
    if (estado_id) where.estado_id = estado_id;
    if (tipo_incidencia_id) where.tipo_incidencia_id = tipo_incidencia_id;

    // Obtener incidencias con paginación
    const [incidencias, total] = await Promise.all([
      prisma.incidencia.findMany({
        where,
        skip,
        take,
        include: {
          tipo_incidencia: true,
          estado: true,
        },
        orderBy: {
          creado_en: 'desc',
        },
      }),
      prisma.incidencia.count({ where }),
    ]);

    res.json({
      data: incidencias,
      pagination: {
        total,
        page: parseInt(page),
        limit: parseInt(limit),
        totalPages: Math.ceil(total / parseInt(limit)),
      },
    });
  } catch (error) {
    next(error);
  }
};

/**
 * Obtener incidencia por ID
 */
const getIncidenciaById = async (req, res, next) => {
  try {
    const { id } = req.params;

    const incidencia = await prisma.incidencia.findUnique({
      where: { id },
      include: {
        tipo_incidencia: true,
        estado: true,
      },
    });

    if (!incidencia) {
      return res.status(404).json({
        error: 'No encontrado',
        message: 'La incidencia no existe',
      });
    }

    res.json({ data: incidencia });
  } catch (error) {
    next(error);
  }
};

/**
 * Actualizar incidencia
 */
const updateIncidencia = async (req, res, next) => {
  try {
    const { id } = req.params;
    const { empleado_id, tipo_incidencia_id, fecha_inicio, fecha_fin, descripcion, estado_id } = req.body;

    // Verificar que la incidencia existe
    const incidenciaExistente = await prisma.incidencia.findUnique({
      where: { id },
    });

    if (!incidenciaExistente) {
      // Si hay archivo nuevo, eliminarlo
      if (req.file) {
        deleteFile(getFileUrl(req.file.filename));
      }
      return res.status(404).json({
        error: 'No encontrado',
        message: 'La incidencia no existe',
      });
    }

    // Preparar datos de actualización
    const updateData = {};
    if (empleado_id) updateData.empleado_id = empleado_id;
    if (tipo_incidencia_id) updateData.tipo_incidencia_id = tipo_incidencia_id;
    if (fecha_inicio) updateData.fecha_inicio = new Date(fecha_inicio);
    if (fecha_fin) updateData.fecha_fin = new Date(fecha_fin);
    if (descripcion) updateData.descripcion = descripcion;
    if (estado_id) updateData.estado_id = estado_id;

    // Si hay nuevo archivo, actualizar y eliminar el anterior
    if (req.file) {
      updateData.url_documento = getFileUrl(req.file.filename);
      // Eliminar archivo anterior
      deleteFile(incidenciaExistente.url_documento);
    }

    // Actualizar la incidencia
    const incidencia = await prisma.incidencia.update({
      where: { id },
      data: updateData,
      include: {
        tipo_incidencia: true,
        estado: true,
      },
    });

    res.json({
      message: 'Incidencia actualizada exitosamente',
      data: incidencia,
    });
  } catch (error) {
    // Si hay error y se subió archivo nuevo, eliminarlo
    if (req.file) {
      deleteFile(getFileUrl(req.file.filename));
    }
    next(error);
  }
};

/**
 * Eliminar incidencia
 */
const deleteIncidencia = async (req, res, next) => {
  try {
    const { id } = req.params;

    // Obtener la incidencia para eliminar el archivo
    const incidencia = await prisma.incidencia.findUnique({
      where: { id },
    });

    if (!incidencia) {
      return res.status(404).json({
        error: 'No encontrado',
        message: 'La incidencia no existe',
      });
    }

    // Eliminar la incidencia
    await prisma.incidencia.delete({
      where: { id },
    });

    // Eliminar el archivo asociado
    deleteFile(incidencia.url_documento);

    res.json({
      message: 'Incidencia eliminada exitosamente',
    });
  } catch (error) {
    next(error);
  }
};

/**
 * Aprobar incidencia
 */
const aprobarIncidencia = async (req, res, next) => {
  try {
    const { id } = req.params;
    const { aprobado_por } = req.body;

    const incidencia = await prisma.incidencia.update({
      where: { id },
      data: {
        aprobado_por,
        aprobado_en: new Date(),
        motivo_rechazo: null, // Limpiar motivo de rechazo si existía
      },
      include: {
        tipo_incidencia: true,
        estado: true,
      },
    });

    res.json({
      message: 'Incidencia aprobada exitosamente',
      data: incidencia,
    });
  } catch (error) {
    next(error);
  }
};

/**
 * Rechazar incidencia
 */
const rechazarIncidencia = async (req, res, next) => {
  try {
    const { id } = req.params;
    const { motivo_rechazo } = req.body;

    const incidencia = await prisma.incidencia.update({
      where: { id },
      data: {
        motivo_rechazo,
        aprobado_por: null, // Limpiar aprobador si existía
        aprobado_en: null, // Limpiar fecha de aprobación si existía
      },
      include: {
        tipo_incidencia: true,
        estado: true,
      },
    });

    res.json({
      message: 'Incidencia rechazada',
      data: incidencia,
    });
  } catch (error) {
    next(error);
  }
};

module.exports = {
  createIncidencia,
  getAllIncidencias,
  getIncidenciaById,
  updateIncidencia,
  deleteIncidencia,
  aprobarIncidencia,
  rechazarIncidencia,
};
