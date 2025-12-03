"""
Ejemplos de Uso del Sistema de Integración ZKTeco
===================================================

Este archivo contiene ejemplos prácticos de cómo usar todas las funcionalidades
del módulo zkteco_connection.py para interactuar con dispositivos ZKTeco.

Autor: Sistema de Control de Asistencia
Fecha: 2025-11-26
"""

from zkteco_connection import ZKTecoConnection, conectar_dispositivo
from datetime import datetime

# ============================================================================
# CONFIGURACIÓN INICIAL
# ============================================================================

# Configurar la dirección IP de tu dispositivo ZKTeco
# Cambia esta IP por la de tu dispositivo en la red LAN
IP_DISPOSITIVO = '192.168.1.201'

# Puerto TCP del dispositivo (por defecto es 4370)
PUERTO = 4370

# Timeout de conexión en segundos
TIMEOUT = 5


# ============================================================================
# EJEMPLO 1: PRUEBA DE CONEXIÓN BÁSICA
# ============================================================================

def ejemplo_prueba_conexion():
    """
    Ejemplo básico de cómo probar la conexión con el dispositivo.
    Este es el primer paso recomendado para verificar que el dispositivo
    está accesible en la red.
    """
    print("\n" + "="*80)
    print("EJEMPLO 1: PRUEBA DE CONEXIÓN")
    print("="*80)
    
    # Paso 1: Crear el objeto de conexión con la IP del dispositivo
    dispositivo = ZKTecoConnection(IP_DISPOSITIVO, PUERTO, TIMEOUT)
    
    # Paso 2: Ejecutar la prueba de conexión
    # Este método intentará conectarse y obtener información básica
    if dispositivo.test_conexion():
        print("\n✓ El dispositivo está accesible y funcionando correctamente")
    else:
        print("\n✗ No se pudo conectar al dispositivo")
        print("  Verifica:")
        print("  - Que la IP sea correcta")
        print("  - Que el dispositivo esté encendido")
        print("  - Que estén en la misma red")


# ============================================================================
# EJEMPLO 2: OBTENER INFORMACIÓN DEL DISPOSITIVO
# ============================================================================

def ejemplo_informacion_dispositivo():
    """
    Ejemplo de cómo obtener información detallada del dispositivo como:
    - Número de serie
    - Versión de firmware
    - Nombre del dispositivo
    - Dirección MAC
    - Hora actual del dispositivo
    """
    print("\n" + "="*80)
    print("EJEMPLO 2: INFORMACIÓN DEL DISPOSITIVO")
    print("="*80)
    
    # Paso 1: Crear y conectar al dispositivo
    dispositivo = ZKTecoConnection(IP_DISPOSITIVO, PUERTO)
    
    if not dispositivo.conectar():
        print("No se pudo conectar al dispositivo")
        return
    
    try:
        # Paso 2: Obtener información general del dispositivo
        print("\n--- Información General ---")
        info = dispositivo.obtener_informacion_dispositivo()
        dispositivo.mostrar_informacion_dispositivo(info)
        
        # Paso 3: Obtener la hora actual del dispositivo
        print("\n--- Hora del Dispositivo ---")
        hora = dispositivo.obtener_hora_dispositivo()
        if hora:
            print(f"Hora actual del dispositivo: {hora}")
            print(f"Hora del sistema: {datetime.now()}")
            
            # Calcular diferencia de tiempo
            diferencia = datetime.now() - hora
            print(f"Diferencia: {diferencia.total_seconds()} segundos")
    
    finally:
        # Paso 4: SIEMPRE desconectar al finalizar
        dispositivo.desconectar()


# ============================================================================
# EJEMPLO 3: GESTIÓN DE USUARIOS
# ============================================================================

