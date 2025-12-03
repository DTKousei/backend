/**
 * Calcula la diferencia en horas entre dos fechas
 */
export const calcularDiferenciaHoras = (fechaInicio, fechaFin) => {
  const diff = new Date(fechaFin) - new Date(fechaInicio);
  return diff / (1000 * 60 * 60); // Convertir a horas
};

/**
 * Valida que una fecha sea válida
 */
export const esFechaValida = (fecha) => {
  const date = new Date(fecha);
  return date instanceof Date && !isNaN(date);
};

/**
 * Formatea una fecha para mostrar
 */
export const formatearFecha = (fecha) => {
  return new Date(fecha).toLocaleString('es-PE', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  });
};

/**
 * Valida que una firma en base64 sea válida
 */
export const validarFirmaBase64 = (firma) => {
  if (!firma) return false;
  
  // Verificar que sea una cadena base64 válida
  const base64Regex = /^data:image\/(png|jpg|jpeg|gif);base64,/;
  return base64Regex.test(firma);
};

/**
 * Genera un nombre de archivo único
 */
export const generarNombreArchivo = (prefijo, extension) => {
  const timestamp = Date.now();
  const random = Math.floor(Math.random() * 1000);
  return `${prefijo}-${timestamp}-${random}.${extension}`;
};

/**
 * Sanitiza un string para usar en nombres de archivo
 */
export const sanitizarNombreArchivo = (nombre) => {
  return nombre
    .toLowerCase()
    .replace(/[^a-z0-9]/g, '-')
    .replace(/-+/g, '-')
    .replace(/^-|-$/g, '');
};
