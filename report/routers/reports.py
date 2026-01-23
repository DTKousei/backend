from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional, List
from sqlalchemy.orm import Session
import os

from services.data_fetcher import fetch_sabana_data
from services.excel_gen import generate_excel_report
from services.pdf_gen import generate_pdf_report
from config.database import get_db
from models.report_log import TipoReporte, FormatoReporte, ReporteGenerado

router = APIRouter(
    prefix="/api/reports",
    tags=["reports"]
)

class ReportRequest(BaseModel):
    """
    Modelo de solicitud para generar reportes.
    """
    mes: str
    anio: str
    area: Optional[str] = None # Nombre exacto del departamento
    user_ids: Optional[List[str]] = None # Lista opcional de usuarios

# --- Helper Functions ---

def get_or_create_type(db: Session, name: str) -> TipoReporte:
    obj = db.query(TipoReporte).filter(TipoReporte.nombre == name).first()
    if not obj:
        obj = TipoReporte(nombre=name, descripcion=f"Reporte de {name}")
        db.add(obj)
        db.commit()
        db.refresh(obj)
    return obj

def get_or_create_format(db: Session, name: str, extension: str, mime: str) -> FormatoReporte:
    obj = db.query(FormatoReporte).filter(FormatoReporte.nombre == name).first()
    if not obj:
        obj = FormatoReporte(nombre=name, extension=extension, mime_type=mime)
        db.add(obj)
        db.commit()
        db.refresh(obj)
    return obj

