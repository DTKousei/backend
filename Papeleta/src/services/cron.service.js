import prisma from '../config/database.js';
import { ESTADO_PERMISO } from '../utils/constants.js';

/**
 * Inicia los procesos en segundo plano (Cron Jobs)
 */
export const iniciarCronJobs = () => {
  console.log('⏰ Servicio de Cron Jobs iniciado: Verificando permisos vencidos cada minuto.');

  // Ejecutar inmediatamente al inicio
  cancelarPermisosVencidos();

  // Ejecutar cada minuto (60000 ms)
  setInterval(async () => {
    try {
      await cancelarPermisosVencidos();
    } catch (error) {
      console.error('Error en cron job de cancelación:', error);
    }
  }, 60000);
};

/**
 * Busca y cancela permisos cuya fecha de fin ya pasó y no han sido aprobados por RRHH
 */
const cancelarPermisosVencidos = async () => {
  try {
    const ahora = new Date();

    // 1. Obtener IDs de estados relevantes
    const estadosBuscados = [ESTADO_PERMISO.PENDIENTE, ESTADO_PERMISO.APROBADO_JEFE];
    
    const estados = await prisma.estado.findMany({
      where: {
        codigo: { in: estadosBuscados }
      }
    });

    const estadoCancelado = await prisma.estado.findFirst({
      where: { codigo: ESTADO_PERMISO.CANCELADO }
    });

    if (!estados.length || !estadoCancelado) {
      console.error('No se encontraron los estados necesarios para el cron job.');
      return;
    }

    const idsEstadosPendientes = estados.map(e => e.id);

    // 2. Buscar y actualizar permisos vencidos
    // updateMany es más eficiente que iterar
    const resultado = await prisma.permiso.updateMany({
      where: {
        estado_id: { in: idsEstadosPendientes },
        fecha_hora_fin: {
          lt: ahora // Menor que ahora (ya pasó)
        },
        // Asegurarnos que fecha_hora_fin no sea nulo (comisiones sin limite no se auto-cancelan por hora)
        NOT: {
            fecha_hora_fin: null
        }
      },
      data: {
        estado_id: estadoCancelado.id
        // Podríamos agregar un campo de auditoría o motivo si existiera en la BD
      }
    });

    if (resultado.count > 0) {
      console.log(`[AUTO-CANCEL] Se han cancelado ${resultado.count} permisos vencidos.`);
    }

  } catch (error) {
    console.error('Error verificando permisos vencidos:', error);
  }
};
