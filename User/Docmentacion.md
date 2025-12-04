Documentación API REST - Backend User
📋 Información General
Descripción del Proyecto
API REST para gestión de usuarios, roles y permisos construida con:

Framework: Express.js 5.1.0
ORM: Prisma 6.19.0
Base de Datos: PostgreSQL
Autenticación: JWT (JSON Web Tokens)
Seguridad: Implementa mejores prácticas OWASP
URL Base
http://localhost:{PORT}/api
Autenticación
La mayoría de los endpoints requieren autenticación mediante JWT. El token debe enviarse en el header Authorization:

Authorization: Bearer {token}
Formato de Respuestas
Respuesta Exitosa:

{
  "success": true,
  "message": "Mensaje descriptivo",
  "data": { ... }
}
Respuesta de Error:

{
  "success": false,
  "message": "Descripción del error",
  "errors": [ ... ]  // Solo en errores de validación
}
🔐 Módulo de Autenticación
Base URL: /api/auth

1. Registrar Usuario
Endpoint: POST /api/auth/register
Acceso: Público
Descripción: Crea un nuevo usuario en el sistema

Entrada (Request Body)
{
  "usuario": "string",
  "correo_electronico": "string",
  "contrasena": "string",
  "rol_id": "uuid"
}
Validaciones
Campo	Reglas
usuario	• Requerido
• 3-50 caracteres
• Solo letras, números, guiones y guiones bajos
• No puede ser: admin, root, superuser, administrator, system
correo_electronico	• Requerido
• Email válido
• Máximo 80 caracteres
contrasena	• Requerido
• 8-128 caracteres
• Debe contener: mayúscula, minúscula, número y carácter especial (@$!%*?&)
• No puede ser contraseña común
rol_id	• Opcional
• UUID válido
Ejemplo de Solicitud
curl -X POST http://localhost:3000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "usuario": "juan_perez",
    "correo_electronico": "juan.perez@example.com",
    "contrasena": "MiPassword123!",
    "rol_id": "550e8400-e29b-41d4-a716-446655440000"
  }'
Salida Exitosa (201 Created)
{
  "success": true,
  "message": "Usuario registrado exitosamente",
  "user": {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "usuario": "juan_perez",
    "correo_electronico": "juan.perez@example.com",
    "esta_activo": true,
    "creado_en": "2025-12-03T18:00:00.000Z",
    "rol": {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "nombre": "Usuario"
    }
  }
}
Errores Posibles
Código	Descripción
400	Usuario o correo ya existe
400	Datos de validación incorrectos
400	Rol no encontrado
2. Iniciar Sesión
Endpoint: POST /api/auth/login
Acceso: Público
Descripción: Autentica un usuario y genera un token JWT
Seguridad: Rate limiting (máximo de intentos por IP)

Entrada (Request Body)
{
  "correo_electronico": "string",
  "contrasena": "string"
}
Validaciones
Campo	Reglas
correo_electronico	• Requerido
• Email válido
• Máximo 80 caracteres
contrasena	• Requerido
• 1-128 caracteres
Ejemplo de Solicitud
curl -X POST http://localhost:3000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "correo_electronico": "juan.perez@example.com",
    "contrasena": "MiPassword123!"
  }'
Salida Exitosa (200 OK)
{
  "success": true,
  "message": "Login exitoso",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "usuario": "juan_perez",
    "correo_electronico": "juan.perez@example.com",
    "esta_activo": true,
    "rol": {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "nombre": "Usuario"
    }
  }
}
Errores Posibles
Código	Descripción
401	Credenciales inválidas
401	Usuario inactivo
429	Demasiados intentos de login
3. Cerrar Sesión
Endpoint: POST /api/auth/logout
Acceso: Privado (requiere token JWT)
Descripción: Invalida el token JWT del usuario

Headers Requeridos
Authorization: Bearer {token}
Entrada
No requiere body

Ejemplo de Solicitud
curl -X POST http://localhost:3000/api/auth/logout \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
Salida Exitosa (200 OK)
{
  "success": true,
  "message": "Sesión cerrada exitosamente"
}
Errores Posibles
Código	Descripción
401	Token inválido o expirado
400	Error al cerrar sesión
4. Cambiar Contraseña
Endpoint: POST /api/auth/change-password
Acceso: Privado (requiere token JWT)
Descripción: Permite al usuario cambiar su contraseña. Invalida todas las sesiones activas.

