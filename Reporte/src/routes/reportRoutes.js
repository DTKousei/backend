import express from 'express';
import reportController from '../controllers/reportController.js';
import {
  generateReportValidators,
  getReportByIdValidators,
  getReportsByEmployeeValidators
} from '../middleware/validators.js';

const router = express.Router();

/**
 * @route   POST /api/reportes/generar
 * @desc    Genera un nuevo reporte de asistencia
 * @access  Public
 */
router.post('/generar', generateReportValidators, reportController.generateReport);

/**
 * @route   POST /api/reportes/generar-resumen
 * @desc    Genera un reporte resumido por días
 * @access  Public
 */
router.post('/generar-resumen', generateReportValidators, reportController.generateDailySummaryReport);

/**
 * @route   GET /api/reportes/:id
 * @desc    Obtiene un reporte por ID
 * @access  Public
 */
router.get('/:id', getReportByIdValidators, reportController.getReportById);

/**
 * @route   GET /api/reportes/empleado/lista
 * @desc    Lista reportes de un empleado
 * @access  Public
 */
router.get('/empleado/lista', getReportsByEmployeeValidators, reportController.getReportsByEmployee);

/**
 * @route   GET /api/reportes/:id/descargar
 * @desc    Descarga el archivo de un reporte
 * @access  Public
 */
router.get('/:id/descargar', getReportByIdValidators, reportController.downloadReport);

/**
 * @route   DELETE /api/reportes/:id
 * @desc    Elimina un reporte
 * @access  Public
 */
router.delete('/:id', getReportByIdValidators, reportController.deleteReport);

export default router;
