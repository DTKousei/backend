"""
Protocolo TCP de ZKTeco - Implementación de Bajo Nivel
=======================================================

Este módulo contiene la implementación de bajo nivel del protocolo TCP
utilizado por los dispositivos ZKTeco. Incluye constantes, comandos y
funciones auxiliares para construir y parsear paquetes TCP.

NOTA: Este archivo es principalmente para referencia y entendimiento
del protocolo. La librería pyzk ya implementa todo esto internamente.

Autor: Sistema de Control de Asistencia
Fecha: 2025-11-26
"""

import struct
from datetime import datetime

# ============================================================================
# CONSTANTES DEL PROTOCOLO ZKTECO
# ============================================================================

# Comandos principales del protocolo TCP
# Cada comando es un código numérico que el dispositivo entiende
CMD_CONNECT = 1000          # Establecer conexión con el dispositivo
CMD_EXIT = 1001             # Cerrar conexión
CMD_ENABLE_DEVICE = 1002    # Habilitar el dispositivo para operación normal
CMD_DISABLE_DEVICE = 1003   # Deshabilitar el dispositivo temporalmente

CMD_GET_TIME = 201          # Obtener la hora del dispositivo
CMD_SET_TIME = 202          # Establecer la hora del dispositivo

CMD_USER_WRQ = 8            # Escribir datos de usuario
CMD_USERTEMP_RRQ = 9        # Leer plantillas de huellas
CMD_DELETE_USER = 18        # Eliminar un usuario
CMD_DELETE_USERTEMP = 19    # Eliminar plantilla de huella

CMD_ATTLOG_RRQ = 13         # Leer registros de asistencia
CMD_CLEAR_ATTLOG = 14       # Limpiar registros de asistencia

CMD_GET_FREE_SIZES = 50     # Obtener espacio disponible
CMD_GET_PLATFORM = 51       # Obtener información de plataforma
CMD_GET_VERSION = 1100      # Obtener versión de firmware
CMD_GET_DEVICE_NAME = 52    # Obtener nombre del dispositivo
CMD_GET_SERIALNUMBER = 53   # Obtener número de serie
CMD_GET_MAC = 54            # Obtener dirección MAC

# Estados de respuesta del dispositivo
CMD_ACK_OK = 2000           # Comando ejecutado exitosamente
CMD_ACK_ERROR = 2001        # Error al ejecutar comando
CMD_ACK_DATA = 2002         # Respuesta con datos

# Tamaños de paquete
PACKET_HEADER_SIZE = 8      # Tamaño del encabezado del paquete (bytes)
MAX_PACKET_SIZE = 65535     # Tamaño máximo de un paquete TCP

# Puerto por defecto
DEFAULT_PORT = 4370         # Puerto TCP estándar de ZKTeco

# Timeout por defecto
DEFAULT_TIMEOUT = 5         # Segundos


# ============================================================================
# ESTRUCTURA DE PAQUETES TCP
# ============================================================================

