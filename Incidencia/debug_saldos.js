const { PrismaClient } = require('@prisma/client');
const prisma = new PrismaClient();

async function main() {
  console.log('--- Debugging Saldos ---');
  
  // 1. Buscar el tipo de incidencia "ONOMASTICO"
  const tipo = await prisma.tipoIncidencia.findFirst({
    where: { nombre: { contains: 'ONOMASTICO', mode: 'insensitive' } }
  });

  if (!tipo) {
    console.log('❌ No se encontró tipo ONOMASTICO');
    return;
  }
  console.log('Tipo Encontrado:', { id: tipo.id, nombre: tipo.nombre });

  // 2. Buscar TODAS las incidencias de este tipo
  const todasIncidencias = await prisma.incidencia.findMany({
    where: { tipo_incidencia_id: tipo.id },
    select: {
      id: true,
      empleado_id: true,
      fecha_inicio: true,
      fecha_fin: true,
      motivo_rechazo: true, // Importante verificar esto
      estado_id: true
    }
  });

  console.log(`\nEncontradas ${todasIncidencias.length} incidencias totales para este tipo.`);
  todasIncidencias.forEach(inc => {
      console.log(`- ID: ${inc.id} | Empleado: ${inc.empleado_id} | Inicio: ${inc.fecha_inicio.toISOString()} | Rechazo: ${inc.motivo_rechazo}`);
  });

  // 3. Simular filtro del controlador
  const year = new Date().getFullYear();
  const startOfYear = new Date(year, 0, 1);
  const endOfYear = new Date(year, 11, 31, 23, 59, 59);
  
  console.log(`\nFiltro de Año Controller: ${year}`);
  console.log(`Start: ${startOfYear.toISOString()}`);
  console.log(`End:   ${endOfYear.toISOString()}`);

  const incidenciasFiltradas = todasIncidencias.filter(inc => {
      const fechaOk = inc.fecha_inicio >= startOfYear && inc.fecha_inicio <= endOfYear;
      const rechazoOk = inc.motivo_rechazo === null;
      console.log(`  > Incidencia ${inc.id}: FechaOk=${fechaOk} (${inc.fecha_inicio.toISOString()}), RechazoOk=${rechazoOk} (${inc.motivo_rechazo})`);
      return fechaOk && rechazoOk;
  });

  console.log(`\nIncidencias tras filtro: ${incidenciasFiltradas.length}`);

}

main()
  .catch(e => console.error(e))
  .finally(async () => await prisma.$disconnect());
