# Documentación del Servicio de Reportes y Asistencia

Este servicio se encarga de generar reportes de asistencia (Sábana) en formatos Excel y PDF, integrando información de asistencia diaria con incidencias y justificaciones obtenidas de servicios externos.

## Configuración Inicial

El servicio requiere ciertas variables de entorno configuradas en el archivo `.env`:

```env
# Base de datos de reportes (Metadata)
DB_USER=root
DB_PASSWORD=
DB_HOST=localhost
DB_PORT=3306
DB_NAME=reports

# URL del API Principal de Asistencia
API_BASE_URL=http://localhost:8000/api

# URL del API de Incidencias (Nueva integración)
INCIDENCIAS_API_URL=http://localhost:3003/api/incidencias
```

## Lógica de Integración de Incidencias

El sistema mejora automáticamente el reporte de asistencia cruzando la información con el sistema de incidencias:

1.  **Obtención de Datos**: Al solicitar un reporte, el sistema consulta:
    - La asistencia diaria desde `API_BASE_URL`.
    - Las incidencias desde `INCIDENCIAS_API_URL`.
2.  **Filtrado**: Solo se consideran las incidencias que tienen el estado **"Aprobado"**.
3.  **Justificación Automática**:
    - El sistema recorre los días con inasistencia marcada como **"FAL"** (Falta).
    - Si la fecha de la falta cae dentro del rango (`fecha_inicio` a `fecha_fin`) de una incidencia aprobada para ese empleado, el sistema reemplaza "FAL" con el código de la incidencia (ej. "PM001", "VAC", etc.).

---

## Endpoints de la API

### 1. Exportar Reporte en Excel

Genera un archivo `.xlsx` con el reporte detallado (Sábana) del mes especificado.

- **URL**: `/api/reports/export/excel`
- **Método**: `POST`
- **Content-Type**: `application/json`

#### Body de Solicitud (JSON)

| Campo      | Tipo   | Requerido | Descripción                                                     |
| ---------- | ------ | --------- | --------------------------------------------------------------- |
| `mes`      | string | Sí        | Número del mes (1-12).                                          |
| `anio`     | string | Sí        | Año del reporte (ej. "2026").                                   |
| `area`     | string | No        | Nombre exacto del departamento (ej. "Direccion").               |
| `user_ids` | list   | No        | Lista de DNIs para filtrar el reporte. Si se omite, trae todos. |

#### Ejemplo de Solicitud (Input)

```json
{
  "mes": "1",
  "anio": "2026",
  "area": "Direccion",
  "user_ids": ["12345678", "87654321"]
}
```

#### Respuesta (Output)

- **Código**: `200 OK`
- **Contenido**: Archivo binario `.xlsx` (Excel).

---

### 2. Exportar Reporte en PDF

Genera una versión imprimible en `.pdf` del reporte.

- **URL**: `/api/reports/export/pdf`
- **Método**: `POST`
- **Content-Type**: `application/json`

#### Ejemplo de Solicitud (Input)

```json
{
  "mes": "1",
  "anio": "2026"
}
```

#### Respuesta (Output)

- **Código**: `200 OK`
- **Contenido**: Archivo binario `.pdf`.

---

### 3. Gestión de Reportes Generados

Endpoints para listar, descargar y eliminar el historial de reportes.

#### A. Listar Reportes (`GET /api/reports/generated/`)

Lista todos los reportes generados con sus detalles.

- **Parámetros Query**: `?skip=0&limit=100`

- **Respuesta (Output)**:

```json
[
  {
    "id": 1,
    "nombre_archivo": "reporte_2026_1_ab3d.xlsx",
    "fecha_generacion": "2026-01-06T10:00:00",
    "formato": "EXCEL",
    "tipo_reporte": "Asistencia General",
    "usuario_id": 1,
    "area": "Direccion",
    "parametros": { "mes": "1", "anio": "2026", "area": "Direccion" }
  }
]
```

#### B. Visualizar/Descargar Reporte (`GET /api/reports/generated/{id}`)

Descarga un reporte. Permite conversión de formato on-demand.

- **Parámetros Query**: `?format=PDF` o `?format=EXCEL`

- **Respuesta (Output)**: Archivo binario.

#### C. Eliminar Reporte (`DELETE /api/reports/generated/{id}`)

Elimina el reporte físicamente y de la base de datos.

- **Respuesta (Output)**:

```json
{
  "message": "Reporte eliminado correctamente"
}
```

---

### 4. Gestión de Tipos de Reporte (CRUD)

Endpoints para administrar los tipos de reporte disponibles en el sistema.

- **Base URL**: `/api/report-types`

#### A. Listar Tipos (`GET /`)

- **Respuesta (Output)**:

```json
[
  {
    "id": 1,
    "nombre": "Asistencia General",
    "descripcion": "Reporte de Asistencia General",
    "activo": true
  }
]
```

#### B. Crear Tipo (`POST /`)

- **Body de Solicitud (Input)**:

```json
{
  "nombre": "Reporte Nocturno",
  "descripcion": "Asistencia del turno noche",
  "activo": true
}
```

#### C. Actualizar Tipo (`PUT /{id}`)

- **Body de Solicitud (Input)**:

```json
{
  "nombre": "Reporte Nocturno V2",
  "descripcion": "Actualizado",
  "activo": true
}
```

#### D. Eliminar Tipo (`DELETE /{id}`)

- **Respuesta (Output)**:

```json
{
  "message": "Tipo de reporte desactivado correctamente."
}
```

---

## Ejecución

Para iniciar el servicio, ejecute el script:

```bash
.\run_app.bat
```

Esto levantará el servidor en `http://0.0.0.0:8001`.