Headers Requeridos
Authorization: Bearer {token}
Entrada (Request Body)
{
  "contrasena_actual": "string",
  "contrasena_nueva": "string"
}
Validaciones
Campo	Reglas
contrasena_actual	• Requerido
• 1-128 caracteres
contrasena_nueva	• Requerido
• 8-128 caracteres
• Debe contener: mayúscula, minúscula, número y carácter especial
• Debe ser diferente a la contraseña actual
Ejemplo de Solicitud
curl -X POST http://localhost:3000/api/auth/change-password \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json" \
  -d '{
    "contrasena_actual": "MiPassword123!",
    "contrasena_nueva": "NuevaPassword456@"
  }'
Salida Exitosa (200 OK)
{
  "success": true,
  "message": "Contraseña cambiada exitosamente. Por favor, inicia sesión nuevamente."
}
Errores Posibles
Código	Descripción
400	Contraseña actual incorrecta
400	Nueva contraseña no cumple requisitos
401	Token inválido
5. Obtener Perfil
Endpoint: GET /api/auth/profile
Acceso: Privado (requiere token JWT)
Descripción: Obtiene el perfil completo del usuario autenticado

Headers Requeridos
Authorization: Bearer {token}
Entrada
No requiere parámetros

Ejemplo de Solicitud
curl -X GET http://localhost:3000/api/auth/profile \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
Salida Exitosa (200 OK)
{
  "success": true,
  "user": {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "usuario": "juan_perez",
    "correo_electronico": "juan.perez@example.com",
    "esta_activo": true,
    "creado_en": "2025-12-03T18:00:00.000Z",
    "actualizado_en": "2025-12-03T18:00:00.000Z",
    "rol": {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "nombre": "Usuario",
      "descripcion": "Usuario estándar del sistema"
    }
  }
}
Errores Posibles
Código	Descripción
401	Token inválido o expirado
400	Error al obtener perfil
6. Verificar Token
Endpoint: GET /api/auth/verify
Acceso: Privado (requiere token JWT)
Descripción: Verifica si el token JWT es válido y está activo

Headers Requeridos
Authorization: Bearer {token}
Entrada
No requiere parámetros

Ejemplo de Solicitud
curl -X GET http://localhost:3000/api/auth/verify \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
Salida Exitosa (200 OK)
{
  "success": true,
  "message": "Token válido",
  "user": {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "usuario": "juan_perez",
    "correo_electronico": "juan.perez@example.com",
    "rol": {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "nombre": "Usuario"
    }
  }
}
Errores Posibles
Código	Descripción
401	Token inválido, expirado o sesión no existe
👥 Módulo de Usuarios
Base URL: /api/users
Nota: Todos los endpoints requieren autenticación JWT

1. Listar Todos los Usuarios
Endpoint: GET /api/users
Acceso: Privado
Descripción: Obtiene la lista de todos los usuarios del sistema

Headers Requeridos
Authorization: Bearer {token}
Entrada
No requiere parámetros

Ejemplo de Solicitud
curl -X GET http://localhost:3000/api/users \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
Salida Exitosa (200 OK)
{
  "success": true,
  "data": [
    {
      "id": "123e4567-e89b-12d3-a456-426614174000",
      "usuario": "juan_perez",
      "correo_electronico": "juan.perez@example.com",
      "esta_activo": true,
      "creado_en": "2025-12-03T18:00:00.000Z",
      "rol": {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "nombre": "Usuario"
      }
    },
    {
      "id": "234e5678-e89b-12d3-a456-426614174001",
      "usuario": "maria_garcia",
      "correo_electronico": "maria.garcia@example.com",
      "esta_activo": true,
      "creado_en": "2025-12-02T10:30:00.000Z",
      "rol": {
        "id": "660e8400-e29b-41d4-a716-446655440001",
        "nombre": "Administrador"
      }
    }
  ]
}
Errores Posibles
Código	Descripción
401	Token inválido
500	Error interno del servidor
2. Obtener Usuario por ID
Endpoint: GET /api/users/:id
Acceso: Privado
Descripción: Obtiene un usuario específico con sus permisos

