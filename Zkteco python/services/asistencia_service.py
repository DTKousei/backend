from datetime import date, datetime, timedelta, time
from sqlalchemy.orm import Session
from sqlalchemy import and_, extract, desc
from typing import List, Optional

from models.usuario import Usuario
from models.asistencia import Asistencia
from models.dispositivo import Dispositivo
from models.turnos import SegmentosHorario, AsignacionHorario, Feriados
from models.reportes import AsistenciaDiaria
from schemas.asistencia import AsistenciaFilter
from zkteco_connection import ZKTecoConnection
from config import settings
import requests

import logging

logger = logging.getLogger(__name__)

class AsistenciaService:
    """
    Servicio para gestión de registros de asistencia y cálculo de reportes
    """

    @staticmethod
    def obtener_asistencias(db: Session, filtros: AsistenciaFilter) -> List[Asistencia]:
        """Obtiene registros crudos de asistencia con filtros"""
        query = db.query(Asistencia)
        
        if filtros.uid:
            query = query.filter(Asistencia.uid == filtros.uid)
        if filtros.dispositivo_id:
            query = query.filter(Asistencia.dispositivo_id == filtros.dispositivo_id)
        if filtros.fecha_inicio:
            query = query.filter(Asistencia.timestamp >= filtros.fecha_inicio)
        if filtros.fecha_fin:
            query = query.filter(Asistencia.timestamp <= filtros.fecha_fin)
            
        return query.order_by(Asistencia.timestamp.desc()).offset(filtros.offset).limit(filtros.limit).all()

    @staticmethod
    def contar_asistencias(db: Session, filtros: AsistenciaFilter) -> int:
        """Cuenta registros totales con filtros"""
        query = db.query(Asistencia)
        if filtros.uid:
            query = query.filter(Asistencia.uid == filtros.uid)
        if filtros.dispositivo_id:
            query = query.filter(Asistencia.dispositivo_id == filtros.dispositivo_id)
        if filtros.fecha_inicio:
            query = query.filter(Asistencia.timestamp >= filtros.fecha_inicio)
        if filtros.fecha_fin:
            query = query.filter(Asistencia.timestamp <= filtros.fecha_fin)
        return query.count()

    @staticmethod
    def obtener_asistencias_tiempo_real(db: Session, dispositivo_id: int, ultimos_minutos: int) -> List[Asistencia]:
        """Obtiene asistencias recientes"""
        limite = datetime.now() - timedelta(minutes=ultimos_minutos)
        return db.query(Asistencia).filter(
            Asistencia.dispositivo_id == dispositivo_id,
            Asistencia.timestamp >= limite
        ).order_by(Asistencia.timestamp.desc()).all()

    @staticmethod
    def sincronizar_asistencias_hoy(db: Session, dispositivo_id: int):
        """Sincroniza SOLO asistencias de HOY desde el dispositivo"""
        dispositivo = db.query(Dispositivo).filter(Dispositivo.id == dispositivo_id).first()
        if not dispositivo:
            return {"success": False, "message": "Dispositivo no encontrado"}
            
        if not dispositivo.activo:
             return {"success": False, "message": "Dispositivo inactivo"}

        conn = ZKTecoConnection(dispositivo.ip_address, dispositivo.puerto, dispositivo.timeout, dispositivo.password)
        if not conn.conectar():
             return {"success": False, "message": "No se pudo conectar al dispositivo"}
        
        try:
            logs = conn.obtener_asistencias()
            nuevos = 0
            total_procesados = 0
            hoy = date.today()
            
            # Filtrar logs solo de hoy
            logs_hoy = [log for log in logs if log.timestamp.date() == hoy]
            
            logger.info(f"[DEBUG] Sincronizar Hoy: Total logs recuperados del dispositivo: {len(logs)}")
            logger.info(f"[DEBUG] Fecha hoy sistema: {hoy}")
            if logs:
                 logger.info(f"[DEBUG] Fecha primer log: {logs[0].timestamp} (Date: {logs[0].timestamp.date()})")
                 logger.info(f"[DEBUG] Fecha ultimo log: {logs[-1].timestamp}")
            logger.info(f"[DEBUG] Total logs para hoy: {len(logs_hoy)}")

            
            for log in logs_hoy:
                total_procesados += 1
                
                # FIX: Usar log.user_id (Badge Number) en lugar de log.uid (Indice interno)
                try:
                    real_uid = int(log.user_id)
                except (ValueError, TypeError):
                    logger.warning(f"Log ignorado: user_id no numerico '{log.user_id}'")
                    continue

                # Verificar si existe (uid + timestamp + dispositivo_id)
                exists = db.query(Asistencia).filter(
                    Asistencia.uid == real_uid,
                    Asistencia.timestamp == log.timestamp,
                    Asistencia.dispositivo_id == dispositivo_id
                ).first()
                
                if not exists:
                    # Verificar si el usuario existe en la BD por UID
                    # IMPORTANTE: El Usuario.uid en BD corresponde al Badge Number (user_id del dispositivo)
                    usuario_existe = db.query(Usuario).filter(Usuario.uid == real_uid).first()
                    
                    if usuario_existe:
                        nuevo_log = Asistencia(
                            uid=real_uid,
                            dispositivo_id=dispositivo_id,
                            timestamp=log.timestamp,
                            status=log.status,
                            punch=log.punch,
                            sincronizado=True,
                            fecha_sincronizacion=datetime.now()
                        )
                        db.add(nuevo_log)
                        nuevos += 1
            
            db.commit()
            return {
                "success": True, 
                "message": f"Sincronización de HOY completada ({hoy})", 
                "registros_nuevos": nuevos, 
                "registros_totales_hoy": len(logs_hoy), 
                "dispositivo_id": dispositivo_id
            }
        except Exception as e:
            db.rollback()
            return {"success": False, "message": str(e)}
        finally:
            conn.desconectar()

    @staticmethod
    def sincronizar_asistencias_desde_dispositivo(db: Session, dispositivo_id: int):
        """Sincroniza asistencias desde el dispositivo físico"""
        dispositivo = db.query(Dispositivo).filter(Dispositivo.id == dispositivo_id).first()
        if not dispositivo:
            return {"success": False, "message": "Dispositivo no encontrado"}
            
        if not dispositivo.activo:
             return {"success": False, "message": "Dispositivo inactivo"}

        conn = ZKTecoConnection(dispositivo.ip_address, dispositivo.puerto, dispositivo.timeout, dispositivo.password)
        if not conn.conectar():
             return {"success": False, "message": "No se pudo conectar al dispositivo"}
        
        try:
            logs = conn.obtener_asistencias()
            nuevos = 0
            total = len(logs)
            
            # Cache de usuarios conocidos para evitar queries repetitivos
            # Set de UIDs que sabemos que existen en la BD (o acabamos de crear)
            known_uids = set()
            existing_users = db.query(Usuario.uid).filter(Usuario.uid != None).all()
            for u in existing_users:
                known_uids.add(u.uid)
                
            for log in logs:
                if log.timestamp.year > 2050:
                    logger.warning(f"Log ignorado por fecha futura inválida: {log.timestamp} (UID: {log.uid})")
                    continue

                try:
                    # IMPLEMENTACION "DESDE CERO":
                    # Mapear log.user_id (string del dispositivo, ej "13") -> DB.uid (int, ej 13)
                    
                    try:
                        real_uid = int(log.user_id)
                    except (ValueError, TypeError):
                        logger.warning(f"Log ignorado: user_id no numerico '{log.user_id}' en registro {log.uid}")
                        continue
                        
                    # 1. Validación de Duplicados (Estricta: UID + Timestamp)
                    # Usamos real_uid para chequear si ya guardamos esta asistencia
                    exists = db.query(Asistencia).filter(
                        Asistencia.uid == real_uid,
                        Asistencia.timestamp == log.timestamp
                    ).first()
                    
                    if exists:
                        continue # Duplicado exacto

                    # 2. Verificar existencia del Usuario
                    # El usuario DEBE existir con ese UID (que debe coincidir con su user_id numérico)
                    if real_uid not in known_uids:
                        # Si no existe, lo ignoramos (UsuarioService debe encargarse primero)
                        # El usuario pidio eliminar logica fantasma.
                        # logger.warning(f"Asistencia ignorada: Usuario UID {real_uid} no existe en DB.")
                        continue 

                    # 3. Insertar Registro
                    nuevo_log = Asistencia(
                        uid=real_uid,
                        dispositivo_id=dispositivo_id,
                        timestamp=log.timestamp,
                        status=log.status,
                        punch=log.punch,
                        sincronizado=True,
                        fecha_sincronizacion=datetime.now()
                    )
                    db.add(nuevo_log)
                    nuevos += 1
                    
                    # Commit periódico
                    if nuevos % 100 == 0:
                        db.commit()
                        
                except Exception as e:
                    logger.error(f"Error procesando log {log.uid}: {e}")
                    continue
            
            db.commit() # Commit final
            
            return {
                "success": True, 
                "message": "Sincronización completada", 
                "registros_nuevos": nuevos, 
                "registros_totales": total, 
                "dispositivo_id": dispositivo_id
            }
        except Exception as e:
            db.rollback()
            return {"success": False, "message": str(e)}
        finally:
            conn.desconectar()

    @staticmethod
    def limpiar_asistencias_dispositivo(db: Session, dispositivo_id: int):
        """Limpia la memoria del dispositivo"""
        dispositivo = db.query(Dispositivo).filter(Dispositivo.id == dispositivo_id).first()
        if not dispositivo:
            return {"success": False, "message": "Dispositivo no encontrado"}
            
        conn = ZKTecoConnection(dispositivo.ip_address, dispositivo.puerto, dispositivo.timeout, dispositivo.password)
        if not conn.conectar():
             return {"success": False, "message": "No se pudo conectar al dispositivo"}

        try:
            if conn.limpiar_asistencias():
                return {"success": True, "message": "Registros eliminados del dispositivo"}
            else:
                return {"success": False, "message": "Error al eliminar registros"}
        finally:
            conn.desconectar()

    @staticmethod
    def registrar_manual(db: Session, datos: 'AsistenciaManualCreate') -> Asistencia:
        """
        Registra una asistencia manual con validaciones
        """
        from schemas.asistencia import TipoAsistencia
        from models.dispositivo import Dispositivo

        # 0. Verificar/Crear dispositivo manual (ID 999)
        dispositivo_manual = db.query(Dispositivo).filter(Dispositivo.id == 999).first()
        if not dispositivo_manual:
            try:
                dispositivo_manual = Dispositivo(
                    id=999,
                    nombre="Manual/Web",
                    ip_address="0.0.0.0",
                    puerto=0,
                    activo=True,
                    timeout=0
                )
                db.add(dispositivo_manual)
                db.commit()
            except Exception as e:
                db.rollback()
                # Si falla por unique constraint de IP u otro, intentamos buscarlo de nuevo o loguear
                logger.error(f"Error creando dispositivo manual: {e}")
                # Puede que otro request lo creara concurrentemente
                dispositivo_manual = db.query(Dispositivo).filter(Dispositivo.id == 999).first()
        
        # 1. Definir punch code
        punch_code = 0 if datos.tipo == TipoAsistencia.ENTRADA else 1
        
        # 2. Buscar último registro del día
        inicio_dia = datetime.combine(datos.fecha_hora.date(), time.min)
        fin_dia = datetime.combine(datos.fecha_hora.date(), time.max)
        
        # Necesitamos el UID del empleado para buscar asistencias
        empleado = db.query(Usuario).filter(Usuario.user_id == datos.empleado_id).first()
        if not empleado:
             raise ValueError("Empleado no encontrado")
             
        ultimo_registro = db.query(Asistencia).filter(
            Asistencia.uid == empleado.uid, # Usar UID
            Asistencia.timestamp >= inicio_dia,
            Asistencia.timestamp <= fin_dia
        ).order_by(Asistencia.timestamp.desc()).first()
        
        # 3. Validaciones
        if datos.tipo == TipoAsistencia.ENTRADA:
            # Validar que no tenga ya una entrada sin salida
            # Si el último registro es una Entrada (punch=0), error
            if ultimo_registro and ultimo_registro.punch == 0:
                raise ValueError("El empleado ya tiene una entrada registrada sin salida. Debe registrar la salida primero.")
                
        elif datos.tipo == TipoAsistencia.SALIDA:
            # Buscar la última entrada abierta y cerrarla
            # Si el último registro NO existe o es una Salida (punch=1), error
            if not ultimo_registro or ultimo_registro.punch == 1:
                raise ValueError("No se encontró una entrada abierta para cerrar. Debe registrar una entrada primero.")
        
        # 4. Crear registro
        registro = Asistencia(
            uid=empleado.uid, # Usar UID recuperado del usuario
            dispositivo_id=999, # ID reservado para manual/web
            timestamp=datos.fecha_hora,
            status=0,
            punch=punch_code,
            sincronizado=True,
            fecha_sincronizacion=datetime.now()
        )
        
        db.add(registro)
        db.commit()
        db.refresh(registro)
        logger.info(f"Asistencia manual registrada: {datos.tipo} - {datos.empleado_id}")
        
        return registro


    # ---------------------------------------------------------
    # NUEVA LÓGICA DE NEGOCIO: PROCESAMIENTO Y REPORTES
    # ---------------------------------------------------------

    @staticmethod
    def verificar_incidencia(user_id: str, fecha_proceso: date) -> tuple[bool, str]:
        """
        Consulta la API de incidencias para ver si el usuario tiene una justificación aprobada.
        Retorna (True, Codigo) si existe, o (False, None).
        """
        try:
            # Añadir filtro por empleado_id para ser mas eficiente y preciso
            url = f"{settings.INCIDENCIAS_API_URL}?empleado_id={user_id}"
            
            resp = requests.get(url, timeout=3)
            if resp.status_code != 200:
                logger.warning(f"Error consultando incidencias: {resp.status_code}")
                return False, None
            
            data = resp.json()
            incidencias = []
            
            # Manejar estructura paginada { data: [...], pagination: {...} } vs Lista directa [...]
            if isinstance(data, dict):
                incidencias = data.get('data', [])
            elif isinstance(data, list):
                incidencias = data
            
            dt_proceso = datetime.combine(fecha_proceso, time.min)
            
            for inc in incidencias:
                # Validar empleado (redundante si la API filtra, pero seguro)
                if str(inc.get('empleado_id')) != str(user_id):
                    continue
                    
                # Validar estado Aprobado
                estado_obj = inc.get('estado', {})
                if not estado_obj or estado_obj.get('nombre') != 'Aprobado':
                    continue
                
                # Validar fechas
                f_inicio_str = inc.get('fecha_inicio') 
                f_fin_str = inc.get('fecha_fin')
                
                if not f_inicio_str or not f_fin_str:
                    continue
                    
                # Parsear fechas (ISO format)
                try:
                    # Cortamos la Z si existe
                    dt_inicio = datetime.fromisoformat(f_inicio_str.replace('Z', '+00:00')).date()
                    dt_fin = datetime.fromisoformat(f_fin_str.replace('Z', '+00:00')).date()
                    
                    if dt_inicio <= fecha_proceso <= dt_fin:
                        # ENCONTRADA
                        tipo_obj = inc.get('tipo_incidencia', {})
                        codigo = tipo_obj.get('codigo', 'JUSTIFICADO')
                        logger.info(f"Justificación encontrada para {user_id} el {fecha_proceso}: {codigo}")
                        return True, codigo
                        
                except Exception as e_date:
                    logger.error(f"Error parseando fechas incidencia: {e_date}")
                    continue
                    
            return False, None
            
        except Exception as e:
            logger.error(f"Excepción verificando incidencias: {e}")
            return False, None

    @staticmethod
    def procesar_asistencia_dia(db: Session, user_id: str, fecha_proceso: date):
        """
        Procesa la asistencia de un usuario para una fecha específica.
        Calcula horas trabajadas, estado (presente, falta, tarde) basándose en su horario.
        """
        
        # 1. Obtener usuario (opcional, para validar existencia)
        usuario = db.query(Usuario).filter(Usuario.user_id == user_id).first()
        if not usuario:
            logger.warning(f"Usuario {user_id} no encontrado")
            return None
        
        logger.info(f"Procesando asistencia para Usuario: {user_id} (UID: {usuario.uid}), Fecha: {fecha_proceso}")

        # 2. Buscar asignación de horario vigente
        asignacion = db.query(AsignacionHorario).filter(
            AsignacionHorario.user_id == user_id,
            AsignacionHorario.fecha_inicio <= fecha_proceso,
            (AsignacionHorario.fecha_fin == None) | (AsignacionHorario.fecha_fin >= fecha_proceso)
        ).order_by(AsignacionHorario.fecha_inicio.desc()).first()

        es_feriado = db.query(Feriados).filter(Feriados.fecha == fecha_proceso).first()
        
        # Estado inicial del reporte
        reporte = db.query(AsistenciaDiaria).filter(
            AsistenciaDiaria.user_id == user_id,
            AsistenciaDiaria.fecha == fecha_proceso
        ).first()

        if not reporte:
            reporte = AsistenciaDiaria(
                user_id=user_id,
                fecha=fecha_proceso
            )
        
        # Reset valores cálculo
        reporte.horas_trabajadas = 0.0
        reporte.horas_esperadas = 0.0
        reporte.entrada_real = None
        reporte.salida_real = None
        reporte.es_justificado = False
        
        # Si es feriado
        if es_feriado:
            reporte.estado_asistencia = "FERIADO"
            reporte.es_justificado = True
        else:
            reporte.estado_asistencia = "FALTA" # Por defecto
        
        if not asignacion:
            logger.info(f"Usuario {user_id} NO tiene horario asignado para {fecha_proceso}")
            if not es_feriado:
                reporte.estado_asistencia = "SIN_HORARIO"
            db.add(reporte)
            db.commit()
            return reporte
        
        logger.info(f"Horario asignado encontrado: ID {asignacion.horario_id}")

        reporte.horario_id_snapshot = asignacion.horario_id
        
        # 3. Obtener segmentos del día (0=Lunes, 6=Domingo)
        dia_semana = fecha_proceso.weekday()
        segmentos = db.query(SegmentosHorario).filter(
            SegmentosHorario.horario_id == asignacion.horario_id,
            SegmentosHorario.dia_semana == dia_semana
        ).order_by(SegmentosHorario.hora_inicio).all()
        
        if not segmentos:
            logger.info(f"Horario {asignacion.horario_id} NO tiene segmentos para dia {dia_semana}")
            if not es_feriado:
                reporte.estado_asistencia = "DIA_LIBRE"
            db.add(reporte)
            db.commit()
            return reporte

        logger.info(f"Segmentos encontrados: {len(segmentos)}")

        # Buscar logs del día usando UID
        inicio_dia = datetime.combine(fecha_proceso, time.min)
        fin_dia = datetime.combine(fecha_proceso, time.max)
        
        # IMPORTANTE: Buscar por UID, no por user_id directamente en la tabla de asistencias
        logs = db.query(Asistencia).filter(
            Asistencia.uid == usuario.uid,
            Asistencia.timestamp >= inicio_dia,
            Asistencia.timestamp <= fin_dia
        ).order_by(Asistencia.timestamp).all()
        
        logger.info(f"Logs crudos encontrados para UID {usuario.uid} en fecha {fecha_proceso}: {len(logs)}")
        # for l in logs:
        #      logger.info(f"  -> Log: {l.timestamp} (Status: {l.status}, Punch: {l.punch})")
        
        logs_times = [log.timestamp.time() for log in logs]
        
        total_horas_trabajadas = 0.0
        total_horas_esperadas = 0.0
        llegada_tarde = False
        hubo_asistencia = False
        
        primer_ingreso = None
        ultima_salida = None

        used_indices = set()

        for segmento in segmentos:
            inicio_seg = segmento.hora_inicio
            fin_seg = segmento.hora_fin
            
            # Cálculo horas esperadas
            dummy_date = date(2000, 1, 1)
            dt_inicio = datetime.combine(dummy_date, inicio_seg)
            dt_fin = datetime.combine(dummy_date, fin_seg)
            duracion_horas = (dt_fin - dt_inicio).total_seconds() / 3600.0
            total_horas_esperadas += duracion_horas
            
            # --- Lógica de "Mejor Coincidencia" (Closest Match) ---
            
            # 1. Buscar MEJOR Entrada
            entrada_valida = None
            entrada_idx = -1
            min_diff_entrada = float('inf')
            
            inicio_min = inicio_seg.hour * 60 + inicio_seg.minute
            
            for i, t in enumerate(logs_times):
                if i in used_indices:
                    continue
                    
                t_min = t.hour * 60 + t.minute
                
                # Ventana: 2h antes hasta tolerancia
                if (inicio_min - 120) <= t_min <= (inicio_min + segmento.tolerancia_minutos + 60):
                    # Candidato válido, verificar si es el más cercano
                    diff = abs(t_min - inicio_min)
                    if diff < min_diff_entrada:
                        min_diff_entrada = diff
                        entrada_valida = t
                        entrada_idx = i
            
            # 2. Buscar MEJOR Salida
            salida_valida = None
            salida_idx = -1
            min_diff_salida = float('inf')
            
            fin_min = fin_seg.hour * 60 + fin_seg.minute
            
            if entrada_valida:
                for i, t in enumerate(logs_times):
                    if i in used_indices or i == entrada_idx:
                        continue
                        
                    # La salida debe ser posterior a la entrada seleccionada
                    # IMPORTANTE: Usamos índices o tiempos para asegurar orden
                    if i <= entrada_idx: 
                        continue
                        
                    t_min = t.hour * 60 + t.minute
                    
                    # Ventana salida: desde (inicio + 30m) hasta (fin + 4h)
                    if (inicio_min + 30) <= t_min <= (fin_min + 240):
                        # Candidato válido, verificar si es el más cercano a hora_fin
                        diff = abs(t_min - fin_min)
                        if diff < min_diff_salida:
                            min_diff_salida = diff
                            salida_valida = t
                            salida_idx = i
            
            # Logs de debug emparejamiento
            if entrada_valida:
                logger.info(f"  [Segmento {inicio_seg}-{fin_seg}] ENTRADA encontrada: {entrada_valida}")
            else:
                logger.info(f"  [Segmento {inicio_seg}-{fin_seg}] NO se encontró entrada válida en ventana {inicio_min-120} - {inicio_min + segmento.tolerancia_minutos + 60}")
                
            if salida_valida:
                logger.info(f"  [Segmento {inicio_seg}-{fin_seg}] SALIDA encontrada: {salida_valida}")
            
            if entrada_valida:
                used_indices.add(entrada_idx)
            
            if salida_valida:
                used_indices.add(salida_idx)
            
            if entrada_valida:
                hubo_asistencia = True
                if not primer_ingreso or entrada_valida < primer_ingreso:
                    primer_ingreso = entrada_valida
                
                t_ent_min = entrada_valida.hour * 60 + entrada_valida.minute
                inicio_seg_min = inicio_seg.hour * 60 + inicio_seg.minute
                if t_ent_min > (inicio_seg_min + segmento.tolerancia_minutos):
                    llegada_tarde = True
            
            if salida_valida:
                if not ultima_salida or salida_valida > ultima_salida:
                    ultima_salida = salida_valida
                    
                dt_ent = datetime.combine(dummy_date, entrada_valida)
                dt_sal = datetime.combine(dummy_date, salida_valida)
                horas_reales = (dt_sal - dt_ent).total_seconds() / 3600.0
                total_horas_trabajadas += horas_reales
                
        # -------------------------------------------------------------
        # LÓGICA DE ESTADO BASE (Basado solo en horas trabajadas)
        # -------------------------------------------------------------
        estado_base = "FALTA" # Default preliminar
        
        # Lógica de Estado en Tiempo Real vs Pasado
        ultimo_fin_seg = max([seg.hora_fin for seg in segmentos]) if segmentos else time(0,0)
        fecha_ahora = datetime.now()
        
        # Limite para marcar salida: Fin de turno + tolerancias (ej 4h)
        dt_fin_turno = datetime.combine(fecha_proceso, ultimo_fin_seg)
        dt_limite_salida = dt_fin_turno + timedelta(hours=2)
        
        es_dia_pasado_o_terminado = (fecha_proceso < fecha_ahora.date()) or (fecha_proceso == fecha_ahora.date() and fecha_ahora > dt_limite_salida)
        
        completo_horas = total_horas_trabajadas >= (total_horas_esperadas - 0.05)
        
        if completo_horas:
            # Horas completas -> PRESENTE o TARDE
            if llegada_tarde:
                estado_base = "TARDE"
            else:
                estado_base = "PRESENTE"
        else:
            # Horas incompletas (o 0 horas)
            if not es_dia_pasado_o_terminado:
                 # AUN ESTA EN HORARIO LABORAL (o dentro del limite)
                 # Si ya marco entrada, decimos PRESENTE/TARDE temporalmente
                 if primer_ingreso:
                    if llegada_tarde:
                        estado_base = "TARDE"
                    else:
                        estado_base = "PRESENTE"
                 # Si no ha marcado nada, sigue siendo FALTA (o S/M)
            else:
                 # DIA TERMINADO y no completó horas
                 estado_base = "FALTA"

        # -------------------------------------------------------------
        # LÓGICA DE PRIORIDAD FINAL (Requirements Usuario)
        # -------------------------------------------------------------
        # Prioridad:
        # 1. Si TRABAJÓ COMPLETO (PRESENTE/TARDE) -> Se queda ese estado (incluso si es feriado, es Feriado Trabajado implícito)
        # 2. Si es FERIADO y no trabajó completo -> FERIADO (Incluso si marcó entrada y se fue, o no vino)
        # 3. Si tiene INCIDENCIA y no trabajó completo -> INCIDENCIA
        # 4. FALTA
        
        tiene_justificacion, codigo_just = AsistenciaService.verificar_incidencia(user_id, fecha_proceso)

        if estado_base in ["PRESENTE", "TARDE"]:
            estado_final = estado_base
            # Caso especial: Si es feriado y trabajó, a veces quieren ver "FERIADO_TRABAJADO" o simplemente "PRESENTE"
            # El usuario dijo: "solo si el usuario tiene su estado presente no priorizar el feriado" -> PRESENTE gana.
        
        elif es_feriado:
             estado_final = "FERIADO"
             reporte.es_justificado = True
             
        elif tiene_justificacion:
             estado_final = codigo_just
             reporte.es_justificado = True
        
        else:
             estado_final = "FALTA"

        logger.info(f"  -> Estado Final: {estado_final} (Base: {estado_base}, Feriado: {bool(es_feriado)}, Incidencia: {tiene_justificacion})")

        reporte.horas_esperadas = total_horas_esperadas
        reporte.horas_trabajadas = round(total_horas_trabajadas, 2)
        reporte.estado_asistencia = estado_final
        reporte.entrada_real = primer_ingreso
        reporte.salida_real = ultima_salida
        
        db.add(reporte)
        db.commit()
        return reporte

    @staticmethod
    def calcular_rango_asistencia(db: Session, fecha_inicio: date, fecha_fin: date, user_id: str = None):
        """
        Procesa un rango de fechas.
        """
        usuarios = []
        if user_id:
            usuarios = db.query(Usuario).filter(Usuario.user_id == user_id).all()
        else:
            usuarios = db.query(Usuario).all() 
            
        delta = fecha_fin - fecha_inicio
        resultados = []
        
        for i in range(delta.days + 1):
            fecha = fecha_inicio + timedelta(days=i)
            for usu in usuarios:
                res = AsistenciaService.procesar_asistencia_dia(db, usu.user_id, fecha)
                if res:
                    resultados.append(res)
                    
        return resultados

    @staticmethod
    def obtener_reporte(db: Session, fecha_inicio: date, fecha_fin: date, user_id: Optional[str] = None) -> List[dict]:
        query = db.query(AsistenciaDiaria).filter(
            AsistenciaDiaria.fecha >= fecha_inicio,
            AsistenciaDiaria.fecha <= fecha_fin
        )
        if user_id:
            query = query.filter(AsistenciaDiaria.user_id == user_id)
        
        results = query.order_by(AsistenciaDiaria.fecha, AsistenciaDiaria.user_id).all()
        
        # Convertir a dict y agregar campos formateados
        reporte_final = []
        for r in results:
            item = {
                "id": r.id,
                "fecha": r.fecha,
                "user_id": r.user_id,
                "horario_id_snapshot": r.horario_id_snapshot,
                "horas_esperadas": r.horas_esperadas,
                "horas_trabajadas": r.horas_trabajadas,
                "estado_asistencia": r.estado_asistencia,
                "es_justificado": r.es_justificado,
                "entrada_real": r.entrada_real,
                "salida_real": r.salida_real,
            }
            
            # Helper para formato
            def fmt(h):
                if h is None: return "00:00"
                hours = int(h)
                minutes = int(round((h - hours) * 60))
                return f"{hours:02d}:{minutes:02d}"
                
            item["horas_esperadas_formato"] = fmt(r.horas_esperadas)
            item["horas_trabajadas_formato"] = fmt(r.horas_trabajadas)
            
            reporte_final.append(item)
            
        return reporte_final
