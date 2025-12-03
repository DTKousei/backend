# API REST para ZKTeco - Guía de Uso

## 📋 Descripción

API REST completa para gestión de dispositivos ZKTeco de control de asistencia. Permite gestionar dispositivos, usuarios, registros de asistencia y horarios, con sincronización automática desde los dispositivos a una base de datos MySQL.

## ✨ Características

- ✅ **Gestión de Dispositivos**: CRUD completo de dispositivos ZKTeco
- ✅ **Gestión de Usuarios**: Crear, modificar y eliminar usuarios con sincronización bidireccional
- ✅ **Registros de Asistencia**: Obtener asistencias en tiempo real o por lotes
- ✅ **Gestión de Horarios**: Configurar horarios de trabajo
- ✅ **Sincronización**: Sincronización automática de hora y datos
- ✅ **Documentación Automática**: Swagger UI y ReDoc
- ✅ **Base de Datos MySQL**: Almacenamiento persistente de todos los datos

## 🚀 Instalación

### 1. Requisitos Previos

- Python 3.8 o superior
- MySQL 5.7 o superior
- Dispositivo ZKTeco en la misma red LAN

### 2. Instalar Dependencias

```bash
pip install -r requirements-api.txt
```

### 3. Configurar Base de Datos

Crear la base de datos en MySQL:

```bash
mysql -u root -p -e "CREATE DATABASE zkteco_db;"
```

### 4. Configurar Variables de Entorno

El archivo `.env` ya está configurado con tus credenciales:

```env
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=
DB_NAME=zkteco_db
```

### 5. Inicializar Base de Datos

```bash
python scripts/init_db.py
```

Este script creará todas las tablas necesarias:

- `dispositivos`
- `usuarios`
- `asistencias`
- `horarios`

## 🎯 Ejecutar la API

```bash
python scripts/run_api.py
```

La API estará disponible en: `http://localhost:8000`

### Documentación Interactiva

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 📚 Endpoints Principales

### Dispositivos

- `POST /api/dispositivos` - Crear dispositivo
- `GET /api/dispositivos` - Listar dispositivos
- `GET /api/dispositivos/{id}` - Obtener dispositivo
- `PUT /api/dispositivos/{id}` - Actualizar dispositivo
- `DELETE /api/dispositivos/{id}` - Eliminar dispositivo
- `POST /api/dispositivos/{id}/test-conexion` - Probar conexión
- `GET /api/dispositivos/{id}/info` - Información del dispositivo

### Usuarios

- `POST /api/usuarios` - Crear usuario
- `GET /api/usuarios` - Listar usuarios
- `GET /api/usuarios/{id}` - Obtener usuario
- `PUT /api/usuarios/{id}` - Actualizar usuario
- `DELETE /api/usuarios/{id}` - Eliminar usuario
- `POST /api/usuarios/{id}/sincronizar` - Sincronizar usuario con dispositivo
- `POST /api/usuarios/dispositivos/{id}/sincronizar` - Sincronizar todos los usuarios desde dispositivo

### Asistencias

- `GET /api/asistencias` - Obtener asistencias con filtros
- `GET /api/asistencias/count` - Contar asistencias
- `GET /api/asistencias/tiempo-real/{dispositivo_id}` - Asistencias en tiempo real
- `POST /api/asistencias/sincronizar/{dispositivo_id}` - Sincronizar asistencias
- `POST /api/asistencias/sincronizar-todos` - Sincronizar todos los dispositivos
- `DELETE /api/asistencias/{dispositivo_id}/limpiar` - Limpiar asistencias del dispositivo

### Horarios

- `POST /api/horarios` - Crear horario
- `GET /api/horarios` - Listar horarios
- `GET /api/horarios/{id}` - Obtener horario
- `PUT /api/horarios/{id}` - Actualizar horario
- `DELETE /api/horarios/{id}` - Eliminar horario

### Sincronización

- `POST /api/sincronizacion/hora/{dispositivo_id}` - Sincronizar hora
- `GET /api/sincronizacion/estado` - Estado de sincronización