Headers Requeridos
Authorization: Bearer {token}
Parámetros URL
Parámetro	Tipo	Descripción
id
UUID	ID del usuario a buscar
Ejemplo de Solicitud
curl -X GET http://localhost:3000/api/users/123e4567-e89b-12d3-a456-426614174000 \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
Salida Exitosa (200 OK)
{
  "success": true,
  "data": {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "usuario": "juan_perez",
    "correo_electronico": "juan.perez@example.com",
    "esta_activo": true,
    "creado_en": "2025-12-03T18:00:00.000Z",
    "actualizado_en": "2025-12-03T18:00:00.000Z",
    "rol": {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "nombre": "Usuario",
      "descripcion": "Usuario estándar"
    },
    "usuario_permisos": [
      {
        "permiso": {
          "id": "770e8400-e29b-41d4-a716-446655440002",
          "nombre": "reports.view",
          "descripcion": "Ver reportes"
        }
      }
    ]
  }
}
Errores Posibles
Código	Descripción
404	Usuario no encontrado
401	Token inválido
3. Crear Usuario
Endpoint: POST /api/users
Acceso: Privado
Descripción: Crea un nuevo usuario en el sistema

Headers Requeridos
Authorization: Bearer {token}
Entrada (Request Body)
{
  "usuario": "string",
  "correo_electronico": "string",
  "contrasena": "string",
  "rol_id": "uuid"
}
Validaciones
Las mismas que en el registro de usuario (ver sección de autenticación)

Ejemplo de Solicitud
curl -X POST http://localhost:3000/api/users \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json" \
  -d '{
    "usuario": "carlos_lopez",
    "correo_electronico": "carlos.lopez@example.com",
    "contrasena": "SecurePass789!",
    "rol_id": "550e8400-e29b-41d4-a716-446655440000"
  }'
Salida Exitosa (201 Created)
{
  "success": true,
  "data": {
    "id": "345e6789-e89b-12d3-a456-426614174002",
    "usuario": "carlos_lopez",
    "correo_electronico": "carlos.lopez@example.com",
    "esta_activo": true,
    "rol_id": "550e8400-e29b-41d4-a716-446655440000",
    "creado_en": "2025-12-03T19:00:00.000Z"
  }
}
Errores Posibles
Código	Descripción
400	Usuario o correo ya existe
400	Datos inválidos
401	Token inválido
4. Actualizar Usuario
Endpoint: PUT /api/users/:id
Acceso: Privado
Descripción: Actualiza un usuario existente

Headers Requeridos
Authorization: Bearer {token}
Parámetros URL
Parámetro	Tipo	Descripción
id
UUID	ID del usuario a actualizar
Entrada (Request Body)
Todos los campos son opcionales

{
  "usuario": "string",
  "correo_electronico": "string",
  "contrasena": "string",
  "rol_id": "uuid",
  "esta_activo": boolean
}
Ejemplo de Solicitud
curl -X PUT http://localhost:3000/api/users/123e4567-e89b-12d3-a456-426614174000 \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json" \
  -d '{
    "usuario": "juan_perez_updated",
    "esta_activo": false
  }'
Salida Exitosa (200 OK)
{
  "success": true,
  "data": {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "usuario": "juan_perez_updated",
    "correo_electronico": "juan.perez@example.com",
    "esta_activo": false,
    "rol_id": "550e8400-e29b-41d4-a716-446655440000",
    "actualizado_en": "2025-12-03T20:00:00.000Z"
  }
}
Errores Posibles
Código	Descripción
400	Usuario no encontrado
400	Datos inválidos
401	Token inválido
5. Eliminar Usuario
Endpoint: DELETE /api/users/:id
Acceso: Privado
Descripción: Elimina un usuario del sistema (elimina también sus sesiones y permisos)

Headers Requeridos
Authorization: Bearer {token}
Parámetros URL
Parámetro	Tipo	Descripción
id
UUID	ID del usuario a eliminar
Ejemplo de Solicitud
curl -X DELETE http://localhost:3000/api/users/123e4567-e89b-12d3-a456-426614174000 \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
Salida Exitosa (200 OK)
{
  "success": true,
  "message": "Usuario eliminado"
}
Errores Posibles
Código	Descripción
400	Usuario no encontrado
401	Token inválido
🎭 Módulo de Roles
Base URL: /api/roles
Nota: Todos los endpoints requieren autenticación JWT

