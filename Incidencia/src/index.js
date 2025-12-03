require('dotenv').config();
const express = require('express');
const cors = require('cors');
const helmet = require('helmet');
const rateLimit = require('express-rate-limit');
const errorHandler = require('./middleware/errorHandler');
const { ensureUploadDirectory } = require('./utils/fileManager');

// Importar rutas
const incidenciasRoutes = require('./routes/incidencias.routes');
const tiposIncidenciaRoutes = require('./routes/tipos-incidencia.routes');
const estadosRoutes = require('./routes/estados.routes');

// Crear aplicación Express
const app = express();

// Asegurar que el directorio de carga existe
ensureUploadDirectory();

// Configuración de middleware
app.use(helmet()); // Seguridad HTTP headers
app.use(cors()); // Habilitar CORS
app.use(express.json()); // Parser de JSON
app.use(express.urlencoded({ extended: true })); // Parser de URL-encoded

// Rate limiting
const limiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutos
  max: 100, // Límite de 100 peticiones por ventana
  message: 'Demasiadas peticiones desde esta IP, por favor intente más tarde.',
});
app.use('/api/', limiter);

// Rutas
app.get('/', (req, res) => {
  res.json({
    message: 'API de Gestión de Incidencias',
    version: '1.0.0',
    endpoints: {
      incidencias: '/api/incidencias',
      tipos_incidencia: '/api/tipos-incidencia',
      estados: '/api/estados',
    },
  });
});

app.use('/api/incidencias', incidenciasRoutes);
app.use('/api/tipos-incidencia', tiposIncidenciaRoutes);
app.use('/api/estados', estadosRoutes);

// Ruta 404
app.use((req, res) => {
  res.status(404).json({
    error: 'Ruta no encontrada',
    message: `La ruta ${req.method} ${req.url} no existe`,
  });
});

// Middleware de manejo de errores (debe ser el último)
app.use(errorHandler);

// Configuración del puerto
const PORT = process.env.PORT || 3000;

// Iniciar servidor
app.listen(PORT, () => {
  console.log(`
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║   🚀 Servidor de Incidencias iniciado correctamente      ║
║                                                           ║
║   📍 Puerto: ${PORT}                                        ║
║   🌐 URL: http://localhost:${PORT}                         ║
║   📁 Directorio de archivos: C:\\IncidenciasDocumentos    ║
║                                                           ║
║   Endpoints disponibles:                                  ║
║   • GET    /api/incidencias                               ║
║   • POST   /api/incidencias                               ║
║   • GET    /api/incidencias/:id                           ║
║   • PUT    /api/incidencias/:id                           ║
║   • DELETE /api/incidencias/:id                           ║
║   • PATCH  /api/incidencias/:id/aprobar                   ║
║   • PATCH  /api/incidencias/:id/rechazar                  ║
║                                                           ║
║   • GET    /api/tipos-incidencia                          ║
║   • POST   /api/tipos-incidencia                          ║
║                                                           ║
║   • GET    /api/estados                                   ║
║   • POST   /api/estados                                   ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
  `);
});

module.exports = app;
