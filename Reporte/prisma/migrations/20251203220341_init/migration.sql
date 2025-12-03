-- CreateEnum
CREATE TYPE "ReportesGeneradosFormatoArchivo" AS ENUM ('PDF', 'XLSX', 'CSV', 'JSON');

-- CreateTable
CREATE TABLE "TipoReporte" (
    "id" SERIAL NOT NULL,
    "nombre" VARCHAR(50) NOT NULL,

    CONSTRAINT "TipoReporte_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "PlantillasReporte" (
    "id" VARCHAR(36) NOT NULL,
    "nombre" VARCHAR(100) NOT NULL,
    "descripcion" TEXT,
    "parametros" JSONB,
    "esta_activo" BOOLEAN NOT NULL,
    "creado_en" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "tipo_reporte_id" INTEGER NOT NULL,

    CONSTRAINT "PlantillasReporte_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "ReportesGenerados" (
    "id" VARCHAR(36) NOT NULL,
    "Empleado_id" VARCHAR(36) NOT NULL,
    "nombre_reporte" VARCHAR(200) NOT NULL,
    "parametros" JSONB NOT NULL,
    "ruta_archivo" VARCHAR(500) NOT NULL,
    "formato_archivo" "ReportesGeneradosFormatoArchivo" NOT NULL,
    "cantidad_registros" INTEGER,
    "generado_en" TIMESTAMP,
    "plantilla_id" VARCHAR(36) NOT NULL,

    CONSTRAINT "ReportesGenerados_pkey" PRIMARY KEY ("id")
);

-- CreateIndex
CREATE INDEX "PlantillasReporte_tipo_reporte_id_idx" ON "PlantillasReporte"("tipo_reporte_id");

-- CreateIndex
CREATE INDEX "ReportesGenerados_plantilla_id_idx" ON "ReportesGenerados"("plantilla_id");

-- AddForeignKey
ALTER TABLE "PlantillasReporte" ADD CONSTRAINT "PlantillasReporte_tipo_reporte_id_fkey" FOREIGN KEY ("tipo_reporte_id") REFERENCES "TipoReporte"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "ReportesGenerados" ADD CONSTRAINT "ReportesGenerados_plantilla_id_fkey" FOREIGN KEY ("plantilla_id") REFERENCES "PlantillasReporte"("id") ON DELETE RESTRICT ON UPDATE CASCADE;
