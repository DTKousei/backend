const express = require('express');
const router = express.Router();
const permissionController = require('../controllers/permissionController.js');
const { authenticate } = require('../middlewares/auth.js');

// Todas las rutas de permisos requieren autenticación
router.use(authenticate);

router.get('/', permissionController.getAll);
router.get('/:id', permissionController.getById);
router.post('/', permissionController.create);
router.put('/:id', permissionController.update);
router.delete('/:id', permissionController.delete);

module.exports = router;
