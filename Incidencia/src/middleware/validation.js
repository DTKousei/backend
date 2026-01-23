const { body, param, validationResult } = require('express-validator');

/**
 * Middleware para verificar resultados de validación
 */
const validate = (req, res, next) => {
  const errors = validationResult(req);
  if (!errors.isEmpty()) {
    return res.status(400).json({
      error: 'Errores de validación',
      details: errors.array(),
    });
  }
  next();
};

/**
 * Validaciones para crear incidencia
 */
const validateCreateIncidencia = [
  body('empleado_id')
    .notEmpty()
    .withMessage('El ID del empleado es requerido')
    .isString()
    .withMessage('El ID del empleado debe ser una cadena'),
  
  body('tipo_incidencia_id')
    .notEmpty()
    .withMessage('El tipo de incidencia es requerido')
    .isUUID()
    .withMessage('El tipo de incidencia debe ser un UUID válido'),
  
  body('fecha_inicio')
    .notEmpty()
    .withMessage('La fecha de inicio es requerida')
    .isISO8601()
    .withMessage('La fecha de inicio debe ser una fecha válida'),
  
  body('fecha_fin')
    .notEmpty()
    .withMessage('La fecha de fin es requerida')
    .isISO8601()
    .withMessage('La fecha de fin debe ser una fecha válida')
    .custom((value, { req }) => {
      if (new Date(value) < new Date(req.body.fecha_inicio)) {
        throw new Error('La fecha de fin debe ser posterior o igual a la fecha de inicio');
      }
      return true;
    }),
  
  body('descripcion')
    .notEmpty()
    .withMessage('La descripción es requerida')
    .isString()
    .withMessage('La descripción debe ser una cadena'),
  
  body('estado_id')
    .notEmpty()
    .withMessage('El estado es requerido')
    .isUUID()
    .withMessage('El estado debe ser un UUID válido'),
  
  validate,
];

/**
 * Validaciones para actualizar incidencia
 */
const validateUpdateIncidencia = [
  param('id')
    .isUUID()
    .withMessage('El ID debe ser un UUID válido'),
  
  body('empleado_id')
    .optional()
    .isString()
    .withMessage('El ID del empleado debe ser una cadena'),
  
  body('tipo_incidencia_id')
    .optional()
    .isUUID()
    .withMessage('El tipo de incidencia debe ser un UUID válido'),
  
  body('fecha_inicio')
    .optional()
    .isISO8601()
    .withMessage('La fecha de inicio debe ser una fecha válida'),
  
  body('fecha_fin')
    .optional()
    .isISO8601()
    .withMessage('La fecha de fin debe ser una fecha válida'),
  
  body('descripcion')
    .optional()
    .isString()
    .withMessage('La descripción debe ser una cadena'),
  
  body('estado_id')
    .optional()
    .isUUID()
    .withMessage('El estado debe ser un UUID válido'),
  
  validate,
];

/**
 * Validaciones para aprobar incidencia
 */
const validateAprobarIncidencia = [
  param('id')
    .isUUID()
    .withMessage('El ID debe ser un UUID válido'),
  
  body('aprobado_por')
    .notEmpty()
    .withMessage('El ID del aprobador es requerido')
    .isString()
    .withMessage('El ID del aprobador debe ser una cadena'),
  
  validate,
];

/**
 * Validaciones para rechazar incidencia
 */
const validateRechazarIncidencia = [
  param('id')
    .isUUID()
    .withMessage('El ID debe ser un UUID válido'),
  
  body('motivo_rechazo')
    .notEmpty()
    .withMessage('El motivo de rechazo es requerido')
    .isString()
    .withMessage('El motivo de rechazo debe ser una cadena'),
  
  validate,
];

/**
 * Validaciones para UUID en parámetros
 */
const validateUUID = [
  param('id')
    .isUUID()
    .withMessage('El ID debe ser un UUID válido'),
  
  validate,
];

/**
 * Validaciones para crear tipo de incidencia
 */
const validateCreateTipoIncidencia = [
  body('nombre')
    .notEmpty()
    .withMessage('El nombre es requerido')
    .isString()
    .withMessage('El nombre debe ser una cadena')
    .isLength({ max: 100 })
    .withMessage('El nombre no puede superar los 100 caracteres'),
  
  body('codigo')
    .notEmpty()
    .withMessage('El código es requerido')
    .isString()
    .withMessage('El código debe ser una cadena')
    .isLength({ max: 20 })
    .withMessage('El código no puede superar los 20 caracteres'),
  
  body('requiere_aprobacion')
    .notEmpty()
    .withMessage('El campo requiere_aprobacion es requerido')
    .isBoolean()
    .withMessage('El campo requiere_aprobacion debe ser un booleano'),
  
  body('requiere_documento')
    .notEmpty()
    .withMessage('El campo requiere_documento es requerido')
    .isBoolean()
    .withMessage('El campo requiere_documento debe ser un booleano'),
  
  body('descuenta_salario')
    .notEmpty()
    .withMessage('El campo descuenta_salario es requerido')
    .isBoolean()
    .withMessage('El campo descuenta_salario debe ser un booleano'),
  
  body('esta_activo')
    .notEmpty()
    .withMessage('El campo esta_activo es requerido')
    .isBoolean()
    .withMessage('El campo esta_activo debe ser un booleano'),

  body('max_dias_anual')
    .optional()
    .isInt({ min: 1 })
    .withMessage('El límite de días anuales debe ser un número entero positivo'),

  body('max_solicitudes_anual')
    .optional()
    .isInt({ min: 1 })
    .withMessage('El límite de solicitudes anuales debe ser un número entero positivo'),

  body('toma_dias_calendario')
    .optional()
    .isBoolean()
    .withMessage('El campo toma_dias_calendario debe ser un booleano'),
  
  validate,
];

/**
 * Validaciones para crear estado
 */
const validateCreateEstado = [
  body('nombre')
    .notEmpty()
    .withMessage('El nombre es requerido')
    .isString()
    .withMessage('El nombre debe ser una cadena')
    .isLength({ max: 50 })
    .withMessage('El nombre no puede superar los 50 caracteres'),
  
  body('descripcion')
    .optional()
    .isString()
    .withMessage('La descripción debe ser una cadena'),
  
  validate,
];

module.exports = {
  validateCreateIncidencia,
  validateUpdateIncidencia,
  validateAprobarIncidencia,
  validateRechazarIncidencia,
  validateUUID,
  validateCreateTipoIncidencia,
  validateCreateEstado,
};
