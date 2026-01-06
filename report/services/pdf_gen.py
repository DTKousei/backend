import os
import uuid
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import landscape, legal
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.lib.enums import TA_CENTER

STORAGE_DIR = "storage"

if not os.path.exists(STORAGE_DIR):
    os.makedirs(STORAGE_DIR)

def generate_pdf_report(data: dict) -> str:
    """
    Genera un reporte en PDF replicando el diseño solicitado:
    - Cabecera doble (Num dia / Nombre dia).
    - Totales al final.
    - Leyenda en el pie.
    """
    # 1. Metadata
    meta = data.get("meta", {})
    mes = meta.get("mes")
    anio = meta.get("anio")
    columnas_dias = data.get("columnas_dias", [])
    employees = data.get("data", [])
    
    # Path
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_id = uuid.uuid4().hex[:6]
    filename = f"reporte_asistencia_{anio}_{mes}_{timestamp}_{unique_id}.pdf"
    file_path = os.path.join(STORAGE_DIR, filename)
    absolute_path = os.path.abspath(file_path)
    
    # Usamos LEGAL landscape para tener más ancho, o A3 si fuera necesario.
    # La imagen parece ancha. Probaremos Legal Landscape (35.56 cm ancho).
    doc = SimpleDocTemplate(absolute_path, pagesize=landscape(legal), 
                            rightMargin=10, leftMargin=10, topMargin=20, bottomMargin=20)
    elements = []
    
    styles = getSampleStyleSheet()
    
    # --- TITULO ---
    title_style = ParagraphStyle(
        'CustomTitle', 
        parent=styles['Heading1'], 
        alignment=TA_CENTER, 
        fontSize=14,
        spaceAfter=10
    )
    elements.append(Paragraph("RESUMEN DE ASISTENCIA DEL PERSONAL DE LA SEDE UGEL SUCRE", title_style))
    
    subtitle_style = ParagraphStyle(
        'CustomSubTitle', 
        parent=styles['Heading2'], 
        alignment=TA_CENTER, 
        fontSize=12,
        spaceAfter=15
    )
    
    # Lista de meses en español
    MESES = [
        "ENERO", "FEBRERO", "MARZO", "ABRIL", "MAYO", "JUNIO",
        "JULIO", "AGOSTO", "SEPTIEMBRE", "OCTUBRE", "NOVIEMBRE", "DICIEMBRE"
    ]
    
    nombre_mes = mes
    try:
        mes_int = int(mes)
        if 1 <= mes_int <= 12:
            nombre_mes = MESES[mes_int - 1]
    except ValueError:
        pass
        
    elements.append(Paragraph(f"ASISTENCIA: {nombre_mes} {anio}", subtitle_style))

    # --- TABLA PRINCIPAL ---
    
    # Definición de Cabeceras
    # Row 0: "N°", "APELLIDOS Y NOMBRES", "DNI", [1, 2, 3...], "DIA MES", "DIAS NO LAB", "TOTAL", "TARD"
    # Row 1: "", "", "", [S, D, L...], "", "", "", ""
    
    # Construcción de filas de cabecera
    header_row_1 = ["N°", "APELLIDOS Y NOMBRES", "DNI"]
    header_row_2 = ["", "", ""] # Espacios para el span vertical
    
    # Días
    for col in columnas_dias:
        header_row_1.append(str(col['dia']))
        header_row_2.append(col['nombre_dia'])
        
    # Totales
    header_row_1.extend(["DIA\nMES", "DIAS\nNO\nLAB.", "TOTAL\nDIAS\nLAB.", "TARD."])
    header_row_2.extend(["", "", "", ""])
    
    table_data = [header_row_1, header_row_2]
    
    # Filas de Datos
    for idx, emp in enumerate(employees, start=1):
        row = [
            str(idx),
            emp.get("nombre", "")[:25], # Truncar
            emp.get("user_id", "")
        ]
        
        # Asistencia
        asistencia = emp.get("asistencia_dias", [])
        # Rellenar hasta fin de mes si falta
        for i in range(len(columnas_dias)):
            if i < len(asistencia):
                row.append(asistencia[i])
            else:
                row.append("")
                
        # Resumen
        resumen = emp.get("resumen", {})
        dias_lab = resumen.get("dias_lab", 0)
        tardanzas = resumen.get("tardanzas", 0)
        
        total_dias_mes = meta.get("dias_total", 30)
        
        row.append(str(total_dias_mes))
        row.append("") # Dias no lab (placeholder)
        row.append(str(dias_lab))
        row.append(str(tardanzas) if tardanzas > 0 else "")
        
        table_data.append(row)
        
    # Anchos de columna
    # Hoja Legal Landscape ~ 33cm útiles.
    # N°: 0.8cm
    # Nombre: 6cm
    # DNI: 2cm
    # Dias: Resto repartido (31 días).
    # Totales: 1.5cm x 4 = 6cm.
    
    # Resto = 33 - (0.8 + 6 + 2 + 6) = 18.2 cm
    # 18.2 / 31 dias = 0.58 cm por dia. (Un poco estrecho, pero legible para iniciales)
    
    col_widths = [0.8*cm, 6*cm, 2.2*cm] + [0.6*cm] * len(columnas_dias) + [1.2*cm, 1.2*cm, 1.2*cm, 1.2*cm]
    
    t = Table(table_data, colWidths=col_widths, repeatRows=2)
    
    style_cmds = [
        # Grid general
        ('GRID', (0,0), (-1,-1), 0.5, colors.black),
        
        # Fuente general
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,0), (-1,-1), 7),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        
        # Cabecera
        ('FONTNAME', (0,0), (-1,1), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,1), 8),
        ('BACKGROUND', (0,0), (-1,1), colors.white),
        
        # Merge vertical para N, Nombre, DNI y Totales
        ('SPAN', (0,0), (0,1)), # N
        ('SPAN', (1,0), (1,1)), # Nombre
        ('SPAN', (2,0), (2,1)), # DNI
        
        # Merge vertical totales (indices negativos)
        ('SPAN', (-4,0), (-4,1)), 
        ('SPAN', (-3,0), (-3,1)),
        ('SPAN', (-2,0), (-2,1)),
        ('SPAN', (-1,0), (-1,1)),
        
        # Alineación izquierda para nombres
        ('ALIGN', (1,2), (1,-1), 'LEFT'),
        ('LEFTPADDING', (1,2), (1,-1), 4),
    ]
    
    # Colorear fines de semana (columnas)
    # Indices columnas dias empiezan en 3.
    for i, col in enumerate(columnas_dias):
        if col.get("es_fin_de_semana"):
            col_idx = 3 + i
            # Pintar toda la columna desde cabecera hasta abajo
            style_cmds.append(('BACKGROUND', (col_idx, 0), (col_idx, -1), colors.lightgrey))
            
    t.setStyle(TableStyle(style_cmds))
    elements.append(t)
    
    elements.append(Spacer(1, 20))
    
    # --- LEYENDA ---
    
    legend_data = [
        ["OBS.", "A", "ASISTIDOS", ":", "L/S", "LICENCIA POR SALUD", "OMI", "OMISIÓN"],
        ["", "C/S", "COMISION DE SERVICIO", ":", "VAC", "VACACIONES", "", ""],
        ["", "FAL", "FALTA", ":", "P/I", "PERMISO INTERNO", "", ""],
        ["", "FER", "FERIADO", ":", "P/C", "PERMISO COMPENSATORIO", "", ""],
        ["", "ONO", "ONOMASTICO", ":", "T/R", "TRABAJO REMOTO", "", ""],
        ["", "A/B", "ABANDONO", ":", "P/S", "PERMISO POR SALUD", "", ""],
        ["", "LS/G", "LICENCIA SIN GOCE", ":", "L/F", "LICENCIA POR FALLECIMIENTO", "", ""],
        ["", "P/E", "PERMISO POR ELECCIONES", ":", "C/J", "CITACION JUDICIAL", "", ""]
    ]
    
    # Estilo leyenda sin bordes
    t_legend = Table(legend_data, colWidths=[1.5*cm, 1*cm, 5*cm, 0.5*cm, 1*cm, 5*cm, 1*cm, 3*cm])
    t_legend.setStyle(TableStyle([
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,0), (-1,-1), 7),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'), # OBS column
    ]))
    
    elements.append(t_legend)
    
    # Footer
    elements.append(Spacer(1, 10))
    fecha_footer = datetime.now().strftime("%d/%m/%Y")
    footer = Paragraph(f"Querobamba, {fecha_footer}", ParagraphStyle('Footer', alignment=TA_CENTER, fontSize=9))
    elements.append(footer)
    
    doc.build(elements)
    
    return absolute_path
