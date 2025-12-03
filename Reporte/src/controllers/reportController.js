import { v4 as uuidv4 } from 'uuid';
import prisma from '../config/database.js';
import attendanceApiService from '../services/attendanceApiService.js';
import excelGeneratorService from '../services/excelGeneratorService.js';
import pdfGeneratorService from '../services/pdfGeneratorService.js';
import fileStorageService from '../services/fileStorageService.js';
import { successResponse, errorResponse } from '../utils/responseFormatter.js';
import { REPORT_FORMATS } from '../config/constants.js';

class ReportController {
  /**
   * Genera un nuevo reporte de asistencia
   */
  async generateReport(req, res, next) {
    try {
      const {
        empleado_id,
        plantilla_id,
        formato_archivo,
        fecha_inicio,
        fecha_fin,
        nombre_reporte
      } = req.body;

      // Verificar que la plantilla existe y está activa
      const plantilla = await prisma.plantillasReporte.findUnique({
        where: { id: plantilla_id },
        include: { tipo_reporte: true }
      });

      if (!plantilla) {
        return res.status(404).json(
          errorResponse('Plantilla no encontrada', 404)
        );
      }

      if (!plantilla.esta_activo) {
        return res.status(400).json(
          errorResponse('La plantilla no está activa', 400)
        );
      }

      // Obtener datos de asistencia desde la API externa
      const filters = {
        user_id: empleado_id,
        fecha_inicio,
        fecha_fin
      };

      const attendanceData = await attendanceApiService.getAttendancesByUser(empleado_id, filters);

      if (!attendanceData || attendanceData.length === 0) {
        return res.status(404).json(
          errorResponse('No se encontraron datos de asistencia para el empleado en el período especificado', 404)
        );
      }

      // Generar el reporte según el formato
      let fileBuffer;
      let fileExtension;
      const reportOptions = {
        title: nombre_reporte || `Reporte de Asistencia - ${plantilla.nombre}`,
        empleadoId: empleado_id,
        fechaInicio: fecha_inicio,
        fechaFin: fecha_fin
      };

      if (formato_archivo === REPORT_FORMATS.XLSX) {
        fileBuffer = await excelGeneratorService.generateAttendanceReport(attendanceData, reportOptions);
        fileExtension = 'xlsx';
      } else if (formato_archivo === REPORT_FORMATS.PDF) {
        fileBuffer = await pdfGeneratorService.generateAttendanceReport(attendanceData, reportOptions);
        fileExtension = 'pdf';
      } else {
        return res.status(400).json(
          errorResponse('Formato de archivo no soportado. Use XLSX o PDF', 400)
        );
      }

      // Guardar el archivo
      const fileName = fileStorageService.generateFileName(
        nombre_reporte || `reporte_${empleado_id}`,
        fileExtension
      );
      const filePath = await fileStorageService.saveFile(fileBuffer, fileName);

      // Guardar registro en la base de datos
      const reporteGenerado = await prisma.reportesGenerados.create({
        data: {
          id: uuidv4(),
          Empleado_id: empleado_id,
          plantilla_id: plantilla_id,
          nombre_reporte: nombre_reporte || `Reporte de Asistencia - ${plantilla.nombre}`,
          parametros: {
            fecha_inicio,
            fecha_fin,
            ...filters
          },
          ruta_archivo: fileStorageService.getRelativePath(fileName),
          formato_archivo: formato_archivo,
          cantidad_registros: attendanceData.length,
          generado_en: new Date()
        },
        include: {
          plantilla: {
            include: {
              tipo_reporte: true
            }
          }
        }
      });

      res.status(201).json(
        successResponse(reporteGenerado, 'Reporte generado exitosamente', 201)
      );
    } catch (error) {
      next(error);
    }
  }

  /**
   * Obtiene un reporte por ID
   */
  async getReportById(req, res, next) {
    try {
      const { id } = req.params;

      const reporte = await prisma.reportesGenerados.findUnique({
        where: { id },
        include: {
          plantilla: {
            include: {
              tipo_reporte: true
            }
          }
        }
      });

      if (!reporte) {
        return res.status(404).json(
          errorResponse('Reporte no encontrado', 404)
        );
      }

      res.json(successResponse(reporte, 'Reporte obtenido exitosamente'));
    } catch (error) {
      next(error);
    }
  }

  /**
   * Lista reportes de un empleado con paginación
   */
  async getReportsByEmployee(req, res, next) {
    try {
      const { empleado_id, page = 1, limit = 10 } = req.query;
      const skip = (parseInt(page) - 1) * parseInt(limit);

      const [reportes, total] = await Promise.all([
        prisma.reportesGenerados.findMany({
          where: { Empleado_id: empleado_id },
          include: {
            plantilla: {
              include: {
                tipo_reporte: true
              }
            }
          },
          orderBy: { generado_en: 'desc' },
          skip,
          take: parseInt(limit)
        }),
        prisma.reportesGenerados.count({
          where: { Empleado_id: empleado_id }
        })
      ]);

      res.json({
        success: true,
        data: reportes,
        pagination: {
          page: parseInt(page),
          limit: parseInt(limit),
          total,
          totalPages: Math.ceil(total / parseInt(limit))
        }
      });
    } catch (error) {
      next(error);
    }
  }

