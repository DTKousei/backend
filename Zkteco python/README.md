# Sistema de Integración con Dispositivos ZKTeco

Sistema completo en Python para conectarse a dispositivos ZKTeco de control de asistencia mediante conexión LAN usando protocolo TCP/IP.

## 📋 Características

- ✅ Conexión TCP/IP por LAN
- ✅ Obtener registros de asistencia (tiempo real y por lotes)
- ✅ Gestión completa de usuarios (añadir, modificar, eliminar)
- ✅ Obtener información del dispositivo (hora, serial, firmware, etc.)
- ✅ Sincronización de hora
- ✅ Monitoreo en tiempo real
- ✅ Código completamente comentado en español

## 🔧 Requisitos

- Python 3.6 o superior
- Dispositivo ZKTeco conectado a la red LAN
- Acceso de red al dispositivo

## 📦 Instalación

1. **Clonar o descargar este proyecto**

2. **Instalar dependencias:**

```bash
pip install -r requirements.txt
```

La dependencia principal es `pyzk`, una librería estable y probada para comunicación con dispositivos ZKTeco.

## 🌐 Configuración de Red

### Verificar la IP del Dispositivo

1. En el dispositivo ZKTeco, navega a: **Menú → Comunicación → Ethernet**
2. Anota la dirección IP (ejemplo: `192.168.1.201`)
3. Anota el puerto (por defecto: `4370`)

### Configurar la IP en el Código

Edita el archivo `ejemplo_uso.py` y cambia la variable `IP_DISPOSITIVO`:

```python
IP_DISPOSITIVO = '192.168.1.201'  # Cambia por la IP de tu dispositivo
```

### Verificar Conectividad

Desde tu computadora, verifica que puedes hacer ping al dispositivo:

```bash
ping 192.168.1.201
```

## 🚀 Uso Rápido

### Ejecutar el Menú de Ejemplos

```bash
python ejemplo_uso.py
```

Esto abrirá un menú interactivo con 8 ejemplos diferentes.

### Ejemplo Básico en Código

```python
from zkteco_connection import ZKTecoConnection

# Crear conexión
dispositivo = ZKTecoConnection('192.168.1.201')

# Conectar
if dispositivo.conectar():
    # Obtener asistencias
    asistencias = dispositivo.obtener_asistencias()
    dispositivo.mostrar_asistencias(asistencias)

    # Desconectar
    dispositivo.desconectar()
```

## 📚 Ejemplos Incluidos

El archivo `ejemplo_uso.py` incluye 8 ejemplos completos:

1. **Prueba de Conexión** - Verificar conectividad con el dispositivo
2. **Información del Dispositivo** - Obtener serial, firmware, MAC, etc.
3. **Gestión de Usuarios** - Añadir, modificar y eliminar usuarios
4. **Registros de Asistencia** - Obtener todos los registros almacenados
5. **Monitoreo en Tiempo Real** - Detectar nuevos registros automáticamente
6. **Sincronizar Hora** - Ajustar la hora del dispositivo
7. **Limpiar Registros** - Eliminar todos los registros de asistencia
8. **Función Auxiliar** - Uso rápido con función helper

## 🔍 Estructura del Proyecto

```
Python/
├── zkteco_connection.py    # Módulo principal con la clase ZKTecoConnection
├── ejemplo_uso.py          # Ejemplos de uso y menú interactivo
├── requirements.txt        # Dependencias del proyecto
└── README.md              # Este archivo
```

## 📖 Documentación de la Clase Principal

### ZKTecoConnection

Clase principal para interactuar con dispositivos ZKTeco.

#### Constructor

```python
dispositivo = ZKTecoConnection(
    ip_address='192.168.1.201',  # IP del dispositivo
    port=4370,                    # Puerto TCP (por defecto 4370)
    timeout=5,                    # Timeout en segundos
    password=0                    # Contraseña del dispositivo
)
```

#### Métodos Principales

##### Conexión

- `conectar()` - Establece conexión TCP con el dispositivo
- `desconectar()` - Cierra la conexión de forma segura
- `test_conexion()` - Prueba la conectividad

##### Asistencias

