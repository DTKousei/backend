import { body, param, query, validationResult } from 'express-validator';
import { AppError } from './error.middleware.js';

/**
 * Middleware para manejar resultados de validación
 */
export const handleValidationErrors = (req, res, next) => {
  const errors = validationResult(req);
  if (!errors.isEmpty()) {
    return res.status(400).json({
      success: false,
      error: 'Error de validación',
      details: errors.array()
    });
  }
  next();
};

/**
 * Validaciones para PermisoTipo
 */
export const validatePermisoTipo = [
  body('nombre')
    .trim()
    .notEmpty().withMessage('El nombre es requerido')
    .isLength({ max: 100 }).withMessage('El nombre no puede exceder 100 caracteres'),
  
  body('codigo')
    .trim()
    .notEmpty().withMessage('El código es requerido')
    .isLength({ max: 20 }).withMessage('El código no puede exceder 20 caracteres')
    .toUpperCase(),
  
  body('descripcion')
    .optional()
    .trim(),
  
  body('requiere_firma_institucion')
    .optional()
    .isBoolean().withMessage('requiere_firma_institucion debe ser booleano'),
  
  body('tiempo_maximo_horas')
    .optional()
    .isInt({ min: 1 }).withMessage('tiempo_maximo_horas debe ser un número entero positivo'),
  
  body('esta_activo')
    .optional()
    .isBoolean().withMessage('esta_activo debe ser booleano'),
  
  handleValidationErrors
];

/**
 * Validaciones para Estado
 */
export const validateEstado = [
  body('nombre')
    .trim()
    .notEmpty().withMessage('El nombre es requerido')
    .isLength({ max: 50 }).withMessage('El nombre no puede exceder 50 caracteres'),
  
  body('codigo')
    .trim()
    .notEmpty().withMessage('El código es requerido')
    .isLength({ max: 20 }).withMessage('El código no puede exceder 20 caracteres')
    .toUpperCase(),
  
  body('descripcion')
    .optional()
    .trim(),
  
  handleValidationErrors
];

/**
 * Validaciones para crear Permiso
 */
export const validateCreatePermiso = [
  body('empleado_id')
    .trim()
    .isLength({ min: 7, max: 9 })
    .withMessage('El ID del empledo es el DNI'),
  
  body('tipo_permiso_id')
    .trim()
    .notEmpty().withMessage('El tipo de permiso es requerido')
    .isUUID().withMessage('El tipo de permiso debe ser un UUID válido'),
  
  body('fecha_hora_inicio')
    .notEmpty().withMessage('La fecha y hora de inicio es requerida')
    .isISO8601().withMessage('Formato de fecha inválido'),
  
  body('fecha_hora_fin')
    .optional()
    .isISO8601().withMessage('Formato de fecha inválido'),
  
  body('motivo')
    .trim()
    .notEmpty().withMessage('El motivo es requerido'),
  
  body('justificacion')
    .trim()
    .notEmpty().withMessage('La justificación es requerida'),
  
  body('institucion_visitada')
    .optional()
    .trim(),
  
  handleValidationErrors
];

/**
 * Validaciones para actualizar Permiso
 */
export const validateUpdatePermiso = [
  body('fecha_hora_inicio')
    .optional()
    .isISO8601().withMessage('Formato de fecha inválido'),
  
  body('fecha_hora_fin')
    .optional()
    .isISO8601().withMessage('Formato de fecha inválido'),
  
  body('motivo')
    .optional()
    .trim(),
  
  body('justificacion')
    .optional()
    .trim(),
  
  body('institucion_visitada')
    .optional()
    .trim(),
  
  handleValidationErrors
];

/**
 * Validaciones para firmar
 */
export const validateFirma = [
  body('tipo_firma')
    .trim()
    .notEmpty().withMessage('El tipo de firma es requerido')
    .isIn(['solicitante', 'jefe_area', 'rrhh', 'institucion'])
    .withMessage('Tipo de firma inválido'),
  
  body('firma')
    .trim()
    .notEmpty().withMessage('La firma es requerida'),
  
  handleValidationErrors
];

/**
 * Validación de UUID en parámetros
 */
export const validateUUID = [
  param('id')
    .isUUID().withMessage('ID inválido'),
  
  handleValidationErrors
];

/**
 * Validaciones para firma digital ONPE
 */
export const validateFirmaDigital = [
  body('tipo_firma')
    .trim()
    .notEmpty().withMessage('El tipo de firma es requerido')
    .isIn(['solicitante', 'jefe_area', 'rrhh', 'institucion'])
    .withMessage('Tipo de firma inválido'),
  
  body('firma_digital')
    .trim()
    .notEmpty().withMessage('La firma digital es requerida'),
  
  body('certificado')
    .optional()
    .isObject().withMessage('El certificado debe ser un objeto'),
  
  handleValidationErrors
];
