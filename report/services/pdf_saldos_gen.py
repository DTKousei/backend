
import os
import uuid
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import landscape, legal, A3
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib.enums import TA_CENTER

STORAGE_DIR = "storage"

if not os.path.exists(STORAGE_DIR):
    os.makedirs(STORAGE_DIR)

def generate_saldos_pdf_report(data: list, anio: int) -> str:
    """
    Generates a PDF report for Incidence Balances (Saldos).
    Layout: 
      - Header: N°, Apellidos y Nombres, DNI
      - Dynamic Columns: One per Incidence Type found in data (Using Short Code).
      - Sub-columns: Consumido | Restante
      - Footer: Legend with Codes and Full Names.
    """
    
    # 1. Identify all unique incidence types
    # We need a map of type_id -> {name, code}
    
    unique_types = {} # type_id -> {name, code}
    
    for emp in data:
        saldos = emp.get("saldos", [])
        for s in saldos:
            tid = s.get("tipo_id")
            tnam = s.get("tipo_nombre", "Unknown")
            # Extract code provided by user or derive it
            tcod = s.get("tipo_codigo")
            if not tcod:
                # Fallback: First 3 chars of name upper case
                tcod = tnam[:3].upper()
                
            if tid:
                unique_types[tid] = {"name": tnam, "code": tcod}
                
    # Sort types by code (or name)
    # List of (id, info_dict)
    sorted_types = sorted(unique_types.items(), key=lambda x: x[1]["code"]) 
    
    # 2. Setup PDF
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_id = uuid.uuid4().hex[:6]
    filename = f"reporte_saldos_{anio}_{timestamp}_{unique_id}.pdf"
    file_path = os.path.join(STORAGE_DIR, filename)
    absolute_path = os.path.abspath(file_path)
    
    # Use A3 Landscape
    page_size = landscape(A3) 
    
    doc = SimpleDocTemplate(absolute_path, pagesize=page_size, 
                            rightMargin=10, leftMargin=10, topMargin=20, bottomMargin=20)
    elements = []
    styles = getSampleStyleSheet()
    
    # Title
    title_style = ParagraphStyle('Title', parent=styles['Heading1'], alignment=TA_CENTER, fontSize=16)
    elements.append(Paragraph(f"REPORTE DE SALDOS DE INCIDENCIAS - {anio}", title_style))
    elements.append(Spacer(1, 20))
    
    # 3. Build Table Data
    h1 = ["N°", "APELLIDOS Y NOMBRES", "DNI"]
    h2 = ["", "", ""]
    
    for _, info in sorted_types:
        h1.append(info["code"]) # Show CODE in header
        h1.append("") # Placeholder for span
        
        h2.append("Cons.")
        h2.append("Rest.")
        
    table_data = [h1, h2]
    
    # Rows
    for idx, emp in enumerate(data, start=1):
        row = [
            str(idx),
            emp.get("nombre_empleado", "")[:40],
            emp.get("dni", "")
        ]
        
        # Build map of this employee's saldos for quick lookup
        emp_saldos_map = {} # type_id -> {consumido, restante}
        for s in emp.get("saldos", []):
            tid = s.get("tipo_id")
            if tid:
                c_dias = s.get("consumido", {}).get("dias", 0)
                r_dias = s.get("restante", {}).get("dias") 
                emp_saldos_map[tid] = (c_dias, r_dias)
                
        # Fill columns for each sorted type
        for tid, _ in sorted_types:
            if tid in emp_saldos_map:
                c, r = emp_saldos_map[tid]
                c_str = str(c) if c is not None else "-"
                r_str = str(r) if r is not None else "∞"
            else:
                c_str = "-"
                r_str = "-"
                
            row.append(c_str)
            row.append(r_str)
            
        table_data.append(row)
        
    # 4. Main Table Styles
    # Widths
    # Base: 1cm, 8cm, 2.5cm.
    # Types: 1.5cm each subcol (3cm total per type)
    col_widths = [1*cm, 8*cm, 2.5*cm]
    for _ in sorted_types:
        col_widths.append(1.2*cm) # Cons
        col_widths.append(1.2*cm) # Rest
        
    t = Table(table_data, colWidths=col_widths, repeatRows=2)
    
    style_cmds = [
        # Grid
        ('GRID', (0,0), (-1,-1), 0.5, colors.black),
        
        # Header
        ('FONTNAME', (0,0), (-1,1), 'Helvetica-Bold'),
        ('ALIGN', (0,0), (-1,1), 'CENTER'),
        ('VALIGN', (0,0), (-1,1), 'MIDDLE'),
        ('BACKGROUND', (0,0), (-1,1), colors.lightgrey),
        
        # Spans Fixed Cols
        ('SPAN', (0,0), (0,1)), # N
        ('SPAN', (1,0), (1,1)), # Nombre
        ('SPAN', (2,0), (2,1)), # DNI
        
        # Data
        ('FONTNAME', (0,2), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,2), (-1,-1), 8),
        ('ALIGN', (0,2), (0,-1), 'CENTER'), # N
        ('ALIGN', (1,2), (1,-1), 'LEFT'),   # Name
        ('ALIGN', (2,2), (-1,-1), 'CENTER'), # Rest (DNI + values)
        ('LEFTPADDING', (1,2), (1,-1), 4),
    ]
    
    # Spans for Types headers
    for i in range(len(sorted_types)):
        start_col = 3 + 2*i
        end_col = start_col + 1
        style_cmds.append(('SPAN', (start_col, 0), (end_col, 0)))
        
    t.setStyle(TableStyle(style_cmds))
    elements.append(t)
    
    # 5. Legend (Footer)
    elements.append(Spacer(1, 25))
    elements.append(Paragraph("LEYENDA DE CÓDIGOS", ParagraphStyle('Heading2', fontSize=10, spaceAfter=5)))
    
    # Build Legend Table
    # Rows of [Code, Name]
    legend_data = []
    # Add headers for legend? Or just data. Just data is cleaner.
    legend_header = ["CÓDIGO", "DESCRIPCIÓN"]
    legend_data.append(legend_header)
    
    for _, info in sorted_types:
        legend_data.append([info["code"], info["name"]])
        
    t_legend = Table(legend_data, colWidths=[3*cm, 10*cm], hAlign='LEFT')
    t_legend.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'), # Header
        ('BACKGROUND', (0,0), (-1,0), colors.whitesmoke),
        ('FONTSIZE', (0,0), (-1,-1), 9),
        ('ALIGN', (0,0), (0,-1), 'CENTER'), # Code centered
        ('ALIGN', (1,0), (1,-1), 'LEFT'),   # Name left
    ]))
    
    elements.append(t_legend)
    
    # Build
    doc.build(elements)
    return absolute_path

