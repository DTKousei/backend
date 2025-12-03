/**
 * Middleware de manejo centralizado de errores
 */
export const errorHandler = (err, req, res, next) => {
  console.error('Error:', err);

  // Error de validación de Prisma
  if (err.code === 'P2002') {
    return res.status(409).json({
      success: false,
      error: 'Ya existe un registro con estos datos únicos',
      details: err.meta
    });
  }

  // Error de registro no encontrado en Prisma
  if (err.code === 'P2025') {
    return res.status(404).json({
      success: false,
      error: 'Registro no encontrado'
    });
  }

  // Error de validación de express-validator
  if (err.array) {
    return res.status(400).json({
      success: false,
      error: 'Error de validación',
      details: err.array()
    });
  }

  // Error de Multer (carga de archivos)
  if (err.name === 'MulterError') {
    return res.status(400).json({
      success: false,
      error: 'Error al cargar el archivo',
      details: err.message
    });
  }

  // Error personalizado
  if (err.statusCode) {
    return res.status(err.statusCode).json({
      success: false,
      error: err.message
    });
  }

  // Error genérico
  res.status(500).json({
    success: false,
    error: 'Error interno del servidor',
    message: process.env.NODE_ENV === 'development' ? err.message : undefined
  });
};

/**
 * Clase para errores personalizados
 */
export class AppError extends Error {
  constructor(message, statusCode = 500) {
    super(message);
    this.statusCode = statusCode;
    this.name = 'AppError';
  }
}
