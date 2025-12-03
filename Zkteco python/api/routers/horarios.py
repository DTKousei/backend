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