1. Listar Todos los Roles
Endpoint: GET /api/roles
Acceso: Privado
Descripción: Obtiene la lista de todos los roles con sus permisos

Headers Requeridos
Authorization: Bearer {token}
Entrada
No requiere parámetros

Ejemplo de Solicitud
curl -X GET http://localhost:3000/api/roles \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
Salida Exitosa (200 OK)
{
  "success": true,
  "data": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "nombre": "Usuario",
      "descripcion": "Usuario estándar del sistema",
      "roles_permisos": [
        {
          "permiso": {
            "id": "770e8400-e29b-41d4-a716-446655440002",
            "nombre": "users.read",
            "descripcion": "Ver usuarios"
          }
        }
      ]
    },
    {
      "id": "660e8400-e29b-41d4-a716-446655440001",
      "nombre": "Administrador",
      "descripcion": "Administrador del sistema",
      "roles_permisos": [
        {
          "permiso": {
            "id": "770e8400-e29b-41d4-a716-446655440002",
            "nombre": "users.read",
            "descripcion": "Ver usuarios"
          }
        },
        {
          "permiso": {
            "id": "880e8400-e29b-41d4-a716-446655440003",
            "nombre": "users.create",
            "descripcion": "Crear usuarios"
          }
        }
      ]
    }
  ]
}
Errores Posibles
Código	Descripción
401	Token inválido
500	Error interno del servidor
2. Obtener Rol por ID
Endpoint: GET /api/roles/:id
Acceso: Privado
Descripción: Obtiene un rol específico con sus permisos

Headers Requeridos
Authorization: Bearer {token}
Parámetros URL
Parámetro	Tipo	Descripción
id
UUID	ID del rol a buscar
Ejemplo de Solicitud
curl -X GET http://localhost:3000/api/roles/550e8400-e29b-41d4-a716-446655440000 \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
Salida Exitosa (200 OK)
{
  "success": true,
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "nombre": "Usuario",
    "descripcion": "Usuario estándar del sistema",
    "roles_permisos": [
      {
        "permiso": {
          "id": "770e8400-e29b-41d4-a716-446655440002",
          "nombre": "users.read",
          "descripcion": "Ver usuarios",
          "creado_en": "2025-12-01T10:00:00.000Z"
        }
      }
    ]
  }
}
Errores Posibles
Código	Descripción
404	Rol no encontrado
401	Token inválido
3. Crear Rol
Endpoint: POST /api/roles
Acceso: Privado
Descripción: Crea un nuevo rol y opcionalmente asigna permisos

Headers Requeridos
Authorization: Bearer {token}
Entrada (Request Body)
{
  "nombre": "string",
  "descripcion": "string",
  "permisos": ["uuid1", "uuid2"]
}
Campo	Tipo	Requerido	Descripción
nombre	string	Sí	Nombre del rol
descripcion	string	No	Descripción del rol
permisos	array[uuid]	No	Array de IDs de permisos a asignar
Ejemplo de Solicitud
curl -X POST http://localhost:3000/api/roles \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Supervisor",
    "descripcion": "Supervisor de área",
    "permisos": [
      "770e8400-e29b-41d4-a716-446655440002",
      "880e8400-e29b-41d4-a716-446655440003"
    ]
  }'
Salida Exitosa (201 Created)
{
  "success": true,
  "data": {
    "id": "990e8400-e29b-41d4-a716-446655440004",
    "nombre": "Supervisor",
    "descripcion": "Supervisor de área"
  }
}
Errores Posibles
Código	Descripción
400	Nombre de rol ya existe
400	IDs de permisos inválidos
401	Token inválido
4. Actualizar Rol
Endpoint: PUT /api/roles/:id
Acceso: Privado
Descripción: Actualiza un rol existente. Si se envía el array de permisos, REEMPLAZA todos los permisos existentes.

Headers Requeridos
Authorization: Bearer {token}
Parámetros URL
Parámetro	Tipo	Descripción
id
UUID	ID del rol a actualizar
Entrada (Request Body)
Todos los campos son opcionales

