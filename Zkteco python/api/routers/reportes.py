from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from models.database import get_db
from services.reporte_service import ReporteService

router = APIRouter(
    prefix="/api/reportes",
    tags=["Reportes"]
)

from schemas.reportes import SabanaRequest

@router.post("/sabana")
def obtener_sabana_asistencia(
    request: SabanaRequest,
    db: Session = Depends(get_db)
):
    """
    Obtiene la Sábana de Asistencia (Matrix Report).
    Si se envían user_ids, filtra por esos IDs de empleados (Biometric ID).
    """
    try:
        reporte = ReporteService.obtener_sabana_asistencia(
            db, 
            request.anio, 
            request.mes, 
            user_ids=request.user_ids,
            area=request.area
        )
        return reporte
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al generar reporte: {str(e)}")
