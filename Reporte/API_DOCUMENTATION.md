# Documentación de API - Reportes de Asistencia

## Información General

**Base URL**: `http://localhost:3001/api`

**Content-Type**: `application/json`

**Formatos de Reporte Soportados**: `XLSX`, `PDF`, `CSV`, `JSON`

---

## 📊 Endpoints de Reportes

### 1. Generar Reporte de Asistencia

Genera un nuevo reporte de asistencia en el formato especificado.

**Endpoint**: `POST /reportes/generar`

**Request Body**:

```json
{
  "empleado_id": "1",
  "plantilla_id": "550e8400-e29b-41d4-a716-446655440000",
  "formato_archivo": "XLSX",
  "fecha_inicio": "2025-11-01",
  "fecha_fin": "2025-11-30",
  "nombre_reporte": "Asistencia Noviembre 2025"
}
```

**Campos**:

- `empleado_id` (string, requerido): ID del empleado
- `plantilla_id` (string, requerido): UUID de la plantilla (36 caracteres)
- `formato_archivo` (string, requerido): Formato del archivo (`XLSX` o `PDF`)
- `fecha_inicio` (string, opcional): Fecha de inicio en formato ISO 8601
- `fecha_fin` (string, opcional): Fecha de fin en formato ISO 8601
- `nombre_reporte` (string, opcional): Nombre personalizado del reporte (máx 200 caracteres)

**Response** (201 Created):

```json
{
  "success": true,
  "message": "Reporte generado exitosamente",
  "data": {
    "id": "650e8400-e29b-41d4-a716-446655440001",
    "Empleado_id": "1",
    "plantilla_id": "550e8400-e29b-41d4-a716-446655440000",
    "nombre_reporte": "Asistencia Noviembre 2025",
    "parametros": {
      "fecha_inicio": "2025-11-01",
      "fecha_fin": "2025-11-30",
      "user_id": "1"
    },
    "ruta_archivo": "./src/storage/reporte_1_1733259123456_a1b2c3d4.xlsx",
    "formato_archivo": "XLSX",
    "cantidad_registros": 45,
    "generado_en": "2025-12-03T21:25:23.456Z",
    "plantilla": {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "nombre": "Reporte Mensual",
      "tipo_reporte": {
        "id": 1,
        "nombre": "Asistencia Detallada"
      }
    }
  },
  "statusCode": 201
}
```

**Errores**:

- `400`: Datos de validación incorrectos
- `404`: Plantilla no encontrada o empleado sin datos de asistencia

---

### 2. Generar Reporte Resumido por Días

Genera un reporte resumido agrupado por días con horas trabajadas.

**Endpoint**: `POST /reportes/generar-resumen`

**Request Body**:

```json
{
  "empleado_id": "1",
  "plantilla_id": "550e8400-e29b-41d4-a716-446655440000",
  "formato_archivo": "PDF",
  "fecha_inicio": "2025-11-01",
  "fecha_fin": "2025-11-30",
  "nombre_reporte": "Resumen Mensual"
}
```

**Response** (201 Created):

```json
{
  "success": true,
  "message": "Reporte resumido generado exitosamente",
  "data": {
    "id": "750e8400-e29b-41d4-a716-446655440002",
    "Empleado_id": "1",
    "nombre_reporte": "Resumen Mensual",
    "formato_archivo": "PDF",
    "cantidad_registros": 22,
    "generado_en": "2025-12-03T21:30:00.000Z",
    "ruta_archivo": "./src/storage/resumen_1_1733259400000_b2c3d4e5.pdf"
  },
  "statusCode": 201
}
```

---

### 3. Obtener Reporte por ID

Obtiene la información de un reporte específico.

**Endpoint**: `GET /reportes/:id`

**Parámetros URL**:

- `id` (string): UUID del reporte

**Ejemplo**: `GET /reportes/650e8400-e29b-41d4-a716-446655440001`

**Response** (200 OK):

```json
{
  "success": true,
  "message": "Reporte obtenido exitosamente",
  "data": {
    "id": "650e8400-e29b-41d4-a716-446655440001",
    "Empleado_id": "1",
    "nombre_reporte": "Asistencia Noviembre 2025",
    "parametros": {
      "fecha_inicio": "2025-11-01",
      "fecha_fin": "2025-11-30"
    },
    "ruta_archivo": "./src/storage/reporte_1_1733259123456_a1b2c3d4.xlsx",
    "formato_archivo": "XLSX",
    "cantidad_registros": 45,
    "generado_en": "2025-12-03T21:25:23.456Z",
    "plantilla": {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "nombre": "Reporte Mensual",
      "descripcion": "Reporte detallado mensual",
      "tipo_reporte": {
        "id": 1,
        "nombre": "Asistencia Detallada"
      }
    }
  }
}
```

