const express = require('express');
const router = express.Router();
const userController = require('../controllers/userController.js');
const { authenticate } = require('../middlewares/auth.js');

// Todas las rutas de usuarios requieren autenticación
router.use(authenticate);

router.get('/', userController.getAll);
router.get('/:id', userController.getById);
router.post('/', userController.create);
router.put('/:id', userController.update);
router.delete('/:id', userController.delete);

module.exports = router;
