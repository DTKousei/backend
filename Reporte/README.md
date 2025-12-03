# API REST de Reportes de Asistencia

API REST completa para la generación y almacenamiento de reportes de asistencia de empleados en formatos Excel y PDF. Los reportes muestran información detallada de control de asistencia (horarios de entrada/salida, horas trabajadas, etc.) obtenida desde una API externa.

## 🚀 Características

- ✅ Generación de reportes en formato **Excel (XLSX)** con estilos profesionales
- ✅ Generación de reportes en formato **PDF** con tablas formateadas
- ✅ Integración con API externa de asistencia
- ✅ Almacenamiento persistente de reportes generados
- ✅ Gestión de plantillas de reportes personalizables
- ✅ Validaciones robustas con express-validator
- ✅ Manejo de errores centralizado
- ✅ Rate limiting para protección contra abuso
- ✅ Seguridad con Helmet y CORS

## 📋 Requisitos Previos

- Node.js >= 18.x
- PostgreSQL >= 13.x
- npm o yarn
- API externa de asistencia ejecutándose

## 🔧 Instalación

### 1. Clonar o navegar al directorio del proyecto

```bash
cd "d:\ActulaizacionUGEL\ptoyecto de control de asistencia\Backend\Reporte"
```

### 2. Instalar dependencias

```bash
npm install
```

### 3. Configurar variables de entorno

Copiar el archivo `.env.example` a `.env` y configurar las variables:

```bash
cp .env.example .env
```

Editar `.env` con tus credenciales:

```env
PORT=3001
NODE_ENV=development

# Database - Actualizar con tus credenciales de PostgreSQL
DATABASE_URL="postgresql://usuario:contraseña@localhost:5432/reportes_db?schema=public"

# External Attendance API
ATTENDANCE_API_URL=http://localhost:8000/api

# File Storage
STORAGE_PATH=./src/storage
MAX_FILE_SIZE_MB=10

# Rate Limiting
RATE_LIMIT_WINDOW_MS=900000
RATE_LIMIT_MAX_REQUESTS=100
```

### 4. Ejecutar migraciones de base de datos

```bash
npm run migrate
```

Este comando creará todas las tablas necesarias en PostgreSQL.

### 5. Generar Prisma Client

```bash
npm run prisma:generate
```

## 🏃 Ejecución

### Modo desarrollo (con hot reload)

```bash
npm run dev
```

### Modo producción

```bash
npm start
```

El servidor se ejecutará en `http://localhost:3001` (o el puerto configurado en `.env`).

## 📚 Estructura del Proyecto

```
Backend/Reporte/
├── prisma/
│   └── schema.prisma          # Esquema de base de datos
├── src/
│   ├── config/
│   │   ├── constants.js       # Constantes y configuración
│   │   └── database.js        # Cliente Prisma
│   ├── controllers/
│   │   ├── reportController.js    # Controlador de reportes
│   │   └── templateController.js  # Controlador de plantillas
│   ├── middleware/
│   │   ├── errorHandler.js    # Manejo de errores
│   │   └── validators.js      # Validadores
│   ├── routes/
│   │   ├── reportRoutes.js    # Rutas de reportes
│   │   └── templateRoutes.js  # Rutas de plantillas
│   ├── services/
│   │   ├── attendanceApiService.js  # Integración API externa
│   │   ├── excelGeneratorService.js # Generación Excel
│   │   ├── pdfGeneratorService.js   # Generación PDF
│   │   └── fileStorageService.js    # Almacenamiento archivos
│   ├── utils/
│   │   ├── dateUtils.js       # Utilidades de fechas
│   │   └── responseFormatter.js # Formato de respuestas
│   ├── storage/               # Archivos generados
│   └── index.js              # Servidor principal
├── .env                      # Variables de entorno
├── .env.example             # Ejemplo de variables
└── package.json             # Dependencias
```

## 🔌 API Endpoints

Ver [API_DOCUMENTATION.md](./API_DOCUMENTATION.md) para documentación detallada de todos los endpoints.

### Resumen de Endpoints

#### Reportes

- `POST /api/reportes/generar` - Generar reporte de asistencia
- `POST /api/reportes/generar-resumen` - Generar reporte resumido por días
- `GET /api/reportes/:id` - Obtener reporte por ID
- `GET /api/reportes/empleado/lista` - Listar reportes de un empleado
- `GET /api/reportes/:id/descargar` - Descargar archivo del reporte
- `DELETE /api/reportes/:id` - Eliminar reporte

#### Plantillas

- `GET /api/plantillas/tipos` - Obtener tipos de reporte
- `POST /api/plantillas` - Crear plantilla
- `GET /api/plantillas` - Listar plantillas
- `GET /api/plantillas/:id` - Obtener plantilla por ID
- `PUT /api/plantillas/:id` - Actualizar plantilla
- `DELETE /api/plantillas/:id` - Desactivar plantilla

## 🧪 Ejemplo de Uso

### 1. Crear una plantilla de reporte

```bash
curl -X POST http://localhost:3001/api/plantillas \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Reporte Mensual de Asistencia",
    "tipo_reporte_id": 1,
    "descripcion": "Reporte detallado de asistencia mensual",
    "esta_activo": true
  }'
```

### 2. Generar un reporte en Excel

```bash
curl -X POST http://localhost:3001/api/reportes/generar \
  -H "Content-Type: application/json" \
  -d '{
    "empleado_id": "1",
    "plantilla_id": "uuid-de-la-plantilla",
    "formato_archivo": "XLSX",
    "fecha_inicio": "2025-11-01",
    "fecha_fin": "2025-11-30",
    "nombre_reporte": "Asistencia Noviembre 2025"
  }'
```

### 3. Descargar el reporte generado

```bash
curl -X GET http://localhost:3001/api/reportes/{id}/descargar \
  --output reporte.xlsx
```

## 🗄️ Base de Datos

El proyecto utiliza PostgreSQL con Prisma ORM. El esquema incluye:

- **TipoReporte**: Tipos de reportes disponibles
- **PlantillasReporte**: Plantillas configurables para reportes
- **ReportesGenerados**: Registro de reportes generados

## 🔒 Seguridad

- **Helmet**: Protección de headers HTTP
- **CORS**: Control de acceso cross-origin
- **Rate Limiting**: Límite de peticiones por IP
- **Validaciones**: Validación exhaustiva de datos de entrada

## 🐛 Troubleshooting

### Error de conexión a PostgreSQL

Verificar que:

1. PostgreSQL está ejecutándose
2. Las credenciales en `DATABASE_URL` son correctas
3. La base de datos existe

### Error al generar reportes

Verificar que:

1. La API externa de asistencia está ejecutándose
2. La URL en `ATTENDANCE_API_URL` es correcta
3. Hay datos de asistencia disponibles para el empleado

### Archivos no se guardan

Verificar que:

1. El directorio `src/storage` existe y tiene permisos de escritura
2. Hay espacio en disco disponible

## 📝 Licencia

ISC

## 👥 Autor

Sistema de Control de Asistencia - UGEL