def ejemplo_gestion_usuarios():
    """
    Ejemplo completo de gestión de usuarios:
    - Listar usuarios existentes
    - Agregar nuevos usuarios
    - Modificar usuarios existentes
    - Eliminar usuarios
    """
    print("\n" + "="*80)
    print("EJEMPLO 3: GESTIÓN DE USUARIOS")
    print("="*80)
    
    # Paso 1: Conectar al dispositivo
    dispositivo = ZKTecoConnection(IP_DISPOSITIVO, PUERTO)
    
    if not dispositivo.conectar():
        print("No se pudo conectar al dispositivo")
        return
    
    try:
        # Paso 2: Listar usuarios existentes
        print("\n--- Usuarios Actuales ---")
        usuarios = dispositivo.obtener_usuarios()
        dispositivo.mostrar_usuarios(usuarios)
        
        # Paso 3: Agregar un nuevo usuario
        print("\n--- Agregando Nuevo Usuario ---")
        # Parámetros:
        # - user_id: ID del usuario (puede ser número de empleado)
        # - name: Nombre completo del usuario
        # - privilege: 0 = usuario normal, 14 = administrador
        # - password: contraseña numérica (opcional)
        dispositivo.agregar_usuario(
            user_id='1001',
            name='Juan Pérez García',
            privilege=0,  # Usuario normal
            password='1234'
        )
        
        # Paso 4: Agregar otro usuario (administrador)
        print("\n--- Agregando Usuario Administrador ---")
        dispositivo.agregar_usuario(
            user_id='9999',
            name='Administrador Sistema',
            privilege=0,  # Administrador
            password='0000'
        )
        
        # Paso 5: Verificar que se agregaron
        print("\n--- Usuarios Después de Agregar ---")
        usuarios = dispositivo.obtener_usuarios()
        dispositivo.mostrar_usuarios(usuarios)
        
        # Paso 6: Modificar un usuario existente
        print("\n--- Modificando Usuario ---")
        # Cambiar el nombre del usuario 1001
        dispositivo.modificar_usuario(
            user_id='9999',
            name='Juan Carlos Pérez García',  # Nuevo nombre
            password='5678', 
            privilege=0 # Nueva contraseña
        )
        
        # Paso 7: Verificar la modificación
        print("\n--- Usuarios Después de Modificar ---")
        usuarios = dispositivo.obtener_usuarios()
        dispositivo.mostrar_usuarios(usuarios)
        
        # Paso 8: Eliminar un usuario
        print("\n--- Eliminando Usuario ---")
        # ADVERTENCIA: Esto eliminará permanentemente al usuario
        # y toda su información biométrica
        # Descomenta la siguiente línea para ejecutar
        # dispositivo.eliminar_usuario('1001')
        print("(Comentado por seguridad - descomenta para ejecutar)")
        
    finally:
        # Paso 9: Desconectar
        dispositivo.desconectar()


# ============================================================================
# EJEMPLO 4: OBTENER REGISTROS DE ASISTENCIA
# ============================================================================

def ejemplo_obtener_asistencias():
    """
    Ejemplo de cómo obtener y mostrar todos los registros de asistencia
    almacenados en el dispositivo.
    """
    print("\n" + "="*80)
    print("EJEMPLO 4: REGISTROS DE ASISTENCIA")
    print("="*80)
    
    # Paso 1: Conectar al dispositivo
    dispositivo = ZKTecoConnection(IP_DISPOSITIVO, PUERTO)
    
    if not dispositivo.conectar():
        print("No se pudo conectar al dispositivo")
        return
    
    try:
        # Paso 2: Obtener todos los registros de asistencia
        print("\n--- Obteniendo Registros de Asistencia ---")
        asistencias = dispositivo.obtener_asistencias()
        
        # Paso 3: Mostrar los registros en formato tabla
        dispositivo.mostrar_asistencias(asistencias)
        
        # Paso 4: Procesar los registros (ejemplo de análisis)
        if asistencias:
            print("\n--- Análisis de Registros ---")
            
            # Contar registros por usuario
            registros_por_usuario = {}
            for asistencia in asistencias:
                user_id = asistencia.user_id
                if user_id in registros_por_usuario:
                    registros_por_usuario[user_id] += 1
                else:
                    registros_por_usuario[user_id] = 1
            
            print("\nRegistros por usuario:")
            for user_id, cantidad in registros_por_usuario.items():
                print(f"  Usuario {user_id}: {cantidad} registros")
            
            # Obtener el registro más reciente
            registro_reciente = max(asistencias, key=lambda x: x.timestamp)
            print(f"\nÚltimo registro:")
            print(f"  Usuario: {registro_reciente.user_id}")
            print(f"  Fecha/Hora: {registro_reciente.timestamp}")
            print(f"  Estado: {registro_reciente.status}")
        
    finally:
        # Paso 5: Desconectar
        dispositivo.desconectar()


# ============================================================================
# EJEMPLO 5: OBTENER ASISTENCIAS EN TIEMPO REAL (MONITOREO CONTINUO)
# ============================================================================

