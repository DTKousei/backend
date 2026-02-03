from sqlalchemy.orm import Session
from sqlalchemy import extract, and_
from calendar import monthrange
from datetime import date
from typing import List, Dict, Any, Optional
from models.usuario import Usuario
from models.reportes import AsistenciaDiaria
from models.horario import Horario # Potentially needed for labels or checking non-working days
from models.turnos import AsignacionHorario, SegmentosHorario # Models for checking schedule
from sqlalchemy import or_
# Si Horario logic is needed for "Feriado" vs "Domingo", we might need more logic here.
# For now relying on AsistenciaDiaria.estado_asistencia or simple calendar logic.
import io
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from datetime import datetime
import schemas.reportes

class ReporteService:
    """
    Servicio para la generación de reportes complejos como la Sábana de Asistencia.
    """

    # Diccionario de Códigos Cortos
    CODIGOS_ASISTENCIA = {
        "PRESENTE": "A",
        "TARDE": "T",
        "FALTA": "FAL",
        "FERIADO": "FER",
        "VACACIONES": "VAC",
        "LICENCIA": "L/S",      # Licencia sin goce (ejemplo)
        "LICENCIA_GO": "L/C",   # Licencia con goce
        "COMISION": "C/S",      # Comisión de servicio
        "PERMISO": "PER",
        "DESCANSO": "D",        # Descanso médico o semanal
        "ABANDONO": "A/B",      # Abandono de trabajo
        "SIN_HORARIO": "S/H"    # Sin horario asignado
    }

    @staticmethod
    def _obtener_codigo_corto(estado: str) -> str:
        """Devuelve el código corto para un estado dado."""
        if not estado:
            return "FAL"
        
        estado_upper = estado.upper()
        # Busqueda directa
        if estado_upper in ReporteService.CODIGOS_ASISTENCIA:
            return ReporteService.CODIGOS_ASISTENCIA[estado_upper]
        
        # Búsquedas parciales o mapeos extra
        if "LICENCIA" in estado_upper:
            return "L/S" # Default a Licencia
        if "COMIS" in estado_upper:
            return "C/S"
        if "PERMISO" in estado_upper:
            return "PER"
        if "VACACION" in estado_upper:
            return "VAC"
        
        return "FAL" # Default si no se reconoce

    @staticmethod
    def obtener_sabana_asistencia(
        db: Session, 
        anio: int, 
        mes: int, 
        user_ids: Optional[List[str]] = None,
        area: Optional[str] = None,
        otros_filtros: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Genera la data para la Sábana de Asistencia (Matrix Report).
        """
        
        # 0. Registrar Generación de Reporte (Auditoria basica)
        # Nota: Idealmente esto va al final o en bloque try/finally, pero para simplicidad lo registramos aqui
        # Si no existe la tabla aun, saltar este paso. (Ya la creamos en models/reportes.py)
        try:
            from models.reportes import ReportesGenerados
            import json
            nuevo_reporte = ReportesGenerados(
                tipo_reporte="Sabana",
                anio=anio,
                mes=mes,
                area=area,
                filtros=json.dumps(otros_filtros) if otros_filtros else None
            )
            db.add(nuevo_reporte)
            db.commit()
        except Exception as e:
            print(f"Advertencia: No se pudo registrar el historial de reporte: {e}")
            db.rollback()

        # 1. Definir rango del mes
        _, num_dias = monthrange(anio, mes)
        fecha_inicio = date(anio, mes, 1)
        fecha_fin = date(anio, mes, num_dias)
        
        # 2. Obtener Empleados
        query_users = db.query(Usuario).order_by(Usuario.nombre)
        
        # 2.1 Filtrar por Departamento (Area)
        # CORRECCION: El area es solo referencial (metadata), no un filtro de base de datos.
        # if area:
        #     from models.departamento import Departamento
        #     query_users = query_users.join(Usuario.departamento_rel).filter(Departamento.nombre == area)
        
        if user_ids:
            query_users = query_users.filter(Usuario.user_id.in_(user_ids))
        
        empleados = query_users.all()
        
        # 3. Obtener Registros de AsistenciaDiaria para el mes
        query_asis = db.query(AsistenciaDiaria).filter(
            extract('year', AsistenciaDiaria.fecha) == anio,
            extract('month', AsistenciaDiaria.fecha) == mes
        )
        if user_ids:
            # Filtrar por user_id (string) de los usuarios seleccionados
            # Ojo: Usuario.id es int, AsistenciaDiaria.user_id es str (from device)
            # Necesitamos los user_id strings de los empleados filtrados
            user_ids_str = [emp.user_id for emp in empleados]
            query_asis = query_asis.filter(AsistenciaDiaria.user_id.in_(user_ids_str))
            
        registros = query_asis.all()
        
        # 4. Indexar registros para acceso rápido: (user_id_str, dia_del_mes) -> AsistenciaDiaria
        map_registros = {}
        for reg in registros:
            dia = reg.fecha.day
            map_registros[(reg.user_id, dia)] = reg

        # 4.5 Obtener Horarios y Asignaciones
        # Necesitamos saber qué horario tenía asignado cada usuario en cada día del mes
        
        # A) Obtener Asignaciones que se solapen con el mes
        # Rango del mes: fecha_inicio a fecha_fin
        
        # IDs de usuarios (strings) que estamos procesando
        user_ids_filtro = [e.user_id for e in empleados]
        
        query_asig = db.query(AsignacionHorario).filter(
            AsignacionHorario.user_id.in_(user_ids_filtro),
            AsignacionHorario.fecha_inicio <= fecha_fin,
            or_(
                AsignacionHorario.fecha_fin == None,
                AsignacionHorario.fecha_fin >= fecha_inicio
            )
        )
        asignaciones = query_asig.all()
        
        # Mapa: user_id -> lista de asignaciones
        map_asignaciones = {}
        horario_ids_involucrados = set()
        
        for asig in asignaciones:
            if asig.user_id not in map_asignaciones:
                map_asignaciones[asig.user_id] = []
            map_asignaciones[asig.user_id].append(asig)
            horario_ids_involucrados.add(asig.horario_id)
            
        # B) Obtener Segmentos de los horarios involucrados
        segmentos = db.query(SegmentosHorario).filter(
            SegmentosHorario.horario_id.in_(list(horario_ids_involucrados))
        ).all()
        
        # Mapa: horario_id -> set de dias laborales (integers 0-6)
        map_dias_laborables = {}
        for seg in segmentos:
            if seg.horario_id not in map_dias_laborables:
                map_dias_laborables[seg.horario_id] = set()
            map_dias_laborables[seg.horario_id].add(seg.dia_semana)

        # 5. Construir Estructura de Respuesta
        
        # Metadatos del mes
        dias_semana_nombres = ["L", "M", "M", "J", "V", "S", "D"]
        columnas_dias = []
        for d in range(1, num_dias + 1):
            fecha_actual = date(anio, mes, d)
            nombre_dia = dias_semana_nombres[fecha_actual.weekday()]
            columnas_dias.append({
                "dia": d,
                "nombre_dia": nombre_dia,
                "es_fin_de_semana": fecha_actual.weekday() >= 5 # 5=Sabado, 6=Domingo
            })

        data_empleados = []
        
        for emp in empleados:
            asistencia_dias = []
            stats = {
                "dias_lab": 0, # Días laborados (Presente)
                "tardanzas": 0,
                "faltas": 0,
                "licencias": 0
            }
            
            for d in range(1, num_dias + 1):
                # Validar fecha futura: Si es mayor a hoy, ignorar (poner vacío y continuar)
                fecha_iter_check = date(anio, mes, d)
                if fecha_iter_check > date.today():
                    asistencia_dias.append("")
                    continue

                key = (emp.user_id, d)
                codigo = ""
                
                should_recalculate = False
                
                if key in map_registros:
                    reg = map_registros[key]
                    # Si el estado es SIN_HORARIO pero creemos que podria haber (stale data), intentamos recalcular
                    if reg.estado_asistencia == "SIN_HORARIO":
                        should_recalculate = True
                    else:
                        estado = reg.estado_asistencia
                        if estado == "DIA_LIBRE":
                             # Si es día libre, mostrar la inicial del día (L, M, S, D...)
                             # para mantener consistencia con los días no procesados.
                             current_date = date(anio, mes, d)
                             iniciales = ["L", "M", "M", "J", "V", "S", "D"]
                             codigo = iniciales[current_date.weekday()]
                        else:
                             codigo = ReporteService._obtener_codigo_corto(estado)
                        
                        # Lógica de Días Laborables / Computables
                        # Se incluyen Feriados, Licencias con Goce y Días Libres (S, D, etc)
                        # Se EXCLUYE L/S (Licencia Sin Goce) y FAL (Falta)
                        # Iniciales de días libres: L, M, J, V, S, D
                        codigos_computables = ["A", "T", "FER", "VAC", "C/S", "PER", "L/C", "S", "D", "L", "M", "J", "V"]
                        
                        if codigo in codigos_computables:
                            stats["dias_lab"] += 1
                        
                        # Estadísticas Específicas
                        if codigo == "T":
                            stats["tardanzas"] += 1
                        elif codigo == "FAL":
                            stats["faltas"] += 1
                        elif codigo in ["L/S", "L/C", "C/S", "VAC", "PER"]:
                            stats["licencias"] += 1
                            
                    # Si se marco para recalcular, caemos al bloque 'else' o lo manejamos aqui
                    if should_recalculate:
                        # Forzamos que entre al bloque de "No hay registro" (o similar logic)
                        pass
                
                # Bloque unificado de calculo/recuperacion
                if key not in map_registros or should_recalculate:
                    # No hay registro procesado en AsistenciaDiaria.
                    # INTENTO DE AUTO-CÁLCULO (Lazy Loading):
                    # Solo intentamos calcular si la fecha es pasado o hoy, para no procesar futuro innecesariamente
                    fecha_iter = date(anio, mes, d)
                    
                    registro_calculado = None
                    if fecha_iter <= date.today():
                        # Evitar circular import
                        from services.asistencia_service import AsistenciaService
                        try:
                            # Procesar el día on-the-fly
                            # Esto consultará Logs (por UID) y generará la AsistenciaDiaria si corresponde
                            registro_calculado = AsistenciaService.procesar_asistencia_dia(db, emp.user_id, fecha_iter)
                        except Exception as e:
                            print(f"Error auto-calculando {emp.user_id} {fecha_iter}: {e}")
                            
                    if registro_calculado:
                        # Si se generó registro, usarlo
                        estado = registro_calculado.estado_asistencia
                        if estado == "DIA_LIBRE":
                             current_date = date(anio, mes, d)
                             iniciales = ["L", "M", "M", "J", "V", "S", "D"]
                             codigo = iniciales[current_date.weekday()]
                        else:
                             codigo = ReporteService._obtener_codigo_corto(estado)
                        
                        # Lógica de Días Laborables / Computables
                        codigos_computables = ["A", "T", "FER", "VAC", "C/S", "PER", "L/C", "S", "D", "L", "M", "J", "V"]
                        
                        if codigo in codigos_computables:
                            stats["dias_lab"] += 1
                            
                        # Estadísticas Específicas
                        if codigo == "T":
                            stats["tardanzas"] += 1
                        elif codigo == "FAL":
                            stats["faltas"] += 1
                        elif codigo in ["L/S", "L/C", "C/S", "VAC", "PER"]:
                            stats["licencias"] += 1
                            
                    else:
                        # Si aún no hay registro (ej. futuro, o error, o el proceso retornó None), aplicar lógica de horario por defecto
                        
                        # 1. Buscar horario activo en fecha_iter
                        horario_activo_id = None
                        if emp.user_id in map_asignaciones:
                            for asignacion in map_asignaciones[emp.user_id]:
                                fin_valido = asignacion.fecha_fin is None or asignacion.fecha_fin >= fecha_iter
                                inicio_valido = asignacion.fecha_inicio <= fecha_iter
                                
                                if inicio_valido and fin_valido:
                                    horario_activo_id = asignacion.horario_id
                                    break
                        
                        # 2. Verificar si es día laborable en ese horario
                        es_dia_laborable = False
                        if horario_activo_id and horario_activo_id in map_dias_laborables:
                            dias_lab_set = map_dias_laborables[horario_activo_id]
                            dia_semana_actual = fecha_iter.weekday() # 0=Lun, 6=Dom
                            if dia_semana_actual in dias_lab_set:
                                es_dia_laborable = True
                        
                        # 3. Determinar estado default
                        if fecha_iter > date.today():
                            codigo = "" # Futuro
                        elif es_dia_laborable:
                            codigo = "FAL"
                            stats["faltas"] += 1
                        else:
                            # Usar inicial del día para Descanso/No Laborable
                            iniciales_dias = ["L", "M", "M", "J", "V", "S", "D"]
                            dia_semana_actual = fecha_iter.weekday()
                            codigo = iniciales_dias[dia_semana_actual]
                
                asistencia_dias.append(codigo)
            
            data_empleados.append({
                "empleado_id": emp.id,
                "nombre": emp.nombre,
                "user_id": emp.user_id,
                "departamento": emp.departamento_rel.nombre if emp.departamento_rel else "Sin Departamento",
                "asistencia_dias": asistencia_dias,
                "resumen": stats
            })

        return {
            "meta": {
                "mes": mes,
                "anio": anio,
                "dias_total": num_dias
            },
            "columnas_dias": columnas_dias,
            "data": data_empleados
        }

    @staticmethod
    def obtener_saldos_incidencias_pdf(db: Session, anio: int, empleado_id: Optional[str] = None):
        """
        Genera un PDF con el reporte de saldos de incidencias.
        """
        from models.incidencia import TipoIncidencia, Incidencia
        from models.usuario import Usuario
        from sqlalchemy import func

        # 1. Obtener Tipos de Incidencia (Columnas)
        tipos = db.query(TipoIncidencia).filter(TipoIncidencia.activo == True).order_by(TipoIncidencia.nombre).all()
        
        # 2. Obtener Empleados
        query_users = db.query(Usuario).filter(Usuario.esta_activo == True).order_by(Usuario.nombre)
        if empleado_id:
            query_users = query_users.filter(Usuario.user_id == empleado_id)
        
        empleados = query_users.all()

        # 3. Calcular Saldos
        data_reporte = []

        headers = ["N°", "DNI", "Apellidos y Nombres"]
        for tipo in tipos:
            headers.append(f"{tipo.nombre[:10]}...") # Abreviar

        # Preparar data
        for idx, emp in enumerate(empleados, 1):
            row = [str(idx), emp.user_id, emp.nombre]
            
            for tipo in tipos:
                # Calcular dias consumidos
                consumidos = db.query(func.sum(Incidencia.dias_consumidos)).filter(
                    Incidencia.empleado_id == emp.user_id,
                    Incidencia.tipo_incidencia_id == tipo.id,
                    extract('year', Incidencia.fecha_inicio) == anio,
                    Incidencia.estado_id != 3 # Excluir Rechazados/Cancelados si aplica. Asumimos 3=Rechazado, validar ID
                ).scalar() or 0
                
                # Formato: Consumido / Max
                # max_dias puede ser null (ilimitado)
                max_txt = str(tipo.max_dias_anio) if tipo.max_dias_anio else "∞"
                row.append(f"{consumidos} / {max_txt}")
            
            data_reporte.append(row)

        # 4. Generar PDF
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=landscape(letter))
        elements = []
        styles = getSampleStyleSheet()

        # Título
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=16,
            alignment=1, # Center
            spaceAfter=30
        )
        elements.append(Paragraph(f"Reporte de Saldos de Incidencias - {anio}", title_style))
        elements.append(Paragraph(f"Generado: {datetime.now().strftime('%d/%m/%Y %H:%M')}", styles['Normal']))
        elements.append(Spacer(1, 20))

        # Tabla
        table_data = [headers] + data_reporte
        
        # Ajustar anchos de columna dinámicamente o fijo
        # DNI (1 inch), Nombre (2.5 inch), Resto repartido
        col_widths = [0.5*inch, 1*inch, 2.5*inch]
        rest_width = (11 - 4) * inch # Landscape letter width approx 11
        if len(tipos) > 0:
            type_col_width = rest_width / len(tipos)
            col_widths.extend([type_col_width] * len(tipos))

        t = Table(table_data, colWidths=col_widths if len(tipos) <= 8 else None) # Si son muchos, auto-adjust o reducir

        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
        ]))

        elements.append(t)
        doc.build(elements)
        
        buffer.seek(0)
        return buffer


    # --- CRUD TipoReporte ---
    @staticmethod
    def get_tipos_reporte(db: Session, skip: int = 0, limit: int = 100):
        from models.reportes import TipoReporte
        return db.query(TipoReporte).offset(skip).limit(limit).all()

    @staticmethod
    def create_tipo_reporte(db: Session, tipo_data: schemas.reportes.TipoReporteCreate):
        from models.reportes import TipoReporte
        db_tipo = TipoReporte(**tipo_data.dict())
        db.add(db_tipo)
        db.commit()
        db.refresh(db_tipo)
        return db_tipo

    @staticmethod
    def update_tipo_reporte(db: Session, tipo_id: int, tipo_data: schemas.reportes.TipoReporteCreate):
        from models.reportes import TipoReporte
        db_tipo = db.query(TipoReporte).filter(TipoReporte.id == tipo_id).first()
        if db_tipo:
            for key, value in tipo_data.dict().items():
                setattr(db_tipo, key, value)
            db.commit()
            db.refresh(db_tipo)
        return db_tipo

    @staticmethod
    def delete_tipo_reporte(db: Session, tipo_id: int):
        from models.reportes import TipoReporte
        db_tipo = db.query(TipoReporte).filter(TipoReporte.id == tipo_id).first()
        if db_tipo:
            db.delete(db_tipo)
            db.commit()
            return True
        return False

    @staticmethod
    def obtener_saldos_incidencias_pdf(db: Session, anio: int, empleado_id: Optional[str] = None):
        """
        Genera un PDF con el reporte de saldos de incidencias.
        """
        from models.incidencia import TipoIncidencia, Incidencia
        from models.usuario import Usuario
        from sqlalchemy import func
        # Log del reporte
        from models.reportes import ReportesGenerados
        import json

        try:
             nuevo_reporte = ReportesGenerados(
                 tipo_reporte="Saldos de Incidencias",
                 anio=anio,
                 mes=0, # Saldos es anual, mes no aplica o poner 0
                 area=None,
                 filtros=json.dumps({"empleado_id": empleado_id, "formato": "PDF"}) if empleado_id else json.dumps({"formato": "PDF"})
             )
             db.add(nuevo_reporte)
             db.commit()
        except Exception as e:
             print(f"Error logging report: {e}")
             db.rollback()

        # 1. Obtener Tipos de Incidencia (Columnas)
        tipos = db.query(TipoIncidencia).filter(TipoIncidencia.activo == True).order_by(TipoIncidencia.nombre).all()
        
        # 2. Obtener Empleados
        query_users = db.query(Usuario).filter(Usuario.esta_activo == True).order_by(Usuario.nombre)
        if empleado_id:
            query_users = query_users.filter(Usuario.user_id == empleado_id)
        
        empleados = query_users.all()

        # 3. Calcular Saldos
        data_reporte = []

        headers = ["N°", "DNI", "Apellidos y Nombres"]
        for tipo in tipos:
            headers.append(f"{tipo.nombre[:10]}...") # Abreviar

        # Preparar data
        for idx, emp in enumerate(empleados, 1):
            row = [str(idx), emp.user_id, emp.nombre]
            
            for tipo in tipos:
                # Calcular dias consumidos
                consumidos = db.query(func.sum(Incidencia.dias_consumidos)).filter(
                    Incidencia.empleado_id == emp.user_id,
                    Incidencia.tipo_incidencia_id == tipo.id,
                    extract('year', Incidencia.fecha_inicio) == anio,
                    Incidencia.estado_id != 3 # Excluir Rechazados/Cancelados si aplica. Asumimos 3=Rechazado, validar ID
                ).scalar() or 0
                
                # Formato: Consumido / Max
                # max_dias puede ser null (ilimitado)
                max_txt = str(tipo.max_dias_anio) if tipo.max_dias_anio else "∞"
                row.append(f"{consumidos} / {max_txt}")
            
            data_reporte.append(row)

        # 4. Generar PDF
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=landscape(letter))
        elements = []
        styles = getSampleStyleSheet()

        # Título
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=16,
            alignment=1, # Center
            spaceAfter=30
        )
        elements.append(Paragraph(f"Reporte de Saldos de Incidencias - {anio}", title_style))
        elements.append(Paragraph(f"Generado: {datetime.now().strftime('%d/%m/%Y %H:%M')}", styles['Normal']))
        elements.append(Spacer(1, 20))

        # Tabla
        table_data = [headers] + data_reporte
        
        # Ajustar anchos de columna dinámicamente o fijo
        # DNI (1 inch), Nombre (2.5 inch), Resto repartido
        col_widths = [0.5*inch, 1*inch, 2.5*inch]
        rest_width = (11 - 4) * inch # Landscape letter width approx 11
        if len(tipos) > 0:
            type_col_width = rest_width / len(tipos)
            col_widths.extend([type_col_width] * len(tipos))

        t = Table(table_data, colWidths=col_widths if len(tipos) <= 8 else None) # Si son muchos, auto-adjust o reducir

        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
        ]))

        elements.append(t)
        doc.build(elements)
        
        buffer.seek(0)
        return buffer
