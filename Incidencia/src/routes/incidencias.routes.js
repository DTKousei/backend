const express = require('express');
const router = express.Router();
const upload = require('../config/upload');
const {
  createIncidencia,
  getAllIncidencias,
  getIncidenciaById,
  updateIncidencia,
  deleteIncidencia,
  aprobarIncidencia,
  rechazarIncidencia,
  getReporteSabana,
  getIncidenciaDocumento,
  getSaldosIncidencias,
} = require('../controllers/incidencias.controller');
const {
  validateCreateIncidencia,
  validateUpdateIncidencia,
  validateAprobarIncidencia,
  validateRechazarIncidencia,
  validateUUID,
} = require('../middleware/validation');

// Rutas de incidencias
router.post('/', upload.single('documento'), validateCreateIncidencia, createIncidencia);
router.get('/', getAllIncidencias);
router.get('/saldos', getSaldosIncidencias);
router.post('/reporte-sabana', getReporteSabana);
router.get('/:id/documento', validateUUID, getIncidenciaDocumento);
router.get('/:id', validateUUID, getIncidenciaById);
router.put('/:id', upload.single('documento'), validateUpdateIncidencia, updateIncidencia);
router.delete('/:id', validateUUID, deleteIncidencia);
router.patch('/:id/aprobar', validateAprobarIncidencia, aprobarIncidencia);
router.patch('/:id/rechazar', validateRechazarIncidencia, rechazarIncidencia);

module.exports = router;
