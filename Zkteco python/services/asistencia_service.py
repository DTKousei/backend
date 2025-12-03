"""
Servicio de Asistencias
Lógica de negocio para gestión de registros de asistencia
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from models.asistencia import Asistencia
from models.dispositivo import Dispositivo
from models.usuario import Usuario
from schemas.asistencia import AsistenciaFilter
from zkteco_connection import ZKTecoConnection
from datetime import datetime
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)


class AsistenciaService:
    """Servicio para gestión de asistencias"""
    
    @staticmethod
    def obtener_asistencias(db: Session, filtros: AsistenciaFilter) -> List[Asistencia]:
        """
        Obtiene asistencias con filtros
        """
        query = db.query(Asistencia)
        
        # Aplicar filtros
        if filtros.user_id:
            query = query.filter(Asistencia.user_id == filtros.user_id)
        
        if filtros.dispositivo_id:
            query = query.filter(Asistencia.dispositivo_id == filtros.dispositivo_id)
        
        if filtros.fecha_inicio:
            query = query.filter(Asistencia.timestamp >= filtros.fecha_inicio)
        
        if filtros.fecha_fin:
            query = query.filter(Asistencia.timestamp <= filtros.fecha_fin)
        
        # Ordenar por timestamp descendente (más recientes primero)
        query = query.order_by(Asistencia.timestamp.desc())
        
        # Aplicar paginación
        return query.offset(filtros.offset).limit(filtros.limit).all()
    
    @staticmethod
    def sincronizar_asistencias_desde_dispositivo(db: Session, dispositivo_id: int) -> dict:
        """
        Sincroniza asistencias desde el dispositivo ZKTeco a la BD
        """
        dispositivo = db.query(Dispositivo).filter(Dispositivo.id == dispositivo_id).first()
        
        if not dispositivo:
            return {
                "success": False,
                "message": "Dispositivo no encontrado",
                "registros_nuevos": 0,
                "registros_totales": 0,
                "dispositivo_id": dispositivo_id
            }
        
        try:
            zk = ZKTecoConnection(
                ip_address=dispositivo.ip_address,
                port=dispositivo.puerto,
                timeout=dispositivo.timeout,
                password=dispositivo.password
            )
            
            if not zk.conectar():
                return {
                    "success": False,
                    "message": "No se pudo conectar al dispositivo",
                    "registros_nuevos": 0,
                    "registros_totales": 0,
                    "dispositivo_id": dispositivo_id
                }
            
            try:
                asistencias_zk = zk.obtener_asistencias()
                registros_nuevos = 0
                
                for asistencia_zk in asistencias_zk:
                    # Verificar si el registro ya existe
                    existe = db.query(Asistencia).filter(
                        and_(
                            Asistencia.user_id == asistencia_zk.user_id,
                            Asistencia.dispositivo_id == dispositivo_id,
                            Asistencia.timestamp == asistencia_zk.timestamp
                        )
                    ).first()
                    
                    if not existe:
                        # Buscar el usuario en la BD
                        usuario = db.query(Usuario).filter(
                            and_(
                                Usuario.user_id == asistencia_zk.user_id,
                                Usuario.dispositivo_id == dispositivo_id
                            )
                        ).first()
                        
                        # Crear nuevo registro
                        db_asistencia = Asistencia(
                            user_id=asistencia_zk.user_id,
                            dispositivo_id=dispositivo_id,
                            usuario_db_id=usuario.id if usuario else None,
                            timestamp=asistencia_zk.timestamp,
                            status=asistencia_zk.status,
                            punch=asistencia_zk.punch,
                            sincronizado=True,
                            fecha_sincronizacion=datetime.now()
                        )
                        
                        db.add(db_asistencia)
                        registros_nuevos += 1
                
                db.commit()
                
                # Actualizar última sincronización del dispositivo
                dispositivo.ultima_sincronizacion = datetime.now()
                db.commit()
                
                return {
                    "success": True,
                    "message": f"Sincronización exitosa. {registros_nuevos} registros nuevos",
                    "registros_nuevos": registros_nuevos,
                    "registros_totales": len(asistencias_zk),
                    "dispositivo_id": dispositivo_id
                }
            
            finally:
                zk.desconectar()
        
        except Exception as e:
            logger.error(f"Error al sincronizar asistencias: {str(e)}")
            return {
                "success": False,
                "message": f"Error: {str(e)}",
                "registros_nuevos": 0,
                "registros_totales": 0,
                "dispositivo_id": dispositivo_id
            }
    
    @staticmethod
    def obtener_asistencias_tiempo_real(db: Session, dispositivo_id: int, ultimos_minutos: int = 5) -> List[Asistencia]:
        """
        Obtiene asistencias en tiempo real (últimos N minutos)
        """
        from datetime import timedelta
        
        tiempo_limite = datetime.now() - timedelta(minutes=ultimos_minutos)
        
        return db.query(Asistencia).filter(
            and_(
                Asistencia.dispositivo_id == dispositivo_id,
                Asistencia.timestamp >= tiempo_limite
            )
        ).order_by(Asistencia.timestamp.desc()).all()
    
    @staticmethod
    def limpiar_asistencias_dispositivo(db: Session, dispositivo_id: int) -> dict:
        """
        Limpia todas las asistencias del dispositivo ZKTeco
        ¡ADVERTENCIA! Esta operación es irreversible
        """
        dispositivo = db.query(Dispositivo).filter(Dispositivo.id == dispositivo_id).first()
        
        if not dispositivo:
            return {
                "success": False,
                "message": "Dispositivo no encontrado"
            }
        
        try:
            zk = ZKTecoConnection(
                ip_address=dispositivo.ip_address,
                port=dispositivo.puerto,
                timeout=dispositivo.timeout,
                password=dispositivo.password
            )
            
            if not zk.conectar():
                return {
                    "success": False,
                    "message": "No se pudo conectar al dispositivo"
                }
            
            try:
                if zk.limpiar_asistencias():
                    return {
                        "success": True,
                        "message": "Asistencias eliminadas del dispositivo exitosamente"
                    }
                else:
                    return {
                        "success": False,
                        "message": "Error al limpiar asistencias del dispositivo"
                    }
            
            finally:
                zk.desconectar()
        
        except Exception as e:
            logger.error(f"Error al limpiar asistencias: {str(e)}")
            return {
                "success": False,
                "message": f"Error: {str(e)}"
            }
    
    @staticmethod
    def contar_asistencias(db: Session, filtros: AsistenciaFilter) -> int:
        """
        Cuenta el total de asistencias que coinciden con los filtros
        """
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
