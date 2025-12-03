import fs from 'fs/promises';
import path from 'path';
import { v4 as uuidv4 } from 'uuid';
import { config } from '../config/constants.js';

class FileStorageService {
  constructor() {
    this.storagePath = path.resolve(config.storagePath);
    this.ensureStorageDirectory();
  }

  /**
   * Asegura que el directorio de almacenamiento existe
   */
  async ensureStorageDirectory() {
    try {
      await fs.access(this.storagePath);
    } catch {
      await fs.mkdir(this.storagePath, { recursive: true });
    }
  }

  /**
   * Genera un nombre de archivo único
   */
  generateFileName(originalName, extension) {
    const timestamp = Date.now();
    const uuid = uuidv4().split('-')[0];
    const sanitizedName = originalName.replace(/[^a-zA-Z0-9]/g, '_');
    return `${sanitizedName}_${timestamp}_${uuid}.${extension}`;
  }

  /**
   * Guarda un archivo en el sistema de archivos
   */
  async saveFile(buffer, fileName) {
    try {
      await this.ensureStorageDirectory();
      const filePath = path.join(this.storagePath, fileName);
      await fs.writeFile(filePath, buffer);
      return filePath;
    } catch (error) {
      throw new Error(`Error al guardar archivo: ${error.message}`);
    }
  }

  /**
   * Lee un archivo del sistema de archivos
   */
  async readFile(fileName) {
    try {
      const filePath = path.join(this.storagePath, fileName);
      const buffer = await fs.readFile(filePath);
      return buffer;
    } catch (error) {
      throw new Error(`Error al leer archivo: ${error.message}`);
    }
  }

  /**
   * Elimina un archivo del sistema de archivos
   */
  async deleteFile(fileName) {
    try {
      const filePath = path.join(this.storagePath, fileName);
      await fs.unlink(filePath);
      return true;
    } catch (error) {
      throw new Error(`Error al eliminar archivo: ${error.message}`);
    }
  }

  /**
   * Verifica si un archivo existe
   */
  async fileExists(fileName) {
    try {
      const filePath = path.join(this.storagePath, fileName);
      await fs.access(filePath);
      return true;
    } catch {
      return false;
    }
  }

  /**
   * Obtiene la ruta relativa de un archivo
   */
  getRelativePath(fileName) {
    return path.join(config.storagePath, fileName);
  }

  /**
   * Obtiene la ruta absoluta de un archivo
   */
  getAbsolutePath(fileName) {
    return path.join(this.storagePath, fileName);
  }
}

export default new FileStorageService();
