const { PrismaClient } = require('@prisma/client');

// 1. Usa 'global' para mantener una única instancia
const prisma = global.prisma || new PrismaClient();

// 2. Solo establece global.prisma en desarrollo para evitar errores de hot-reloading
if (process.env.NODE_ENV !== 'production') {
  global.prisma = prisma;
}

// 3. Exportar la instancia
module.exports = prisma;