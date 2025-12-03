import { body, param, query, validationResult } from 'express-validator';
import { REPORT_FORMATS } from '../config/constants.js';

/**
 * Middleware para verificar errores de validación
 */
export const validate = (req, res, next) => {
  const errors = validationResult(req);
  if (!errors.isEmpty()) {
    return res.status(400).json({
      success: false,
      message: 'Errores de validación',
      errors: errors.array()
    });
  }
  next();
};

/**
 * Validadores para generación de reportes
 */
export const generateReportValidators = [
  body('empleado_id')
    .notEmpty().withMessage('El ID del empleado es requerido')
    .isString().withMessage('El ID del empleado debe ser un string'),
  
  body('plantilla_id')
    .notEmpty().withMessage('El ID de la plantilla es requerido')
    .isString().withMessage('El ID de la plantilla debe ser un string')
    .isLength({ min: 36, max: 36 }).withMessage('El ID de la plantilla debe ser un UUID válido'),
  
  body('formato_archivo')
    .notEmpty().withMessage('El formato de archivo es requerido')
    .isIn(Object.values(REPORT_FORMATS)).withMessage(`El formato debe ser uno de: ${Object.values(REPORT_FORMATS).join(', ')}`),
  
  body('fecha_inicio')
    .optional()
    .isISO8601().withMessage('La fecha de inicio debe ser una fecha válida (ISO 8601)'),
  
  body('fecha_fin')
    .optional()
    .isISO8601().withMessage('La fecha de fin debe ser una fecha válida (ISO 8601)'),
  
  body('nombre_reporte')
    .optional()
    .isString().withMessage('El nombre del reporte debe ser un string')
    .isLength({ max: 200 }).withMessage('El nombre del reporte no puede exceder 200 caracteres'),
  
  validate
];

/**
 * Validadores para obtener reporte por ID
 */
export const getReportByIdValidators = [
  param('id')
    .notEmpty().withMessage('El ID del reporte es requerido')
    .isString().withMessage('El ID debe ser un string')
    .isLength({ min: 36, max: 36 }).withMessage('El ID debe ser un UUID válido'),
  
  validate
];

/**
 * Validadores para listar reportes por empleado
 */
export const getReportsByEmployeeValidators = [
  query('empleado_id')
    .notEmpty().withMessage('El ID del empleado es requerido')
    .isString().withMessage('El ID del empleado debe ser un string'),
  
  query('page')
    .optional()
    .isInt({ min: 1 }).withMessage('La página debe ser un número entero mayor a 0'),
  
  query('limit')
    .optional()
    .isInt({ min: 1, max: 100 }).withMessage('El límite debe ser un número entre 1 y 100'),
  
  validate
];

/**
 * Validadores para crear plantilla
 */
export const createTemplateValidators = [
  body('nombre')
    .notEmpty().withMessage('El nombre de la plantilla es requerido')
    .isString().withMessage('El nombre debe ser un string')
    .isLength({ max: 100 }).withMessage('El nombre no puede exceder 100 caracteres'),
  
  body('tipo_reporte_id')
    .notEmpty().withMessage('El tipo de reporte es requerido')
    .isInt({ min: 1 }).withMessage('El tipo de reporte debe ser un número entero válido'),
  
  body('descripcion')
    .optional()
    .isString().withMessage('La descripción debe ser un string'),
  
  body('parametros')
    .optional()
    .isObject().withMessage('Los parámetros deben ser un objeto JSON'),
  
  body('esta_activo')
    .optional()
    .isBoolean().withMessage('esta_activo debe ser un valor booleano'),
  
  validate
];

/**
 * Validadores para actualizar plantilla
 */
export const updateTemplateValidators = [
  param('id')
    .notEmpty().withMessage('El ID de la plantilla es requerido')
    .isString().withMessage('El ID debe ser un string')
    .isLength({ min: 36, max: 36 }).withMessage('El ID debe ser un UUID válido'),
  
  body('nombre')
    .optional()
    .isString().withMessage('El nombre debe ser un string')
    .isLength({ max: 100 }).withMessage('El nombre no puede exceder 100 caracteres'),
  
  body('descripcion')
    .optional()
    .isString().withMessage('La descripción debe ser un string'),
  
  body('parametros')
    .optional()
    .isObject().withMessage('Los parámetros deben ser un objeto JSON'),
  
  body('esta_activo')
    .optional()
    .isBoolean().withMessage('esta_activo debe ser un valor booleano'),
  
  validate
];