## 💡 Ejemplos de Uso

### Crear un Dispositivo

```bash
curl -X POST "http://localhost:8000/api/dispositivos" \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Dispositivo Principal",
    "ip_address": "192.168.1.201",
    "puerto": 4370,
    "ubicacion": "Entrada Principal",
    "activo": true
  }'
```

### Crear un Usuario

```bash
curl -X POST "http://localhost:8000/api/usuarios" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "001",
    "nombre": "Juan Pérez",
    "privilegio": 0,
    "dispositivo_id": 1,
    "email": "juan@example.com"
  }'
```

### Sincronizar Asistencias

```bash
curl -X POST "http://localhost:8000/api/asistencias/sincronizar/1"
```

### Obtener Asistencias con Filtros

```bash
curl "http://localhost:8000/api/asistencias?dispositivo_id=1&limit=50"
```

### Obtener Asistencias en Tiempo Real

```bash
curl "http://localhost:8000/api/asistencias/tiempo-real/1?ultimos_minutos=5"
```

## 🔧 Configuración Avanzada

### Cambiar Puerto de la API

Editar `.env`:

```env
API_PORT=8080
```

### Configurar CORS

Editar `.env`:

```env
CORS_ORIGINS=http://localhost:3000,http://localhost:8080,https://miapp.com
```

### Sincronización Automática

Editar `.env`:

```env
AUTO_SYNC_ENABLED=True
AUTO_SYNC_INTERVAL=300  # 5 minutos
```

## 📊 Estructura del Proyecto

```
Zkteco python/
├── api/
│   ├── main.py              # Aplicación principal FastAPI
│   └── routers/             # Routers de endpoints
│       ├── dispositivos.py
│       ├── usuarios.py
│       ├── asistencias.py
│       ├── horarios.py
│       └── sincronizacion.py
├── models/                  # Modelos de base de datos
│   ├── database.py
│   ├── dispositivo.py
│   ├── usuario.py
│   ├── asistencia.py
│   └── horario.py
├── schemas/                 # Schemas de validación Pydantic
│   ├── dispositivo.py
│   ├── usuario.py
│   ├── asistencia.py
│   └── horario.py
├── services/                # Lógica de negocio
│   ├── dispositivo_service.py
│   ├── usuario_service.py
│   ├── asistencia_service.py
│   ├── horario_service.py
│   └── sincronizacion_service.py
├── scripts/                 # Scripts de utilidad
│   ├── init_db.py
│   └── run_api.py
├── config.py                # Configuración
├── .env                     # Variables de entorno
├── requirements-api.txt     # Dependencias
└── README_API.md           # Esta documentación
```

## 🐛 Solución de Problemas

### Error de Conexión a MySQL

```
Error: Can't connect to MySQL server
```

**Solución**: Verificar que MySQL esté ejecutándose y las credenciales sean correctas.

### Error: Base de datos no existe

```
Error: Unknown database 'zkteco_db'
```

**Solución**: Crear la base de datos:

```bash
mysql -u root -p -e "CREATE DATABASE zkteco_db;"
```

### Error de Conexión al Dispositivo

```
Error: No se pudo conectar al dispositivo
```

**Solución**:

1. Verificar que el dispositivo esté encendido
2. Verificar que esté en la misma red
3. Hacer ping a la IP del dispositivo
4. Verificar que el puerto sea 4370

## 📝 Notas Importantes

- Los registros de asistencia se sincronizan desde el dispositivo a la BD, no se eliminan del dispositivo automáticamente
- Los usuarios se pueden sincronizar bidireccionalmente (BD ↔ Dispositivo)
- La sincronización de hora usa la hora del sistema servidor
- Todos los endpoints están documentados en Swagger UI

## 🤝 Soporte

Para más información sobre el módulo de conexión ZKTeco, consultar:

- `zkteco_connection.py` - Módulo de conexión
- `ejemplo_uso.py` - Ejemplos de uso directo

## 📄 Licencia

Este proyecto es para uso interno de UGEL.
