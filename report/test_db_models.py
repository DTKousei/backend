from config.database import Base, engine, SessionLocal
from models.report_log import TipoReporte, FormatoReporte, ReporteGenerado
import sys

def init_db():
    print("Creating tables...")
    Base.metadata.create_all(bind=engine)
    print("Tables created.")

def seed_data(db):
    print("Seeding data...")
    types = ["Asistencia General", "Tardanzas", "Horas Extras", "Inasistencias", "Incidencias"]
    formats = [("PDF", ".pdf", "application/pdf"), ("EXCEL", ".xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")]

    for t in types:
        if not db.query(TipoReporte).filter_by(nombre=t).first():
            db.add(TipoReporte(nombre=t, descripcion=f"Reporte de {t}"))
            print(f"Added Type: {t}")
    
    for name, ext, mime in formats:
        if not db.query(FormatoReporte).filter_by(nombre=name).first():
            db.add(FormatoReporte(nombre=name, extension=ext, mime_type=mime))
            print(f"Added Format: {name}")
    
    db.commit()
    print("Seeding complete.")

def test_insertion(db):
    print("Testing insertion...")
    try:
        tipo = db.query(TipoReporte).filter_by(nombre="Asistencia General").first()
        formato = db.query(FormatoReporte).filter_by(nombre="PDF").first()
        
        if not tipo or not formato:
            print("Error: Types or Formats not found!")
            return

        report = ReporteGenerado(
            usuario_id=999,
            tipo_reporte_id=tipo.id,
            formato_id=formato.id,
            nombre_archivo="test_report.pdf",
            ruta_archivo="/tmp/test_report.pdf",
            parametros_usados={"test": True}
        )
        db.add(report)
        db.commit()
        db.refresh(report)
        print(f"Successfully created report log: {report}")
        
        # Verify fetch
        fetched = db.query(ReporteGenerado).filter_by(id=report.id).first()
        print(f"Fetched report: {fetched.nombre_archivo} - Type: {fetched.tipo_reporte.nombre} - Fmt: {fetched.formato.nombre}")
        
    except Exception as e:
        print(f"Error during insertion test: {e}")

if __name__ == "__main__":
    init_db()
    db = SessionLocal()
    try:
        seed_data(db)
        test_insertion(db)
    finally:
        db.close()
