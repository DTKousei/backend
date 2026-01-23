from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from models.database import get_db
from services.reporte_service import ReporteService

router = APIRouter(
    prefix="/api/reportes",
    tags=["Reportes"]
)

from schemas.reportes import SabanaRequest, SaldosRequest, TipoReporteCreate, TipoReporte

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
            area=request.area,
            otros_filtros=request.model_dump(exclude={'anio', 'mes', 'user_ids', 'area'})
        )
        return reporte
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al generar reporte: {str(e)}")

@router.post("/export/saldos-pdf")
def exportar_saldos_pdf(
    request: SaldosRequest,
    db: Session = Depends(get_db)
):
    """
    Genera y descarga el reporte PDF de saldos de incidencias.
    """
    try:
        buffer = ReporteService.obtener_saldos_incidencias_pdf(
            db, 
            request.anio, 
            request.empleado_id
        )
        
        filename = f"saldos_incidencias_{request.anio}.pdf"
        return StreamingResponse(
            buffer,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al generar PDF: {str(e)}")
@router.get("/generated/")
def list_generated_reports(db: Session = Depends(get_db)):
    """
    Lista el historial de reportes generados.
    """
    from models.reportes import ReportesGenerados
    import json

    reportes = db.query(ReportesGenerados).order_by(ReportesGenerados.fecha_generacion.desc()).all()
    
    result = []
    for r in reportes:
        # Inferir formato y nombre bonito
        formato = "EXCEL"
        if "Saldos" in r.tipo_reporte or "PDF" in (r.filtros or ""):
            formato = "PDF"
        
        # Parsear filtros
        try:
            filtros_dict = json.loads(r.filtros) if r.filtros else {}
        except:
            filtros_dict = {}

        result.append({
            "id": r.id,
            "report_type_name": r.tipo_reporte, # Mapeo directo para el frontend
            "usuario_id": r.usuario_generador_id or 1, # Default admin
            "fecha_generacion": r.fecha_generacion.isoformat(),
            "filtros": filtros_dict,
            "parametros": filtros_dict, # Alias
            "area": r.area,
            "formato": formato,
            "estado": "COMPLETED"
        })
    
    return {"data": result}

# --- CRUD Endpoints for Report Types ---
@router.get("/report-types", response_model=dict)
def get_report_types(db: Session = Depends(get_db)):
    tipos = ReporteService.get_tipos_reporte(db)
    return {"data": tipos}

@router.post("/report-types", response_model=TipoReporte)
def create_report_type(tipo: TipoReporteCreate, db: Session = Depends(get_db)):
    return ReporteService.create_tipo_reporte(db, tipo)

@router.put("/report-types/{tipo_id}", response_model=TipoReporte)
def update_report_type(tipo_id: int, tipo: TipoReporteCreate, db: Session = Depends(get_db)):
    return ReporteService.update_tipo_reporte(db, tipo_id, tipo)

@router.delete("/report-types/{tipo_id}")
def delete_report_type(tipo_id: int, db: Session = Depends(get_db)):
    success = ReporteService.delete_tipo_reporte(db, tipo_id)
    if not success:
        raise HTTPException(status_code=404, detail="Tipo de reporte no encontrado")
    return {"message": "Eliminado correctamente"}