{
  "nombre": "string",
  "descripcion": "string",
  "permisos": ["uuid1", "uuid2"]
}
Ejemplo de Solicitud
curl -X PUT http://localhost:3000/api/roles/990e8400-e29b-41d4-a716-446655440004 \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Supervisor Senior",
    "permisos": [
      "770e8400-e29b-41d4-a716-446655440002"
    ]
  }'
Salida Exitosa (200 OK)
{
  "success": true,
  "data": {
    "id": "990e8400-e29b-41d4-a716-446655440004",
    "nombre": "Supervisor Senior",
    "descripcion": "Supervisor de área"
  }
}
Errores Posibles
Código	Descripción
400	Rol no encontrado
400	IDs de permisos inválidos
401	Token inválido
5. Eliminar Rol
Endpoint: DELETE /api/roles/:id
Acceso: Privado
Descripción: Elimina un rol del sistema. No se puede eliminar si hay usuarios asignados.

Headers Requeridos
Authorization: Bearer {token}
Parámetros URL
Parámetro	Tipo	Descripción
id
UUID	ID del rol a eliminar
Ejemplo de Solicitud
curl -X DELETE http://localhost:3000/api/roles/990e8400-e29b-41d4-a716-446655440004 \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
Salida Exitosa (200 OK)
{
  "success": true,
  "message": "Rol eliminado"
}
Errores Posibles
Código	Descripción
400	Rol no encontrado
400	No se puede eliminar (hay usuarios con este rol)
401	Token inválido
🔑 Módulo de Permisos
Base URL: /api/permissions
Nota: Todos los endpoints requieren autenticación JWT

1. Listar Todos los Permisos
Endpoint: GET /api/permissions
Acceso: Privado
Descripción: Obtiene la lista de todos los permisos del sistema

Headers Requeridos
Authorization: Bearer {token}
Entrada
No requiere parámetros

Ejemplo de Solicitud
curl -X GET http://localhost:3000/api/permissions \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
Salida Exitosa (200 OK)
{
  "success": true,
  "data": [
    {
      "id": "770e8400-e29b-41d4-a716-446655440002",
      "nombre": "users.read",
      "descripcion": "Ver usuarios",
      "creado_en": "2025-12-01T10:00:00.000Z"
    },
    {
      "id": "880e8400-e29b-41d4-a716-446655440003",
      "nombre": "users.create",
      "descripcion": "Crear usuarios",
      "creado_en": "2025-12-01T10:00:00.000Z"
    },
    {
      "id": "aa0e8400-e29b-41d4-a716-446655440005",
      "nombre": "reports.view",
      "descripcion": "Ver reportes",
      "creado_en": "2025-12-01T10:00:00.000Z"
    }
  ]
}
Errores Posibles
Código	Descripción
401	Token inválido
500	Error interno del servidor
2. Obtener Permiso por ID
Endpoint: GET /api/permissions/:id
Acceso: Privado
Descripción: Obtiene un permiso específico

Headers Requeridos
Authorization: Bearer {token}
Parámetros URL
Parámetro	Tipo	Descripción
id
UUID	ID del permiso a buscar
Ejemplo de Solicitud
curl -X GET http://localhost:3000/api/permissions/770e8400-e29b-41d4-a716-446655440002 \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
Salida Exitosa (200 OK)
{
  "success": true,
  "data": {
    "id": "770e8400-e29b-41d4-a716-446655440002",
    "nombre": "users.read",
    "descripcion": "Ver usuarios",
    "creado_en": "2025-12-01T10:00:00.000Z"
  }
}
Errores Posibles
Código	Descripción
404	Permiso no encontrado
401	Token inválido
3. Crear Permiso
Endpoint: POST /api/permissions
Acceso: Privado
Descripción: Crea un nuevo permiso en el sistema

Headers Requeridos
Authorization: Bearer {token}
Entrada (Request Body)
{
  "nombre": "string",
  "descripcion": "string"
}
Campo	Tipo	Requerido	Descripción
nombre	string	Sí	Nombre único del permiso (formato: recurso.accion)
descripcion	string	No	Descripción del permiso
Convención de Nombres
Se recomienda usar el formato recurso.accion:

