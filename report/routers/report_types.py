from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional

from config.database import get_db
from models.report_log import TipoReporte

router = APIRouter(
    prefix="/api/report-types",
    tags=["Report Types"]
)

# --- Pydantic Models ---
class TipoReporteBase(BaseModel):
    nombre: str
    descripcion: Optional[str] = None
    activo: Optional[bool] = True

class TipoReporteCreate(TipoReporteBase):
    pass

class TipoReporteUpdate(TipoReporteBase):
    pass

class TipoReporteResponse(TipoReporteBase):
    id: int

    class Config:
        orm_mode = True

# --- Endpoints ---

@router.get("/", response_model=List[TipoReporteResponse])
def read_report_types(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Lista todos los tipos de reporte.
    """
    tipos = db.query(TipoReporte).offset(skip).limit(limit).all()
    return tipos

@router.post("/", response_model=TipoReporteResponse)
def create_report_type(tipo: TipoReporteCreate, db: Session = Depends(get_db)):
    """
    Crea un nuevo tipo de reporte.
    """
    existing_type = db.query(TipoReporte).filter(TipoReporte.nombre == tipo.nombre).first()
    if existing_type:
        raise HTTPException(status_code=400, detail="El tipo de reporte ya existe.")
    
    nuevo_tipo = TipoReporte(
        nombre=tipo.nombre,
        descripcion=tipo.descripcion,
        activo=tipo.activo
    )
    db.add(nuevo_tipo)
    db.commit()
    db.refresh(nuevo_tipo)
    return nuevo_tipo

@router.put("/{type_id}", response_model=TipoReporteResponse)
def update_report_type(type_id: int, tipo_update: TipoReporteUpdate, db: Session = Depends(get_db)):
    """
    Actualiza un tipo de reporte existente.
    """
    db_tipo = db.query(TipoReporte).filter(TipoReporte.id == type_id).first()
    if not db_tipo:
        raise HTTPException(status_code=404, detail="Tipo de reporte no encontrado.")
    
    db_tipo.nombre = tipo_update.nombre
    db_tipo.descripcion = tipo_update.descripcion
    db_tipo.activo = tipo_update.activo
    
    db.commit()
    db.refresh(db_tipo)
    return db_tipo

@router.delete("/{type_id}")
def delete_report_type(type_id: int, db: Session = Depends(get_db)):
    """
    Elimina (lógicamente) o desactiva un tipo de reporte.
    Nota: Si hay reportes asociados, se recomienda desactivar en lugar de borrar.
    Aquí implementaremos soft-delete seteando activo=False para seguridad referencial.
    """
    db_tipo = db.query(TipoReporte).filter(TipoReporte.id == type_id).first()
    if not db_tipo:
        raise HTTPException(status_code=404, detail="Tipo de reporte no encontrado.")
    
    # Soft delete
    db_tipo.activo = False
    db.commit()
    
    return {"message": "Tipo de reporte desactivado correctamente."}