class ZKPacket:
    """
    Representa un paquete del protocolo TCP de ZKTeco.
    
    Estructura de un paquete:
    - Bytes 0-1: Inicio del paquete (siempre 0x5050)
    - Bytes 2-3: ID de la sesión
    - Bytes 4-5: Código de respuesta/comando
    - Bytes 6-7: Checksum
    - Bytes 8+: Datos del paquete
    """
    
    def __init__(self, command, data=b'', session_id=0):
        """
        Inicializa un paquete ZKTeco.
        
        Parámetros:
            command (int): Código del comando a enviar
            data (bytes): Datos adicionales del comando
            session_id (int): ID de la sesión actual
        """
        self.command = command
        self.data = data
        self.session_id = session_id
    
    def build(self):
        """
        Construye el paquete completo en formato binario para enviar por TCP.
        
        Proceso:
        1. Crear el encabezado con el comando y session_id
        2. Calcular el checksum de los datos
        3. Combinar encabezado + datos
        4. Retornar el paquete completo en bytes
        
        Retorna:
            bytes: Paquete completo listo para enviar
        """
        # Paso 1: Calcular el checksum
        # El checksum es la suma de todos los bytes de datos
        checksum = self._calculate_checksum(self.data)
        
        # Paso 2: Construir el encabezado del paquete
        # Formato: inicio(2) + session_id(2) + command(2) + checksum(2)
        header = struct.pack(
            '<HHHH',  # < = little-endian, H = unsigned short (2 bytes)
            0x5050,   # Inicio del paquete (constante)
            self.session_id,  # ID de sesión
            self.command,     # Código del comando
            checksum          # Checksum calculado
        )
        
        # Paso 3: Combinar encabezado y datos
        packet = header + self.data
        
        return packet
    
    @staticmethod
    def parse(packet_bytes):
        """
        Parsea un paquete recibido del dispositivo.
        
        Parámetros:
            packet_bytes (bytes): Bytes recibidos del dispositivo
        
        Retorna:
            dict: Diccionario con los componentes del paquete
        """
        # Verificar que el paquete tenga al menos el tamaño del encabezado
        if len(packet_bytes) < PACKET_HEADER_SIZE:
            raise ValueError("Paquete demasiado corto")
        
        # Parsear el encabezado
        # Formato: inicio(2) + session_id(2) + reply_code(2) + checksum(2)
        start, session_id, reply_code, checksum = struct.unpack(
            '<HHHH',
            packet_bytes[:PACKET_HEADER_SIZE]
        )
        
        # Verificar que el inicio sea correcto
        if start != 0x5050:
            raise ValueError("Inicio de paquete inválido")
        
        # Extraer los datos (todo después del encabezado)
        data = packet_bytes[PACKET_HEADER_SIZE:]
        
        # Retornar los componentes parseados
        return {
            'session_id': session_id,
            'reply_code': reply_code,
            'checksum': checksum,
            'data': data
        }
    
    @staticmethod
    def _calculate_checksum(data):
        """
        Calcula el checksum de los datos.
        
        El checksum es simplemente la suma de todos los bytes,
        tomando solo los 16 bits menos significativos.
        
        Parámetros:
            data (bytes): Datos para calcular checksum
        
        Retorna:
            int: Checksum calculado (16 bits)
        """
        # Sumar todos los bytes
        checksum = sum(data)
        
        # Tomar solo los 16 bits menos significativos
        checksum = checksum & 0xFFFF
        
        return checksum


# ============================================================================
# FUNCIONES AUXILIARES PARA CODIFICACIÓN DE DATOS
# ============================================================================

def encode_time(dt):
    """
    Codifica un objeto datetime en el formato que ZKTeco espera.
    
    ZKTeco usa un formato de 4 bytes para representar fecha/hora:
    - Año: desde 2000
    - Mes: 1-12
    - Día: 1-31
    - Hora: 0-23
    - Minuto: 0-59
    - Segundo: 0-59
    
    Parámetros:
        dt (datetime): Objeto datetime a codificar
    
    Retorna:
        bytes: 4 bytes representando la fecha/hora
    """
    # Codificar cada componente
    year = dt.year - 2000  # Año relativo a 2000
    month = dt.month
    day = dt.day
    hour = dt.hour
    minute = dt.minute
    second = dt.second
    
    # Empaquetar en 4 bytes
    # Formato específico de ZKTeco
    encoded = struct.pack(
        'BBBBBB',  # 6 bytes unsigned
        year, month, day, hour, minute, second
    )
    
    return encoded


def decode_time(time_bytes):
    """
    Decodifica bytes de tiempo de ZKTeco a un objeto datetime.
    
    Parámetros:
        time_bytes (bytes): Bytes de tiempo del dispositivo
    
    Retorna:
        datetime: Objeto datetime decodificado
    """
    # Desempaquetar los bytes
    year, month, day, hour, minute, second = struct.unpack(
        'BBBBBB',
        time_bytes[:6]
    )
    
    # Crear objeto datetime
    # Sumar 2000 al año
    dt = datetime(
        year + 2000,
        month,
        day,
        hour,
        minute,
        second
    )
    
    return dt


def encode_user_id(user_id):
    """
    Codifica un ID de usuario en el formato de ZKTeco.
    
    Parámetros:
        user_id (str): ID del usuario
    
    Retorna:
        bytes: ID codificado
    """
    # Convertir a bytes con codificación ASCII
    # ZKTeco usa strings terminados en null
    encoded = user_id.encode('ascii') + b'\x00'
    return encoded