def _generate_and_save(db: Session, request: ReportRequest, format_name: str, usuario_id: int):
    """
    Lógica común para obtener datos, generar archivo y guardar registro.
    """
    # 1. Obtener Datos
    data = fetch_sabana_data(request.mes, request.anio, request.user_ids, request.area)
    
    # 2. Configurar Formato
    if format_name.upper() == "EXCEL":
        file_path = generate_excel_report(data)
        fmt_obj = get_or_create_format(db, "EXCEL", ".xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    elif format_name.upper() == "PDF":
        file_path = generate_pdf_report(data)
        fmt_obj = get_or_create_format(db, "PDF", ".pdf", "application/pdf")
    else:
        raise ValueError(f"Formato no soportado: {format_name}")
        
    file_name = os.path.basename(file_path)
    
    # 3. Registrar en BD
    tipo = get_or_create_type(db, "Asistencia General")
    
    reporte = ReporteGenerado(
        usuario_id=usuario_id,
        tipo_reporte_id=tipo.id,
        formato_id=fmt_obj.id,
        nombre_archivo=file_name,
        ruta_archivo=file_path,
        area=request.area,
        parametros_usados={"mes": request.mes, "anio": request.anio, "user_ids": request.user_ids, "area": request.area}
    )
    db.add(reporte)
    db.commit()
    db.refresh(reporte)
    
    return reporte

# --- Endpoints ---

@router.post("/export/excel")
def export_excel(request: ReportRequest, db: Session = Depends(get_db)):
    """
    Endpoint para exportar el reporte de asistencia en formato Excel.
    """
    try:
        usuario_id = 1 # TODO: Obtener del token
        reporte = _generate_and_save(db, request, "EXCEL", usuario_id)
        
        return FileResponse(
            path=reporte.ruta_archivo, 
            filename=reporte.nombre_archivo, 
            media_type=reporte.formato.mime_type
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/export/pdf")
def export_pdf(request: ReportRequest, db: Session = Depends(get_db)):
    """
    Endpoint para exportar el reporte de asistencia en formato PDF.
    """
    try:
        usuario_id = 1 # TODO: Obtener del token
        reporte = _generate_and_save(db, request, "PDF", usuario_id)
        
        return FileResponse(
            path=reporte.ruta_archivo, 
            filename=reporte.nombre_archivo, 
            media_type=reporte.formato.mime_type
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class SaldosRequest(BaseModel):
    anio: int
    empleado_id: Optional[str] = None

from services.data_fetcher import fetch_saldos_incidencias
from services.pdf_saldos_gen import generate_saldos_pdf_report

@router.post("/export/saldos-pdf")
def export_saldos_pdf(request: SaldosRequest, db: Session = Depends(get_db)):
    """
    Endpoint para exportar el reporte de saldos de incidencias en PDF.
    """
    try:
        # 1. Obtener Datos
        data = fetch_saldos_incidencias(anio=request.anio, empleado_id=request.empleado_id)
        
        if not data:
             raise HTTPException(status_code=404, detail="No se encontraron datos de saldos para el año especificado.")

        # 2. Generar PDF
        file_path = generate_saldos_pdf_report(data, request.anio)
        file_name = os.path.basename(file_path)
        
        # 3. Registrar en BD
        # Reusamos lógica similar a _generate_and_save pero manual pq los argumentos varían
        format_obj = get_or_create_format(db, "PDF", ".pdf", "application/pdf")
        tipo_obj = get_or_create_type(db, "Saldos Incidencias")
        
        usuario_id = 1 # TODO: Token
        
        reporte = ReporteGenerado(
            usuario_id=usuario_id,
            tipo_reporte_id=tipo_obj.id,
            formato_id=format_obj.id,
            nombre_archivo=file_name,
            ruta_archivo=file_path,
            area=None,
            parametros_usados={"anio": request.anio, "empleado_id": request.empleado_id}
        )
        db.add(reporte)
        db.commit()
        db.refresh(reporte)
        
        return FileResponse(
            path=reporte.ruta_archivo, 
            filename=reporte.nombre_archivo, 
            media_type=reporte.formato.mime_type
        )

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/generated/{report_id}")
def view_generated_report(
    report_id: int, 
    format: Optional[str] = Query(None, description="Formato deseado (PDF, EXCEL)"), 
    db: Session = Depends(get_db)
):
    """
    Obtiene un reporte generado previamente. 
    Si se solicita un formato diferente al original, se intenta buscar un duplicado existente 
    o se genera uno nuevo bajo demanda.
    """
    # 1. Buscar reporte original
    original_report = db.query(ReporteGenerado).filter(ReporteGenerado.id == report_id).first()
    if not original_report:
        raise HTTPException(status_code=404, detail="Reporte no encontrado")

    # Si no se especifica formato, usar el original
    target_format = format.upper() if format else original_report.formato.nombre.upper()
    
    # Si el formato solicitado es el mismo del reporte original
    if target_format == original_report.formato.nombre.upper():
        if os.path.exists(original_report.ruta_archivo):
            return FileResponse(
                path=original_report.ruta_archivo,
                filename=original_report.nombre_archivo,
                media_type=original_report.formato.mime_type
            )
        else:
            # Archivo perdido, regenerar
            # Convertir parametros_usados (JSON) a objeto Request
            params = original_report.parametros_usados or {}
            req = ReportRequest(
                mes=params.get("mes"),
                anio=params.get("anio"),
                user_ids=params.get("user_ids"),
                area=params.get("area")
            )
            reporte_nuevo = _generate_and_save(db, req, target_format, original_report.usuario_id)
            return FileResponse(
                path=reporte_nuevo.ruta_archivo,
                filename=reporte_nuevo.nombre_archivo,
                media_type=reporte_nuevo.formato.mime_type
            )

    # 2. Si el formato es DIFERENTE, buscar si existe un reporte equivalente
    # Buscamos el ID del formato objetivo
    target_fmt_obj = get_or_create_format(db, target_format, 
                                          ".pdf" if target_format == "PDF" else ".xlsx", 
                                          "application/pdf" if target_format == "PDF" else "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    
    existing_report = db.query(ReporteGenerado).filter(
        ReporteGenerado.usuario_id == original_report.usuario_id,
        ReporteGenerado.tipo_reporte_id == original_report.tipo_reporte_id,
        ReporteGenerado.formato_id == target_fmt_obj.id,
        # Nota: La comparación de JSON en SQL puede variar por dialecto, 
        # pero para casos simples y mismo orden de claves suele funcionar o se debe hacer en codigo.
        # Aquí asumimos que si coinciden los parametros críticos es suficiente.
        # Una mejor aproximación seria guardar un hash de los parámetros.
        # Por simplicidad ahora, haremos un filtro extra en python si es necesario, 
        # pero intentemos filtro directo primero si SQLAlchemy lo soporta para el backend.
    ).all()

    # Filtrar en Python para asegurar coincidencia de parametros (JSON)
    found_report = None
    for r in existing_report:
        if r.parametros_usados == original_report.parametros_usados:
            if os.path.exists(r.ruta_archivo):
                found_report = r
                break
    
    if found_report:
        return FileResponse(
             path=found_report.ruta_archivo,
             filename=found_report.nombre_archivo,
             media_type=found_report.formato.mime_type
        )

    # 3. Si no existe, Generar Nuevo Formato on-demand
    params = original_report.parametros_usados or {}
    req = ReportRequest(
        mes=params.get("mes"),
        anio=params.get("anio"),
        user_ids=params.get("user_ids"),
        area=params.get("area")
    )
    
    try:
        new_report = _generate_and_save(db, req, target_format, original_report.usuario_id)
        return FileResponse(
            path=new_report.ruta_archivo,
            filename=new_report.nombre_archivo,
            media_type=new_report.formato.mime_type
        )
    except ValueError:
         raise HTTPException(status_code=400, detail=f"Formato '{target_format}' no soportado para conversión.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generando reporte: {str(e)}")

@router.get("/generated/", response_model=List[dict])
def list_generated_reports(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Lista los reportes generados con paginación.
    """
    reports = db.query(ReporteGenerado).order_by(ReporteGenerado.fecha_generacion.desc()).offset(skip).limit(limit).all()
    
    # Transformar a dict para respuesta, incluyendo nombres de relaciones
    result = []
    for r in reports:
        result.append({
            "id": r.id,
            "nombre_archivo": r.nombre_archivo,
            "fecha_generacion": r.fecha_generacion,
            "formato": r.formato.nombre if r.formato else None,
            "tipo_reporte": r.tipo_reporte.nombre if r.tipo_reporte else None,
            "usuario_id": r.usuario_id,
            "area": r.area,
            "parametros": r.parametros_usados
        })
    return result

@router.delete("/generated/{report_id}")
def delete_generated_report(report_id: int, db: Session = Depends(get_db)):
    """
    Elimina un reporte generado: borra el archivo físico y el registro en la BD.
    """
    report = db.query(ReporteGenerado).filter(ReporteGenerado.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Reporte no encontrado")
        
    # 1. Borrar archivo físico
    if report.ruta_archivo and os.path.exists(report.ruta_archivo):
        try:
            os.remove(report.ruta_archivo)
        except Exception as e:
            # Log error pero continuar con borrado de registro? 
            # Mejor avisar pero permitir borrado si el archivo ya no existe o hay error de permisos?
            # Por ahora lanzamos error 500 si falla borrado fisico para evitar inconsistencia
            raise HTTPException(status_code=500, detail=f"Error eliminando archivo físico: {str(e)}")

    # 2. Borrar registro BD
    db.delete(report)
    db.commit()
    
    return {"message": "Reporte eliminado correctamente"}
