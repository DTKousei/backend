const { PrismaClient } = require('@prisma/client');
const prisma = new PrismaClient();

async function main() {
  console.log('--- Debugging Saldos Simple ---');
  
  const incidencias = await prisma.incidencia.findMany({
    where: { 
        tipo_incidencia: { nombre: { contains: 'ONOMASTICO', mode: 'insensitive' } }
    },
    take: 5
  });

  console.log(JSON.stringify(incidencias, null, 2));

  // Check counts
  const count = await prisma.incidencia.count({
      where: {
        tipo_incidencia: { nombre: { contains: 'ONOMASTICO', mode: 'insensitive' } },
        motivo_rechazo: null
      }
  });
  console.log('Count where motivo_rechazo is NULL:', count);

  const countEmpty = await prisma.incidencia.count({
    where: {
      tipo_incidencia: { nombre: { contains: 'ONOMASTICO', mode: 'insensitive' } },
      motivo_rechazo: ''
    }
});
console.log('Count where motivo_rechazo is EMPTY STRING:', countEmpty);

  const fs = require('fs');
  fs.writeFileSync('debug_output.json', JSON.stringify(incidencias, null, 2));
  console.log('Output written to debug_output.json');

}

main()
  .catch(e => console.error(e))
  .finally(async () => await prisma.$disconnect());
