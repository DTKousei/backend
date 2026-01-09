"""
Modelo de Asistencia
Representa un registro de asistencia (marcación) de un usuario
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Index
from sqlalchemy.orm import relationship
from datetime import datetime
from models.database import Base


class Asistencia(Base):
    """
    Tabla de registros de asistencia
    """
    __tablename__ = "asistencias"
    
    # Campos principales
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    uid = Column(Integer, ForeignKey("usuarios.uid", ondelete="CASCADE", onupdate="CASCADE"), nullable=False, index=True, comment="UID del usuario (interno dispositivo)")
    
    # Relaciones
    dispositivo_id = Column(Integer, ForeignKey("dispositivos.id", ondelete="CASCADE"), nullable=False)
    # usuario_db_id eliminado, usamos user_id directo
    
    # Información del registro
    timestamp = Column(DateTime, nullable=False, index=True, comment="Fecha y hora de la marcación")
    status = Column(Integer, default=0, comment="Estado del registro")
    punch = Column(Integer, default=0, comment="Tipo de marcación")
    
    # Control de sincronización
    sincronizado = Column(Boolean, default=True, comment="Si fue sincronizado desde el dispositivo")
    fecha_sincronizacion = Column(DateTime, default=datetime.now, comment="Fecha de sincronización")
    
    # Timestamp de creación
    fecha_creacion = Column(DateTime, default=datetime.now, comment="Fecha de registro en BD")
    
    # Relaciones
    dispositivo = relationship("Dispositivo", back_populates="asistencias")
    usuario = relationship("Usuario", back_populates="asistencias")
    
    # Índices compuestos para búsquedas eficientes
    __table_args__ = (
        Index('idx_uid_timestamp', 'uid', 'timestamp'),
        Index('idx_dispositivo_timestamp', 'dispositivo_id', 'timestamp'),
        Index('idx_timestamp_dispositivo', 'timestamp', 'dispositivo_id'),
    )
    
    def __repr__(self):
        return f"<Asistencia(id={self.id}, uid={self.uid}, timestamp='{self.timestamp}')>"
    
    def to_dict(self):
        """Convierte el objeto a diccionario"""
        return {
            "id": self.id,
            "uid": self.uid,
            "dispositivo_id": self.dispositivo_id,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "status": self.status,
            "punch": self.punch,
            "sincronizado": self.sincronizado,
            "fecha_sincronizacion": self.fecha_sincronizacion.isoformat() if self.fecha_sincronizacion else None,
            "fecha_creacion": self.fecha_creacion.isoformat() if self.fecha_creacion else None,
        }
