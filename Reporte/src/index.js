import express from 'express';
import cors from 'cors';
import helmet from 'helmet';
import morgan from 'morgan';
import rateLimit from 'express-rate-limit';
import { config } from './config/constants.js';
import { errorHandler, notFoundHandler } from './middleware/errorHandler.js';
import reportRoutes from './routes/reportRoutes.js';
import templateRoutes from './routes/templateRoutes.js';

const app = express();

// Middleware de seguridad
app.use(helmet());

// CORS
app.use(cors({
  origin: '*', // Configurar según necesidades de producción
  methods: ['GET', 'POST', 'PUT', 'DELETE'],
  allowedHeaders: ['Content-Type', 'Authorization']
}));

// Rate limiting
const limiter = rateLimit({
  windowMs: config.rateLimitWindowMs,
  max: config.rateLimitMaxRequests,
  message: 'Demasiadas peticiones desde esta IP, por favor intente más tarde.',
  standardHeaders: true,
  legacyHeaders: false,
});
app.use('/api/', limiter);

// Body parser
app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true, limit: '10mb' }));

// Logging
if (config.nodeEnv === 'development') {
  app.use(morgan('dev'));
} else {
  app.use(morgan('combined'));
}

// Ruta de health check
app.get('/health', (req, res) => {
  res.json({
    success: true,
    message: 'API de Reportes de Asistencia funcionando correctamente',
    timestamp: new Date().toISOString(),
    environment: config.nodeEnv
  });
});

// Rutas principales
app.use('/api/reportes', reportRoutes);
app.use('/api/plantillas', templateRoutes);

// Ruta raíz
app.get('/', (req, res) => {
  res.json({
    success: true,
    message: 'API REST de Reportes de Asistencia',
    version: '1.0.0',
    endpoints: {
      reportes: '/api/reportes',
      plantillas: '/api/plantillas',
      health: '/health'
    }
  });
});

// Manejo de rutas no encontradas
app.use(notFoundHandler);

// Manejo de errores
app.use(errorHandler);

// Iniciar servidor
const PORT = config.port;
app.listen(PORT, () => {
  console.log(`
╔════════════════════════════════════════════════════════════╗
║  🚀 Servidor de Reportes de Asistencia                    ║
║  ✅ Ejecutándose en: http://localhost:${PORT}                 ║
║  📝 Ambiente: ${config.nodeEnv.toUpperCase().padEnd(43)}║
║  🔗 API Externa: ${config.attendanceApiUrl.padEnd(37)}║
╚════════════════════════════════════════════════════════════╝
  `);
});

// Manejo de errores no capturados
process.on('unhandledRejection', (err) => {
  console.error('❌ Unhandled Rejection:', err);
  process.exit(1);
});

process.on('uncaughtException', (err) => {
  console.error('❌ Uncaught Exception:', err);
  process.exit(1);
});

export default app;
