require('dotenv').config();
const app = require('./app');

const PORT = process.env.PORT || 3000;
const HOST = process.env.HOST || 'localhost';

const server = app.listen(PORT, () => {
  console.log(`
╔═══════════════════════════════════════════╗
║                                           ║
║   🚀 Servidor iniciado correctamente      ║
║                                           ║
║   📍 Puerto: ${PORT}                         ║
║   🌍 URL: http://${HOST}:${PORT}           ║
║   🔧 Entorno: ${process.env.NODE_ENV || 'development'}                 ║
║   🕐 Hora: ${new Date().toLocaleString('es-PE')}      ║
║                                           ║
║   📚 Endpoints disponibles:               ║
║   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━   ║
║   📖 Públicos:                        ║
║   - POST /api/auth/register               ║
║   - POST /api/auth/login                  ║
║                                           ║
║   🔒 Privados (requieren token):          ║
║   - POST /api/auth/logout                 ║
║   - POST /api/auth/change-password        ║
║   - GET  /api/auth/profile                ║
║   - GET  /api/auth/verify                 ║
║                                           ║
║   💡 Tip: Usa Postman o Thunder Client    ║
║      para probar los endpoints            ║
║                                           ║
╚═══════════════════════════════════════════╝
  `);
  
  console.log('✨ Listo para recibir peticiones!\n');
});

// Manejo de cierre graceful del servidor
process.on('SIGTERM', gracefulShutdown);
process.on('SIGINT', gracefulShutdown);

function gracefulShutdown() {
  console.log('\n👋 Señal de cierre recibida. Cerrando servidor de forma segura...');
  
  server.close(() => {
    console.log('✅ Servidor HTTP cerrado');
    console.log('🔌 Cerrando conexiones a la base de datos...');
    
    // Prisma se desconecta automáticamente en el proceso beforeExit
    process.exit(0);
  });

  // Forzar cierre después de 10 segundos si no se cerró naturalmente
  setTimeout(() => {
    console.error('❌ No se pudo cerrar el servidor de forma segura, forzando cierre...');
    process.exit(1);
  }, 10000);
}

// Manejo de errores no capturados
process.on('unhandledRejection', (reason, promise) => {
  console.error('❌ Unhandled Rejection detectado:');
  console.error('Promise:', promise);
  console.error('Razón:', reason);
  // En producción podrías querer cerrar el proceso
  // process.exit(1);
});

process.on('uncaughtException', (error) => {
  console.error('❌ Uncaught Exception detectado:');
  console.error(error);
  // Cerrar el proceso de forma segura
  gracefulShutdown();
});

module.exports = server;