**Errores**:

- `404`: Reporte no encontrado

---

### 4. Listar Reportes por Empleado

Lista todos los reportes generados para un empleado con paginación.

**Endpoint**: `GET /reportes/empleado/lista`

**Query Parameters**:

- `empleado_id` (string, requerido): ID del empleado
- `page` (integer, opcional): Número de página (default: 1)
- `limit` (integer, opcional): Registros por página (default: 10, máx: 100)

**Ejemplo**: `GET /reportes/empleado/lista?empleado_id=1&page=1&limit=10`

**Response** (200 OK):

```json
{
  "success": true,
  "data": [
    {
      "id": "650e8400-e29b-41d4-a716-446655440001",
      "Empleado_id": "1",
      "nombre_reporte": "Asistencia Noviembre 2025",
      "formato_archivo": "XLSX",
      "cantidad_registros": 45,
      "generado_en": "2025-12-03T21:25:23.456Z",
      "plantilla": {
        "nombre": "Reporte Mensual",
        "tipo_reporte": {
          "nombre": "Asistencia Detallada"
        }
      }
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 10,
    "total": 15,
    "totalPages": 2
  }
}
```

---

### 5. Descargar Reporte

Descarga el archivo físico de un reporte.

**Endpoint**: `GET /reportes/:id/descargar`

**Parámetros URL**:

- `id` (string): UUID del reporte

**Ejemplo**: `GET /reportes/650e8400-e29b-41d4-a716-446655440001/descargar`

**Response** (200 OK):

- **Content-Type**: `application/pdf` o `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`
- **Content-Disposition**: `attachment; filename="reporte_1_1733259123456_a1b2c3d4.xlsx"`
- **Body**: Archivo binario

**Errores**:

- `404`: Reporte o archivo no encontrado

---

### 6. Eliminar Reporte

Elimina un reporte y su archivo asociado.

**Endpoint**: `DELETE /reportes/:id`

**Parámetros URL**:

- `id` (string): UUID del reporte

**Ejemplo**: `DELETE /reportes/650e8400-e29b-41d4-a716-446655440001`

**Response** (200 OK):

```json
{
  "success": true,
  "message": "Reporte eliminado exitosamente",
  "data": null
}
```

**Errores**:

- `404`: Reporte no encontrado

---

## 📋 Endpoints de Plantillas

### 1. Obtener Tipos de Reporte

Lista todos los tipos de reporte disponibles.

**Endpoint**: `GET /plantillas/tipos`

**Response** (200 OK):

```json
{
  "success": true,
  "message": "Tipos de reporte obtenidos exitosamente",
  "data": [
    {
      "id": 1,
      "nombre": "Asistencia Detallada"
    },
    {
      "id": 2,
      "nombre": "Resumen Mensual"
    }
  ]
}
```

---

### 2. Crear Plantilla

Crea una nueva plantilla de reporte.

**Endpoint**: `POST /plantillas`

**Request Body**:

```json
{
  "nombre": "Reporte Semanal de Asistencia",
  "tipo_reporte_id": 1,
  "descripcion": "Reporte detallado de asistencia semanal",
  "parametros": {
    "incluir_totales": true,
    "formato_fecha": "DD/MM/YYYY"
  },
  "esta_activo": true
}
```

**Campos**:

- `nombre` (string, requerido): Nombre de la plantilla (máx 100 caracteres)
- `tipo_reporte_id` (integer, requerido): ID del tipo de reporte
- `descripcion` (string, opcional): Descripción de la plantilla
- `parametros` (object, opcional): Parámetros personalizados en formato JSON
- `esta_activo` (boolean, opcional): Estado activo (default: true)

**Response** (201 Created):

```json
{
  "success": true,
  "message": "Plantilla creada exitosamente",
  "data": {
    "id": "850e8400-e29b-41d4-a716-446655440003",
    "nombre": "Reporte Semanal de Asistencia",
    "tipo_reporte_id": 1,
    "descripcion": "Reporte detallado de asistencia semanal",
    "parametros": {
      "incluir_totales": true,
      "formato_fecha": "DD/MM/YYYY"
    },
    "esta_activo": true,
    "creado_en": "2025-12-03T21:40:00.000Z",
    "tipo_reporte": {
      "id": 1,
      "nombre": "Asistencia Detallada"
    }
  },
  "statusCode": 201
}
```

**Errores**:

- `400`: Datos de validación incorrectos
- `404`: Tipo de reporte no encontrado

---

### 3. Listar Plantillas

Lista todas las plantillas con filtros opcionales.

**Endpoint**: `GET /plantillas`

