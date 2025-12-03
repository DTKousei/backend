# Ejemplos de Uso de la API ZKTeco

Esta guía contiene ejemplos prácticos de cómo usar la API REST.

## 📋 Tabla de Contenidos

1. [Gestión de Dispositivos](#gestión-de-dispositivos)
2. [Gestión de Usuarios](#gestión-de-usuarios)
3. [Registros de Asistencia](#registros-de-asistencia)
4. [Gestión de Horarios](#gestión-de-horarios)
5. [Sincronización](#sincronización)

---

## Gestión de Dispositivos

### 1. Crear un Dispositivo

**Request:**

```bash
curl -X POST "http://localhost:8000/api/dispositivos" \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Dispositivo Entrada Principal",
    "ip_address": "192.168.1.201",
    "puerto": 4370,
    "ubicacion": "Recepción - Piso 1",
    "password": 0,
    "timeout": 5,
    "activo": true
  }'
```

**Response:**

```json
{
  "id": 1,
  "nombre": "Dispositivo Entrada Principal",
  "ip_address": "192.168.1.201",
  "puerto": 4370,
  "ubicacion": "Recepción - Piso 1",
  "activo": true,
  "fecha_creacion": "2025-11-27T10:00:00",
  "fecha_actualizacion": "2025-11-27T10:00:00"
}
```

### 2. Listar Dispositivos

```bash
curl "http://localhost:8000/api/dispositivos"
```

### 3. Probar Conexión

```bash
curl -X POST "http://localhost:8000/api/dispositivos/1/test-conexion"
```

**Response:**

```json
{
  "success": true,
  "message": "Conexión exitosa",
  "info": {
    "serial_number": "BAQM123456",
    "firmware_version": "Ver 6.60",
    "platform": "ZEM600",
    "ip_address": "192.168.1.201",
    "puerto": 4370,
    "hora_dispositivo": "2025-11-27T10:05:30"
  }
}
```

---

## Gestión de Usuarios

### 1. Crear Usuario (con sincronización automática)

**Request:**

```bash
curl -X POST "http://localhost:8000/api/usuarios?sincronizar=true" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "001",
    "nombre": "Juan Carlos Pérez García",
    "privilegio": 0,
    "password": "1234",
    "dispositivo_id": 1,
    "email": "juan.perez@ugel.gob.pe",
    "telefono": "987654321",
    "departamento": "Administración",
    "cargo": "Asistente Administrativo"
  }'
```

**Response:**

```json
{
  "id": 1,
  "user_id": "001",
  "nombre": "Juan Carlos Pérez García",
  "privilegio": 0,
  "dispositivo_id": 1,
  "email": "juan.perez@ugel.gob.pe",
  "telefono": "987654321",
  "departamento": "Administración",
  "cargo": "Asistente Administrativo",
  "fecha_creacion": "2025-11-27T10:10:00"
}
```

### 2. Sincronizar Usuarios desde Dispositivo

```bash
curl -X POST "http://localhost:8000/api/usuarios/dispositivos/1/sincronizar"
```

**Response:**

```json
{
  "success": true,
  "message": "Sincronización exitosa",
  "usuarios_nuevos": 5,
  "usuarios_actualizados": 3
}
```

### 3. Listar Usuarios de un Dispositivo

```bash
curl "http://localhost:8000/api/usuarios?dispositivo_id=1&limit=50"
```

---

## Registros de Asistencia

### 1. Sincronizar Asistencias desde Dispositivo

```bash
curl -X POST "http://localhost:8000/api/asistencias/sincronizar/1"
```

**Response:**

```json
{
  "success": true,
  "message": "Sincronización exitosa. 25 registros nuevos",
  "registros_nuevos": 25,
  "registros_totales": 150,
  "dispositivo_id": 1
}
```

### 2. Obtener Asistencias con Filtros

**Por fecha:**

```bash
curl "http://localhost:8000/api/asistencias?fecha_inicio=2025-11-27T00:00:00&fecha_fin=2025-11-27T23:59:59&limit=100"
```

**Por usuario:**

```bash
curl "http://localhost:8000/api/asistencias?user_id=001&limit=50"
```

**Por dispositivo:**

```bash
curl "http://localhost:8000/api/asistencias?dispositivo_id=1&limit=100"
```

**Combinado:**

```bash
curl "http://localhost:8000/api/asistencias?user_id=001&dispositivo_id=1&fecha_inicio=2025-11-01T00:00:00&fecha_fin=2025-11-30T23:59:59"
```

**Response:**

```json
[
  {
    "id": 1,
    "user_id": "001",
    "dispositivo_id": 1,
    "timestamp": "2025-11-27T08:15:30",
    "status": 0,
    "punch": 0,
    "sincronizado": true,
    "fecha_sincronizacion": "2025-11-27T10:00:00"
  },
  {
    "id": 2,
    "user_id": "001",
    "dispositivo_id": 1,
    "timestamp": "2025-11-27T17:30:45",
    "status": 0,
    "punch": 0,
    "sincronizado": true,
    "fecha_sincronizacion": "2025-11-27T18:00:00"
  }
]
```

### 3. Obtener Asistencias en Tiempo Real

```bash
curl "http://localhost:8000/api/asistencias/tiempo-real/1?ultimos_minutos=5"
```

### 4. Contar Asistencias

```bash
curl "http://localhost:8000/api/asistencias/count?dispositivo_id=1&fecha_inicio=2025-11-01T00:00:00&fecha_fin=2025-11-30T23:59:59"
```

**Response:**

```json
{
  "total": 450
}
```

### 5. Sincronizar Todos los Dispositivos

```bash
curl -X POST "http://localhost:8000/api/asistencias/sincronizar-todos"
```

**Response:**

```json
{
  "total_dispositivos": 3,
  "resultados": [
    {
      "dispositivo_id": 1,
      "dispositivo_nombre": "Entrada Principal",
      "success": true,
      "registros_nuevos": 15,
      "registros_totales": 200
    },
    {
      "dispositivo_id": 2,
      "dispositivo_nombre": "Salida Trasera",
      "success": true,
      "registros_nuevos": 8,
      "registros_totales": 120
    }
  ]
}
```

---

## Gestión de Horarios

### 1. Crear Horario

```bash
curl -X POST "http://localhost:8000/api/horarios" \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Horario Administrativo",
    "descripcion": "Horario para personal administrativo",
    "hora_entrada": "08:00:00",
    "hora_salida": "17:00:00",
    "dias_semana": ["lunes", "martes", "miercoles", "jueves", "viernes"],
    "tolerancia_entrada": 15,
    "tolerancia_salida": 10,
    "activo": true
  }'
```

### 2. Listar Horarios Activos

```bash
curl "http://localhost:8000/api/horarios?activo=true"
```

---

## Sincronización

### 1. Sincronizar Hora del Dispositivo

```bash
curl -X POST "http://localhost:8000/api/sincronizacion/hora/1"
```

**Response:**

```json
{
  "success": true,
  "message": "Hora sincronizada exitosamente",
  "hora_anterior": "2025-11-27T09:55:00",
  "hora_nueva": "2025-11-27T10:00:00",
  "hora_sistema": "2025-11-27T10:00:00"
}
```

### 2. Obtener Estado de Sincronización

```bash
curl "http://localhost:8000/api/sincronizacion/estado"
```

**Response:**

```json
{
  "total_dispositivos": 2,
  "dispositivos": [
    {
      "id": 1,
      "nombre": "Entrada Principal",
      "ip_address": "192.168.1.201",
      "ultima_sincronizacion": "2025-11-27T10:00:00",
      "minutos_desde_sync": 5,
      "activo": true
    },
    {
      "id": 2,
      "nombre": "Salida Trasera",
      "ip_address": "192.168.1.202",
      "ultima_sincronizacion": "2025-11-27T09:45:00",
      "minutos_desde_sync": 20,
      "activo": true
    }
  ]
}
```

---

## Ejemplos con Python

### Usando requests

```python
import requests
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8000"

# 1. Crear dispositivo
dispositivo = {
    "nombre": "Dispositivo Principal",
    "ip_address": "192.168.1.201",
    "puerto": 4370,
    "ubicacion": "Entrada",
    "activo": True
}

response = requests.post(f"{BASE_URL}/api/dispositivos", json=dispositivo)
dispositivo_id = response.json()["id"]
print(f"Dispositivo creado con ID: {dispositivo_id}")

# 2. Crear usuario
usuario = {
    "user_id": "001",
    "nombre": "Juan Pérez",
    "privilegio": 0,
    "dispositivo_id": dispositivo_id
}

response = requests.post(f"{BASE_URL}/api/usuarios", json=usuario)
print(f"Usuario creado: {response.json()['nombre']}")

# 3. Sincronizar asistencias
response = requests.post(f"{BASE_URL}/api/asistencias/sincronizar/{dispositivo_id}")
resultado = response.json()
print(f"Sincronizados {resultado['registros_nuevos']} registros nuevos")

# 4. Obtener asistencias del día
hoy_inicio = datetime.now().replace(hour=0, minute=0, second=0)
hoy_fin = datetime.now().replace(hour=23, minute=59, second=59)

params = {
    "dispositivo_id": dispositivo_id,
    "fecha_inicio": hoy_inicio.isoformat(),
    "fecha_fin": hoy_fin.isoformat(),
    "limit": 100
}

response = requests.get(f"{BASE_URL}/api/asistencias", params=params)
asistencias = response.json()
print(f"Asistencias del día: {len(asistencias)}")

for asistencia in asistencias:
    print(f"  - Usuario {asistencia['user_id']}: {asistencia['timestamp']}")
```

---

## Notas Importantes

1. **Sincronización**: Los endpoints de sincronización pueden tardar dependiendo de la cantidad de datos
2. **Paginación**: Use `limit` y `offset` para manejar grandes volúmenes de datos
3. **Filtros**: Combine múltiples filtros para consultas específicas
4. **Tiempo Real**: El endpoint de tiempo real es útil para dashboards y monitoreo
5. **Documentación**: Visite `/docs` para probar los endpoints interactivamente
