# Documentación API - Sistema de Gestión de Incidencias

## Tabla de Contenidos

1. [Introducción](#introducción)
2. [Configuración Inicial](#configuración-inicial)
3. [Endpoints - Estados](#endpoints---estados)
4. [Endpoints - Tipos de Incidencia](#endpoints---tipos-de-incidencia)
5. [Endpoints - Incidencias](#endpoints---incidencias)
6. [Guía de Uso Paso a Paso](#guía-de-uso-paso-a-paso)
7. [Códigos de Error](#códigos-de-error)

---

## Introducción

Esta API REST permite gestionar incidencias de empleados (justificaciones por faltas o permisos) con soporte para carga de documentos PDF.

**URL Base:** `http://localhost:3003`

**Formato de Respuesta:** JSON

---

## Configuración Inicial

### 1. Variables de Entorno

Crear archivo `.env` con:

```env
DATABASE_URL="postgresql://usuario:contraseña@localhost:5432/nombre_bd"
PORT=3003
NODE_ENV=development
```

### 2. Iniciar el Servidor

```bash
npm install
npm run dev
```

El servidor estará disponible en `http://localhost:3003`

---

## Endpoints - Estados

### 1. Crear Estado

**Endpoint:** `POST /api/estados`

**Headers:**

```
Content-Type: application/json
```

**Body (JSON):**

```json
{
  "nombre": "Pendiente",
  "descripcion": "Incidencia pendiente de revisión"
}
```

**Campos:**
| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| nombre | string | Sí | Nombre del estado (máx. 50 caracteres) |
| descripcion | string | No | Descripción del estado |

**Respuesta Exitosa (201 Created):**

```json
{
  "message": "Estado creado exitosamente",
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "nombre": "Pendiente",
    "descripcion": "Incidencia pendiente de revisión"
  }
}
```

**Ejemplo con cURL:**

```bash
curl -X POST http://localhost:3003/api/estados \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Pendiente",
    "descripcion": "Incidencia pendiente de revisión"
  }'
```

---

### 2. Listar Estados

**Endpoint:** `GET /api/estados`

**Headers:** Ninguno requerido

**Respuesta Exitosa (200 OK):**

```json
{
  "data": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "nombre": "Pendiente",
      "descripcion": "Incidencia pendiente de revisión"
    },
    {
      "id": "660e8400-e29b-41d4-a716-446655440001",
      "nombre": "Aprobado",
      "descripcion": "Incidencia aprobada"
    }
  ]
}
```

**Ejemplo con cURL:**

```bash
curl http://localhost:3003/api/estados
```

---

### 3. Obtener Estado por ID

**Endpoint:** `GET /api/estados/:id`

**Parámetros de URL:**

- `id` (UUID): ID del estado

**Respuesta Exitosa (200 OK):**

```json
{
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "nombre": "Pendiente",
    "descripcion": "Incidencia pendiente de revisión",
    "incidencias": [
      {
        "id": "770e8400-e29b-41d4-a716-446655440002",
        "empleado_id": "emp-123",
        "descripcion": "Cita médica",
        "creado_en": "2025-12-03T10:00:00.000Z"
      }
    ]
  }
}
```

**Ejemplo con cURL:**

```bash
curl http://localhost:3003/api/estados/550e8400-e29b-41d4-a716-446655440000
```

---

### 4. Actualizar Estado

**Endpoint:** `PUT /api/estados/:id`

**Headers:**

```
Content-Type: application/json
```

**Body (JSON):**

```json
{
  "nombre": "En Revisión",
  "descripcion": "Incidencia en proceso de revisión"
}
```

**Respuesta Exitosa (200 OK):**

```json
{
  "message": "Estado actualizado exitosamente",
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "nombre": "En Revisión",
    "descripcion": "Incidencia en proceso de revisión"
  }
}
```

---

### 5. Eliminar Estado

**Endpoint:** `DELETE /api/estados/:id`

**Respuesta Exitosa (200 OK):**

```json
{
  "message": "Estado eliminado exitosamente"
}
```

**Error si hay incidencias asociadas (400 Bad Request):**

```json
{
  "error": "No se puede eliminar",
  "message": "Existen 5 incidencia(s) con este estado. Cámbielas primero a otro estado."
}
```

---

## Endpoints - Tipos de Incidencia

### 1. Crear Tipo de Incidencia

**Endpoint:** `POST /api/tipos-incidencia`

**Headers:**

```
Content-Type: application/json
```

**Body (JSON):**

```json
{
  "nombre": "Permiso Médico",
  "codigo": "PM001",
  "requiere_aprobacion": true,
  "requiere_documento": true,
  "descuenta_salario": false,
  "esta_activo": true,
  "max_dias_anual": 30,
  "max_solicitudes_anual": 12,
  "toma_dias_calendario": true
}
```

**Campos:**
| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| nombre | string | Sí | Nombre del tipo (máx. 100 caracteres) |
| codigo | string | Sí | Código único (máx. 20 caracteres) |
| requiere_aprobacion | boolean | Sí | Si requiere aprobación |
| requiere_documento | boolean | Sí | Si requiere documento PDF |
| descuenta_salario | boolean | Sí | Si descuenta del salario |
| esta_activo | boolean | Sí | Si está activo |
| max_dias_anual | integer | No | Límite de días permitidos por año |
| max_solicitudes_anual | integer | No | Límite de veces que se puede solicitar por año |
| toma_dias_calendario | boolean | No | true: cuenta L-D, false: cuenta solo días hábiles (L-V) |

**Respuesta Exitosa (201 Created):**

```json
{
  "message": "Tipo de incidencia creado exitosamente",
  "data": {
    "id": "880e8400-e29b-41d4-a716-446655440003",
    "nombre": "Permiso Médico",
    "codigo": "PM001",
    "requiere_aprobacion": true,
    "requiere_documento": true,
    "descuenta_salario": false,
    "esta_activo": true,
    "max_dias_anual": 30,
    "max_solicitudes_anual": 12,
    "toma_dias_calendario": true,
    "creado_en": "2025-12-03T10:00:00.000Z"
  }
}
```

**Ejemplo con cURL:**

```bash
curl -X POST http://localhost:3003/api/tipos-incidencia \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Permiso Médico",
    "codigo": "PM001",
    "requiere_aprobacion": true,
    "requiere_documento": true,
    "descuenta_salario": false,
    "esta_activo": true,
    "max_dias_anual": 30
  }'
```

---

### 2. Listar Tipos de Incidencia

**Endpoint:** `GET /api/tipos-incidencia`

**Query Parameters (opcionales):**

- `esta_activo` (boolean): Filtrar por estado activo/inactivo

**Ejemplo:** `GET /api/tipos-incidencia?esta_activo=true`

**Respuesta Exitosa (200 OK):**

```json
{
  "data": [
    {
      "id": "880e8400-e29b-41d4-a716-446655440003",
      "nombre": "Permiso Médico",
      "codigo": "PM001",
      "requiere_aprobacion": true,
      "requiere_documento": true,
      "descuenta_salario": false,
      "esta_activo": true,
      "creado_en": "2025-12-03T10:00:00.000Z"
    }
  ]
}
```

---

### 3. Obtener Tipo de Incidencia por ID

**Endpoint:** `GET /api/tipos-incidencia/:id`

**Respuesta Exitosa (200 OK):**

```json
{
  "data": {
    "id": "880e8400-e29b-41d4-a716-446655440003",
    "nombre": "Permiso Médico",
    "codigo": "PM001",
    "requiere_aprobacion": true,
    "requiere_documento": true,
    "descuenta_salario": false,
    "esta_activo": true,
    "creado_en": "2025-12-03T10:00:00.000Z",
    "incidencias": [
      {
        "id": "990e8400-e29b-41d4-a716-446655440004",
        "empleado_id": "emp-123",
        "descripcion": "Cita médica programada",
        "creado_en": "2025-12-03T11:00:00.000Z"
      }
    ]
  }
}
```

---

### 4. Actualizar Tipo de Incidencia

**Endpoint:** `PUT /api/tipos-incidencia/:id`

**Body (JSON):** (Todos los campos son opcionales)

```json
{
  "nombre": "Permiso Médico Actualizado",
  "esta_activo": false,
  "max_dias_anual": 45
}
```

**Respuesta Exitosa (200 OK):**

```json
{
  "message": "Tipo de incidencia actualizado exitosamente",
  "data": {
    "id": "880e8400-e29b-41d4-a716-446655440003",
    "nombre": "Permiso Médico Actualizado",
    "codigo": "PM001",
    "requiere_aprobacion": true,
    "requiere_documento": true,
    "descuenta_salario": false,
    "esta_activo": false,
    "creado_en": "2025-12-03T10:00:00.000Z"
  }
}
```

---

### 5. Eliminar Tipo de Incidencia

**Endpoint:** `DELETE /api/tipos-incidencia/:id`

**Respuesta Exitosa (200 OK):**

```json
{
  "message": "Tipo de incidencia eliminado exitosamente"
}
```

**Error si hay incidencias asociadas (400 Bad Request):**

```json
{
  "error": "No se puede eliminar",
  "message": "Existen 3 incidencia(s) asociadas a este tipo. Elimínelas primero o desactive el tipo."
}
```

---

## Endpoints - Incidencias

### 1. Crear Incidencia (con PDF)

**Endpoint:** `POST /api/incidencias`

**Headers:**

```
Content-Type: multipart/form-data
```

**Form Data:**
| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| empleado_id | string | Sí | ID del empleado |
| tipo_incidencia_id | UUID | Sí | ID del tipo de incidencia |
| fecha_inicio | date (ISO 8601) | Sí | Fecha de inicio (YYYY-MM-DD) |
| fecha_fin | date (ISO 8601) | Sí | Fecha de fin (>= fecha_inicio) |
| descripcion | string | Sí | Descripción de la incidencia |
| estado_id | UUID | Sí | ID del estado |
| documento | file (PDF) | Sí | Archivo PDF (máx. 10 MB) |

**Respuesta Exitosa (201 Created):**

```json
{
  "message": "Incidencia creada exitosamente",
  "data": {
    "id": "aa0e8400-e29b-41d4-a716-446655440005",
    "empleado_id": "emp-123",
    "tipo_incidencia_id": "880e8400-e29b-41d4-a716-446655440003",
    "fecha_inicio": "2025-12-03T00:00:00.000Z",
    "fecha_fin": "2025-12-03T00:00:00.000Z",
    "descripcion": "Cita médica programada",
    "url_documento": "C:\\IncidenciasDocumentos\\justificante-1733241234567-987654321.pdf",
    "estado_id": "550e8400-e29b-41d4-a716-446655440000",
    "aprobado_por": null,
    "aprobado_en": null,
    "motivo_rechazo": null,
    "creado_en": "2025-12-03T15:00:00.000Z",
    "tipo_incidencia": {
      "id": "880e8400-e29b-41d4-a716-446655440003",
      "nombre": "Permiso Médico",
      "codigo": "PM001"
    },
    "estado": {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "nombre": "Pendiente"
    }
  }
}
```

**Ejemplo con cURL:**

```bash
curl -X POST http://localhost:3003/api/incidencias \
  -F "empleado_id=emp-123" \
  -F "tipo_incidencia_id=880e8400-e29b-41d4-a716-446655440003" \
  -F "fecha_inicio=2025-12-03" \
  -F "fecha_fin=2025-12-03" \
  -F "descripcion=Cita médica programada" \
  -F "estado_id=550e8400-e29b-41d4-a716-446655440000" \
  -F "documento=@/ruta/al/archivo.pdf"
```

**Errores Comunes:**

**Sin archivo PDF (400 Bad Request):**

```json
{
  "error": "Documento requerido",
  "message": "Debe cargar un documento PDF como justificante"
}
```

**Archivo no es PDF (400 Bad Request):**

```json
{
  "error": "Tipo de archivo no válido",
  "message": "Solo se permiten archivos PDF"
}
```

**Archivo muy grande (400 Bad Request):**

```json
{
  "error": "Archivo demasiado grande",
  "message": "El archivo no puede superar los 10 MB"
}
```

**Fecha inválida (400 Bad Request):**

```json
{
  "error": "Errores de validación",
  "details": [
    {
      "msg": "La fecha de fin debe ser posterior o igual a la fecha de inicio",
      "param": "fecha_fin",
      "location": "body"
    }
  ]
}
```

**Límite excedido (400 Bad Request):**

```json
{
  "error": "Límite excedido",
  "message": "Esta solicitud de 5 días excede su saldo. Ha consumido 28 de 30 días permitidos este año."
}
```

---

### 2. Listar Incidencias

**Endpoint:** `GET /api/incidencias`

**Query Parameters (opcionales):**
| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| page | number | Número de página (default: 1) |
| limit | number | Elementos por página (default: 10) |
| empleado_id | string | Filtrar por empleado |
| estado_id | UUID | Filtrar por estado |
| tipo_incidencia_id | UUID | Filtrar por tipo de incidencia |

**Ejemplo:** `GET /api/incidencias?page=1&limit=5&empleado_id=emp-123`

**Respuesta Exitosa (200 OK):**

```json
{
  "data": [
    {
      "id": "aa0e8400-e29b-41d4-a716-446655440005",
      "empleado_id": "emp-123",
      "tipo_incidencia_id": "880e8400-e29b-41d4-a716-446655440003",
      "fecha_inicio": "2025-12-03T00:00:00.000Z",
      "fecha_fin": "2025-12-03T00:00:00.000Z",
      "descripcion": "Cita médica programada",
      "url_documento": "C:\\IncidenciasDocumentos\\justificante-1733241234567-987654321.pdf",
      "estado_id": "550e8400-e29b-41d4-a716-446655440000",
      "aprobado_por": null,
      "aprobado_en": null,
      "motivo_rechazo": null,
      "creado_en": "2025-12-03T15:00:00.000Z",
      "tipo_incidencia": {
        "id": "880e8400-e29b-41d4-a716-446655440003",
        "nombre": "Permiso Médico",
        "codigo": "PM001",
        "requiere_aprobacion": true,
        "requiere_documento": true,
        "descuenta_salario": false,
        "esta_activo": true
      },
      "estado": {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "nombre": "Pendiente",
        "descripcion": "Incidencia pendiente de revisión"
      }
    }
  ],
  "pagination": {
    "total": 15,
    "page": 1,
    "limit": 5,
    "totalPages": 3
  }
}
```

**Ejemplo con cURL:**

```bash
curl "http://localhost:3003/api/incidencias?page=1&limit=10&empleado_id=emp-123"
```

---

### 3. Obtener Incidencia por ID

**Endpoint:** `GET /api/incidencias/:id`

**Respuesta Exitosa (200 OK):**

```json
{
  "data": {
    "id": "aa0e8400-e29b-41d4-a716-446655440005",
    "empleado_id": "emp-123",
    "tipo_incidencia_id": "880e8400-e29b-41d4-a716-446655440003",
    "fecha_inicio": "2025-12-03T00:00:00.000Z",
    "fecha_fin": "2025-12-03T00:00:00.000Z",
    "descripcion": "Cita médica programada",
    "url_documento": "C:\\IncidenciasDocumentos\\justificante-1733241234567-987654321.pdf",
    "estado_id": "550e8400-e29b-41d4-a716-446655440000",
    "aprobado_por": null,
    "aprobado_en": null,
    "motivo_rechazo": null,
    "creado_en": "2025-12-03T15:00:00.000Z",
    "tipo_incidencia": {
      "id": "880e8400-e29b-41d4-a716-446655440003",
      "nombre": "Permiso Médico",
      "codigo": "PM001",
      "requiere_aprobacion": true,
      "requiere_documento": true,
      "descuenta_salario": false,
      "esta_activo": true,
      "creado_en": "2025-12-03T10:00:00.000Z"
    },
    "estado": {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "nombre": "Pendiente",
      "descripcion": "Incidencia pendiente de revisión"
    }
  }
}
```

**Error si no existe (404 Not Found):**

```json
{
  "error": "No encontrado",
  "message": "La incidencia no existe"
}
```

---

### 4. Actualizar Incidencia

**Endpoint:** `PUT /api/incidencias/:id`

**Headers:**

```
Content-Type: multipart/form-data
```

**Form Data (todos opcionales):**

- `empleado_id` (string)
- `tipo_incidencia_id` (UUID)
- `fecha_inicio` (date)
- `fecha_fin` (date)
- `descripcion` (string)
- `estado_id` (UUID)
- `documento` (file PDF) - Si se envía, reemplaza el anterior

**Respuesta Exitosa (200 OK):**

```json
{
  "message": "Incidencia actualizada exitosamente",
  "data": {
    "id": "aa0e8400-e29b-41d4-a716-446655440005",
    "empleado_id": "emp-123",
    "tipo_incidencia_id": "880e8400-e29b-41d4-a716-446655440003",
    "fecha_inicio": "2025-12-03T00:00:00.000Z",
    "fecha_fin": "2025-12-04T00:00:00.000Z",
    "descripcion": "Cita médica programada - Control mensual",
    "url_documento": "C:\\IncidenciasDocumentos\\justificante-1733241234567-987654321.pdf",
    "estado_id": "550e8400-e29b-41d4-a716-446655440000",
    "aprobado_por": null,
    "aprobado_en": null,
    "motivo_rechazo": null,
    "creado_en": "2025-12-03T15:00:00.000Z",
    "tipo_incidencia": {
      "id": "880e8400-e29b-41d4-a716-446655440003",
      "nombre": "Permiso Médico"
    },
    "estado": {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "nombre": "Pendiente"
    }
  }
}
```

**Ejemplo con cURL (solo actualizar descripción):**

```bash
curl -X PUT http://localhost:3003/api/incidencias/aa0e8400-e29b-41d4-a716-446655440005 \
  -F "descripcion=Cita médica programada - Control mensual"
```

**Ejemplo con cURL (actualizar con nuevo PDF):**

```bash
curl -X PUT http://localhost:3003/api/incidencias/aa0e8400-e29b-41d4-a716-446655440005 \
  -F "descripcion=Actualizado con nuevo documento" \
  -F "documento=@/ruta/al/nuevo-archivo.pdf"
```

---

### 5. Eliminar Incidencia

**Endpoint:** `DELETE /api/incidencias/:id`

**Respuesta Exitosa (200 OK):**

```json
{
  "message": "Incidencia eliminada exitosamente"
}
```

> **Nota:** Al eliminar una incidencia, el archivo PDF asociado también se elimina del disco.

**Ejemplo con cURL:**

```bash
curl -X DELETE http://localhost:3003/api/incidencias/aa0e8400-e29b-41d4-a716-446655440005
```

---

### 6. Aprobar Incidencia

**Endpoint:** `PATCH /api/incidencias/:id/aprobar`

**Headers:**

```
Content-Type: application/json
```

**Body (JSON):**

```json
{
  "aprobado_por": "supervisor-456"
}
```

**Campos:**
| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| aprobado_por | string | Sí | ID del supervisor que aprueba |

**Respuesta Exitosa (200 OK):**

```json
{
  "message": "Incidencia aprobada exitosamente",
  "data": {
    "id": "aa0e8400-e29b-41d4-a716-446655440005",
    "empleado_id": "emp-123",
    "tipo_incidencia_id": "880e8400-e29b-41d4-a716-446655440003",
    "fecha_inicio": "2025-12-03T00:00:00.000Z",
    "fecha_fin": "2025-12-03T00:00:00.000Z",
    "descripcion": "Cita médica programada",
    "url_documento": "C:\\IncidenciasDocumentos\\justificante-1733241234567-987654321.pdf",
    "estado_id": "550e8400-e29b-41d4-a716-446655440000",
    "aprobado_por": "supervisor-456",
    "aprobado_en": "2025-12-03T16:30:00.000Z",
    "motivo_rechazo": null,
    "creado_en": "2025-12-03T15:00:00.000Z",
    "tipo_incidencia": {
      "id": "880e8400-e29b-41d4-a716-446655440003",
      "nombre": "Permiso Médico"
    },
    "estado": {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "nombre": "Pendiente"
    }
  }
}
```

**Ejemplo con cURL:**

```bash
curl -X PATCH http://localhost:3003/api/incidencias/aa0e8400-e29b-41d4-a716-446655440005/aprobar \
  -H "Content-Type: application/json" \
  -d '{"aprobado_por": "supervisor-456"}'
```

---

### 7. Rechazar Incidencia

**Endpoint:** `PATCH /api/incidencias/:id/rechazar`

**Headers:**

```
Content-Type: application/json
```

**Body (JSON):**

```json
{
  "motivo_rechazo": "El documento presentado no es válido"
}
```

**Campos:**
| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| motivo_rechazo | string | Sí | Motivo del rechazo |

**Respuesta Exitosa (200 OK):**

```json
{
  "message": "Incidencia rechazada",
  "data": {
    "id": "aa0e8400-e29b-41d4-a716-446655440005",
    "empleado_id": "emp-123",
    "tipo_incidencia_id": "880e8400-e29b-41d4-a716-446655440003",
    "fecha_inicio": "2025-12-03T00:00:00.000Z",
    "fecha_fin": "2025-12-03T00:00:00.000Z",
    "descripcion": "Cita médica programada",
    "url_documento": "C:\\IncidenciasDocumentos\\justificante-1733241234567-987654321.pdf",
    "estado_id": "550e8400-e29b-41d4-a716-446655440000",
    "aprobado_por": null,
    "aprobado_en": null,
    "motivo_rechazo": "El documento presentado no es válido",
    "creado_en": "2025-12-03T15:00:00.000Z",
    "tipo_incidencia": {
      "id": "880e8400-e29b-41d4-a716-446655440003",
      "nombre": "Permiso Médico"
    },
    "estado": {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "nombre": "Pendiente"
    }
  }
}
```

**Ejemplo con cURL:**

```bash
curl -X PATCH http://localhost:3003/api/incidencias/aa0e8400-e29b-41d4-a716-446655440005/rechazar \
  -H "Content-Type: application/json" \
  -d '{"motivo_rechazo": "El documento presentado no es válido"}'
```

---

## Guía de Uso Paso a Paso

### Escenario Completo: Registrar una Incidencia

#### Paso 1: Crear Estados Necesarios

```bash
# Estado: Pendiente
curl -X POST http://localhost:3003/api/estados \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Pendiente",
    "descripcion": "Incidencia pendiente de revisión"
  }'

# Guardar el ID retornado, ejemplo: 550e8400-e29b-41d4-a716-446655440000

# Estado: Aprobado
curl -X POST http://localhost:3003/api/estados \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Aprobado",
    "descripcion": "Incidencia aprobada"
  }'

# Estado: Rechazado
curl -X POST http://localhost:3003/api/estados \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Rechazado",
    "descripcion": "Incidencia rechazada"
  }'
```

#### Paso 2: Crear Tipos de Incidencia

```bash
# Tipo: Permiso Médico
curl -X POST http://localhost:3003/api/tipos-incidencia \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Permiso Médico",
    "codigo": "PM001",
    "requiere_aprobacion": true,
    "requiere_documento": true,
    "descuenta_salario": false,
    "esta_activo": true
  }'

# Guardar el ID retornado, ejemplo: 880e8400-e29b-41d4-a716-446655440003

# Tipo: Permiso Personal
curl -X POST http://localhost:3003/api/tipos-incidencia \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Permiso Personal",
    "codigo": "PP001",
    "requiere_aprobacion": true,
    "requiere_documento": false,
    "descuenta_salario": true,
    "esta_activo": true
  }'
```

#### Paso 3: Crear una Incidencia con Documento

```bash
curl -X POST http://localhost:3003/api/incidencias \
  -F "empleado_id=emp-123" \
  -F "tipo_incidencia_id=880e8400-e29b-41d4-a716-446655440003" \
  -F "fecha_inicio=2025-12-03" \
  -F "fecha_fin=2025-12-03" \
  -F "descripcion=Cita médica programada en el hospital" \
  -F "estado_id=550e8400-e29b-41d4-a716-446655440000" \
  -F "documento=@C:/Users/Usuario/Documents/justificante-medico.pdf"
```

**Respuesta esperada:**

```json
{
  "message": "Incidencia creada exitosamente",
  "data": {
    "id": "aa0e8400-e29b-41d4-a716-446655440005",
    "empleado_id": "emp-123",
    "url_documento": "C:\\IncidenciasDocumentos\\justificante-medico-1733241234567-987654321.pdf",
    ...
  }
}
```

> **Importante:** Guardar el `id` de la incidencia creada para los siguientes pasos.

#### Paso 4: Consultar la Incidencia Creada

```bash
curl http://localhost:3003/api/incidencias/aa0e8400-e29b-41d4-a716-446655440005
```

#### Paso 5: Listar Incidencias del Empleado

```bash
curl "http://localhost:3003/api/incidencias?empleado_id=emp-123&page=1&limit=10"
```

#### Paso 6: Aprobar la Incidencia

```bash
curl -X PATCH http://localhost:3003
/api/incidencias/aa0e8400-e29b-41d4-a716-446655440005/aprobar \
  -H "Content-Type: application/json" \
  -d '{
    "aprobado_por": "supervisor-456"
  }'
```

**Respuesta esperada:**

```json
{
  "message": "Incidencia aprobada exitosamente",
  "data": {
    "id": "aa0e8400-e29b-41d4-a716-446655440005",
    "aprobado_por": "supervisor-456",
    "aprobado_en": "2025-12-03T16:30:00.000Z",
    "motivo_rechazo": null,
    ...
  }
}
```

#### Paso 7 (Alternativo): Rechazar la Incidencia

```bash
curl -X PATCH http://localhost:3003/api/incidencias/aa0e8400-e29b-41d4-a716-446655440005/rechazar \
  -H "Content-Type: application/json" \
  -d '{
    "motivo_rechazo": "El documento no corresponde a la fecha indicada"
  }'
```

#### Paso 8: Actualizar la Incidencia

```bash
# Actualizar solo la descripción
curl -X PUT http://localhost:3003/api/incidencias/aa0e8400-e29b-41d4-a716-446655440005 \
  -F "descripcion=Cita médica programada - Control mensual de rutina"

# O actualizar con nuevo documento
curl -X PUT http://localhost:3003/api/incidencias/aa0e8400-e29b-41d4-a716-446655440005 \
  -F "descripcion=Cita médica con nuevo justificante" \
  -F "documento=@C:/Users/Usuario/Documents/nuevo-justificante.pdf"
```

---

## Códigos de Error

### Códigos HTTP

| Código | Significado           | Descripción                 |
| ------ | --------------------- | --------------------------- |
| 200    | OK                    | Solicitud exitosa           |
| 201    | Created               | Recurso creado exitosamente |
| 400    | Bad Request           | Error en los datos enviados |
| 404    | Not Found             | Recurso no encontrado       |
| 409    | Conflict              | Conflicto (ej: duplicado)   |
| 500    | Internal Server Error | Error del servidor          |

### Errores Comunes

#### 1. Error de Validación (400)

```json
{
  "error": "Errores de validación",
  "details": [
    {
      "msg": "El ID debe ser un UUID válido",
      "param": "id",
      "location": "params"
    }
  ]
}
```

#### 2. Recurso No Encontrado (404)

```json
{
  "error": "No encontrado",
  "message": "La incidencia no existe"
}
```

#### 3. Archivo Inválido (400)

```json
{
  "error": "Tipo de archivo no válido",
  "message": "Solo se permiten archivos PDF"
}
```

#### 4. Archivo Muy Grande (400)

```json
{
  "error": "Archivo demasiado grande",
  "message": "El archivo no puede superar los 10 MB"
}
```

#### 5. Conflicto de Duplicado (409)

```json
{
  "error": "Conflicto de duplicado",
  "message": "Ya existe un registro con estos datos"
}
```

#### 6. Error de Base de Datos (404)

```json
{
  "error": "No encontrado",
  "message": "El registro solicitado no existe"
}
```

---

## Notas Adicionales

### Formato de Fechas

- Todas las fechas deben enviarse en formato ISO 8601: `YYYY-MM-DD`
- Ejemplo: `2025-12-03`

### UUIDs

- Todos los IDs son UUIDs versión 4
- Ejemplo: `550e8400-e29b-41d4-a716-446655440000`

### Archivos PDF

- Ubicación de almacenamiento: `C:\IncidenciasDocumentos\`
- Tamaño máximo: 10 MB
- Solo se aceptan archivos con extensión `.pdf`
- Los archivos se renombran automáticamente con timestamp único

### Paginación

- Por defecto: 10 elementos por página
- Máximo recomendado: 100 elementos por página

### Rate Limiting

- Límite: 100 peticiones por 15 minutos por IP
- Si se excede, recibirás un error 429 (Too Many Requests)

---

## Herramientas Recomendadas para Pruebas

1. **Postman** - Cliente HTTP con interfaz gráfica
2. **Thunder Client** - Extensión de VS Code
3. **cURL** - Línea de comandos (ejemplos en esta documentación)
4. **Insomnia** - Cliente HTTP alternativo

---

## Soporte

Para reportar problemas o solicitar nuevas funcionalidades, contacta al equipo de desarrollo.

**Versión de la API:** 1.0.0  
**Última actualización:** Diciembre 2025

### 8. Obtener Saldos y Consumos de Incidencias

Este endpoint permite consultar el estado de consumo de incidencias (días y veces solicitadas) frente a los límites anuales configurados, devolviendo un detalle de lo consumido y lo restante.

> **Nota:** Si un límite es `null`, significa que es ilimitado y el saldo restante también se mostrará como `null`.

**Endpoint:** `GET /api/incidencias/saldos`

**Query Parameters (opcionales):**
| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| empleado_id | string | Filtrar por un empleado específico |
| anio | number | Año a consultar (Default: Año actual) |

**Respuesta Exitosa (200 OK):**

```json
{
  "anio": 2025,
  "data": [
    {
      "empleado_id": "emp-123",
      "saldos": [
        {
          "tipo_id": "uuid-tipo-vacaciones",
          "tipo_nombre": "Vacaciones",
          "tipo_codigo": "VAC001",
          "limites": {
            "dias": 30,
            "solicitudes": null
          },
          "consumido": {
            "dias": 20,
            "solicitudes": 2
          },
          "restante": {
            "dias": 10,
            "solicitudes": null
          },
          "detalle": [
            {
              "id": "uuid-incidencia-1",
              "fecha_inicio": "2025-01-01",
              "fecha_fin": "2025-01-15",
              "dias": 15,
              "estado_id": "uuid-estado-aprobado"
            },
            {
              "id": "uuid-incidencia-2",
              "fecha_inicio": "2025-06-01",
              "fecha_fin": "2025-06-05",
              "dias": 5,
              "estado_id": "uuid-estado-pendiente"
            }
          ]
        },
        {
          "tipo_id": "uuid-tipo-onomastico",
          "tipo_nombre": "Onomástico",
          "tipo_codigo": "ONM001",
          "limites": {
            "dias": null,
            "solicitudes": 1
          },
          "consumido": {
            "dias": 1,
            "solicitudes": 1
          },
          "restante": {
            "dias": null,
            "solicitudes": 0
          },
          "detalle": [
            {
              "id": "uuid-incidencia-3",
              "fecha_inicio": "2025-05-20",
              "fecha_fin": "2025-05-20",
              "dias": 1,
              "estado_id": "uuid-estado-aprobado"
            }
          ]
        }
      ]
    }
  ]
}
```

**Ejemplo con cURL:**

```bash
curl "http://localhost:3003/api/incidencias/saldos?empleado_id=12345678&anio=2026"
```
