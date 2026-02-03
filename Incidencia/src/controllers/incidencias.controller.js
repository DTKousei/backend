const prisma = require('../utils/prisma');
const fs = require('fs');
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

    // --- Validación de Límites (Días y Solicitudes) ---
    const tipoIncidencia = await prisma.tipoIncidencia.findUnique({
      where: { id: tipo_incidencia_id },
    });

    if (!tipoIncidencia) {
      if (req.file) deleteFile(getFileUrl(req.file.filename));
      return res.status(404).json({ error: 'No encontrado', message: 'Tipo de incidencia no existe' });
    }

    // Solo validamos si hay límites configurados
    if (tipoIncidencia.max_dias_anual || tipoIncidencia.max_solicitudes_anual) {
      const fechaSolicitud = new Date(fecha_inicio);
      const startYear = fechaSolicitud.getFullYear();
      const startOfYear = new Date(startYear, 0, 1); // 1 de Enero
      const endOfYear = new Date(startYear, 11, 31, 23, 59, 59); // 31 de Diciembre

      // Buscar incidencias previas del mismo tipo para este empleado en el año actual (excluyendo rechazadas)
      const incidenciasPrevias = await prisma.incidencia.findMany({
        where: {
          empleado_id,
          tipo_incidencia_id,
          motivo_rechazo: null, // Contamos pendientes y aprobadas
          fecha_inicio: {
            gte: startOfYear,
            lte: endOfYear
          }
        }
      });

      // Validar límite de solicitudes (frecuencia)
      if (tipoIncidencia.max_solicitudes_anual && incidenciasPrevias.length >= tipoIncidencia.max_solicitudes_anual) {
        if (req.file) deleteFile(getFileUrl(req.file.filename));
        return res.status(400).json({
          error: 'Límite excedido',
          message: `Ha alcanzado el límite de ${tipoIncidencia.max_solicitudes_anual} solicitud(es) por año para este tipo de incidencia.`
        });
      }

      // Validar límite de días acumulados
      if (tipoIncidencia.max_dias_anual) {
        const countDays = (start, end, calendarDays) => {
          let count = 0;
          let current = new Date(start);
          const endDate = new Date(end);
          // Normalizar horas para comparar solo fechas
          current.setHours(0,0,0,0);
          endDate.setHours(0,0,0,0);

          while (current <= endDate) {
            const day = current.getDay();
            // calendarDays=true cuenta todo. calendarDays=false excluye Domingo(0) y Sábado(6)
            if (calendarDays || (day !== 0 && day !== 6)) {
              count++;
            }
            current.setDate(current.getDate() + 1);
          }
          return count;
        };

        let diasConsumidos = 0;
        for (const inc of incidenciasPrevias) {
          diasConsumidos += countDays(inc.fecha_inicio, inc.fecha_fin, tipoIncidencia.toma_dias_calendario);
        }

        const diasSolicitados = countDays(fecha_inicio, fecha_fin, tipoIncidencia.toma_dias_calendario);

        if (diasConsumidos + diasSolicitados > tipoIncidencia.max_dias_anual) {
          if (req.file) deleteFile(getFileUrl(req.file.filename));
          return res.status(400).json({
            error: 'Límite excedido',
            message: `Esta solicitud de ${diasSolicitados} días excede su saldo. Ha consumido ${diasConsumidos} de ${tipoIncidencia.max_dias_anual} días permitidos este año.`
          });
        }
      }
    }
    // --- Fin Validación de Límites ---

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
    const { page = 1, limit, empleado_id, estado_id, tipo_incidencia_id } = req.query;

    // Construir filtros
    const where = {};
    if (empleado_id) where.empleado_id = empleado_id;
    if (estado_id) where.estado_id = estado_id;
    if (tipo_incidencia_id) where.tipo_incidencia_id = tipo_incidencia_id;

    // Configurar paginación solo si se envía limit
    let paginationOptions = {};
    if (limit) {
      paginationOptions = {
        skip: (parseInt(page) - 1) * parseInt(limit),
        take: parseInt(limit),
      };
    }

    // Obtener incidencias
    const [incidencias, total] = await Promise.all([
      prisma.incidencia.findMany({
        where,
        ...paginationOptions,
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
        limit: limit ? parseInt(limit) : total,
        totalPages: limit ? Math.ceil(total / parseInt(limit)) : 1,
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

/**
 * Obtener reporte de sábana (conteo de incidencias)
 */
const getReporteSabana = async (req, res, next) => {
  try {
    const { fecha_inicio, fecha_fin, empleado_ids } = req.body;

    // Validar fechas
    if (!fecha_inicio || !fecha_fin) {
      return res.status(400).json({
        error: 'Fechas requeridas',
        message: 'Debe proporcionar fecha_inicio y fecha_fin',
      });
    }

    const reportStartDate = new Date(fecha_inicio);
    const reportEndDate = new Date(fecha_fin);

    // Filtros dinámicos
    const where = {
      fecha_inicio: {
        gte: reportStartDate,
        lte: reportEndDate,
      },
    };

    if (empleado_ids && Array.isArray(empleado_ids) && empleado_ids.length > 0) {
      where.empleado_id = { in: empleado_ids };
    }

    // Obtener conteo agrupado
    const conteo = await prisma.incidencia.groupBy({
      by: ['empleado_id', 'tipo_incidencia_id', 'estado_id'],
      _count: {
        _all: true,
      },
      where,
    });

    // Obtener catálogos para mapear nombres
    const [tipos, estados] = await Promise.all([
      prisma.tipoIncidencia.findMany(),
      prisma.estado.findMany(),
    ]);

    // Crear mapas para búsqueda rápida
    const tiposMap = tipos.reduce((acc, curr) => ({ ...acc, [curr.id]: curr.nombre }), {});
    const estadosMap = estados.reduce((acc, curr) => ({ ...acc, [curr.id]: curr.nombre }), {});

    // Formatear respuesta
    const reporte = conteo.map((item) => ({
      empleado_id: item.empleado_id,
      tipo_incidencia_id: item.tipo_incidencia_id,
      tipo_incidencia: tiposMap[item.tipo_incidencia_id] || 'Desconocido',
      estado_id: item.estado_id,
      estado: estadosMap[item.estado_id] || 'Desconocido',
      total: item._count._all,
    }));

    res.json({
      data: reporte,
      meta: {
        fecha_inicio: reportStartDate,
        fecha_fin: reportEndDate,
        cantidad_registros: reporte.length
      }
    });

  } catch (error) {
    next(error);
  }
};

/**
 * Obtener documento de incidencia
 */
const getIncidenciaDocumento = async (req, res, next) => {
  try {
    const { id } = req.params;

    const incidencia = await prisma.incidencia.findUnique({
      where: { id },
      select: { url_documento: true }
    });

    if (!incidencia || !incidencia.url_documento) {
      return res.status(404).json({
        error: 'No encontrado',
        message: 'La incidencia no tiene documento adjunto',
      });
    }

    const filePath = incidencia.url_documento;

    if (!fs.existsSync(filePath)) {
      return res.status(404).json({
        error: 'No encontrado',
        message: 'El archivo físico no existe',
      });
    }

    res.sendFile(filePath);
  } catch (error) {
    next(error);
  }
};

/**
 * Obtener saldos y consumos de incidencias
 */
const getSaldosIncidencias = async (req, res, next) => {
  try {
    const { empleado_id, anio } = req.query;
    
    // Validar año o usar el actual
    const year = anio && !isNaN(parseInt(anio)) ? parseInt(anio) : new Date().getFullYear();
    const startOfYear = new Date(year, 0, 1);
    const endOfYear = new Date(year, 11, 31, 23, 59, 59);

    // 1. Obtener tipos de incidencia activos y sus límites
    const tiposIncidencia = await prisma.tipoIncidencia.findMany({
      where: { esta_activo: true }
    });

    // 2. Construir filtro de incidencias
    const whereIncidencias = {
      motivo_rechazo: null, // Solo aprobadas o pendientes
      fecha_inicio: {
        gte: startOfYear,
        lte: endOfYear
      }
    };
    
    // Limpiar empleado_id de espacios
    if (empleado_id) {
        whereIncidencias.empleado_id = empleado_id.trim();
    }

    // 3. Obtener incidencias del periodo
    const incidencias = await prisma.incidencia.findMany({
      where: whereIncidencias,
      orderBy: { fecha_inicio: 'asc' },
      include: { tipo_incidencia: true } // Para tener referencia si fuera necesario
    });

    // 4. Agrupar por Empleado -> Tipo
    const reporte = {};

    // Helper para contar días
    const countDays = (start, end, calendarDays) => {
      let count = 0;
      let current = new Date(start);
      const endDate = new Date(end);
      current.setHours(0,0,0,0);
      endDate.setHours(0,0,0,0);
      while (current <= endDate) {
        const day = current.getDay();
        if (calendarDays || (day !== 0 && day !== 6)) count++;
        current.setDate(current.getDate() + 1);
      }
      return count;
    };

    // Inicializar estructura para empleados encontrados en incidencias (o solo el solicitado)
    // Si se peridó un empleado específico pero no tiene incidencias, igual deberíamos mostrar sus saldos en 0?
    // Para simplificar, iteramos sobre las incidencias encontradas. 
    // Si se requiere ver empleados sin movimientos, se necesitaría consultar la tabla empleados.
    // Asumiremos que mostramos solo quienes tener actividad O si es un empleado_id especifico.

    const empleadosSet = new Set(incidencias.map(i => i.empleado_id));
    if (empleado_id) empleadosSet.add(empleado_id);

    for (const empId of empleadosSet) {
      reporte[empId] = tiposIncidencia.map(tipo => ({
        tipo_id: tipo.id,
        tipo_nombre: tipo.nombre,
        tipo_codigo: tipo.codigo,
        limites: {
          dias: tipo.max_dias_anual,
          solicitudes: tipo.max_solicitudes_anual
        },
        consumido: {
          dias: 0,
          solicitudes: 0
        },
        restante: {
          dias: tipo.max_dias_anual, // Si es null, sigue siendo null (infinito)
          solicitudes: tipo.max_solicitudes_anual
        },
        detalle: []
      }));
    }

    // Procesar incidencias
    for (const inc of incidencias) {
      if (!reporte[inc.empleado_id]) continue; // Por seguridad

      // Buscar el tipo en el reporte del empleado
      const tipoReporte = reporte[inc.empleado_id].find(t => t.tipo_id === inc.tipo_incidencia_id);
      
      if (tipoReporte) {
        // Encontrar configuración real del tipo para saber si cuenta fines de semana
        const tipoConfig = tiposIncidencia.find(t => t.id === inc.tipo_incidencia_id);
        const diasCalculados = countDays(inc.fecha_inicio, inc.fecha_fin, tipoConfig.toma_dias_calendario);

        // Actualizar consumos
        tipoReporte.consumido.dias += diasCalculados;
        tipoReporte.consumido.solicitudes += 1;

        // Agregar detalle
        tipoReporte.detalle.push({
          id: inc.id,
          fecha_inicio: inc.fecha_inicio.toISOString().split('T')[0],
          fecha_fin: inc.fecha_fin.toISOString().split('T')[0],
          dias: diasCalculados,
          estado_id: inc.estado_id
        });
      }
    }

    // Calcular restantes finales
    Object.values(reporte).forEach(listaTipos => {
      listaTipos.forEach(item => {
        if (item.limites.dias !== null) {
          item.restante.dias = Math.max(0, item.limites.dias - item.consumido.dias);
        } else {
            item.restante.dias = null; // Infinito
        }

        if (item.limites.solicitudes !== null) {
          item.restante.solicitudes = Math.max(0, item.limites.solicitudes - item.consumido.solicitudes);
        } else {
            item.restante.solicitudes = null; // Infinito
        }
      });
    });

    // Formatear respuesta array
    const dataResponse = Object.keys(reporte).map(empId => ({
      empleado_id: empId,
      saldos: reporte[empId]
    }));

    res.json({
      anio: year,
      data: dataResponse
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
  getReporteSabana,
  getIncidenciaDocumento,
  getSaldosIncidencias,
};
