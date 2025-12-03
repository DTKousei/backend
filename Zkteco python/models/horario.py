"""
Modelo de Horario
Representa un horario de trabajo configurado en el sistema
"""

from sqlalchemy import Column, Integer, String, Time, Boolean, DateTime, JSON
from datetime import datetime, time
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
    
    # Horarios
    hora_entrada = Column(Time, nullable=False, comment="Hora de entrada")
    hora_salida = Column(Time, nullable=False, comment="Hora de salida")
    
    # Configuración de días
    # Almacenado como JSON: ["lunes", "martes", "miercoles", "jueves", "viernes"]
    dias_semana = Column(JSON, comment="Días de la semana que aplica este horario")
    
    # Tolerancias (en minutos)
    tolerancia_entrada = Column(Integer, default=0, comment="Minutos de tolerancia para entrada")
    tolerancia_salida = Column(Integer, default=0, comment="Minutos de tolerancia para salida")
    
    # Estado
    activo = Column(Boolean, default=True, comment="Si el horario está activo")
    
    # Timestamps
    fecha_creacion = Column(DateTime, default=datetime.now, comment="Fecha de creación")
    fecha_actualizacion = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="Última actualización")
    
    def __repr__(self):
        return f"<Horario(id={self.id}, nombre='{self.nombre}', entrada={self.hora_entrada}, salida={self.hora_salida})>"
    
    def to_dict(self):
        """Convierte el objeto a diccionario"""
        return {
            "id": self.id,
            "nombre": self.nombre,
            "descripcion": self.descripcion,
            "hora_entrada": self.hora_entrada.isoformat() if self.hora_entrada else None,
            "hora_salida": self.hora_salida.isoformat() if self.hora_salida else None,
            "dias_semana": self.dias_semana,
            "tolerancia_entrada": self.tolerancia_entrada,
            "tolerancia_salida": self.tolerancia_salida,
            "activo": self.activo,
            "fecha_creacion": self.fecha_creacion.isoformat() if self.fecha_creacion else None,
            "fecha_actualizacion": self.fecha_actualizacion.isoformat() if self.fecha_actualizacion else None,
        }
