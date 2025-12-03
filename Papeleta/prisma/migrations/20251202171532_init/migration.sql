/*
  Warnings:

  - You are about to drop the column `firma_supervisor_area_en` on the `permisos` table. All the data in the column will be lost.
  - You are about to drop the column `firma_supervisor_rrhh` on the `permisos` table. All the data in the column will be lost.
  - You are about to drop the column `firma_supervisor_rrhh_en` on the `permisos` table. All the data in the column will be lost.
  - A unique constraint covering the columns `[codigo]` on the table `estados` will be added. If there are existing duplicate values, this will fail.
  - A unique constraint covering the columns `[codigo]` on the table `permisos_tipos` will be added. If there are existing duplicate values, this will fail.
  - Added the required column `actualizado_en` to the `estados` table without a default value. This is not possible if the table is not empty.
  - Added the required column `codigo` to the `estados` table without a default value. This is not possible if the table is not empty.
  - Added the required column `actualizado_en` to the `permisos` table without a default value. This is not possible if the table is not empty.
  - Made the column `creado_en` on table `permisos` required. This step will fail if there are existing NULL values in that column.
  - Added the required column `actualizado_en` to the `permisos_tipos` table without a default value. This is not possible if the table is not empty.
  - Made the column `esta_activo` on table `permisos_tipos` required. This step will fail if there are existing NULL values in that column.

*/
-- AlterTable
ALTER TABLE "estados" ADD COLUMN     "actualizado_en" TIMESTAMP(3) NOT NULL,
ADD COLUMN     "codigo" VARCHAR(20) NOT NULL,
ADD COLUMN     "creado_en" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP;

-- AlterTable
ALTER TABLE "permisos" DROP COLUMN "firma_supervisor_area_en",
DROP COLUMN "firma_supervisor_rrhh",
DROP COLUMN "firma_supervisor_rrhh_en",
ADD COLUMN     "actualizado_en" TIMESTAMP(3) NOT NULL,
ADD COLUMN     "firma_jefe_area" TEXT,
ADD COLUMN     "firma_jefe_area_en" TIMESTAMP(3),
ADD COLUMN     "firma_rrhh" TEXT,
ADD COLUMN     "firma_rrhh_en" TIMESTAMP(3),
ADD COLUMN     "firma_solicitante_en" TIMESTAMP(3),
ADD COLUMN     "hora_salida_calculada" TIMESTAMP(3),
ADD COLUMN     "institucion_visitada" VARCHAR(255),
ADD COLUMN     "pdf_firmado_path" VARCHAR(500),
ADD COLUMN     "pdf_generado_path" VARCHAR(500),
ALTER COLUMN "firma_solicitante" DROP NOT NULL,
ALTER COLUMN "firma_solicitante" SET DATA TYPE TEXT,
ALTER COLUMN "firma_institucion" DROP NOT NULL,
ALTER COLUMN "firma_institucion" SET DATA TYPE TEXT,
ALTER COLUMN "creado_en" SET NOT NULL,
ALTER COLUMN "creado_en" SET DEFAULT CURRENT_TIMESTAMP;

-- AlterTable
ALTER TABLE "permisos_tipos" ADD COLUMN     "actualizado_en" TIMESTAMP(3) NOT NULL,
ADD COLUMN     "creado_en" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
ADD COLUMN     "requiere_firma_institucion" BOOLEAN NOT NULL DEFAULT false,
ADD COLUMN     "tiempo_maximo_horas" INTEGER,
ALTER COLUMN "esta_activo" SET NOT NULL,
ALTER COLUMN "esta_activo" SET DEFAULT true;

-- CreateIndex
CREATE UNIQUE INDEX "estados_codigo_key" ON "estados"("codigo");

-- CreateIndex
CREATE INDEX "permisos_empleado_id_idx" ON "permisos"("empleado_id");

-- CreateIndex
CREATE INDEX "permisos_estado_id_idx" ON "permisos"("estado_id");

-- CreateIndex
CREATE INDEX "permisos_tipo_permiso_id_idx" ON "permisos"("tipo_permiso_id");

-- CreateIndex
CREATE INDEX "permisos_fecha_hora_inicio_idx" ON "permisos"("fecha_hora_inicio");

-- CreateIndex
CREATE UNIQUE INDEX "permisos_tipos_codigo_key" ON "permisos_tipos"("codigo");
