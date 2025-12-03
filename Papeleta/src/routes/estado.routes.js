import express from 'express';
import {
  obtenerEstados,
  obtenerEstadoPorId,
  crearEstado,
  actualizarEstado,
  eliminarEstado
} from '../controllers/estado.controller.js';
import { validateEstado, validateUUID } from '../middleware/validation.middleware.js';

const router = express.Router();

/**
 * @route   GET /api/estados
 * @desc    Obtener todos los estados
 */
router.get('/', obtenerEstados);

/**
 * @route   GET /api/estados/:id
 * @desc    Obtener un estado por ID
 */
router.get('/:id', validateUUID, obtenerEstadoPorId);

/**
 * @route   POST /api/estados
 * @desc    Crear un nuevo estado
 */
router.post('/', validateEstado, crearEstado);

/**
 * @route   PUT /api/estados/:id
 * @desc    Actualizar un estado
 */
router.put('/:id', validateUUID, actualizarEstado);

/**
 * @route   DELETE /api/estados/:id
 * @desc    Eliminar un estado
 */
router.delete('/:id', validateUUID, eliminarEstado);

export default router;
