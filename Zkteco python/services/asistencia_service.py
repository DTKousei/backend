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
        
        if filtros.user_id:
            query = query.filter(Asistencia.user_id == filtros.user_id)
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
        if filtros.user_id:
            query = query.filter(Asistencia.user_id == filtros.user_id)
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
            
            for log in logs:
                # Verificar si existe (user_id + timestamp + dispositivo_id)
                exists = db.query(Asistencia).filter(
                    Asistencia.user_id == log.user_id,
                    Asistencia.timestamp == log.timestamp,
                    Asistencia.dispositivo_id == dispositivo_id
                ).first()
                
                if not exists:
                    # Verificar si el usuario existe en la BD para respetar FK
                    usuario_existe = db.query(Usuario).filter(Usuario.user_id == log.user_id).first()
                    
                    if usuario_existe:
                        nuevo_log = Asistencia(
                            user_id=log.user_id,
                            dispositivo_id=dispositivo_id,
                            # usuario_db_id removed
                            timestamp=log.timestamp,
                            status=log.status,
                            punch=log.punch,
                            sincronizado=True,
                            fecha_sincronizacion=datetime.now()
                        )
                        db.add(nuevo_log)
                        nuevos += 1
                    else:
                        logger.warning(f"Log ignorado: Usuario {log.user_id} no existe en BD")
            
            db.commit()
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
        
        ultimo_registro = db.query(Asistencia).filter(
            Asistencia.user_id == datos.empleado_id,
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
            user_id=datos.empleado_id,
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
            if not es_feriado:
                reporte.estado_asistencia = "SIN_HORARIO"
            db.add(reporte)
            db.commit()
            return reporte

        reporte.horario_id_snapshot = asignacion.horario_id
        
        # 3. Obtener segmentos del día (0=Lunes, 6=Domingo)
        dia_semana = fecha_proceso.weekday()
        segmentos = db.query(SegmentosHorario).filter(
            SegmentosHorario.horario_id == asignacion.horario_id,
            SegmentosHorario.dia_semana == dia_semana
        ).order_by(SegmentosHorario.hora_inicio).all()
        
        if not segmentos:
            if not es_feriado:
                reporte.estado_asistencia = "DIA_LIBRE"
            db.add(reporte)
            db.commit()
            return reporte

        # Buscar logs del día
        inicio_dia = datetime.combine(fecha_proceso, time.min)
        fin_dia = datetime.combine(fecha_proceso, time.max)
        
        logs = db.query(Asistencia).filter(
            Asistencia.user_id == user_id,
            Asistencia.timestamp >= inicio_dia,
            Asistencia.timestamp <= fin_dia
        ).order_by(Asistencia.timestamp).all()
        
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
                
        # Estado final
        if es_feriado:
            estado_final = "FERIADO"
            if hubo_asistencia:
                 estado_final = "FERIADO_TRABAJADO"
        elif not hubo_asistencia:
            estado_final = "FALTA"
        else:
            if llegada_tarde:
                estado_final = "TARDE"
            else:
                estado_final = "PRESENTE"
            
            if total_horas_trabajadas < (total_horas_esperadas * 0.5):
                estado_final = "INCOMPLETO"

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
    def obtener_reporte(db: Session, fecha_inicio: date, fecha_fin: date, user_id: Optional[str] = None) -> List[AsistenciaDiaria]:
        query = db.query(AsistenciaDiaria).filter(
            AsistenciaDiaria.fecha >= fecha_inicio,
            AsistenciaDiaria.fecha <= fecha_fin
        )
        if user_id:
            query = query.filter(AsistenciaDiaria.user_id == user_id)
        return query.order_by(AsistenciaDiaria.fecha, AsistenciaDiaria.user_id).all()