def ejemplo_monitoreo_tiempo_real():
    """
    Ejemplo de cómo monitorear asistencias en tiempo real.
    Este método consulta periódicamente el dispositivo para detectar
    nuevos registros de asistencia.
    """
    print("\n" + "="*80)
    print("EJEMPLO 5: MONITOREO EN TIEMPO REAL")
    print("="*80)
    
    import time
    
    # Paso 1: Conectar al dispositivo
    dispositivo = ZKTecoConnection(IP_DISPOSITIVO, PUERTO)
    
    if not dispositivo.conectar():
        print("No se pudo conectar al dispositivo")
        return
    
    try:
        # Paso 2: Obtener registros iniciales para establecer baseline
        print("\n--- Obteniendo registros iniciales ---")
        asistencias_anteriores = dispositivo.obtener_asistencias()
        cantidad_anterior = len(asistencias_anteriores)
        print(f"Registros actuales: {cantidad_anterior}")
        
        print("\n--- Iniciando monitoreo (presiona Ctrl+C para detener) ---")
        print("Esperando nuevos registros...\n")
        
        # Paso 3: Loop de monitoreo
        while True:
            try:
                # Esperar 5 segundos entre consultas
                time.sleep(5)
                
                # Obtener registros actuales
                asistencias_actuales = dispositivo.obtener_asistencias()
                cantidad_actual = len(asistencias_actuales)
                
                # Paso 4: Detectar nuevos registros
                if cantidad_actual > cantidad_anterior:
                    nuevos_registros = cantidad_actual - cantidad_anterior
                    print(f"\n¡{nuevos_registros} nuevo(s) registro(s) detectado(s)!")
                    
                    # Mostrar solo los nuevos registros
                    for i in range(nuevos_registros):
                        registro = asistencias_actuales[-(i+1)]
                        print(f"  Usuario: {registro.user_id}")
                        print(f"  Hora: {registro.timestamp}")
                        print(f"  Estado: {registro.status}")
                        print("-" * 40)
                    
                    cantidad_anterior = cantidad_actual
                else:
                    # Mostrar punto para indicar que está monitoreando
                    print(".", end="", flush=True)
            
            except KeyboardInterrupt:
                # Permitir salir con Ctrl+C
                print("\n\nMonitoreo detenido por el usuario")
                break
    
    finally:
        # Paso 5: Desconectar
        dispositivo.desconectar()


# ============================================================================
# EJEMPLO 6: SINCRONIZAR HORA DEL DISPOSITIVO
# ============================================================================

def ejemplo_sincronizar_hora():
    """
    Ejemplo de cómo sincronizar la hora del dispositivo con la hora del sistema.
    Esto es importante para mantener registros precisos.
    """
    print("\n" + "="*80)
    print("EJEMPLO 6: SINCRONIZACIÓN DE HORA")
    print("="*80)
    
    # Paso 1: Conectar al dispositivo
    dispositivo = ZKTecoConnection(IP_DISPOSITIVO, PUERTO)
    
    if not dispositivo.conectar():
        print("No se pudo conectar al dispositivo")
        return
    
    try:
        # Paso 2: Obtener hora actual del dispositivo
        print("\n--- Hora Antes de Sincronizar ---")
        hora_dispositivo = dispositivo.obtener_hora_dispositivo()
        hora_sistema = datetime.now()
        
        print(f"Hora del dispositivo: {hora_dispositivo}")
        print(f"Hora del sistema: {hora_sistema}")
        
        if hora_dispositivo:
            diferencia = (hora_sistema - hora_dispositivo).total_seconds()
            print(f"Diferencia: {diferencia} segundos")
        
        # Paso 3: Sincronizar hora
        print("\n--- Sincronizando Hora ---")
        if dispositivo.establecer_hora_dispositivo(datetime.now()):
            print("Hora sincronizada exitosamente")
            
            # Paso 4: Verificar sincronización
            print("\n--- Hora Después de Sincronizar ---")
            hora_nueva = dispositivo.obtener_hora_dispositivo()
            print(f"Hora del dispositivo: {hora_nueva}")
            print(f"Hora del sistema: {datetime.now()}")
    
    finally:
        # Paso 5: Desconectar
        dispositivo.desconectar()


# ============================================================================
# EJEMPLO 7: LIMPIAR REGISTROS DE ASISTENCIA
# ============================================================================

def ejemplo_limpiar_asistencias():
    """
    Ejemplo de cómo limpiar todos los registros de asistencia del dispositivo.
    ¡ADVERTENCIA! Esta operación es IRREVERSIBLE.
    """
    print("\n" + "="*80)
    print("EJEMPLO 7: LIMPIAR REGISTROS DE ASISTENCIA")
    print("="*80)
    
    # Paso 1: Conectar al dispositivo
    dispositivo = ZKTecoConnection(IP_DISPOSITIVO, PUERTO)
    
    if not dispositivo.conectar():
        print("No se pudo conectar al dispositivo")
        return
    
    try:
        # Paso 2: Mostrar registros actuales
        print("\n--- Registros Actuales ---")
        asistencias = dispositivo.obtener_asistencias()
        print(f"Total de registros: {len(asistencias)}")
        
        # Paso 3: Confirmar antes de eliminar
        print("\n¡ADVERTENCIA! Esta operación eliminará TODOS los registros")
        print("Esta operación es IRREVERSIBLE")
        
        # Descomenta las siguientes líneas para ejecutar
        # confirmacion = input("¿Está seguro? (escriba 'SI' para confirmar): ")
        # if confirmacion == 'SI':
        #     if dispositivo.limpiar_asistencias():
        #         print("\nRegistros eliminados exitosamente")
        #         
        #         # Verificar que se eliminaron
        #         asistencias = dispositivo.obtener_asistencias()
        #         print(f"Registros restantes: {len(asistencias)}")
        # else:
        #     print("\nOperación cancelada")
        
        print("\n(Código comentado por seguridad - descomenta para ejecutar)")
    
    finally:
        # Paso 4: Desconectar
        dispositivo.desconectar()