users.create, users.read, users.update, users.delete
roles.manage
reports.view, reports.export
attendance.register, attendance.approve
Ejemplo de Solicitud
curl -X POST http://localhost:3000/api/permissions \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "attendance.manage",
    "descripcion": "Gestionar registros de asistencia"
  }'
Salida Exitosa (201 Created)
{
  "success": true,
  "data": {
    "id": "bb0e8400-e29b-41d4-a716-446655440006",
    "nombre": "attendance.manage",
    "descripcion": "Gestionar registros de asistencia",
    "creado_en": "2025-12-03T20:00:00.000Z"
  }
}
Errores Posibles
Código	Descripción
400	Nombre de permiso ya existe
400	Datos inválidos
401	Token inválido
4. Actualizar Permiso
Endpoint: PUT /api/permissions/:id
Acceso: Privado
Descripción: Actualiza un permiso existente

Headers Requeridos
Authorization: Bearer {token}
Parámetros URL
Parámetro	Tipo	Descripción
id
UUID	ID del permiso a actualizar
Entrada (Request Body)
Todos los campos son opcionales

{
  "nombre": "string",
  "descripcion": "string"
}
Ejemplo de Solicitud
curl -X PUT http://localhost:3000/api/permissions/bb0e8400-e29b-41d4-a716-446655440006 \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json" \
  -d '{
    "descripcion": "Gestionar y aprobar registros de asistencia"
  }'
Salida Exitosa (200 OK)
{
  "success": true,
  "data": {
    "id": "bb0e8400-e29b-41d4-a716-446655440006",
    "nombre": "attendance.manage",
    "descripcion": "Gestionar y aprobar registros de asistencia",
    "creado_en": "2025-12-03T20:00:00.000Z"
  }
}
Errores Posibles
Código	Descripción
400	Permiso no encontrado
400	Nombre ya existe
401	Token inválido
5. Eliminar Permiso
Endpoint: DELETE /api/permissions/:id
Acceso: Privado
Descripción: Elimina un permiso del sistema. Elimina automáticamente las relaciones en roles y usuarios.

Headers Requeridos
Authorization: Bearer {token}
Parámetros URL
Parámetro	Tipo	Descripción
id
UUID	ID del permiso a eliminar
Ejemplo de Solicitud
curl -X DELETE http://localhost:3000/api/permissions/bb0e8400-e29b-41d4-a716-446655440006 \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
Salida Exitosa (200 OK)
{
  "success": true,
  "message": "Permiso eliminado"
}
Errores Posibles
Código	Descripción
400	Permiso no encontrado
401	Token inválido
🔒 Seguridad
Características de Seguridad Implementadas
Helmet: Protección de headers HTTP
CORS: Control de acceso entre dominios
Rate Limiting: Límite de peticiones por IP
Input Sanitization: Sanitización de entradas para prevenir XSS
Password Hashing: Contraseñas hasheadas con bcrypt
JWT: Tokens seguros con expiración
Timing Attack Prevention: Prevención de ataques de temporización
Validaciones de Contraseña
Las contraseñas deben cumplir:

Mínimo 8 caracteres, máximo 128
Al menos una letra mayúscula
Al menos una letra minúscula
Al menos un número
Al menos un carácter especial (@$!%*?&)
No puede ser una contraseña común
Rate Limiting
API General: Límite configurado por IP
Login: Rate limiting específico para prevenir fuerza bruta
📊 Modelo de Base de Datos
Tablas Principales
usuarios
id (UUID, PK)
usuario (VARCHAR 50, UNIQUE)
correo_electronico (VARCHAR 80)
contrasena_hash (VARCHAR 255)
rol_id (UUID, FK -> roles)
esta_activo (BOOLEAN)
creado_en (TIMESTAMP)
actualizado_en (TIMESTAMP)
roles
id (UUID, PK)
nombre (VARCHAR 50)
descripcion (TEXT)
permisos
id (UUID, PK)
nombre (VARCHAR 100)
descripcion (TEXT)
creado_en (TIMESTAMP)
roles_permisos (Tabla de relación)
rol_id (UUID, PK, FK -> roles)
permiso_id (UUID, PK, FK -> permisos)
usuario_permisos (Tabla de relación)
usuario_id (UUID, PK, FK -> usuarios)
permiso_id (UUID, PK, FK -> permisos)
sesiones_usuario
id (UUID, PK)
usuario_id (UUID, FK -> usuarios)
token (VARCHAR 500)
expira_en (TIMESTAMP)
creado_en (TIMESTAMP)
🚀 Guía de Uso Paso a Paso
Escenario 1: Registro e Inicio de Sesión
Paso 1: Registrar un nuevo usuario

