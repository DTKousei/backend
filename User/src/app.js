// Archivo: src/app.js (CORREGIDO)

const express = require('express');
const cors = require('cors');
require('dotenv').config();

// ============================================
// IMPORTACIONES
// ============================================

// ¡CORREGIDO! Ahora importa el enrutador principal (index.js)
const mainRouter = require('./routes/index.js'); 

const {
  helmetConfig,
  apiLimiter,
  sanitizeInput,
  preventTimingAttack
} = require('./middlewares/security');

const app = express();

// ============================================
// MIDDLEWARES DE SEGURIDAD (OWASP)
// ============================================
app.use(helmetConfig);
app.use(cors({
  origin: process.env.CORS_ORIGIN || '*',
  credentials: true,
  methods: ['GET', 'POST', 'PUT', 'DELETE', 'PATCH'],
  allowedHeaders: ['Content-Type', 'Authorization']
}));
app.use('/api', apiLimiter);
app.use(preventTimingAttack);

// ============================================
// MIDDLEWARES DE PARSEO
// ============================================
app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true, limit: '10mb' }));
app.use(sanitizeInput);

// ============================================
// RUTAS
// ============================================

// ¡CORREGIDO! app.js usa el enrutador principal con el prefijo /api
app.use('/api', mainRouter); 

// ============================================
// MANEJO DE ERRORES 404
// ============================================
app.use((req, res) => {
  res.status(404).json({
    success: false,
    message: 'Ruta no encontrada'
  });
});

// ============================================
// MANEJO DE ERRORES GLOBAL
// ============================================
app.use((error, req, res, next) => {
  console.error('Error:', error);
  
  const message = process.env.NODE_ENV === 'production' 
    ? 'Error interno del servidor'
    : error.message;

  res.status(error.status || 500).json({
    success: false,
    message,
    ...(process.env.NODE_ENV === 'development' && { stack: error.stack })
  });
});

module.exports = app;