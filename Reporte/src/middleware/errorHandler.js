import { errorResponse } from '../utils/responseFormatter.js';

/**
 * Middleware global para manejo de errores
 */
export const errorHandler = (err, req, res, next) => {
  console.error('Error:', err);

  // Error de validación de Prisma
  if (err.code === 'P2002') {
    return res.status(409).json(
      errorResponse('Ya existe un registro con estos datos', 409, {
        field: err.meta?.target
      })
    );
  }

  // Error de registro no encontrado
  if (err.code === 'P2025') {
    return res.status(404).json(
      errorResponse('Registro no encontrado', 404)
    );
  }

  // Error de validación
  if (err.name === 'ValidationError') {
    return res.status(400).json(
      errorResponse('Error de validación', 400, err.errors)
    );
  }

  // Error de sintaxis JSON
  if (err instanceof SyntaxError && err.status === 400 && 'body' in err) {
    return res.status(400).json(
      errorResponse('JSON inválido en el cuerpo de la petición', 400)
    );
  }

  // Error genérico
  const statusCode = err.statusCode || 500;
  const message = err.message || 'Error interno del servidor';

  res.status(statusCode).json(
    errorResponse(message, statusCode, process.env.NODE_ENV === 'development' ? err.stack : null)
  );
};

/**
 * Middleware para rutas no encontradas
 */
export const notFoundHandler = (req, res) => {
  res.status(404).json(
    errorResponse(`Ruta no encontrada: ${req.method} ${req.path}`, 404)
  );
};