curl -X POST http://localhost:3000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "usuario": "nuevo_usuario",
    "correo_electronico": "nuevo@example.com",
    "contrasena": "Password123!",
    "rol_id": "550e8400-e29b-41d4-a716-446655440000"
  }'
Paso 2: Iniciar sesión

curl -X POST http://localhost:3000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "correo_electronico": "nuevo@example.com",
    "contrasena": "Password123!"
  }'
Paso 3: Guardar el token recibido

{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
Paso 4: Usar el token en peticiones subsecuentes

curl -X GET http://localhost:3000/api/auth/profile \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
Escenario 2: Gestión de Roles y Permisos
Paso 1: Crear permisos

# Crear permiso de lectura
curl -X POST http://localhost:3000/api/permissions \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "documents.read",
    "descripcion": "Ver documentos"
  }'
# Crear permiso de escritura
curl -X POST http://localhost:3000/api/permissions \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "documents.write",
    "descripcion": "Crear y editar documentos"
  }'
Paso 2: Crear un rol con permisos

curl -X POST http://localhost:3000/api/roles \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Editor",
    "descripcion": "Editor de documentos",
    "permisos": [
      "permiso-id-1",
      "permiso-id-2"
    ]
  }'
Paso 3: Asignar rol a un usuario

curl -X PUT http://localhost:3000/api/users/{user-id} \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "rol_id": "{rol-id}"
  }'
Escenario 3: Cambio de Contraseña
Paso 1: Usuario autenticado cambia su contraseña

curl -X POST http://localhost:3000/api/auth/change-password \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "contrasena_actual": "Password123!",
    "contrasena_nueva": "NewPassword456@"
  }'
Paso 2: Iniciar sesión nuevamente con la nueva contraseña

curl -X POST http://localhost:3000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "correo_electronico": "usuario@example.com",
    "contrasena": "NewPassword456@"
  }'
⚠️ Errores Comunes
Error 401: Unauthorized
Causas:

Token JWT inválido o expirado
Token no enviado en el header
Sesión cerrada o invalidada
Solución:

# Verificar que el token esté en el header
Authorization: Bearer {token}
# Si el token expiró, hacer login nuevamente
Error 400: Bad Request
Causas:

Datos de validación incorrectos
Campos requeridos faltantes
Formato de datos incorrecto
Solución:

# Revisar el mensaje de error para ver qué campo falló
{
  "success": false,
  "message": "Errores de validación",
  "errors": [
    {
      "field": "contrasena",
      "message": "La contraseña debe contener al menos una mayúscula"
    }
  ]
}
Error 404: Not Found
Causas:

Recurso no existe (usuario, rol, permiso)
ID incorrecto
Solución:

# Verificar que el ID sea correcto
# Listar recursos disponibles primero
curl -X GET http://localhost:3000/api/users \
  -H "Authorization: Bearer {token}"
Error 429: Too Many Requests
Causas:

Demasiados intentos de login
Rate limit excedido
Solución:

# Esperar unos minutos antes de intentar nuevamente
# El rate limit se resetea automáticamente
📝 Notas Adicionales
Variables de Entorno Requeridas
DATABASE_URL=postgresql://user:password@localhost:5432/database
JWT_SECRET=tu_secreto_jwt_muy_seguro
JWT_EXPIRES_IN=24h
PORT=3000
NODE_ENV=development
CORS_ORIGIN=*
Comandos Útiles
# Iniciar servidor en desarrollo
npm run dev
# Generar cliente Prisma
npm run prisma:generate
# Ejecutar migraciones
npm run prisma:migrate
# Abrir Prisma Studio
npm run prisma:studio
# Ejecutar seed
npm run seed
📞 Soporte
Para más información sobre el proyecto, consulta:

Código fuente en: d:\ActulaizacionUGEL\ptoyecto de control de asistencia\Backend\User
Esquema de base de datos: 
schema.prisma
Configuración de la aplicación: 
app.js