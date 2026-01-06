from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Text, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from config.database import Base

class TipoReporte(Base):
    """
    Tabla para especificar el tipo de reporte (e.g., Asistencia General, Tardanzas, etc.)
    """
    __tablename__ = "tipos_reporte"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), unique=True, index=True) # e.g., 'Asistencia General'
    descripcion = Column(Text, nullable=True)
    activo = Column(Boolean, default=True)

    reportes = relationship("ReporteGenerado", back_populates="tipo_reporte")

class FormatoReporte(Base):
    """
    Tabla para especificar el formato del documento (PDF, EXCEL, etc.)
    """
    __tablename__ = "formatos_reporte"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(50), unique=True, index=True)   # e.g., 'PDF', 'EXCEL'
    extension = Column(String(10), nullable=False)         # e.g., '.pdf', '.xlsx'
    mime_type = Column(String(100), nullable=True)         # e.g., 'application/pdf'

    reportes = relationship("ReporteGenerado", back_populates="formato")

class ReporteGenerado(Base):
    """
    Tabla para registrar el historial de reportes generados.
    """
    __tablename__ = "reportes_generados"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, index=True)  # ID del usuario que generó el reporte (referencia externa)
    
    tipo_reporte_id = Column(Integer, ForeignKey("tipos_reporte.id"))
    tipo_reporte = relationship("TipoReporte", back_populates="reportes")

    formato_id = Column(Integer, ForeignKey("formatos_reporte.id"))
    formato = relationship("FormatoReporte", back_populates="reportes")

    nombre_archivo = Column(String(255), nullable=False)
    ruta_archivo = Column(String(500), nullable=False)     # Ruta absoluta o relativa donde se guarda
    fecha_generacion = Column(DateTime, default=datetime.now)
    
    # Metadata adicional opcional (filtros usados, rango de fechas, etc.)
    area = Column(String(100), nullable=True) # Nombre del departamento/área
    parametros_usados = Column(JSON, nullable=True) 

    def __repr__(self):
        return f"<ReporteGenerado(id={self.id}, nombre='{self.nombre_archivo}')>"
