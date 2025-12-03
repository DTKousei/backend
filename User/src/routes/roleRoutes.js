const express = require('express');
const router = express.Router();
const roleController = require('../controllers/roleController.js');
const { authenticate } = require('../middlewares/auth.js');

// Todas las rutas de roles requieren autenticación
router.use(authenticate);

router.get('/', roleController.getAll);
router.get('/:id', roleController.getById);
router.post('/', roleController.create);
router.put('/:id', roleController.update);
router.delete('/:id', roleController.delete);

module.exports = router;
