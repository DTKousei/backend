import { PrismaClient } from '@prisma/client';
import { TIPO_PERMISO, ESTADO_PERMISO, PERMISO_CONFIG } from '../src/utils/constants.js';

const prisma = new PrismaClient();

async function main() {
  console.log('🌱 Iniciando seed de la base de datos...');

  // Limpiar datos existentes (opcional, comentar si no deseas limpiar)
  // await prisma.permiso.deleteMany();
  // await prisma.permisoTipo.deleteMany();
  // await prisma.estado.deleteMany();

  // Crear tipos de permisos
  console.log('📝 Creando tipos de permisos...');
  
  const tipoComision = await prisma.permisoTipo.upsert({
    where: { codigo: TIPO_PERMISO.COMISION_SERVICIO },
    update: {},
    create: {
      nombre: 'Comisión de Servicio',
      codigo: TIPO_PERMISO.COMISION_SERVICIO,
      descripcion: PERMISO_CONFIG[TIPO_PERMISO.COMISION_SERVICIO].descripcion,
      requiere_firma_institucion: PERMISO_CONFIG[TIPO_PERMISO.COMISION_SERVICIO].requiere_firma_institucion,
      tiempo_maximo_horas: PERMISO_CONFIG[TIPO_PERMISO.COMISION_SERVICIO].tiempo_maximo_horas,
      esta_activo: true
    }
  });

  const tipoPersonal = await prisma.permisoTipo.upsert({
    where: { codigo: TIPO_PERMISO.PERMISO_PERSONAL },
    update: {},
    create: {
      nombre: 'Permiso Personal',
      codigo: TIPO_PERMISO.PERMISO_PERSONAL,
      descripcion: PERMISO_CONFIG[TIPO_PERMISO.PERMISO_PERSONAL].descripcion,
      requiere_firma_institucion: PERMISO_CONFIG[TIPO_PERMISO.PERMISO_PERSONAL].requiere_firma_institucion,
      tiempo_maximo_horas: PERMISO_CONFIG[TIPO_PERMISO.PERMISO_PERSONAL].tiempo_maximo_horas,
      esta_activo: true
    }
  });

  console.log(`✅ Tipo de permiso creado: ${tipoComision.nombre}`);
  console.log(`✅ Tipo de permiso creado: ${tipoPersonal.nombre}`);

  // Crear estados
  console.log('\n📊 Creando estados...');

  const estados = [
    {
      nombre: 'Pendiente',
      codigo: ESTADO_PERMISO.PENDIENTE,
      descripcion: 'Permiso pendiente de aprobación'
    },
    {
      nombre: 'Aprobado por Jefe',
      codigo: ESTADO_PERMISO.APROBADO_JEFE,
      descripcion: 'Permiso aprobado por el jefe de área'
    },
    {
      nombre: 'Aprobado por RRHH',
      codigo: ESTADO_PERMISO.APROBADO_RRHH,
      descripcion: 'Permiso aprobado por Recursos Humanos'
    },
    {
      nombre: 'Aprobado',
      codigo: ESTADO_PERMISO.APROBADO,
      descripcion: 'Permiso completamente aprobado'
    },
    {
      nombre: 'Rechazado',
      codigo: ESTADO_PERMISO.RECHAZADO,
      descripcion: 'Permiso rechazado'
    },
    {
      nombre: 'Cancelado',
      codigo: ESTADO_PERMISO.CANCELADO,
      descripcion: 'Permiso cancelado por el solicitante'
    }
  ];

  for (const estado of estados) {
    const estadoCreado = await prisma.estado.upsert({
      where: { codigo: estado.codigo },
      update: {},
      create: estado
    });
    console.log(`✅ Estado creado: ${estadoCreado.nombre}`);
  }

  console.log('\n🎉 Seed completado exitosamente!');
}

main()
  .catch((e) => {
    console.error('❌ Error en seed:', e);
    process.exit(1);
  })
  .finally(async () => {
    await prisma.$disconnect();
  });
