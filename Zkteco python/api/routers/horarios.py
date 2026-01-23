"""
Router de Horarios
Endpoints para gestión de horarios de trabajo
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from models.database import get_db
from schemas.horario import (
    HorarioCreate,
    HorarioUpdate,
    HorarioResponse
)
from services.horario_service import HorarioService

router = APIRouter(prefix="/api/horarios", tags=["Horarios"])


@router.post("/", response_model=HorarioResponse, status_code=status.HTTP_201_CREATED)
def crear_horario(horario: HorarioCreate, db: Session = Depends(get_db)):
    """
    Crea un nuevo horario de trabajo
    """
    return HorarioService.crear_horario(db, horario)


@router.get("/", response_model=List[HorarioResponse])
def listar_horarios(
    activo: Optional[bool] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Lista todos los horarios con paginación
    """
    return HorarioService.obtener_horarios(db, activo=activo, skip=skip, limit=limit)


@router.get("/{horario_id}", response_model=HorarioResponse)
def obtener_horario(horario_id: int, db: Session = Depends(get_db)):
    """
    Obtiene un horario específico por ID
    """
    horario = HorarioService.obtener_horario(db, horario_id)
    if not horario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Horario {horario_id} no encontrado"
        )
    return horario


@router.put("/{horario_id}", response_model=HorarioResponse)
def actualizar_horario(
    horario_id: int,
    horario_update: HorarioUpdate,
    db: Session = Depends(get_db)
):
    """
    Actualiza un horario existente
    """
    horario = HorarioService.actualizar_horario(db, horario_id, horario_update)
    if not horario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Horario {horario_id} no encontrado"
        )
    return horario


@router.delete("/{horario_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_horario(horario_id: int, db: Session = Depends(get_db)):
    """
    Elimina un horario
    """
    if not HorarioService.eliminar_horario(db, horario_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Horario {horario_id} no encontrado"
        )
    return True


# Endpoints para Segmentos
from schemas.horario import SegmentoHorarioCreate, SegmentoHorarioResponse, AsignacionHorarioCreate, AsignacionHorarioResponse, SegmentoHorarioBulkCreate, FeriadoCreate, FeriadoResponse, AsignacionHorarioDetailResponse, SegmentoHorarioUpdate

@router.post("/segmentos/", response_model=SegmentoHorarioResponse, status_code=status.HTTP_201_CREATED)
def crear_segmento(segmento: SegmentoHorarioCreate, db: Session = Depends(get_db)):
    return HorarioService.crear_segmento(db, segmento)

@router.post("/segmentos/bulk", response_model=List[SegmentoHorarioResponse], status_code=status.HTTP_201_CREATED)
def crear_segmentos_masivo(bulk_data: SegmentoHorarioBulkCreate, db: Session = Depends(get_db)):
    return HorarioService.crear_segmentos_bulk(db, bulk_data)


@router.get("/{horario_id}/segmentos", response_model=List[SegmentoHorarioResponse])
def listar_segmentos(horario_id: int, db: Session = Depends(get_db)):
    return HorarioService.obtener_segmentos(db, horario_id)

@router.delete("/segmentos/{segmento_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_segmento(segmento_id: int, db: Session = Depends(get_db)):
    if not HorarioService.eliminar_segmento(db, segmento_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Segmento {segmento_id} no encontrado"
        )

@router.put("/segmentos/{segmento_id}", response_model=SegmentoHorarioResponse)
def actualizar_segmento(
    segmento_id: int,
    segmento_update: SegmentoHorarioUpdate,
    db: Session = Depends(get_db)
):
    """
    Actualiza un segmento de horario existente
    """
    segmento = HorarioService.actualizar_segmento(db, segmento_id, segmento_update)
    if not segmento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Segmento {segmento_id} no encontrado"
        )
    return segmento

# Endpoints para Asignaciones
@router.post("/asignar", response_model=AsignacionHorarioResponse)
def asignar_horario(asignacion: AsignacionHorarioCreate, db: Session = Depends(get_db)):
    # Validar fechas logic? Dejamos que el service o BD manejen por ahora
    # Validar fechas logic? Dejamos que el service o BD manejen por ahora
    return HorarioService.asignar_horario(db, asignacion)

@router.get("/asignaciones/usuario/{user_id}", response_model=List[AsignacionHorarioDetailResponse])
def listar_asignaciones_usuario(user_id: str, db: Session = Depends(get_db)):
    return HorarioService.obtener_asignaciones_por_usuario(db, user_id)



# Endpoints para Feriados
@router.post("/feriados/", response_model=FeriadoResponse, status_code=status.HTTP_201_CREATED)
def crear_feriado(feriado: FeriadoCreate, db: Session = Depends(get_db)):
    return HorarioService.crear_feriado(db, feriado)

@router.get("/feriados/", response_model=List[FeriadoResponse])
def listar_feriados(db: Session = Depends(get_db)):
    return HorarioService.obtener_feriados(db)

@router.delete("/feriados/{feriado_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_feriado(feriado_id: int, db: Session = Depends(get_db)):
    if not HorarioService.eliminar_feriado(db, feriado_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Feriado {feriado_id} no encontrado"
        )

