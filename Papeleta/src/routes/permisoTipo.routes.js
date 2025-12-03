import express from 'express';
import {
  obtenerTiposPermisos,
  obtenerTipoPermisoPorId,
  crearTipoPermiso,
  actualizarTipoPermiso,
  eliminarTipoPermiso
} from '../controllers/permisoTipo.controller.js';
import { validatePermisoTipo, validateUUID } from '../middleware/validation.middleware.js';

const router = express.Router();

/**
 * @route   GET /api/permiso-tipos
 * @desc    Obtener todos los tipos de permisos
 * @query   activo (opcional): true/false
 */
router.get('/', obtenerTiposPermisos);

/**
 * @route   GET /api/permiso-tipos/:id
 * @desc    Obtener un tipo de permiso por ID
 */
router.get('/:id', validateUUID, obtenerTipoPermisoPorId);

/**
 * @route   POST /api/permiso-tipos
 * @desc    Crear un nuevo tipo de permiso
 */
router.post('/', validatePermisoTipo, crearTipoPermiso);

/**
 * @route   PUT /api/permiso-tipos/:id
 * @desc    Actualizar un tipo de permiso
 */
router.put('/:id', validateUUID, actualizarTipoPermiso);

/**
 * @route   DELETE /api/permiso-tipos/:id
 * @desc    Eliminar un tipo de permiso
 */
router.delete('/:id', validateUUID, eliminarTipoPermiso);

export default router;
