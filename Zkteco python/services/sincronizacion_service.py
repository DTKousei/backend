"""
Servicio de Sincronización
Lógica para sincronización de hora y datos con dispositivos
"""

from sqlalchemy.orm import Session
from models.dispositivo import Dispositivo
from zkteco_connection import ZKTecoConnection
from datetime import datetime
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class SincronizacionService:
    """Servicio para sincronización con dispositivos"""
    
    @staticmethod
    def sincronizar_hora_dispositivo(db: Session, dispositivo_id: int, nueva_hora: Optional[datetime] = None) -> dict:
        """
        Sincroniza la hora del dispositivo con la hora del sistema o una hora específica
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
                # Obtener hora actual del dispositivo
                hora_anterior = zk.obtener_hora_dispositivo()
                
                # Establecer nueva hora (usar hora del sistema si no se proporciona)
                if nueva_hora is None:
                    nueva_hora = datetime.now()
                
                if zk.establecer_hora_dispositivo(nueva_hora):
                    # Verificar la nueva hora
                    hora_nueva = zk.obtener_hora_dispositivo()
                    
                    return {
                        "success": True,
                        "message": "Hora sincronizada exitosamente",
                        "hora_anterior": hora_anterior.isoformat() if hora_anterior else None,
                        "hora_nueva": hora_nueva.isoformat() if hora_nueva else None,
                        "hora_sistema": nueva_hora.isoformat()
                    }
                else:
                    return {
                        "success": False,
                        "message": "Error al establecer la hora del dispositivo"
                    }
            
            finally:
                zk.desconectar()
        
        except Exception as e:
            logger.error(f"Error al sincronizar hora: {str(e)}")
            return {
                "success": False,
                "message": f"Error: {str(e)}"
            }
    
    @staticmethod
    def obtener_estado_sincronizacion(db: Session) -> dict:
        """
        Obtiene el estado de sincronización de todos los dispositivos
        """
        dispositivos = db.query(Dispositivo).filter(Dispositivo.activo == True).all()
        
        estado = {
            "total_dispositivos": len(dispositivos),
            "dispositivos": []
        }
        
        for dispositivo in dispositivos:
            info_dispositivo = {
                "id": dispositivo.id,
                "nombre": dispositivo.nombre,
                "ip_address": dispositivo.ip_address,
                "ultima_sincronizacion": dispositivo.ultima_sincronizacion.isoformat() if dispositivo.ultima_sincronizacion else None,
                "activo": dispositivo.activo
            }
            
            # Calcular tiempo desde última sincronización
            if dispositivo.ultima_sincronizacion:
                tiempo_desde_sync = datetime.now() - dispositivo.ultima_sincronizacion
                info_dispositivo["minutos_desde_sync"] = int(tiempo_desde_sync.total_seconds() / 60)
            else:
                info_dispositivo["minutos_desde_sync"] = None
            
            estado["dispositivos"].append(info_dispositivo)
        
        return estado