  /**
   * Descarga el archivo de un reporte
   */
  async downloadReport(req, res, next) {
    try {
      const { id } = req.params;

      const reporte = await prisma.reportesGenerados.findUnique({
        where: { id }
      });

      if (!reporte) {
        return res.status(404).json(
          errorResponse('Reporte no encontrado', 404)
        );
      }

      // Extraer el nombre del archivo de la ruta
      const fileName = reporte.ruta_archivo.split(/[/\\]/).pop();
      
      // Verificar que el archivo existe
      const fileExists = await fileStorageService.fileExists(fileName);
      if (!fileExists) {
        return res.status(404).json(
          errorResponse('Archivo del reporte no encontrado', 404)
        );
      }

      // Leer el archivo
      const fileBuffer = await fileStorageService.readFile(fileName);

      // Configurar headers para descarga
      const contentType = reporte.formato_archivo === 'PDF' 
        ? 'application/pdf' 
        : 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet';

      res.setHeader('Content-Type', contentType);
      res.setHeader('Content-Disposition', `attachment; filename="${fileName}"`);
      res.send(fileBuffer);
    } catch (error) {
      next(error);
    }
  }

  /**
   * Elimina un reporte
   */
  async deleteReport(req, res, next) {
    try {
      const { id } = req.params;

      const reporte = await prisma.reportesGenerados.findUnique({
        where: { id }
      });

      if (!reporte) {
        return res.status(404).json(
          errorResponse('Reporte no encontrado', 404)
        );
      }

      // Eliminar archivo físico
      const fileName = reporte.ruta_archivo.split(/[/\\]/).pop();
      try {
        await fileStorageService.deleteFile(fileName);
      } catch (error) {
        console.warn('No se pudo eliminar el archivo físico:', error.message);
      }

      // Eliminar registro de la base de datos
      await prisma.reportesGenerados.delete({
        where: { id }
      });

      res.json(successResponse(null, 'Reporte eliminado exitosamente'));
    } catch (error) {
      next(error);
    }
  }

  /**
   * Genera un reporte resumido por días
   */
  async generateDailySummaryReport(req, res, next) {
    try {
      const {
        empleado_id,
        plantilla_id,
        formato_archivo,
        fecha_inicio,
        fecha_fin,
        nombre_reporte
      } = req.body;

      // Verificar plantilla
      const plantilla = await prisma.plantillasReporte.findUnique({
        where: { id: plantilla_id }
      });

      if (!plantilla || !plantilla.esta_activo) {
        return res.status(404).json(
          errorResponse('Plantilla no encontrada o inactiva', 404)
        );
      }

      // Obtener y procesar datos
      const attendanceData = await attendanceApiService.getAttendancesByUser(empleado_id, {
        fecha_inicio,
        fecha_fin
      });

      const processedData = attendanceApiService.processAttendanceData(attendanceData);

      // Generar reporte
      let fileBuffer;
      let fileExtension;
      const reportOptions = {
        title: nombre_reporte || 'Resumen Diario de Asistencia',
        empleadoId: empleado_id,
        fechaInicio: fecha_inicio,
        fechaFin: fecha_fin
      };

      if (formato_archivo === REPORT_FORMATS.XLSX) {
        fileBuffer = await excelGeneratorService.generateDailySummaryReport(processedData, reportOptions);
        fileExtension = 'xlsx';
      } else if (formato_archivo === REPORT_FORMATS.PDF) {
        fileBuffer = await pdfGeneratorService.generateDailySummaryReport(processedData, reportOptions);
        fileExtension = 'pdf';
      } else {
        return res.status(400).json(
          errorResponse('Formato no soportado', 400)
        );
      }

      // Guardar archivo
      const fileName = fileStorageService.generateFileName(
        nombre_reporte || `resumen_${empleado_id}`,
        fileExtension
      );
      await fileStorageService.saveFile(fileBuffer, fileName);

      // Guardar en BD
      const reporteGenerado = await prisma.reportesGenerados.create({
        data: {
          id: uuidv4(),
          Empleado_id: empleado_id,
          plantilla_id: plantilla_id,
          nombre_reporte: nombre_reporte || 'Resumen Diario de Asistencia',
          parametros: { fecha_inicio, fecha_fin, tipo: 'resumen_diario' },
          ruta_archivo: fileStorageService.getRelativePath(fileName),
          formato_archivo: formato_archivo,
          cantidad_registros: processedData.length,
          generado_en: new Date()
        }
      });

      res.status(201).json(
        successResponse(reporteGenerado, 'Reporte resumido generado exitosamente', 201)
      );
    } catch (error) {
      next(error);
    }
  }
}

export default new ReportController();
