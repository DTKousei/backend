import express from 'express';
import {
  obtenerPermisos,
  obtenerPermisoPorId,
  crearPermiso,
  actualizarPermiso,
  eliminarPermiso,
  firmarPermiso,
  generarPDF,
  cargarPDFFirmado,
  verPDF
} from '../controllers/permiso.controller.js';
import {
  firmarPermisoDigital,
  verificarFirmaDigital,
  recibirCallbackRefirma
} from '../controllers/permisoDigital.controller.js';
import {
  validateCreatePermiso,
  validateUpdatePermiso,
  validateFirma,
  validateFirmaDigital,
  validateUUID
} from '../middleware/validation.middleware.js';
import { upload } from '../config/upload.js';

const router = express.Router();

/**
 * @route   GET /api/permisos
 * @desc    Obtener todos los permisos con filtros
 * @query   empleado_id, tipo_permiso_id, estado_id, fecha_desde, fecha_hasta, page, limit
 */
router.get('/', obtenerPermisos);

/**
 * @route   GET /api/permisos/:id
 * @desc    Obtener un permiso por ID
 */
router.get('/:id', validateUUID, obtenerPermisoPorId);

/**
 * @route   POST /api/permisos
 * @desc    Crear un nuevo permiso
 */
router.post('/', validateCreatePermiso, crearPermiso);

/**
 * @route   POST /api/permisos/callback
 * @desc    Recepción de PDF firmado desde ReFirma (ONPE)
 */
router.post('/callback', upload.single('Filename'), recibirCallbackRefirma);

/**
 * @route   PUT /api/permisos/:id
 * @desc    Actualizar un permiso
 */
router.put('/:id', validateUUID, validateUpdatePermiso, actualizarPermiso);

/**
 * @route   DELETE /api/permisos/:id
 * @desc    Eliminar un permiso
 */
router.delete('/:id', validateUUID, eliminarPermiso);

/**
 * @route   PATCH /api/permisos/:id/firmar
 * @desc    Agregar firma tradicional (base64) a un permiso
 * @body    tipo_firma (solicitante|jefe_area|rrhh|institucion), firma (base64)
 */
router.patch('/:id/firmar', validateUUID, validateFirma, firmarPermiso);

/**
 * @route   PATCH /api/permisos/:id/firmar-digital
 * @desc    Agregar firma digital ONPE a un permiso
 * @body    tipo_firma, firma_digital (PKCS#7), certificado
 */
router.patch('/:id/firmar-digital', validateUUID, validateFirmaDigital, firmarPermisoDigital);

/**
 * @route   GET /api/permisos/:id/verificar-firma/:tipoFirma
 * @desc    Verificar firma digital de un permiso
 */
router.get('/:id/verificar-firma/:tipoFirma', validateUUID, verificarFirmaDigital);

/**
 * @route   GET /api/permisos/:id/pdf
 * @desc    Generar y descargar PDF del permiso
 */
router.get('/:id/pdf', validateUUID, generarPDF);

/**
 * @route   GET /api/permisos/:id/pdf/ver
 * @desc    Ver PDF del permiso en el navegador (evita regenerarlo si existe)
 */
router.get('/:id/pdf/ver', validateUUID, verPDF);

/**
 * @route   POST /api/permisos/:id/upload-pdf
 * @desc    Cargar PDF firmado
 */
router.post(
  '/:id/upload-pdf',
  validateUUID,
  upload.single('pdf'),
  cargarPDFFirmado
);

export default router;
