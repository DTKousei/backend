const express = require('express');
const router = express.Router();
const {
  createEstado,
  getAllEstados,
  getEstadoById,
  updateEstado,
  deleteEstado,
} = require('../controllers/estados.controller');
const {
  validateCreateEstado,
  validateUUID,
} = require('../middleware/validation');

// Rutas de estados
router.post('/', validateCreateEstado, createEstado);
router.get('/', getAllEstados);
router.get('/:id', validateUUID, getEstadoById);
router.put('/:id', validateUUID, updateEstado);
router.delete('/:id', validateUUID, deleteEstado);

module.exports = router;
