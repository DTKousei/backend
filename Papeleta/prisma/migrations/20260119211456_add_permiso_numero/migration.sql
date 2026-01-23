/*
  Warnings:

  - A unique constraint covering the columns `[numero]` on the table `permisos` will be added. If there are existing duplicate values, this will fail.

*/
-- AlterTable
ALTER TABLE "permisos" ADD COLUMN     "numero" SERIAL NOT NULL;

-- CreateIndex
CREATE UNIQUE INDEX "permisos_numero_key" ON "permisos"("numero");