**Query Parameters**:

- `activas_solo` (string, opcional): Filtrar solo activas (`true`/`false`, default: `true`)
- `tipo_reporte_id` (integer, opcional): Filtrar por tipo de reporte

**Ejemplo**: `GET /plantillas?activas_solo=true&tipo_reporte_id=1`

**Response** (200 OK):

```json
{
  "success": true,
  "message": "Plantillas obtenidas exitosamente",
  "data": [
    {
      "id": "850e8400-e29b-41d4-a716-446655440003",
      "nombre": "Reporte Semanal de Asistencia",
      "descripcion": "Reporte detallado de asistencia semanal",
      "esta_activo": true,
      "creado_en": "2025-12-03T21:40:00.000Z",
      "tipo_reporte": {
        "id": 1,
        "nombre": "Asistencia Detallada"
      }
    }
  ]
}
```

---

### 4. Obtener Plantilla por ID

Obtiene una plantilla específica.

**Endpoint**: `GET /plantillas/:id`

**Parámetros URL**:

- `id` (string): UUID de la plantilla

**Response** (200 OK):

```json
{
  "success": true,
  "message": "Plantilla obtenida exitosamente",
  "data": {
    "id": "850e8400-e29b-41d4-a716-446655440003",
    "nombre": "Reporte Semanal de Asistencia",
    "descripcion": "Reporte detallado de asistencia semanal",
    "parametros": {
      "incluir_totales": true
    },
    "esta_activo": true,
    "tipo_reporte": {
      "id": 1,
      "nombre": "Asistencia Detallada"
    }
  }
}
```

---

### 5. Actualizar Plantilla

Actualiza una plantilla existente.

**Endpoint**: `PUT /plantillas/:id`

**Request Body** (todos los campos son opcionales):

```json
{
  "nombre": "Reporte Semanal Actualizado",
  "descripcion": "Nueva descripción",
  "parametros": {
    "incluir_totales": false
  },
  "esta_activo": true
}
```

**Response** (200 OK):

```json
{
  "success": true,
  "message": "Plantilla actualizada exitosamente",
  "data": {
    "id": "850e8400-e29b-41d4-a716-446655440003",
    "nombre": "Reporte Semanal Actualizado",
    "descripcion": "Nueva descripción",
    "esta_activo": true
  }
}
```

---

### 6. Desactivar Plantilla

Desactiva una plantilla (soft delete).

**Endpoint**: `DELETE /plantillas/:id`

**Response** (200 OK):

```json
{
  "success": true,
  "message": "Plantilla desactivada exitosamente",
  "data": null
}
```

---

## 🔍 Códigos de Estado HTTP

| Código | Descripción                                          |
| ------ | ---------------------------------------------------- |
| 200    | OK - Petición exitosa                                |
| 201    | Created - Recurso creado exitosamente                |
| 400    | Bad Request - Datos de validación incorrectos        |
| 404    | Not Found - Recurso no encontrado                    |
| 409    | Conflict - Conflicto con datos existentes            |
| 429    | Too Many Requests - Límite de rate limiting excedido |
| 500    | Internal Server Error - Error del servidor           |

---

## 📝 Formato de Errores

Todas las respuestas de error siguen este formato:

```json
{
  "success": false,
  "message": "Descripción del error",
  "errors": [
    {
      "field": "empleado_id",
      "message": "El ID del empleado es requerido"
    }
  ],
  "statusCode": 400
}
```

---

## 🔐 Rate Limiting

- **Ventana**: 15 minutos (900,000 ms)
- **Máximo de peticiones**: 100 por IP
- **Header de respuesta**: `X-RateLimit-Limit`, `X-RateLimit-Remaining`

Cuando se excede el límite:

```json
{
  "success": false,
  "message": "Demasiadas peticiones desde esta IP, por favor intente más tarde.",
  "statusCode": 429
}
```

---

## 📊 Estructura de Datos de Asistencia

Los datos obtenidos de la API externa tienen el siguiente formato:

```json
{
  "user_id": "1",
  "timestamp": "2025-11-27T15:38:52",
  "status": 1,
  "punch": 4,
  "id": 9,
  "dispositivo_id": 1,
  "sincronizado": true,
  "fecha_sincronizacion": "2025-11-27T15:39:17",
  "fecha_creacion": "2025-11-27T15:39:17"
}
```

**Valores de `status`**:

- `0`: Ausente
- `1`: Presente
- `2`: Tardanza
- `3`: Permiso

**Valores de `punch`**:

- `0`: Entrada
- `1`: Salida
- `2`: Inicio Break
- `3`: Fin Break
- `4`: Inicio Almuerzo
- `5`: Fin Almuerzo
