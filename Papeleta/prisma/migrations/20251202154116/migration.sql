-- CreateTable
CREATE TABLE "permisos_tipos" (
    "id" TEXT NOT NULL,
    "nombre" VARCHAR(100) NOT NULL,
    "codigo" VARCHAR(20) NOT NULL,
    "descripcion" TEXT,
    "esta_activo" BOOLEAN,

    CONSTRAINT "permisos_tipos_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "estados" (
    "id" TEXT NOT NULL,
    "nombre" VARCHAR(50) NOT NULL,
    "descripcion" TEXT,

    CONSTRAINT "estados_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "permisos" (
    "id" TEXT NOT NULL,
    "empleado_id" VARCHAR(36) NOT NULL,
    "tipo_permiso_id" VARCHAR(36) NOT NULL,
    "estado_id" VARCHAR(36) NOT NULL,
    "fecha_hora_inicio" TIMESTAMP(3) NOT NULL,
    "fecha_hora_fin" TIMESTAMP(3),
    "motivo" TEXT NOT NULL,
    "justificacion" TEXT NOT NULL,
    "firma_solicitante" VARCHAR(500) NOT NULL,
    "firma_supervisor_rrhh" VARCHAR(500) NOT NULL,
    "firma_institucion" VARCHAR(500) NOT NULL,
    "firma_supervisor_area_en" TIMESTAMP(3),
    "firma_supervisor_rrhh_en" TIMESTAMP(3),
    "firma_institucion_en" TIMESTAMP(3),
    "creado_en" TIMESTAMP(3),

    CONSTRAINT "permisos_pkey" PRIMARY KEY ("id")
);

-- AddForeignKey
ALTER TABLE "permisos" ADD CONSTRAINT "permisos_tipo_permiso_id_fkey" FOREIGN KEY ("tipo_permiso_id") REFERENCES "permisos_tipos"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "permisos" ADD CONSTRAINT "permisos_estado_id_fkey" FOREIGN KEY ("estado_id") REFERENCES "estados"("id") ON DELETE RESTRICT ON UPDATE CASCADE;
