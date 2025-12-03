"""
Modelo de Dispositivo ZKTeco
Representa un dispositivo de control de asistencia en la base de datos
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from models.database import Base


class Dispositivo(Base):
    """
    Tabla de dispositivos ZKTeco conectados al sistema
    """
    __tablename__ = "dispositivos"
    
    # Campos principales
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nombre = Column(String(100), nullable=False, comment="Nombre descriptivo del dispositivo")
    ip_address = Column(String(15), nullable=False, unique=True, comment="Dirección IP del dispositivo")
    puerto = Column(Integer, default=4370, comment="Puerto TCP del dispositivo")
    ubicacion = Column(String(200), comment="Ubicación física del dispositivo")
    
    # Información del dispositivo
    serial_number = Column(String(50), unique=True, comment="Número de serie del dispositivo")
    firmware_version = Column(String(50), comment="Versión del firmware")
    platform = Column(String(50), comment="Plataforma del dispositivo")
    device_name = Column(String(100), comment="Nombre del dispositivo en ZKTeco")
    mac_address = Column(String(17), comment="Dirección MAC")
    
    # Estado y configuración
    activo = Column(Boolean, default=True, comment="Si el dispositivo está activo")
    password = Column(Integer, default=0, comment="Contraseña del dispositivo")
    timeout = Column(Integer, default=5, comment="Timeout de conexión en segundos")
    
    # Timestamps
    fecha_creacion = Column(DateTime, default=datetime.now, comment="Fecha de registro")
    fecha_actualizacion = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="Última actualización")
    ultima_sincronizacion = Column(DateTime, comment="Última sincronización exitosa")
    
    # Relaciones
    usuarios = relationship("Usuario", back_populates="dispositivo", cascade="all, delete-orphan")
    asistencias = relationship("Asistencia", back_populates="dispositivo", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Dispositivo(id={self.id}, nombre='{self.nombre}', ip='{self.ip_address}')>"
    
    def to_dict(self):
        """Convierte el objeto a diccionario"""
        return {
            "id": self.id,
            "nombre": self.nombre,
            "ip_address": self.ip_address,
            "puerto": self.puerto,
            "ubicacion": self.ubicacion,
            "serial_number": self.serial_number,
            "firmware_version": self.firmware_version,
            "platform": self.platform,
            "device_name": self.device_name,
            "mac_address": self.mac_address,
            "activo": self.activo,
            "fecha_creacion": self.fecha_creacion.isoformat() if self.fecha_creacion else None,
            "fecha_actualizacion": self.fecha_actualizacion.isoformat() if self.fecha_actualizacion else None,
            "ultima_sincronizacion": self.ultima_sincronizacion.isoformat() if self.ultima_sincronizacion else None,
        }
