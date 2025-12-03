/**
 * Middleware global para manejo de errores
 */
const errorHandler = (err, req, res, next) => {
  console.error('Error:', err);

  // Error de validación de Multer
  if (err.message === 'Solo se permiten archivos PDF') {
    return res.status(400).json({
      error: 'Tipo de archivo no válido',
      message: 'Solo se permiten archivos PDF',
    });
  }

  // Error de tamaño de archivo de Multer
  if (err.code === 'LIMIT_FILE_SIZE') {
    return res.status(400).json({
      error: 'Archivo demasiado grande',
      message: 'El archivo no puede superar los 10 MB',
    });
  }

  // Errores de Multer
  if (err.name === 'MulterError') {
    return res.status(400).json({
      error: 'Error de carga de archivo',
      message: err.message,
    });
  }

  // Errores de Prisma
  if (err.code === 'P2002') {
    return res.status(409).json({
      error: 'Conflicto de duplicado',
      message: 'Ya existe un registro con estos datos',
    });
  }

  if (err.code === 'P2025') {
    return res.status(404).json({
      error: 'No encontrado',
      message: 'El registro solicitado no existe',
    });
  }

  // Error genérico
  res.status(err.status || 500).json({
    error: err.message || 'Error interno del servidor',
    ...(process.env.NODE_ENV === 'development' && { stack: err.stack }),
  });
};

module.exports = errorHandler;
