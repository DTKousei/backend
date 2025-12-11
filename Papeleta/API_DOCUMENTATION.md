# API REST - Documentación Completa de Endpoints

## 📚 Tabla de Contenidos

1. [Configuración Inicial](#configuración-inicial)
2. [Tipos de Permisos](#tipos-de-permisos)
3. [Estados](#estados)
4. [Permisos (Papeletas)](#permisos-papeletas)
5. [Firmas Tradicionales](#firmas-tradicionales)
6. [Firmas Digitales ONPE](#firmas-digitales-onpe)
7. [Generación de PDF](#generación-de-pdf)
8. [Carga de PDF](#carga-de-pdf)
9. [Flujos Completos](#flujos-completos)

---

## Configuración Inicial

### Base URL

```
http://localhost:3002
```

### Headers Comunes

```http
Content-Type: application/json
```

---

## Tipos de Permisos

### 1. Listar Tipos de Permisos

**Endpoint:** `GET /api/permiso-tipos`

**Query Parameters:**

- `activo` (opcional): `true` o `false`

**Ejemplo de Petición:**

```bash
curl http://localhost:3002/api/permiso-tipos
```

**Respuesta Exitosa (200):**

```json
{
  "success": true,
  "data": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "nombre": "Comisión de Servicio",
      "codigo": "COMISION_SERVICIO",
      "descripcion": "Comisión de servicio a otra institución",
      "requiere_firma_institucion": true,
      "tiempo_maximo_horas": null,
      "esta_activo": true,
      "creado_en": "2024-12-02T10:00:00.000Z",
      "actualizado_en": "2024-12-02T10:00:00.000Z"
    },
    {
      "id": "650e8400-e29b-41d4-a716-446655440001",
      "nombre": "Permiso Personal",
      "codigo": "PERMISO_PERSONAL",
      "descripcion": "Permiso personal (máximo 2 horas)",
      "requiere_firma_institucion": false,
      "tiempo_maximo_horas": 2,
      "esta_activo": true,
      "creado_en": "2024-12-02T10:00:00.000Z",
      "actualizado_en": "2024-12-02T10:00:00.000Z"
    }
  ],
  "total": 2
}
```

---

### 2. Obtener Tipo de Permiso por ID

**Endpoint:** `GET /api/permiso-tipos/:id`

**Ejemplo de Petición:**

```bash
curl http://localhost:3002/api/permiso-tipos/550e8400-e29b-41d4-a716-446655440000
```

**Respuesta Exitosa (200):**

```json
{
  "success": true,
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "nombre": "Comisión de Servicio",
    "codigo": "COMISION_SERVICIO",
    "descripcion": "Comisión de servicio a otra institución",
    "requiere_firma_institucion": true,
    "tiempo_maximo_horas": null,
    "esta_activo": true,
    "creado_en": "2024-12-02T10:00:00.000Z",
    "actualizado_en": "2024-12-02T10:00:00.000Z",
    "_count": {
      "permisos": 5
    }
  }
}
```

---

### 3. Crear Tipo de Permiso

**Endpoint:** `POST /api/permiso-tipos`

**Body (JSON):**

```json
{
  "nombre": "Permiso Médico",
  "codigo": "PERMISO_MEDICO",
  "descripcion": "Permiso por motivos de salud",
  "requiere_firma_institucion": false,
  "tiempo_maximo_horas": 4,
  "esta_activo": true
}
```

**Ejemplo de Petición:**

```bash
curl -X POST http://localhost:3002/api/permiso-tipos \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Permiso Médico",
    "codigo": "PERMISO_MEDICO",
    "descripcion": "Permiso por motivos de salud",
    "requiere_firma_institucion": false,
    "tiempo_maximo_horas": 4,
    "esta_activo": true
  }'
```

**Respuesta Exitosa (201):**

```json
{
  "success": true,
  "message": "Tipo de permiso creado exitosamente",
  "data": {
    "id": "750e8400-e29b-41d4-a716-446655440002",
    "nombre": "Permiso Médico",
    "codigo": "PERMISO_MEDICO",
    "descripcion": "Permiso por motivos de salud",
    "requiere_firma_institucion": false,
    "tiempo_maximo_horas": 4,
    "esta_activo": true,
    "creado_en": "2024-12-02T15:30:00.000Z",
    "actualizado_en": "2024-12-02T15:30:00.000Z"
  }
}
```

---

## Estados

### 1. Listar Estados

**Endpoint:** `GET /api/estados`

**Ejemplo de Petición:**

```bash
curl http://localhost:3002/api/estados
```

**Respuesta Exitosa (200):**

```json
{
  "success": true,
  "data": [
    {
      "id": "850e8400-e29b-41d4-a716-446655440003",
      "nombre": "Pendiente",
      "codigo": "PENDIENTE",
      "descripcion": "Permiso pendiente de aprobación",
      "creado_en": "2024-12-02T10:00:00.000Z",
      "actualizado_en": "2024-12-02T10:00:00.000Z"
    },
    {
      "id": "950e8400-e29b-41d4-a716-446655440004",
      "nombre": "Aprobado",
      "codigo": "APROBADO",
      "descripcion": "Permiso completamente aprobado",
      "creado_en": "2024-12-02T10:00:00.000Z",
      "actualizado_en": "2024-12-02T10:00:00.000Z"
    }
  ],
  "total": 2
}
```

---

## Permisos (Papeletas)

### 1. Crear Permiso Personal

**Endpoint:** `POST /api/permisos`

**Body (JSON):**

```json
{
  "empleado_id": "12345678",
  "tipo_permiso_id": "650e8400-e29b-41d4-a716-446655440001",
  "fecha_hora_inicio": "2024-12-03T14:00:00",
  "fecha_hora_fin": "2024-12-03T16:00:00",
  "motivo": "Trámite bancario urgente",
  "justificacion": "Necesito realizar gestiones en el banco que solo se pueden hacer presencialmente"
}
```

**Ejemplo de Petición:**

```bash
curl -X POST http://localhost:3002/api/permisos \
  -H "Content-Type: application/json" \
  -d '{
    "empleado_id": "12345678",
    "tipo_permiso_id": "650e8400-e29b-41d4-a716-446655440001",
    "fecha_hora_inicio": "2024-12-03T14:00:00",
    "fecha_hora_fin": "2024-12-03T16:00:00",
    "motivo": "Trámite bancario urgente",
    "justificacion": "Necesito realizar gestiones en el banco"
  }'
```

**Respuesta Exitosa (201):**

```json
{
  "success": true,
  "message": "Permiso creado exitosamente",
  "data": {
    "id": "a50e8400-e29b-41d4-a716-446655440005",
    "empleado_id": "12345678",
    "tipo_permiso_id": "650e8400-e29b-41d4-a716-446655440001",
    "estado_id": "850e8400-e29b-41d4-a716-446655440003",
    "fecha_hora_inicio": "2024-12-03T14:00:00.000Z",
    "fecha_hora_fin": "2024-12-03T16:00:00.000Z",
    "hora_salida_calculada": "2024-12-03T16:00:00.000Z",
    "motivo": "Trámite bancario urgente",
    "justificacion": "Necesito realizar gestiones en el banco",
    "institucion_visitada": null,
    "creado_en": "2024-12-02T15:35:00.000Z",
    "actualizado_en": "2024-12-02T15:35:00.000Z",
    "tipo_permiso": {
      "id": "650e8400-e29b-41d4-a716-446655440001",
      "nombre": "Permiso Personal",
      "codigo": "PERMISO_PERSONAL",
      "requiere_firma_institucion": false,
      "tiempo_maximo_horas": 2
    },
    "estado": {
      "id": "850e8400-e29b-41d4-a716-446655440003",
      "nombre": "Pendiente",
      "codigo": "PENDIENTE"
    }
  }
}
```

---

### 2. Crear Comisión de Servicio

**Endpoint:** `POST /api/permisos`

**Body (JSON):**

```json
{
  "empleado_id": "87654321",
  "tipo_permiso_id": "550e8400-e29b-41d4-a716-446655440000",
  "fecha_hora_inicio": "2024-12-04T08:00:00",
  "motivo": "Reunión de coordinación interinstitucional",
  "justificacion": "Coordinación de proyectos educativos con el Ministerio de Educación",
  "institucion_visitada": "Ministerio de Educación - MINEDU"
}
```

**Ejemplo de Petición:**

```bash
curl -X POST http://localhost:3002/api/permisos \
  -H "Content-Type: application/json" \
  -d '{
    "empleado_id": "87654321",
    "tipo_permiso_id": "550e8400-e29b-41d4-a716-446655440000",
    "fecha_hora_inicio": "2024-12-04T08:00:00",
    "motivo": "Reunión de coordinación interinstitucional",
    "justificacion": "Coordinación de proyectos educativos",
    "institucion_visitada": "Ministerio de Educación - MINEDU"
  }'
```

**Respuesta Exitosa (201):**

```json
{
  "success": true,
  "message": "Permiso creado exitosamente",
  "data": {
    "id": "b50e8400-e29b-41d4-a716-446655440006",
    "empleado_id": "87654321",
    "tipo_permiso_id": "550e8400-e29b-41d4-a716-446655440000",
    "estado_id": "850e8400-e29b-41d4-a716-446655440003",
    "fecha_hora_inicio": "2024-12-04T08:00:00.000Z",
    "fecha_hora_fin": null,
    "hora_salida_calculada": null,
    "motivo": "Reunión de coordinación interinstitucional",
    "justificacion": "Coordinación de proyectos educativos",
    "institucion_visitada": "Ministerio de Educación - MINEDU",
    "tipo_permiso": {
      "nombre": "Comisión de Servicio",
      "requiere_firma_institucion": true,
      "tiempo_maximo_horas": null
    },
    "estado": {
      "nombre": "Pendiente"
    }
  }
}
```

---

### 3. Listar Permisos con Filtros

**Endpoint:** `GET /api/permisos`

**Query Parameters:**

- `empleado_id` (opcional): DNI del empleado
- `tipo_permiso_id` (opcional): UUID del tipo de permiso
- `estado_id` (opcional): UUID del estado
- `fecha_desde` (opcional): Fecha ISO8601
- `fecha_hasta` (opcional): Fecha ISO8601
- `page` (opcional): Número de página (default: 1)
- `limit` (opcional): Registros por página (default: 10)

**Ejemplo de Petición:**

```bash
# Listar todos los permisos del empleado 12345678
curl "http://localhost:3002/api/permisos?empleado_id=12345678&page=1&limit=10"

# Listar permisos por rango de fechas
curl "http://localhost:3002/api/permisos?fecha_desde=2024-12-01&fecha_hasta=2024-12-31"
```

**Respuesta Exitosa (200):**

```json
{
  "success": true,
  "data": [
    {
      "id": "a50e8400-e29b-41d4-a716-446655440005",
      "empleado_id": "12345678",
      "fecha_hora_inicio": "2024-12-03T14:00:00.000Z",
      "motivo": "Trámite bancario urgente",
      "tipo_permiso": {
        "nombre": "Permiso Personal"
      },
      "estado": {
        "nombre": "Pendiente"
      },
      "creado_en": "2024-12-02T15:35:00.000Z"
    }
  ],
  "pagination": {
    "total": 1,
    "page": 1,
    "limit": 10,
    "totalPages": 1
  }
}
```

---

## Firmas Tradicionales

### Firmar con Imagen Base64

**Endpoint:** `PATCH /api/permisos/:id/firmar`

**Body (JSON):**

```json
{
  "tipo_firma": "solicitante",
  "firma": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
}
```

**Tipos de Firma Válidos:**

- `solicitante` - Firma del empleado que solicita
- `jefe_area` - Firma del jefe de área
- `rrhh` - Firma de Recursos Humanos
- `institucion` - Firma de institución visitada (solo comisión de servicio)

**Ejemplo de Petición:**

```bash
curl -X PATCH http://localhost:3002/api/permisos/a50e8400-e29b-41d4-a716-446655440005/firmar \
  -H "Content-Type: application/json" \
  -d '{
    "tipo_firma": "solicitante",
    "firma": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAAB..."
  }'
```

**Respuesta Exitosa (200):**

```json
{
  "success": true,
  "message": "Firma registrada exitosamente",
  "data": {
    "id": "a50e8400-e29b-41d4-a716-446655440005",
    "firma_solicitante": "data:image/png;base64,iVBORw0KGgo...",
    "firma_solicitante_en": "2024-12-02T15:40:00.000Z",
    "metodo_firma_solicitante": "base64",
    "estado": {
      "nombre": "Pendiente"
    }
  },
  "firmas_completas": false
}
```

---

## Firmas Digitales ONPE

### Firmar con Certificado Digital

**Endpoint:** `PATCH /api/permisos/:id/firmar-digital`

**Body (JSON):**

```json
{
  "tipo_firma": "solicitante",
  "firma_digital": "MIAGCSqGSIb3DQEHAqCAMIACAQExDzANBglghkgBZQMEAgEFADCABgkqhkiG9w0BBwGggCSABIIQ...",
  "certificado": {
    "dni": "12345678",
    "nombre": "Juan Carlos Pérez García",
    "entidad_emisora": "RENIEC",
    "fecha_emision": "2023-01-15T00:00:00.000Z",
    "fecha_expiracion": "2025-01-15T00:00:00.000Z",
    "numero_serie": "1234567890ABCDEF"
  }
}
```

**Ejemplo de Petición:**

```bash
curl -X PATCH http://localhost:3002/api/permisos/a50e8400-e29b-41d4-a716-446655440005/firmar-digital \
  -H "Content-Type: application/json" \
  -d '{
    "tipo_firma": "solicitante",
    "firma_digital": "MIAGCSqGSIb3DQEHAqCAMIACAQExDzANBglghkgBZQMEAgEFADCABgkqhkiG9w0BBwGggCSABIIQ...",
    "certificado": {
      "dni": "12345678",
      "nombre": "Juan Carlos Pérez García"
    }
  }'
```

**Respuesta Exitosa (200):**

```json
{
  "success": true,
  "message": "Firma digital registrada exitosamente",
  "data": {
    "id": "a50e8400-e29b-41d4-a716-446655440005",
    "firma_solicitante_digital": "MIAGCSqGSIb3DQEHAqCAMIACAQExDzANBglghkgBZQMEAgEFADCABgkqhkiG9w0BBwGggCSABIIQ...",
    "firma_solicitante_en": "2024-12-02T15:45:00.000Z",
    "certificado_solicitante": {
      "dni": "12345678",
      "nombre": "Juan Carlos Pérez García",
      "entidad_emisora": "RENIEC",
      "fecha_emision": "2023-01-15T00:00:00.000Z",
      "fecha_expiracion": "2025-01-15T00:00:00.000Z",
      "numero_serie": "1234567890ABCDEF"
    },
    "firma_solicitante_validada": true,
    "metodo_firma_solicitante": "onpe",
    "documento_hash": "a1b2c3d4e5f6..."
  },
  "certificado": {
    "dni": "12345678",
    "nombre": "Juan Carlos Pérez García",
    "entidad_emisora": "RENIEC",
    "fecha_emision": "2023-01-15T00:00:00.000Z",
    "fecha_expiracion": "2025-01-15T00:00:00.000Z"
  },
  "qr_verificacion": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAMgAAADI...",
  "url_verificacion": "http://localhost:3002/api/permisos/a50e8400-e29b-41d4-a716-446655440005/verificar-firma/solicitante?hash=abc123",
  "firmas_completas": false
}
```

---

### Verificar Firma Digital

**Endpoint:** `GET /api/permisos/:id/verificar-firma/:tipoFirma`

**Ejemplo de Petición:**

```bash
curl http://localhost:3002/api/permisos/a50e8400-e29b-41d4-a716-446655440005/verificar-firma/solicitante
```

**Respuesta Exitosa (200):**

```json
{
  "success": true,
  "data": {
    "permiso_id": "a50e8400-e29b-41d4-a716-446655440005",
    "tipo_firma": "solicitante",
    "metodo_firma": "onpe",
    "validada": true,
    "firmante": {
      "nombre": "Juan Carlos Pérez García",
      "dni": "12345678",
      "cargo": "SOLICITANTE"
    },
    "certificado": {
      "entidad_emisora": "RENIEC",
      "numero_serie": "1234567890ABCDEF",
      "vigente_desde": "2023-01-15T00:00:00.000Z",
      "vigente_hasta": "2025-01-15T00:00:00.000Z"
    },
    "fecha_firma": "2024-12-02T15:45:00.000Z",
    "documento_hash": "a1b2c3d4e5f6...",
    "permiso": {
      "empleado_id": "12345678",
      "tipo_permiso": "Permiso Personal",
      "estado": "Pendiente",
      "fecha_inicio": "2024-12-03T14:00:00.000Z"
    }
  }
}
```

---

## Generación de PDF

### Generar y Descargar PDF

**Endpoint:** `GET /api/permisos/:id/pdf`

**Ejemplo de Petición:**

```bash
curl http://localhost:3002/api/permisos/a50e8400-e29b-41d4-a716-446655440005/pdf \
  --output papeleta.pdf
```

**Respuesta:** Archivo PDF descargado

**Contenido del PDF:**

- Encabezado con número de papeleta
- Datos del solicitante
- Información del permiso
- Firmas (tradicionales o digitales con QR)
- Pie de página con fecha de generación

---

## Carga de PDF

### Cargar PDF Firmado Físicamente

**Endpoint:** `POST /api/permisos/:id/upload-pdf`

**Content-Type:** `multipart/form-data`

**Form Data:**

- `pdf`: Archivo PDF (máximo 5MB)

**Ejemplo de Petición:**

```bash
curl -X POST http://localhost:3002/api/permisos/b50e8400-e29b-41d4-a716-446655440006/upload-pdf \
  -F "pdf=@papeleta-firmada.pdf"
```

**Respuesta Exitosa (200):**

```json
{
  "success": true,
  "message": "PDF cargado exitosamente",
  "data": {
    "id": "b50e8400-e29b-41d4-a716-446655440006",
    "pdf_firmado_path": "/uploads/papeleta-1733162400000-123.pdf"
  },
  "archivo": {
    "nombre": "papeleta-1733162400000-123.pdf",
    "ruta": "/uploads/papeleta-1733162400000-123.pdf",
    "tamano": 245678
  }
}
```

---

## Flujos Completos

### Flujo 1: Permiso Personal con Firmas Tradicionales

**Paso 1: Crear el permiso**

```bash
curl -X POST http://localhost:3002/api/permisos \
  -H "Content-Type: application/json" \
  -d '{
    "empleado_id": "12345678",
    "tipo_permiso_id": "650e8400-e29b-41d4-a716-446655440001",
    "fecha_hora_inicio": "2024-12-03T14:00:00",
    "fecha_hora_fin": "2024-12-03T16:00:00",
    "motivo": "Trámite bancario",
    "justificacion": "Gestiones urgentes"
  }'
```

**Paso 2: Firmar como solicitante**

```bash
curl -X PATCH http://localhost:3002/api/permisos/{PERMISO_ID}/firmar \
  -H "Content-Type: application/json" \
  -d '{
    "tipo_firma": "solicitante",
    "firma": "data:image/png;base64,..."
  }'
```

**Paso 3: Firmar como jefe de área**

```bash
curl -X PATCH http://localhost:3002/api/permisos/{PERMISO_ID}/firmar \
  -H "Content-Type: application/json" \
  -d '{
    "tipo_firma": "jefe_area",
    "firma": "data:image/png;base64,..."
  }'
```

**Paso 4: Firmar como RRHH**

```bash
curl -X PATCH http://localhost:3002/api/permisos/{PERMISO_ID}/firmar \
  -H "Content-Type: application/json" \
  -d '{
    "tipo_firma": "rrhh",
    "firma": "data:image/png;base64,..."
  }'
```

**Paso 5: Generar PDF**

```bash
curl http://localhost:3002/api/permisos/{PERMISO_ID}/pdf \
  --output papeleta-aprobada.pdf
```

---

### Flujo 2: Comisión de Servicio con Firmas Digitales ONPE

**Paso 1: Crear la comisión**

```bash
curl -X POST http://localhost:3002/api/permisos \
  -H "Content-Type: application/json" \
  -d '{
    "empleado_id": "87654321",
    "tipo_permiso_id": "550e8400-e29b-41d4-a716-446655440000",
    "fecha_hora_inicio": "2024-12-04T08:00:00",
    "motivo": "Reunión interinstitucional",
    "justificacion": "Coordinación de proyectos",
    "institucion_visitada": "MINEDU"
  }'
```

**Paso 2: Firmar digitalmente como solicitante**

```bash
curl -X PATCH http://localhost:3002/api/permisos/{PERMISO_ID}/firmar-digital \
  -H "Content-Type: application/json" \
  -d '{
    "tipo_firma": "solicitante",
    "firma_digital": "MIAGCSqGSIb3...",
    "certificado": {
      "dni": "87654321",
      "nombre": "María López"
    }
  }'
```

**Paso 3: Firmar digitalmente como jefe**

```bash
curl -X PATCH http://localhost:3002/api/permisos/{PERMISO_ID}/firmar-digital \
  -H "Content-Type: application/json" \
  -d '{
    "tipo_firma": "jefe_area",
    "firma_digital": "MIAGCSqGSIb3...",
    "certificado": {
      "dni": "11111111",
      "nombre": "Carlos Sánchez"
    }
  }'
```

**Paso 4: Firmar digitalmente como RRHH**

```bash
curl -X PATCH http://localhost:3002/api/permisos/{PERMISO_ID}/firmar-digital \
  -H "Content-Type: application/json" \
  -d '{
    "tipo_firma": "rrhh",
    "firma_digital": "MIAGCSqGSIb3...",
    "certificado": {
      "dni": "22222222",
      "nombre": "Ana Torres"
    }
  }'
```

**Paso 5: Generar PDF para llevar a institución**

```bash
curl http://localhost:3002/api/permisos/{PERMISO_ID}/pdf \
  --output papeleta-para-firma.pdf
```

**Paso 6: Cargar PDF con firma de institución**

```bash
curl -X POST http://localhost:3002/api/permisos/{PERMISO_ID}/upload-pdf \
  -F "pdf=@papeleta-firmada-institucion.pdf"
```

**Paso 7: Verificar firma (público)**

```bash
curl http://localhost:3002/api/permisos/{PERMISO_ID}/verificar-firma/solicitante
```

---

## Códigos de Error

| Código | Descripción                       |
| ------ | --------------------------------- |
| 400    | Bad Request - Datos inválidos     |
| 404    | Not Found - Recurso no encontrado |
| 409    | Conflict - Registro duplicado     |
| 500    | Internal Server Error             |

**Ejemplo de Error (400):**

```json
{
  "success": false,
  "error": "Error de validación",
  "details": [
    {
      "msg": "El ID del empleado es el DNI",
      "param": "empleado_id",
      "location": "body"
    }
  ]
}
```

**Ejemplo de Error (404):**

```json
{
  "success": false,
  "error": "Permiso no encontrado"
}
```

---

## Notas Importantes

1. **Orden de Firmas:** Debe respetarse el orden jerárquico:

   - Solicitante → Jefe de Área → RRHH → Institución (si aplica)

2. **Validación de DNI:** El empleado_id ahora es el DNI (7-9 dígitos)

3. **Firmas Digitales:** Requieren certificado digital válido emitido por RENIEC u ONPE

4. **Códigos QR:** Solo se generan para firmas digitales ONPE

5. **PDFs:** Se guardan automáticamente en `/generated` y `/uploads`

6. **Tiempo Máximo:** Permiso personal tiene límite de 2 horas, comisión de servicio no tiene límite
