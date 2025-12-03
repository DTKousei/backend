const express = require('express');
const router = express.Router();
const {
  createTipoIncidencia,
  getAllTiposIncidencia,
  getTipoIncidenciaById,
  updateTipoIncidencia,
  deleteTipoIncidencia,
} = require('../controllers/tipos-incidencia.controller');
const {
  validateCreateTipoIncidencia,
  validateUUID,
} = require('../middleware/validation');

// Rutas de tipos de incidencia
router.post('/', validateCreateTipoIncidencia, createTipoIncidencia);
router.get('/', getAllTiposIncidencia);
router.get('/:id', validateUUID, getTipoIncidenciaById);
router.put('/:id', validateUUID, updateTipoIncidencia);
router.delete('/:id', validateUUID, deleteTipoIncidencia);

module.exports = router;
