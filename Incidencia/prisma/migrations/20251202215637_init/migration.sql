-- CreateTable
CREATE TABLE "tipos_incidencia" (
    "id" TEXT NOT NULL,
    "nombre" VARCHAR(100) NOT NULL,
    "codigo" VARCHAR(20) NOT NULL,
    "requiere_aprobacion" BOOLEAN NOT NULL,
    "requiere_documento" BOOLEAN NOT NULL,
    "descuenta_salario" BOOLEAN NOT NULL,
    "esta_activo" BOOLEAN NOT NULL,
    "creado_en" TIMESTAMP(3),

    CONSTRAINT "tipos_incidencia_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "estados" (
    "id" TEXT NOT NULL,
    "nombre" VARCHAR(50) NOT NULL,
    "descripcion" TEXT,

    CONSTRAINT "estados_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "incidencias" (
    "id" TEXT NOT NULL,
    "empleado_id" VARCHAR(36) NOT NULL,
    "tipo_incidencia_id" VARCHAR(36) NOT NULL,
    "fecha_inicio" DATE NOT NULL,
    "fecha_fin" DATE NOT NULL,
    "descripcion" TEXT NOT NULL,
    "url_documento" VARCHAR(500) NOT NULL,
    "estado_id" VARCHAR(36) NOT NULL,
    "aprobado_por" VARCHAR(36),
    "aprobado_en" TIMESTAMP(3),
    "motivo_rechazo" TEXT,
    "creado_en" TIMESTAMP(3),

    CONSTRAINT "incidencias_pkey" PRIMARY KEY ("id")
);

-- AddForeignKey
ALTER TABLE "incidencias" ADD CONSTRAINT "incidencias_tipo_incidencia_id_fkey" FOREIGN KEY ("tipo_incidencia_id") REFERENCES "tipos_incidencia"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "incidencias" ADD CONSTRAINT "incidencias_estado_id_fkey" FOREIGN KEY ("estado_id") REFERENCES "estados"("id") ON DELETE RESTRICT ON UPDATE CASCADE;
