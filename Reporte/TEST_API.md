# Test API REST - Reportes de Asistencia

## 1. Health Check

curl http://localhost:3004/health

## 2. Root Endpoint

curl http://localhost:3004/

## 3. Obtener Tipos de Reporte

curl http://localhost:3004/api/plantillas/tipos

## 4. Crear Plantilla

curl -X POST http://localhost:3004/api/plantillas `  -H "Content-Type: application/json"`
-d '{
"nombre": "Reporte Mensual de Asistencia",
"tipo_reporte_id": 1,
"descripcion": "Reporte detallado de asistencia mensual",
"esta_activo": true
}'

## 5. Listar Plantillas

curl http://localhost:3004/api/plantillas

## 6. Generar Reporte Excel

# Nota: Reemplazar PLANTILLA_ID con el ID obtenido en el paso 4

curl -X POST http://localhost:3004/api/reportes/generar `  -H "Content-Type: application/json"`
-d '{
"empleado_id": "1",
"plantilla_id": "PLANTILLA_ID",
"formato_archivo": "XLSX",
"fecha_inicio": "2025-11-01",
"fecha_fin": "2025-11-30",
"nombre_reporte": "Asistencia Noviembre 2025"
}'

## 7. Generar Reporte PDF

curl -X POST http://localhost:3004/api/reportes/generar `  -H "Content-Type: application/json"`
-d '{
"empleado_id": "1",
"plantilla_id": "PLANTILLA_ID",
"formato_archivo": "PDF",
"fecha_inicio": "2025-11-01",
"fecha_fin": "2025-11-30",
"nombre_reporte": "Asistencia Noviembre 2025 PDF"
}'

## 8. Listar Reportes de un Empleado

curl "http://localhost:3004/api/reportes/empleado/lista?empleado_id=1&page=1&limit=10"

## 9. Descargar Reporte

# Nota: Reemplazar REPORTE_ID con el ID obtenido

curl -X GET http://localhost:3004/api/reportes/REPORTE_ID/descargar --output reporte.xlsx