def decode_user_id(user_bytes):
    """
    Decodifica bytes de ID de usuario de ZKTeco.
    
    Parámetros:
        user_bytes (bytes): Bytes del ID de usuario
    
    Retorna:
        str: ID de usuario decodificado
    """
    # Decodificar y remover el null terminator
    user_id = user_bytes.rstrip(b'\x00').decode('ascii')
    return user_id


# ============================================================================
# INFORMACIÓN DE REFERENCIA
# ============================================================================

"""
FLUJO DE COMUNICACIÓN TCP CON ZKTECO:

1. CONEXIÓN:
   Cliente → Dispositivo: CMD_CONNECT
   Dispositivo → Cliente: CMD_ACK_OK + session_id
   
2. DESHABILITAR DISPOSITIVO (para operaciones):
   Cliente → Dispositivo: CMD_DISABLE_DEVICE
   Dispositivo → Cliente: CMD_ACK_OK
   
3. OPERACIONES (ejemplos):
   
   a) Obtener hora:
      Cliente → Dispositivo: CMD_GET_TIME
      Dispositivo → Cliente: CMD_ACK_OK + datos de hora
   
   b) Obtener asistencias:
      Cliente → Dispositivo: CMD_ATTLOG_RRQ
      Dispositivo → Cliente: CMD_ACK_DATA + registros (puede ser múltiples paquetes)
   
   c) Agregar usuario:
      Cliente → Dispositivo: CMD_USER_WRQ + datos de usuario
      Dispositivo → Cliente: CMD_ACK_OK
   
4. HABILITAR DISPOSITIVO:
   Cliente → Dispositivo: CMD_ENABLE_DEVICE
   Dispositivo → Cliente: CMD_ACK_OK
   
5. DESCONEXIÓN:
   Cliente → Dispositivo: CMD_EXIT
   Dispositivo → Cliente: CMD_ACK_OK

NOTAS IMPORTANTES:
- Todos los números se envían en formato little-endian
- Los strings se terminan con byte null (\\x00)
- El dispositivo puede enviar datos en múltiples paquetes
- Siempre verificar el checksum de los paquetes recibidos
- El session_id debe mantenerse durante toda la sesión
"""

# ============================================================================
# EJEMPLO DE USO (SOLO REFERENCIA)
# ============================================================================

if __name__ == "__main__":
    """
    Este código es solo para referencia del protocolo.
    Para uso real, utiliza la clase ZKTecoConnection que implementa
    todo esto usando la librería pyzk.
    """
    
    print("="*80)
    print("PROTOCOLO TCP DE ZKTECO - INFORMACIÓN DE REFERENCIA")
    print("="*80)
    
    print("\nComandos principales:")
    print(f"  CMD_CONNECT: {CMD_CONNECT}")
    print(f"  CMD_DISABLE_DEVICE: {CMD_DISABLE_DEVICE}")
    print(f"  CMD_ENABLE_DEVICE: {CMD_ENABLE_DEVICE}")
    print(f"  CMD_GET_TIME: {CMD_GET_TIME}")
    print(f"  CMD_ATTLOG_RRQ: {CMD_ATTLOG_RRQ}")
    print(f"  CMD_USER_WRQ: {CMD_USER_WRQ}")
    
    print("\nRespuestas del dispositivo:")
    print(f"  CMD_ACK_OK: {CMD_ACK_OK}")
    print(f"  CMD_ACK_ERROR: {CMD_ACK_ERROR}")
    print(f"  CMD_ACK_DATA: {CMD_ACK_DATA}")
    
    print("\nEjemplo de construcción de paquete:")
    packet = ZKPacket(CMD_CONNECT, session_id=0)
    packet_bytes = packet.build()
    print(f"  Paquete CMD_CONNECT: {packet_bytes.hex()}")
    
    print("\nEjemplo de codificación de tiempo:")
    now = datetime.now()
    encoded_time = encode_time(now)
    print(f"  Tiempo actual: {now}")
    print(f"  Codificado: {encoded_time.hex()}")
    
    print("\n" + "="*80)
    print("Para uso real, consulta zkteco_connection.py y ejemplo_uso.py")
    print("="*80)
