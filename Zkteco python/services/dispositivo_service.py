"""
Servicio de Dispositivos
Lógica de negocio para gestión de dispositivos ZKTeco
"""

from sqlalchemy.orm import Session
from models.dispositivo import Dispositivo
from schemas.dispositivo import DispositivoCreate, DispositivoUpdate, DispositivoInfo
from zkteco_connection import ZKTecoConnection
from datetime import datetime
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)


class DispositivoService:
    """Servicio para gestión de dispositivos"""
    
    @staticmethod
    def crear_dispositivo(db: Session, dispositivo: DispositivoCreate) -> Dispositivo:
        """
        Crea un nuevo dispositivo en la base de datos
        """
        db_dispositivo = Dispositivo(
            nombre=dispositivo.nombre,
            ip_address=dispositivo.ip_address,
            puerto=dispositivo.puerto,
            ubicacion=dispositivo.ubicacion,
            password=dispositivo.password,
            timeout=dispositivo.timeout,
            activo=dispositivo.activo
        )
        
        db.add(db_dispositivo)
        db.commit()
        db.refresh(db_dispositivo)
        
        logger.info(f"Dispositivo creado: {db_dispositivo.nombre} ({db_dispositivo.ip_address})")
        return db_dispositivo
    
    @staticmethod
    def obtener_dispositivo(db: Session, dispositivo_id: int) -> Optional[Dispositivo]:
        """
        Obtiene un dispositivo por su ID
        """
        return db.query(Dispositivo).filter(Dispositivo.id == dispositivo_id).first()
    
    @staticmethod
    def obtener_dispositivos(db: Session, skip: int = 0, limit: int = 100, activo: Optional[bool] = None) -> List[Dispositivo]:
        """
        Obtiene lista de dispositivos con paginación
        """
        query = db.query(Dispositivo)
        
        if activo is not None:
            query = query.filter(Dispositivo.activo == activo)
        
        return query.offset(skip).limit(limit).all()
    
    @staticmethod
    def actualizar_dispositivo(db: Session, dispositivo_id: int, dispositivo_update: DispositivoUpdate) -> Optional[Dispositivo]:
        """
        Actualiza un dispositivo existente
        """
        db_dispositivo = DispositivoService.obtener_dispositivo(db, dispositivo_id)
        
        if not db_dispositivo:
            return None
        
        # Actualizar solo los campos proporcionados
        update_data = dispositivo_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_dispositivo, field, value)
        
        db_dispositivo.fecha_actualizacion = datetime.now()
        db.commit()
        db.refresh(db_dispositivo)
        
        logger.info(f"Dispositivo actualizado: {db_dispositivo.id}")
        return db_dispositivo
    
    @staticmethod
    def eliminar_dispositivo(db: Session, dispositivo_id: int) -> bool:
        """
        Elimina un dispositivo
        """
        db_dispositivo = DispositivoService.obtener_dispositivo(db, dispositivo_id)
        
        if not db_dispositivo:
            return False
        
        db.delete(db_dispositivo)
        db.commit()
        
        logger.info(f"Dispositivo eliminado: {dispositivo_id}")
        return True
    
    @staticmethod
    def test_conexion(db: Session, dispositivo_id: int) -> dict:
        """
        Prueba la conexión con un dispositivo ZKTeco
        """
        db_dispositivo = DispositivoService.obtener_dispositivo(db, dispositivo_id)
        
        if not db_dispositivo:
            return {
                "success": False,
                "message": "Dispositivo no encontrado",
                "info": None
            }
        
        try:
            # Crear conexión ZKTeco
            zk = ZKTecoConnection(
                ip_address=db_dispositivo.ip_address,
                port=db_dispositivo.puerto,
                timeout=db_dispositivo.timeout,
                password=db_dispositivo.password
            )
            
            # Intentar conectar
            if not zk.conectar():
                return {
                    "success": False,
                    "message": "No se pudo conectar al dispositivo",
                    "info": None
                }
            
            try:
                # Obtener información del dispositivo
                info = zk.obtener_informacion_dispositivo()
                hora = zk.obtener_hora_dispositivo()
                
                # Actualizar información en la base de datos
                db_dispositivo.serial_number = info.get('serial_number')
                db_dispositivo.firmware_version = info.get('firmware_version')
                db_dispositivo.platform = info.get('platform')
                db_dispositivo.device_name = info.get('device_name')
                db_dispositivo.mac_address = info.get('mac_address')
                db_dispositivo.ultima_sincronizacion = datetime.now()
                
                db.commit()
                
                return {
                    "success": True,
                    "message": "Conexión exitosa",
                    "info": DispositivoInfo(
                        serial_number=info.get('serial_number'),
                        firmware_version=info.get('firmware_version'),
                        platform=info.get('platform'),
                        device_name=info.get('device_name'),
                        mac_address=info.get('mac_address'),
                        ip_address=db_dispositivo.ip_address,
                        puerto=db_dispositivo.puerto,
                        hora_dispositivo=hora
                    )
                }
            
            finally:
                zk.desconectar()
        
        except Exception as e:
            logger.error(f"Error al probar conexión: {str(e)}")
            return {
                "success": False,
                "message": f"Error: {str(e)}",
                "info": None
            }
    
    @staticmethod
    def obtener_informacion_dispositivo(db: Session, dispositivo_id: int) -> Optional[dict]:
        """
        Obtiene información detallada del dispositivo desde ZKTeco
        """
        db_dispositivo = DispositivoService.obtener_dispositivo(db, dispositivo_id)
        
        if not db_dispositivo:
            return None
        
        try:
            zk = ZKTecoConnection(
                ip_address=db_dispositivo.ip_address,
                port=db_dispositivo.puerto,
                timeout=db_dispositivo.timeout,
                password=db_dispositivo.password
            )
            
            if not zk.conectar():
                return None
            
            try:
                info = zk.obtener_informacion_dispositivo()
                hora = zk.obtener_hora_dispositivo()
                info['hora_dispositivo'] = hora
                # Asegurar campos requeridos por el schema
                info['puerto'] = db_dispositivo.puerto
                if 'ip_address' not in info:
                    info['ip_address'] = db_dispositivo.ip_address
                return info
            
            finally:
                zk.desconectar()
        
        except Exception as e:
            logger.error(f"Error al obtener información: {str(e)}")
            return None
