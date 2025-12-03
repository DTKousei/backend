import express from 'express';
import templateController from '../controllers/templateController.js';
import {
  createTemplateValidators,
  updateTemplateValidators,
  getReportByIdValidators
} from '../middleware/validators.js';

const router = express.Router();

/**
 * @route   GET /api/plantillas/tipos
 * @desc    Obtiene todos los tipos de reporte disponibles
 * @access  Public
 */
router.get('/tipos', templateController.getReportTypes);

/**
 * @route   POST /api/plantillas
 * @desc    Crea una nueva plantilla de reporte
 * @access  Public
 */
router.post('/', createTemplateValidators, templateController.createTemplate);

/**
 * @route   GET /api/plantillas
 * @desc    Obtiene todas las plantillas (con filtros opcionales)
 * @access  Public
 */
router.get('/', templateController.getTemplates);

/**
 * @route   GET /api/plantillas/:id
 * @desc    Obtiene una plantilla por ID
 * @access  Public
 */
router.get('/:id', getReportByIdValidators, templateController.getTemplateById);

/**
 * @route   PUT /api/plantillas/:id
 * @desc    Actualiza una plantilla existente
 * @access  Public
 */
router.put('/:id', updateTemplateValidators, templateController.updateTemplate);

/**
 * @route   DELETE /api/plantillas/:id
 * @desc    Desactiva una plantilla (soft delete)
 * @access  Public
 */
router.delete('/:id', getReportByIdValidators, templateController.deleteTemplate);

export default router;
