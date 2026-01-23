const { PrismaClient } = require('@prisma/client');
const prisma = new PrismaClient();

async function main() {
  console.log('--- Checking IDs ---');
  
  const withPrefix = await prisma.incidencia.count({
    where: { empleado_id: 'emp-40126700' }
  });

  const withoutPrefix = await prisma.incidencia.count({
    where: { empleado_id: '40126700' }
  });

  console.log(`Incidencias con emp-40126700: ${withPrefix}`);
  console.log(`Incidencias con 40126700: ${withoutPrefix}`);
}

main()
  .catch(e => console.error(e))
  .finally(async () => await prisma.$disconnect());
