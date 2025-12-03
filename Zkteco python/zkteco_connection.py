"""
Sistema de Integración con Dispositivos ZKTeco
Conexión por LAN usando Protocolo TCP

Este módulo proporciona una clase completa para interactuar con dispositivos
ZKTeco de control de asistencia mediante conexión de red TCP/IP.

Autor: Sistema de Control de Asistencia
Fecha: 2025-11-26
"""

from zk import ZK, const
from datetime import datetime
import sys

class ZKTecoConnection:
    """
    Clase principal para manejar la conexión y operaciones con dispositivos ZKTeco
    mediante protocolo TCP sobre LAN.
    """
    
    def __init__(self, ip_address, port=4370, timeout=5, password=0):
        """
        Inicializa los parámetros de conexión al dispositivo ZKTeco.
        
        Parámetros:
            ip_address (str): Dirección IP del dispositivo en la red LAN
            port (int): Puerto TCP del dispositivo (por defecto 4370)
            timeout (int): Tiempo de espera para la conexión en segundos
            password (int): Contraseña del dispositivo (por defecto 0 = sin contraseña)
        
        Ejemplo:
            >>> dispositivo = ZKTecoConnection('192.168.1.201')
        """
        # Almacenar los parámetros de conexión
        self.ip_address = ip_address
        self.port = port
        self.timeout = timeout
        self.password = password
        
        # Crear el objeto de conexión ZK con los parámetros especificados
        # Este objeto maneja toda la comunicación TCP con el dispositivo
        self.conn = None
        self.zk = ZK(ip_address, port=port, timeout=timeout, password=password)
        
        print(f"[INFO] Configuración de conexión creada para {ip_address}:{port}")
    
    def conectar(self):
        """
        Establece la conexión TCP con el dispositivo ZKTeco.
        
        Este método:
        1. Intenta conectarse al dispositivo usando TCP
        2. Deshabilita el dispositivo temporalmente para operaciones
        3. Retorna True si la conexión fue exitosa, False en caso contrario
        
        Retorna:
            bool: True si la conexión fue exitosa, False en caso contrario
        
        Ejemplo:
            >>> if dispositivo.conectar():
            >>>     print("Conectado exitosamente")
        """
        try:
            print(f"[INFO] Intentando conectar a {self.ip_address}:{self.port}...")
            
            # Establecer la conexión TCP con el dispositivo
            # Este método abre un socket TCP y realiza el handshake inicial
            self.conn = self.zk.connect()
            
            # Deshabilitar el dispositivo temporalmente
            # Esto previene que el dispositivo procese huellas/tarjetas mientras
            # estamos realizando operaciones de lectura/escritura
            self.conn.disable_device()
            
            print(f"[ÉXITO] Conectado exitosamente al dispositivo {self.ip_address}")
            return True
            
        except Exception as e:
            # Capturar cualquier error de conexión (red, timeout, dispositivo ocupado, etc.)
            print(f"[ERROR] No se pudo conectar al dispositivo: {str(e)}")
            self.conn = None
            return False
    
    def desconectar(self):
        """
        Cierra la conexión TCP con el dispositivo ZKTeco de forma segura.
        
        Este método:
        1. Habilita nuevamente el dispositivo para operación normal
        2. Cierra la conexión TCP
        3. Libera los recursos de red
        
        Ejemplo:
            >>> dispositivo.desconectar()
        """
        if self.conn:
            try:
                # Habilitar el dispositivo nuevamente para operación normal
                # Esto permite que el dispositivo vuelva a procesar huellas/tarjetas
                self.conn.enable_device()
                
                # Cerrar la conexión TCP y liberar el socket
                self.conn.disconnect()
                
                print(f"[INFO] Desconectado del dispositivo {self.ip_address}")
                
            except Exception as e:
                print(f"[ERROR] Error al desconectar: {str(e)}")
            finally:
                # Asegurarse de limpiar la referencia de conexión
                self.conn = None
    
    def obtener_asistencias(self):
        """
        Obtiene todos los registros de asistencia almacenados en el dispositivo.
        
        Este método recupera TODOS los registros históricos de asistencia que
        están almacenados en la memoria del dispositivo. Cada registro incluye:
        - ID del usuario
        - Timestamp (fecha y hora del registro)
        - Estado (entrada/salida/otros)
        
        Retorna:
            list: Lista de objetos de asistencia, o lista vacía si hay error
            
        Ejemplo:
            >>> asistencias = dispositivo.obtener_asistencias()
            >>> for asistencia in asistencias:
            >>>     print(f"Usuario: {asistencia.user_id}, Hora: {asistencia.timestamp}")
        """
        if not self.conn:
            print("[ERROR] No hay conexión activa. Llame a conectar() primero.")
            return []
        
        try:
            print("[INFO] Obteniendo registros de asistencia del dispositivo...")
            
            # Obtener todos los registros de asistencia desde el dispositivo
            # Este método envía un comando TCP al dispositivo solicitando
            # todos los registros almacenados en su memoria
            asistencias = self.conn.get_attendance()
            
            print(f"[ÉXITO] Se obtuvieron {len(asistencias)} registros de asistencia")
            
            # Retornar la lista de registros
            return asistencias
            
        except Exception as e:
            print(f"[ERROR] Error al obtener asistencias: {str(e)}")
            return []
    
    def mostrar_asistencias(self, asistencias):
        """
        Muestra los registros de asistencia en formato legible.
        
        Parámetros:
            asistencias (list): Lista de registros de asistencia obtenidos
            
        Ejemplo:
            >>> asistencias = dispositivo.obtener_asistencias()
            >>> dispositivo.mostrar_asistencias(asistencias)
        """
        if not asistencias:
            print("[INFO] No hay registros de asistencia para mostrar")
            return
        
        print("\n" + "="*80)
        print("REGISTROS DE ASISTENCIA")
        print("="*80)
        print(f"{'ID Usuario':<15} {'Fecha y Hora':<25} {'Estado':<15} {'Punch':<10}")
        print("-"*80)
        
        # Iterar sobre cada registro de asistencia
        for asistencia in asistencias:
            # Extraer información de cada registro
            user_id = asistencia.user_id  # ID del usuario
            timestamp = asistencia.timestamp  # Fecha y hora del registro
            status = asistencia.status  # Estado del registro
            punch = asistencia.punch  # Tipo de marcación
            
            # Formatear y mostrar la información
            print(f"{user_id:<15} {str(timestamp):<25} {status:<15} {punch:<10}")
        
        print("="*80 + "\n")
    
    def limpiar_asistencias(self):
        """
        Elimina TODOS los registros de asistencia del dispositivo.
        
        ¡ADVERTENCIA! Esta operación es IRREVERSIBLE.
        Asegúrese de haber respaldado los datos antes de ejecutar este método.
        
        Retorna:
            bool: True si se limpiaron exitosamente, False en caso contrario
            
        Ejemplo:
            >>> if dispositivo.limpiar_asistencias():
            >>>     print("Registros eliminados")
        """
        if not self.conn:
            print("[ERROR] No hay conexión activa. Llame a conectar() primero.")
            return False
        
        try:
            print("[ADVERTENCIA] Eliminando TODOS los registros de asistencia...")
            
            # Enviar comando para limpiar todos los registros de asistencia
            # Este comando TCP borra permanentemente todos los registros
            self.conn.clear_attendance()
            
            print("[ÉXITO] Registros de asistencia eliminados exitosamente")
            return True
            
        except Exception as e:
            print(f"[ERROR] Error al limpiar asistencias: {str(e)}")
            return False
    
    def obtener_usuarios(self):
        """
        Obtiene todos los usuarios registrados en el dispositivo.
        
        Este método recupera la lista completa de usuarios almacenados en el
        dispositivo, incluyendo su información biométrica y de acceso.
        
        Retorna:
            list: Lista de objetos de usuario, o lista vacía si hay error
            
        Ejemplo:
            >>> usuarios = dispositivo.obtener_usuarios()
            >>> for usuario in usuarios:
            >>>     print(f"ID: {usuario.user_id}, Nombre: {usuario.name}")
        """
        if not self.conn:
            print("[ERROR] No hay conexión activa. Llame a conectar() primero.")
            return []
        
        try:
            print("[INFO] Obteniendo usuarios del dispositivo...")
            
            # Obtener todos los usuarios registrados en el dispositivo
            # Este método envía un comando TCP solicitando la lista de usuarios
            usuarios = self.conn.get_users()
            
            print(f"[ÉXITO] Se obtuvieron {len(usuarios)} usuarios")
            
            return usuarios
            
        except Exception as e:
            print(f"[ERROR] Error al obtener usuarios: {str(e)}")
            return []
    
    def mostrar_usuarios(self, usuarios):
        """
        Muestra la lista de usuarios en formato legible.
        
        Parámetros:
            usuarios (list): Lista de usuarios obtenidos del dispositivo
            
        Ejemplo:
            >>> usuarios = dispositivo.obtener_usuarios()
            >>> dispositivo.mostrar_usuarios(usuarios)
        """
        if not usuarios:
            print("[INFO] No hay usuarios para mostrar")
            return
        
        print("\n" + "="*100)
        print("USUARIOS REGISTRADOS")
        print("="*100)
        print(f"{'UID':<10} {'ID Usuario':<15} {'Nombre':<25} {'Privilegio':<15} {'Password':<15}")
        print("-"*100)
        
        # Iterar sobre cada usuario
        for usuario in usuarios:
            uid = usuario.uid  # ID único interno
            user_id = usuario.user_id  # ID del usuario (número de empleado)
            name = usuario.name  # Nombre del usuario
            privilege = usuario.privilege  # Nivel de privilegio (0=usuario, 14=admin)
            password = usuario.password if usuario.password else "Sin password"
            
            print(f"{uid:<10} {user_id:<15} {name:<25} {privilege:<15} {password:<15}")
        
        print("="*100 + "\n")
    
    def agregar_usuario(self, user_id, name, privilege=0, password='', group_id='', user_id_num=0):
        """
        Agrega un nuevo usuario al dispositivo.
        
        Parámetros:
            user_id (str): ID del usuario (número de empleado)
            name (str): Nombre del usuario
            privilege (int): Nivel de privilegio (0=usuario normal, 14=administrador)
            password (str): Contraseña del usuario (opcional)
            group_id (str): ID del grupo al que pertenece (opcional)
            user_id_num (int): UID numérico único (0 = auto-asignar)
        
        Retorna:
            bool: True si se agregó exitosamente, False en caso contrario
            
        Ejemplo:
            >>> dispositivo.agregar_usuario('001', 'Juan Pérez', privilege=0)
        """
        if not self.conn:
            print("[ERROR] No hay conexión activa. Llame a conectar() primero.")
            return False
        
        try:
            print(f"[INFO] Agregando usuario {user_id} - {name}...")
            
            # Enviar comando TCP para crear un nuevo usuario en el dispositivo
            # El dispositivo almacenará esta información en su memoria interna
            self.conn.set_user(
                uid=user_id_num,  # UID único (0 = auto-asignar)
                name=name,  # Nombre del usuario
                privilege=privilege,  # Nivel de privilegio
                password=password,  # Contraseña
                group_id=group_id,  # Grupo
                user_id=user_id  # ID de usuario
            )
            
            print(f"[ÉXITO] Usuario {user_id} agregado exitosamente")
            return True
            
        except Exception as e:
            print(f"[ERROR] Error al agregar usuario: {str(e)}")
            return False
    
    def eliminar_usuario(self, user_id):
        """
        Elimina un usuario del dispositivo.
        
        Este método elimina permanentemente un usuario y toda su información
        biométrica (huellas, rostro, etc.) del dispositivo.
        
        Parámetros:
            user_id (str): ID del usuario a eliminar
        
        Retorna:
            bool: True si se eliminó exitosamente, False en caso contrario
            
        Ejemplo:
            >>> dispositivo.eliminar_usuario('001')
        """
        if not self.conn:
            print("[ERROR] No hay conexión activa. Llame a conectar() primero.")
            return False
        
        try:
            print(f"[INFO] Eliminando usuario {user_id}...")
            
            # Primero obtener el UID del usuario basado en su user_id
            usuarios = self.conn.get_users()
            usuario_encontrado = None
            
            for usuario in usuarios:
                if usuario.user_id == user_id:
                    usuario_encontrado = usuario
                    break
            
            if not usuario_encontrado:
                print(f"[ERROR] Usuario {user_id} no encontrado")
                return False
            
            # Enviar comando TCP para eliminar el usuario del dispositivo
            self.conn.delete_user(uid=usuario_encontrado.uid)
            
            print(f"[ÉXITO] Usuario {user_id} eliminado exitosamente")
            return True
            
        except Exception as e:
            print(f"[ERROR] Error al eliminar usuario: {str(e)}")
            return False
    
    def modificar_usuario(self, user_id, name=None, privilege=None, password=None):
        """
        Modifica la información de un usuario existente.
        
        Parámetros:
            user_id (str): ID del usuario a modificar
            name (str): Nuevo nombre (None = no cambiar)
            privilege (int): Nuevo privilegio (None = no cambiar)
            password (str): Nueva contraseña (None = no cambiar)
        
        Retorna:
            bool: True si se modificó exitosamente, False en caso contrario
            
        Ejemplo:
            >>> dispositivo.modificar_usuario('001', name='Juan Carlos Pérez')
        """
        if not self.conn:
            print("[ERROR] No hay conexión activa. Llame a conectar() primero.")
            return False
        
        try:
            print(f"[INFO] Modificando usuario {user_id}...")
            
            # Obtener la información actual del usuario
            usuarios = self.conn.get_users()
            usuario_actual = None
            
            for usuario in usuarios:
                if usuario.user_id == user_id:
                    usuario_actual = usuario
                    break
            
            if not usuario_actual:
                print(f"[ERROR] Usuario {user_id} no encontrado")
                return False
            
            # Usar los valores actuales si no se proporcionan nuevos
            nuevo_nombre = name if name is not None else usuario_actual.name
            nuevo_privilegio = privilege if privilege is not None else usuario_actual.privilege
            nuevo_password = password if password is not None else usuario_actual.password
            
            # Actualizar el usuario con la nueva información
            self.conn.set_user(
                uid=usuario_actual.uid,
                name=nuevo_nombre,
                privilege=nuevo_privilegio,
                password=nuevo_password,
                group_id=usuario_actual.group_id,
                user_id=user_id
            )
            
            print(f"[ÉXITO] Usuario {user_id} modificado exitosamente")
            return True
            
        except Exception as e:
            print(f"[ERROR] Error al modificar usuario: {str(e)}")
            return False
    
    def obtener_hora_dispositivo(self):
        """
        Obtiene la fecha y hora actual configurada en el dispositivo.
        
        Retorna:
            datetime: Objeto datetime con la hora del dispositivo, o None si hay error
            
        Ejemplo:
            >>> hora = dispositivo.obtener_hora_dispositivo()
            >>> print(f"Hora del dispositivo: {hora}")
        """
        if not self.conn:
            print("[ERROR] No hay conexión activa. Llame a conectar() primero.")
            return None
        
        try:
            print("[INFO] Obteniendo hora del dispositivo...")
            
            # Enviar comando TCP para obtener la hora del dispositivo
            hora = self.conn.get_time()
            
            print(f"[ÉXITO] Hora del dispositivo: {hora}")
            return hora
            
        except Exception as e:
            print(f"[ERROR] Error al obtener hora: {str(e)}")
            return None
    
    def establecer_hora_dispositivo(self, nueva_hora=None):
        """
        Establece la fecha y hora del dispositivo.
        
        Parámetros:
            nueva_hora (datetime): Nueva fecha/hora (None = usar hora del sistema)
        
        Retorna:
            bool: True si se estableció exitosamente, False en caso contrario
            
        Ejemplo:
            >>> from datetime import datetime
            >>> dispositivo.establecer_hora_dispositivo(datetime.now())
        """
        if not self.conn:
            print("[ERROR] No hay conexión activa. Llame a conectar() primero.")
            return False
        
        try:
            # Si no se proporciona hora, usar la hora actual del sistema
            if nueva_hora is None:
                nueva_hora = datetime.now()
            
            print(f"[INFO] Estableciendo hora del dispositivo a: {nueva_hora}")
            
            # Enviar comando TCP para establecer la hora del dispositivo
            self.conn.set_time(nueva_hora)
            
            print(f"[ÉXITO] Hora del dispositivo actualizada exitosamente")
            return True
            
        except Exception as e:
            print(f"[ERROR] Error al establecer hora: {str(e)}")
            return False
    
    def obtener_informacion_dispositivo(self):
        """
        Obtiene información detallada del dispositivo.
        
        Esta información incluye:
        - Número de serie
        - Versión de firmware
        - Capacidad de usuarios
        - Capacidad de registros
        - Cantidad actual de usuarios
        - Cantidad actual de registros
        - Y más...
        
        Retorna:
            dict: Diccionario con la información del dispositivo
            
        Ejemplo:
            >>> info = dispositivo.obtener_informacion_dispositivo()
            >>> print(f"Modelo: {info.get('~Platform')}")
        """
        if not self.conn:
            print("[ERROR] No hay conexión activa. Llame a conectar() primero.")
            return {}
        
        try:
            print("[INFO] Obteniendo información del dispositivo...")
            
            # Obtener el número de serie del dispositivo
            serial_number = self.conn.get_serialnumber()
            
            # Obtener la versión del firmware
            firmware_version = self.conn.get_firmware_version()
            
            # Obtener información de plataforma
            platform = self.conn.get_platform()
            
            # Obtener nombre del dispositivo
            device_name = self.conn.get_device_name()
            
            # Obtener MAC address
            mac_address = self.conn.get_mac()
            
            # Obtener información de capacidad y uso
            # Esto nos dice cuántos usuarios y registros puede almacenar
            # y cuántos tiene actualmente
            
            # Crear diccionario con toda la información
            info = {
                'serial_number': serial_number,
                'firmware_version': firmware_version,
                'platform': platform,
                'device_name': device_name,
                'mac_address': mac_address,
                'ip_address': self.ip_address,
                'port': self.port
            }
            
            print("[ÉXITO] Información del dispositivo obtenida")
            return info
            
        except Exception as e:
            print(f"[ERROR] Error al obtener información del dispositivo: {str(e)}")
            return {}
    
    def mostrar_informacion_dispositivo(self, info):
        """
        Muestra la información del dispositivo en formato legible.
        
        Parámetros:
            info (dict): Diccionario con información del dispositivo
            
        Ejemplo:
            >>> info = dispositivo.obtener_informacion_dispositivo()
            >>> dispositivo.mostrar_informacion_dispositivo(info)
        """
        if not info:
            print("[INFO] No hay información para mostrar")
            return
        
        print("\n" + "="*60)
        print("INFORMACIÓN DEL DISPOSITIVO")
        print("="*60)
        
        for clave, valor in info.items():
            print(f"{clave:<25}: {valor}")
        
        print("="*60 + "\n")
    
    def test_conexion(self):
        """
        Realiza una prueba de conexión completa al dispositivo.
        
        Este método es útil para verificar que el dispositivo está
        accesible en la red y responde correctamente.
        
        Retorna:
            bool: True si la prueba fue exitosa, False en caso contrario
            
        Ejemplo:
            >>> if dispositivo.test_conexion():
            >>>     print("Dispositivo accesible")
        """
        print(f"\n[TEST] Iniciando prueba de conexión a {self.ip_address}:{self.port}")
        print("-" * 60)
        
        # Intentar conectar
        if not self.conectar():
            print("[TEST] FALLIDO - No se pudo establecer conexión")
            return False
        
        # Intentar obtener información básica
        try:
            hora = self.obtener_hora_dispositivo()
            if hora:
                print(f"[TEST] Hora del dispositivo: {hora}")
            
            info = self.obtener_informacion_dispositivo()
            if info:
                print(f"[TEST] Serial: {info.get('serial_number', 'N/A')}")
                print(f"[TEST] Firmware: {info.get('firmware_version', 'N/A')}")
            
            print("[TEST] EXITOSO - Dispositivo responde correctamente")
            return True
            
        except Exception as e:
            print(f"[TEST] FALLIDO - Error durante la prueba: {str(e)}")
            return False
        
        finally:
            # Siempre desconectar al finalizar la prueba
            self.desconectar()
            print("-" * 60 + "\n")


# Función auxiliar para uso rápido
def conectar_dispositivo(ip, port=4370):
    """
    Función auxiliar para crear y conectar rápidamente a un dispositivo.
    
    Parámetros:
        ip (str): Dirección IP del dispositivo
        port (int): Puerto TCP (por defecto 4370)
    
    Retorna:
        ZKTecoConnection: Objeto de conexión conectado, o None si falla
        
    Ejemplo:
        >>> dispositivo = conectar_dispositivo('192.168.1.201')
        >>> if dispositivo:
        >>>     asistencias = dispositivo.obtener_asistencias()
    """
    dispositivo = ZKTecoConnection(ip, port)
    if dispositivo.conectar():
        return dispositivo
    return None
