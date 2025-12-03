import { v4 as uuidv4 } from 'uuid';
import prisma from '../config/database.js';
import { successResponse, errorResponse } from '../utils/responseFormatter.js';

class TemplateController {
  /**
   * Crea una nueva plantilla de reporte
   */
  async createTemplate(req, res, next) {
    try {
      const {
        nombre,
        tipo_reporte_id,
        descripcion,
        parametros,
        esta_activo = true
      } = req.body;

      // Verificar que el tipo de reporte existe
      const tipoReporte = await prisma.tipoReporte.findUnique({
        where: { id: tipo_reporte_id }
      });

      if (!tipoReporte) {
        return res.status(404).json(
          errorResponse('Tipo de reporte no encontrado', 404)
        );
      }

      const plantilla = await prisma.plantillasReporte.create({
        data: {
          id: uuidv4(),
          nombre,
          tipo_reporte_id,
          descripcion,
          parametros: parametros || {},
          esta_activo,
          creado_en: new Date()
        },
        include: {
          tipo_reporte: true
        }
      });

      res.status(201).json(
        successResponse(plantilla, 'Plantilla creada exitosamente', 201)
      );
    } catch (error) {
      next(error);
    }
  }

  /**
   * Obtiene todas las plantillas activas
   */
  async getTemplates(req, res, next) {
    try {
      const { activas_solo = 'true', tipo_reporte_id } = req.query;

      const where = {};
      
      if (activas_solo === 'true') {
        where.esta_activo = true;
      }
      
      if (tipo_reporte_id) {
        where.tipo_reporte_id = parseInt(tipo_reporte_id);
      }

      const plantillas = await prisma.plantillasReporte.findMany({
        where,
        include: {
          tipo_reporte: true
        },
        orderBy: {
          creado_en: 'desc'
        }
      });

      res.json(
        successResponse(plantillas, 'Plantillas obtenidas exitosamente')
      );
    } catch (error) {
      next(error);
    }
  }

  /**
   * Obtiene una plantilla por ID
   */
  async getTemplateById(req, res, next) {
    try {
      const { id } = req.params;

      const plantilla = await prisma.plantillasReporte.findUnique({
        where: { id },
        include: {
          tipo_reporte: true
        }
      });

      if (!plantilla) {
        return res.status(404).json(
          errorResponse('Plantilla no encontrada', 404)
        );
      }

      res.json(
        successResponse(plantilla, 'Plantilla obtenida exitosamente')
      );
    } catch (error) {
      next(error);
    }
  }

  /**
   * Actualiza una plantilla existente
   */
  async updateTemplate(req, res, next) {
    try {
      const { id } = req.params;
      const { nombre, descripcion, parametros, esta_activo } = req.body;

      // Verificar que la plantilla existe
      const plantillaExistente = await prisma.plantillasReporte.findUnique({
        where: { id }
      });

      if (!plantillaExistente) {
        return res.status(404).json(
          errorResponse('Plantilla no encontrada', 404)
        );
      }

      const dataToUpdate = {};
      if (nombre !== undefined) dataToUpdate.nombre = nombre;
      if (descripcion !== undefined) dataToUpdate.descripcion = descripcion;
      if (parametros !== undefined) dataToUpdate.parametros = parametros;
      if (esta_activo !== undefined) dataToUpdate.esta_activo = esta_activo;

      const plantillaActualizada = await prisma.plantillasReporte.update({
        where: { id },
        data: dataToUpdate,
        include: {
          tipo_reporte: true
        }
      });

      res.json(
        successResponse(plantillaActualizada, 'Plantilla actualizada exitosamente')
      );
    } catch (error) {
      next(error);
    }
  }

  /**
   * Desactiva una plantilla (soft delete)
   */
  async deleteTemplate(req, res, next) {
    try {
      const { id } = req.params;

      const plantilla = await prisma.plantillasReporte.findUnique({
        where: { id }
      });

      if (!plantilla) {
        return res.status(404).json(
          errorResponse('Plantilla no encontrada', 404)
        );
      }

      await prisma.plantillasReporte.update({
        where: { id },
        data: { esta_activo: false }
      });

      res.json(
        successResponse(null, 'Plantilla desactivada exitosamente')
      );
    } catch (error) {
      next(error);
    }
  }

  /**
   * Obtiene todos los tipos de reporte disponibles
   */
  async getReportTypes(req, res, next) {
    try {
      const tiposReporte = await prisma.tipoReporte.findMany({
        orderBy: {
          nombre: 'asc'
        }
      });

      res.json(
        successResponse(tiposReporte, 'Tipos de reporte obtenidos exitosamente')
      );
    } catch (error) {
      next(error);
    }
  }
}

export default new TemplateController();
