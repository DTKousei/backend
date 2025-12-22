"""
Servicio de Horarios
Lógica de negocio para gestión de horarios
"""

from sqlalchemy.orm import Session
from models.horario import Horario
from models.turnos import SegmentosHorario, AsignacionHorario, Feriados
from schemas.horario import HorarioCreate, HorarioUpdate, SegmentoHorarioCreate, AsignacionHorarioCreate, SegmentoHorarioBulkCreate, FeriadoCreate
from datetime import datetime
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)


class HorarioService:
    """Servicio para gestión de horarios"""
    
    def crear_horario(db: Session, horario: HorarioCreate) -> Horario:
        """
        Crea un nuevo horario
        """
        db_horario = Horario(
            nombre=horario.nombre,
            descripcion=horario.descripcion,
            activo=horario.activo
        )
        
        db.add(db_horario)
        db.commit()
        db.refresh(db_horario)
        
        logger.info(f"Horario creado: {db_horario.nombre}")
        return db_horario
        
    # Segmentos
    @staticmethod
    def crear_segmento(db: Session, segmento: SegmentoHorarioCreate) -> SegmentosHorario:
        db_segmento = SegmentosHorario(**segmento.model_dump())
        db.add(db_segmento)
        db.commit()
        db.refresh(db_segmento)
        return db_segmento

    @staticmethod
    def crear_segmentos_bulk(db: Session, bulk_data: SegmentoHorarioBulkCreate) -> List[SegmentosHorario]:
        nuevos_segmentos = []
        for dia in bulk_data.dias_semana:
            if not (0 <= dia <= 6):
                 continue 
                 
            seg = SegmentosHorario(
                horario_id=bulk_data.horario_id,
                dia_semana=dia,
                hora_inicio=bulk_data.hora_inicio,
                hora_fin=bulk_data.hora_fin,
                tolerancia_minutos=bulk_data.tolerancia_minutos,
                orden_turno=bulk_data.orden_turno
            )
            db.add(seg)
            nuevos_segmentos.append(seg)
        db.commit()
        for s in nuevos_segmentos:
            db.refresh(s)
        return nuevos_segmentos


    @staticmethod
    def obtener_segmentos(db: Session, horario_id: int) -> List[SegmentosHorario]:
        return db.query(SegmentosHorario).filter(SegmentosHorario.horario_id == horario_id).order_by(SegmentosHorario.dia_semana, SegmentosHorario.hora_inicio).all()

    @staticmethod
    def eliminar_segmento(db: Session, segmento_id: int) -> bool:
        seg = db.query(SegmentosHorario).filter(SegmentosHorario.id == segmento_id).first()
        if not seg:
            return False
        db.delete(seg)
        db.commit()
        return True

    # Asignaciones
    @staticmethod
    def asignar_horario(db: Session, asignacion: AsignacionHorarioCreate) -> AsignacionHorario:
        db_asignacion = AsignacionHorario(**asignacion.model_dump())
        db.add(db_asignacion)
        db.commit()
        db.refresh(db_asignacion)
        return db_asignacion

    @staticmethod
    def obtener_asignaciones_por_usuario(db: Session, user_id: str) -> List[AsignacionHorario]:
        return db.query(AsignacionHorario).filter(AsignacionHorario.user_id == user_id).all()


    
    @staticmethod
    def obtener_horario(db: Session, horario_id: int) -> Optional[Horario]:
        """
        Obtiene un horario por su ID
        """
        return db.query(Horario).filter(Horario.id == horario_id).first()
    
    @staticmethod
    def obtener_horarios(db: Session, activo: Optional[bool] = None, skip: int = 0, limit: int = 100) -> List[Horario]:
        """
        Obtiene lista de horarios con paginación
        """
        query = db.query(Horario)
        
        if activo is not None:
            query = query.filter(Horario.activo == activo)
        
        return query.offset(skip).limit(limit).all()
    
    @staticmethod
    def actualizar_horario(db: Session, horario_id: int, horario_update: HorarioUpdate) -> Optional[Horario]:
        """
        Actualiza un horario existente
        """
        db_horario = HorarioService.obtener_horario(db, horario_id)
        
        if not db_horario:
            return None
        
        # Actualizar solo los campos proporcionados
        update_data = horario_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_horario, field, value)
        
        db_horario.fecha_actualizacion = datetime.now()
        db.commit()
        db.refresh(db_horario)
        
        logger.info(f"Horario actualizado: {db_horario.id}")
        return db_horario
    
    @staticmethod
    def eliminar_horario(db: Session, horario_id: int) -> bool:
        """
        Elimina un horario
        """
        db_horario = HorarioService.obtener_horario(db, horario_id)
        
        if not db_horario:
            return False
        
        db.delete(db_horario)
        db.commit()
        
        logger.info(f"Horario eliminado: {horario_id}")
        return True

    # Feriados
    @staticmethod
    def crear_feriado(db: Session, feriado: FeriadoCreate) -> Feriados:
        db_feriado = Feriados(**feriado.model_dump())
        db.add(db_feriado)
        db.commit()
        db.refresh(db_feriado)
        return db_feriado

    @staticmethod
    def obtener_feriados(db: Session, skip: int = 0, limit: int = 100) -> List[Feriados]:
        return db.query(Feriados).offset(skip).limit(limit).all()

    @staticmethod
    def eliminar_feriado(db: Session, feriado_id: int) -> bool:
        db_feriado = db.query(Feriados).filter(Feriados.id == feriado_id).first()
        if not db_feriado:
            return False
        db.delete(db_feriado)
        db.commit()
        return True
