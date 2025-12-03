const fs = require('fs');
const path = require('path');

// Directorio donde se almacenarán los documentos PDF
const UPLOAD_DIR = 'C:\\IncidenciasDocumentos';

/**
 * Asegura que el directorio de carga exista
 */
const ensureUploadDirectory = () => {
  if (!fs.existsSync(UPLOAD_DIR)) {
    fs.mkdirSync(UPLOAD_DIR, { recursive: true });
    console.log(`✓ Directorio de carga creado: ${UPLOAD_DIR}`);
  }
};

/**
 * Elimina un archivo del sistema de archivos de forma segura
 * @param {string} filePath - Ruta completa del archivo a eliminar
 * @returns {boolean} - true si se eliminó correctamente, false en caso contrario
 */
const deleteFile = (filePath) => {
  try {
    if (fs.existsSync(filePath)) {
      fs.unlinkSync(filePath);
      console.log(`✓ Archivo eliminado: ${filePath}`);
      return true;
    }
    return false;
  } catch (error) {
    console.error(`✗ Error al eliminar archivo: ${error.message}`);
    return false;
  }
};

/**
 * Obtiene la ruta completa del archivo a partir del nombre
 * @param {string} filename - Nombre del archivo
 * @returns {string} - Ruta completa del archivo
 */
const getFilePath = (filename) => {
  return path.join(UPLOAD_DIR, filename);
};

/**
 * Obtiene la URL del archivo (en este caso, la ruta local)
 * @param {string} filename - Nombre del archivo
 * @returns {string} - URL/ruta del archivo
 */
const getFileUrl = (filename) => {
  return getFilePath(filename);
};

module.exports = {
  UPLOAD_DIR,
  ensureUploadDirectory,
  deleteFile,
  getFilePath,
  getFileUrl,
};