- `obtener_asistencias()` - Obtiene todos los registros de asistencia
- `mostrar_asistencias(asistencias)` - Muestra registros en formato tabla
- `limpiar_asistencias()` - Elimina todos los registros (¡irreversible!)

##### Usuarios

- `obtener_usuarios()` - Obtiene todos los usuarios registrados
- `mostrar_usuarios(usuarios)` - Muestra usuarios en formato tabla
- `agregar_usuario(user_id, name, privilege, password)` - Añade un usuario
- `modificar_usuario(user_id, name, privilege, password)` - Modifica un usuario
- `eliminar_usuario(user_id)` - Elimina un usuario

##### Información del Dispositivo

- `obtener_informacion_dispositivo()` - Obtiene información completa
- `mostrar_informacion_dispositivo(info)` - Muestra información en formato tabla
- `obtener_hora_dispositivo()` - Obtiene la hora del dispositivo
- `establecer_hora_dispositivo(nueva_hora)` - Establece la hora del dispositivo

## 🔐 Niveles de Privilegio de Usuarios

- `0` - Usuario normal
- `14` - Administrador

## 📊 Estructura de Datos

### Registro de Asistencia

```python
asistencia.user_id      # ID del usuario
asistencia.timestamp    # Fecha y hora del registro
asistencia.status       # Estado del registro
asistencia.punch        # Tipo de marcación
```

### Usuario

```python
usuario.uid             # ID único interno
usuario.user_id         # ID del usuario (número de empleado)
usuario.name            # Nombre del usuario
usuario.privilege       # Nivel de privilegio (0 o 14)
usuario.password        # Contraseña del usuario
usuario.group_id        # ID del grupo
```

## 🛠️ Solución de Problemas

### Error: "No se pudo conectar al dispositivo"

**Posibles causas:**

1. IP incorrecta - Verifica la IP en el dispositivo
2. Dispositivo apagado - Asegúrate de que esté encendido
3. Red diferente - Deben estar en la misma red LAN
4. Firewall - Verifica que el puerto 4370 esté abierto
5. Dispositivo ocupado - Otro programa puede estar conectado

**Solución:**

```bash
# Verificar conectividad
ping 192.168.1.201

# Verificar puerto (Windows)
Test-NetConnection -ComputerName 192.168.1.201 -Port 4370
```

### Error: "Timeout"

**Solución:**
Aumenta el timeout en el constructor:

```python
dispositivo = ZKTecoConnection('192.168.1.201', timeout=10)
```

### Error: "Usuario no encontrado"

**Solución:**
Verifica que el `user_id` sea exactamente el mismo que está registrado:

```python
usuarios = dispositivo.obtener_usuarios()
dispositivo.mostrar_usuarios(usuarios)
```

## 📝 Notas Importantes

1. **Siempre desconectar:** Usa `try-finally` para asegurar la desconexión:

   ```python
   try:
       dispositivo.conectar()
       # ... operaciones ...
   finally:
       dispositivo.desconectar()
   ```

2. **Operaciones irreversibles:** Los métodos `limpiar_asistencias()` y `eliminar_usuario()` son permanentes.

3. **Deshabilitar dispositivo:** Durante las operaciones, el dispositivo se deshabilita temporalmente (no procesa huellas/tarjetas).

4. **Sincronización de hora:** Es importante mantener la hora sincronizada para registros precisos.

## 🔄 Protocolo TCP

Este sistema utiliza el protocolo TCP/IP estándar de ZKTeco:

- **Puerto por defecto:** 4370
- **Protocolo:** TCP
- **Comunicación:** Binaria con comandos específicos de ZKTeco

## 📄 Licencia

Este código es de uso libre para proyectos educativos y comerciales.

## 👨‍💻 Soporte

Para problemas o preguntas:

1. Verifica la configuración de red
2. Revisa los ejemplos incluidos
3. Consulta la documentación del dispositivo ZKTeco

## 🎯 Próximos Pasos

Después de instalar y probar:

1. Ejecuta `python ejemplo_uso.py` y selecciona la opción 1 para probar la conexión
2. Si la conexión es exitosa, prueba obtener información del dispositivo (opción 2)
3. Experimenta con los otros ejemplos según tus necesidades

¡Listo para usar! 🚀
