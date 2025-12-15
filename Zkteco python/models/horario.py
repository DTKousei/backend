"""
Modelo de Horario
Representa un horario de trabajo configurado en el sistema
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime
from datetime import datetime
from models.database import Base


class Horario(Base):
    """
    Tabla de horarios de trabajo
    """
    __tablename__ = "horarios"
    
    # Campos principales
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nombre = Column(String(100), nullable=False, comment="Nombre del horario")
    descripcion = Column(String(255), comment="Descripción del horario")
    
    # Configuración de días
    # Se ha movido la lógica a SegmentosHorario en models/turnos.py

    
    # Estado
    activo = Column(Boolean, default=True, comment="Si el horario está activo")
    
    # Timestamps
    fecha_creacion = Column(DateTime, default=datetime.now, comment="Fecha de creación")
    fecha_actualizacion = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="Última actualización")
    
    def __repr__(self):
        return f"<Horario(id={self.id}, nombre='{self.nombre}')>"
    
    def to_dict(self):
        """Convierte el objeto a diccionario"""
        return {
            "id": self.id,
            "nombre": self.nombre,
            "descripcion": self.descripcion,
            "activo": self.activo,
            "fecha_creacion": self.fecha_creacion.isoformat() if self.fecha_creacion else None,
            "fecha_actualizacion": self.fecha_actualizacion.isoformat() if self.fecha_actualizacion else None,
        }
