const express = require('express');
const router = express.Router();
const authController = require('../controllers/authController.js');
const { authenticate } = require('../middlewares/auth.js');
const { loginLimiter } = require('../middlewares/security.js');
const {
  registerValidation,
  loginValidation,
  changePasswordValidation,
  handleValidationErrors
} = require('../middlewares/validation');

/**
 * @route   POST /api/auth/register
 * @desc    Registrar nuevo usuario
 * @access  Public
 */
router.post(
  '/register',
  registerValidation,
  handleValidationErrors,
  authController.register
);

/**
 * @route   POST /api/auth/login
 * @desc    Iniciar sesión
 * @access  Public
 */
router.post(
  '/login',
  loginLimiter, // Rate limiting específico para login
  loginValidation,
  handleValidationErrors,
  authController.login
);

/**
 * @route   POST /api/auth/logout
 * @desc    Cerrar sesión
 * @access  Private
 */
router.post(
  '/logout',
  authenticate,
  authController.logout
);

/**
 * @route   POST /api/auth/change-password
 * @desc    Cambiar contraseña
 * @access  Private
 */
router.post(
  '/change-password',
  authenticate,
  changePasswordValidation,
  handleValidationErrors,
  authController.changePassword
);

/**
 * @route   GET /api/auth/profile
 * @desc    Obtener perfil del usuario
 * @access  Private
 */
router.get(
  '/profile',
  authenticate,
  authController.getProfile
);

/**
 * @route   GET /api/auth/verify
 * @desc    Verificar token
 * @access  Private
 */
router.get(
  '/verify',
  authenticate,
  authController.verifyToken
);

module.exports = router;