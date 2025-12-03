import dotenv from 'dotenv';
import express from 'express';
import cors from 'cors';
import morgan from 'morgan';
import path from 'path';
import { fileURLToPath } from 'url';
import fs from 'fs';

// Importar rutas
import permisoTipoRoutes from './routes/permisoTipo.routes.js';
import estadoRoutes from './routes/estado.routes.js';
import permisoRoutes from './routes/permiso.routes.js';

// Importar middleware de errores
import { errorHandler } from './middleware/error.middleware.js';

// Configuración de __dirname para ES modules
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Cargar variables de entorno
dotenv.config();

const app = express();
const PORT = process.env.PORT || 3000;

// Crear directorios necesarios
const uploadsDir = path.join(__dirname, '..', 'uploads');
const generatedDir = path.join(__dirname, '..', 'generated');

if (!fs.existsSync(uploadsDir)) {
  fs.mkdirSync(uploadsDir, { recursive: true });
}

if (!fs.existsSync(generatedDir)) {
  fs.mkdirSync(generatedDir, { recursive: true });
}

// Middleware
app.use(cors());
app.use(morgan('dev'));
app.use(express.json({ limit: '10mb' })); // Para firmas en base64
app.use(express.urlencoded({ extended: true, limit: '10mb' }));

// Servir archivos estáticos
app.use('/uploads', express.static(uploadsDir));
app.use('/generated', express.static(generatedDir));

// Rutas
app.get('/', (req, res) => {
  res.json({
    message: 'API REST - Sistema de Papeletas (Permisos)',
    version: '1.0.0',
    endpoints: {
      permisoTipos: '/api/permiso-tipos',
      estados: '/api/estados',
      permisos: '/api/permisos'
    }
  });
});

app.use('/api/permiso-tipos', permisoTipoRoutes);
app.use('/api/estados', estadoRoutes);
app.use('/api/permisos', permisoRoutes);

// Middleware de manejo de errores (debe ir al final)
app.use(errorHandler);

// Iniciar servidor
app.listen(PORT, () => {
  console.log(`🚀 Servidor corriendo en http://localhost:${PORT}`);
  console.log(`📁 Directorio de uploads: ${uploadsDir}`);
  console.log(`📄 Directorio de PDFs generados: ${generatedDir}`);
});

export default app;
