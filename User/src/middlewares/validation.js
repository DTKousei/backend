const { body, param, query, validationResult } = require('express-validator');

/**
 * Validaciones para registro de usuario
 * Siguiendo mejores prácticas de OWASP
 */
const registerValidation = [
  body('usuario')
    .trim()
    .notEmpty()
    .withMessage('El usuario es requerido')
    .isLength({ min: 3, max: 50 })
    .withMessage('El usuario debe tener entre 3 y 50 caracteres')
    .matches(/^[a-zA-Z0-9_-]+$/)
    .withMessage('El usuario solo puede contener letras, números, guiones y guiones bajos')
    .custom((value) => {
      // Prevenir nombres de usuario sensibles
      const forbiddenUsernames = ['admin', 'root', 'superuser', 'administrator', 'system'];
      if (forbiddenUsernames.includes(value.toLowerCase())) {
        throw new Error('Este nombre de usuario no está disponible');
      }
      return true;
    }),

  body('correo_electronico')
    .trim()
    .notEmpty()
    .withMessage('El correo electrónico es requerido')
    .isEmail()
    .withMessage('Debe proporcionar un email válido')
    .normalizeEmail()
    .isLength({ max: 80 })
    .withMessage('El email no debe exceder 80 caracteres')
    .custom((value) => {
      // Validar dominios permitidos (opcional)
      // const allowedDomains = ['gmail.com', 'outlook.com', 'empresa.com'];
      // const domain = value.split('@')[1];
      // if (!allowedDomains.includes(domain)) {
      //   throw new Error('Dominio de email no permitido');
      // }
      return true;
    }),

  body('contrasena')
    .notEmpty()
    .withMessage('La contraseña es requerida')
    .isLength({ min: 8, max: 128 })
    .withMessage('La contraseña debe tener entre 8 y 128 caracteres')
    .matches(/^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]/)
    .withMessage('La contraseña debe contener al menos: una mayúscula, una minúscula, un número y un carácter especial (@$!%*?&)')
    .custom((value) => {
      // Prevenir contraseñas comunes
      const commonPasswords = ['Password123!', 'Admin123!', 'Qwerty123!', 'Welcome123!'];
      if (commonPasswords.includes(value)) {
        throw new Error('Esta contraseña es demasiado común, por favor elige otra');
      }
      return true;
    }),

  body('rol_id')
    .optional()
    .trim()
    .isLength({ min: 5, max: 40 })
    .withMessage('El rol_id debe ser un UUID válido')
];

/**
 * Validaciones para login
 */
const loginValidation = [
  body('correo_electronico')
    .trim()
    .notEmpty()
    .withMessage('El correo electrónico es requerido')
    .isEmail()
    .withMessage('Debe proporcionar un email válido')
    .normalizeEmail()
    .isLength({ max: 80 })
    .withMessage('El email no debe exceder 80 caracteres')
  ,

  body('contrasena')
    .notEmpty()
    .withMessage('La contraseña es requerida')
    .isLength({ min: 1, max: 128 })
    .withMessage('Contraseña inválida')
];

/**
 * Validaciones para cambio de contraseña
 */
const changePasswordValidation = [
  body('contrasena_actual')
    .notEmpty()
    .withMessage('La contraseña actual es requerida')
    .isLength({ min: 1, max: 128 })
    .withMessage('Contraseña actual inválida'),

  body('contrasena_nueva')
    .notEmpty()
    .withMessage('La nueva contraseña es requerida')
    .isLength({ min: 8, max: 128 })
    .withMessage('La nueva contraseña debe tener entre 8 y 128 caracteres')
    .matches(/^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]/)
    .withMessage('La nueva contraseña debe contener al menos: una mayúscula, una minúscula, un número y un carácter especial (@$!%*?&)')
    .custom((value, { req }) => {
      if (value === req.body.contrasena_actual) {
        throw new Error('La nueva contraseña debe ser diferente a la actual');
      }
      return true;
    })
];

/**
 * Validación de UUID en parámetros
 */
const uuidParamValidation = (paramName = 'id') => [
  param(paramName)
    .trim()
    .notEmpty()
    .withMessage(`${paramName} es requerido`)
    .isUUID()
    .withMessage(`${paramName} debe ser un UUID válido`)
];

/**
 * Validación de paginación
 */
const paginationValidation = [
  query('page')
    .optional()
    .isInt({ min: 1 })
    .withMessage('La página debe ser un número entero mayor a 0')
    .toInt(),

  query('limit')
    .optional()
    .isInt({ min: 1, max: 100 })
    .withMessage('El límite debe estar entre 1 y 100')
    .toInt()
];

/**
 * Validación de búsqueda
 */
const searchValidation = [
  query('q')
    .optional()
    .trim()
    .isLength({ min: 1, max: 100 })
    .withMessage('La búsqueda debe tener entre 1 y 100 caracteres')
    .matches(/^[a-zA-Z0-9\s_-]+$/)
    .withMessage('La búsqueda contiene caracteres no permitidos')
];

/**
 * Validación para actualización de perfil
 */
const updateProfileValidation = [
  body('usuario')
    .optional()
    .trim()
    .isLength({ min: 3, max: 50 })
    .withMessage('El usuario debe tener entre 3 y 50 caracteres')
    .matches(/^[a-zA-Z0-9_-]+$/)
    .withMessage('El usuario solo puede contener letras, números, guiones y guiones bajos'),

  body('correo_electronico')
    .optional()
    .trim()
    .isEmail()
    .withMessage('Debe proporcionar un email válido')
    .normalizeEmail()
    .isLength({ max: 80 })
    .withMessage('El email no debe exceder 80 caracteres')
];

/**
 * Middleware para manejar errores de validación
 * Este debe ser el último en la cadena de validaciones
 */
const handleValidationErrors = (req, res, next) => {
  const errors = validationResult(req);

  if (!errors.isEmpty()) {
    // Formatear errores de forma más clara
    const formattedErrors = errors.array().map(err => ({
      field: err.path || err.param,
      message: err.msg,
      value: err.value
    }));

    return res.status(400).json({
      success: false,
      message: 'Errores de validación en los datos proporcionados',
      errors: formattedErrors
    });
  }

  next();
};

/**
 * Sanitización adicional para prevenir XSS
 */
const sanitizeHtml = (req, res, next) => {
  const sanitizeString = (str) => {
    if (typeof str !== 'string') return str;

    // Eliminar tags HTML básicos
    return str
      .replace(/<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi, '')
      .replace(/<iframe\b[^<]*(?:(?!<\/iframe>)<[^<]*)*<\/iframe>/gi, '')
      .replace(/javascript:/gi, '')
      .replace(/on\w+\s*=/gi, '');
  };

  // Sanitizar body
  if (req.body && typeof req.body === 'object') {
    Object.keys(req.body).forEach(key => {
      if (typeof req.body[key] === 'string') {
        req.body[key] = sanitizeString(req.body[key]);
      }
    });
  }

  // Sanitizar query
  if (req.query && typeof req.query === 'object') {
    Object.keys(req.query).forEach(key => {
      if (typeof req.query[key] === 'string') {
        req.query[key] = sanitizeString(req.query[key]);
      }
    });
  }

  next();
};

module.exports = {
  registerValidation,
  loginValidation,
  changePasswordValidation,
  uuidParamValidation,
  paginationValidation,
  searchValidation,
  updateProfileValidation,
  handleValidationErrors,
  sanitizeHtml
};