# ============================================================================
# EJEMPLO 8: USO CON FUNCIÓN AUXILIAR
# ============================================================================

def ejemplo_funcion_auxiliar():
    """
    Ejemplo de cómo usar la función auxiliar conectar_dispositivo()
    para una conexión rápida.
    """
    print("\n" + "="*80)
    print("EJEMPLO 8: FUNCIÓN AUXILIAR DE CONEXIÓN")
    print("="*80)
    
    # Paso 1: Usar la función auxiliar para conectar rápidamente
    dispositivo = conectar_dispositivo(IP_DISPOSITIVO, PUERTO)
    
    if not dispositivo:
        print("No se pudo conectar al dispositivo")
        return
    
    try:
        # Paso 2: Usar el dispositivo conectado
        print("\n--- Información Rápida ---")
        
        # Obtener hora
        hora = dispositivo.obtener_hora_dispositivo()
        print(f"Hora: {hora}")
        
        # Contar usuarios
        usuarios = dispositivo.obtener_usuarios()
        print(f"Usuarios registrados: {len(usuarios)}")
        
        # Contar asistencias
        asistencias = dispositivo.obtener_asistencias()
        print(f"Registros de asistencia: {len(asistencias)}")
    
    finally:
        # Paso 3: Desconectar
        dispositivo.desconectar()


# ============================================================================
# FUNCIÓN PRINCIPAL - MENÚ DE EJEMPLOS
# ============================================================================

def menu_principal():
    """
    Menú interactivo para ejecutar los diferentes ejemplos.
    """
    while True:
        print("\n" + "="*80)
        print("SISTEMA DE INTEGRACIÓN ZKTECO - EJEMPLOS")
        print("="*80)
        print("\nSeleccione un ejemplo para ejecutar:")
        print("\n1. Prueba de Conexión")
        print("2. Información del Dispositivo")
        print("3. Gestión de Usuarios")
        print("4. Obtener Registros de Asistencia")
        print("5. Monitoreo en Tiempo Real")
        print("6. Sincronizar Hora")
        print("7. Limpiar Registros de Asistencia")
        print("8. Función Auxiliar de Conexión")
        print("\n0. Salir")
        
        try:
            opcion = input("\nOpción: ").strip()
            
            if opcion == '1':
                ejemplo_prueba_conexion()
            elif opcion == '2':
                ejemplo_informacion_dispositivo()
            elif opcion == '3':
                ejemplo_gestion_usuarios()
            elif opcion == '4':
                ejemplo_obtener_asistencias()
            elif opcion == '5':
                ejemplo_monitoreo_tiempo_real()
            elif opcion == '6':
                ejemplo_sincronizar_hora()
            elif opcion == '7':
                ejemplo_limpiar_asistencias()
            elif opcion == '8':
                ejemplo_funcion_auxiliar()
            elif opcion == '0':
                print("\n¡Hasta luego!")
                break
            else:
                print("\nOpción no válida. Intente nuevamente.")
            
            input("\nPresione Enter para continuar...")
            
        except KeyboardInterrupt:
            print("\n\n¡Hasta luego!")
            break
        except Exception as e:
            print(f"\nError: {str(e)}")
            input("\nPresione Enter para continuar...")


# ============================================================================
# PUNTO DE ENTRADA
# ============================================================================

if __name__ == "__main__":
    """
    Punto de entrada del programa.
    
    ANTES DE EJECUTAR:
    1. Asegúrate de haber instalado las dependencias:
       pip install -r requirements.txt
    
    2. Configura la IP de tu dispositivo en la variable IP_DISPOSITIVO
       al inicio de este archivo.
    
    3. Verifica que tu computadora y el dispositivo estén en la misma red LAN.
    
    4. Ejecuta este archivo:
       python ejemplo_uso.py
    """
    
    print("\n" + "="*80)
    print("BIENVENIDO AL SISTEMA DE INTEGRACIÓN ZKTECO")
    print("="*80)
    print(f"\nConfiguración actual:")
    print(f"  IP del dispositivo: {IP_DISPOSITIVO}")
    print(f"  Puerto: {PUERTO}")
    print(f"  Timeout: {TIMEOUT} segundos")
    print("\n" + "="*80)
    
    # Ejecutar el menú principal
    menu_principal()
