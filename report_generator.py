"""
JouleLens — Report Generator.
PDF and JSON export for profiling run reports.
"""

import json
from io import BytesIO
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.colors import HexColor, black, white
from reportlab.lib.units import inch, mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT


def generate_pdf_report(run_dict):
    """Generate a PDF report for a profiling run. Returns BytesIO buffer."""
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        rightMargin=25*mm, leftMargin=25*mm,
        topMargin=20*mm, bottomMargin=20*mm,
    )
    
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'JLTitle', parent=styles['Heading1'],
        fontSize=22, textColor=HexColor('#00FF88'),
        spaceAfter=6, alignment=TA_CENTER,
    )
    subtitle_style = ParagraphStyle(
        'JLSubtitle', parent=styles['Normal'],
        fontSize=10, textColor=HexColor('#8B949E'),
        alignment=TA_CENTER, spaceAfter=20,
    )
    heading_style = ParagraphStyle(
        'JLHeading', parent=styles['Heading2'],
        fontSize=14, textColor=HexColor('#58A6FF'),
        spaceBefore=16, spaceAfter=8,
    )
    body_style = ParagraphStyle(
        'JLBody', parent=styles['Normal'],
        fontSize=10, textColor=black, spaceAfter=6,
    )
    score_style = ParagraphStyle(
        'JLScore', parent=styles['Normal'],
        fontSize=28, alignment=TA_CENTER,
        spaceBefore=10, spaceAfter=10,
        textColor=HexColor('#00FF88'),
    )
    footer_style = ParagraphStyle(
        'JLFooter', parent=styles['Normal'],
        fontSize=8, textColor=HexColor('#8B949E'),
        alignment=TA_CENTER, spaceBefore=30,
    )
    
    elements = []
    
    # Header
    elements.append(Paragraph("JouleLens Energy Report", title_style))
    elements.append(Paragraph("The energy profiler that makes every Joule visible", subtitle_style))
    elements.append(HRFlowable(width="100%", thickness=1, color=HexColor('#30363D')))
    elements.append(Spacer(1, 10))
    
    # Run Metadata
    elements.append(Paragraph("Run Details", heading_style))
    run_id = run_dict.get('id', 'N/A')
    ts = run_dict.get('timestamp', run_dict.get('created_at', 'N/A'))
    region = run_dict.get('region', 'N/A')
    workload = run_dict.get('workload_type', 'N/A')
    
    meta_data = [
        ['Run ID', str(run_id)],
        ['Timestamp', str(ts)],
        ['Region', str(region)],
        ['Workload Type', str(workload)],
    ]
    meta_table = Table(meta_data, colWidths=[120, 350])
    meta_table.setStyle(TableStyle([
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('TEXTCOLOR', (0, 0), (0, -1), HexColor('#333333')),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
    ]))
    elements.append(meta_table)
    elements.append(Spacer(1, 10))
    
    # Code Snippet
    elements.append(Paragraph("Code Snippet", heading_style))
    code = run_dict.get('code_snippet', '')
    if len(code) > 500:
        code = code[:500] + '...'
    code_display = code.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('\n', '<br/>')
    code_style = ParagraphStyle('Code', parent=styles['Code'], fontSize=8, leading=11)
    elements.append(Paragraph(code_display, code_style))
    elements.append(Spacer(1, 10))
    
    # Joule Score
    elements.append(Paragraph("Joule Score", heading_style))
    score = run_dict.get('joule_score', 'C')
    score_colors = {"A": "#00FF88", "B": "#3FB950", "C": "#F0A500", "D": "#FF8C00", "F": "#FF4B4B"}
    s_style = ParagraphStyle('S', parent=score_style, textColor=HexColor(score_colors.get(score, '#F0A500')))
    elements.append(Paragraph(f"Score: {score}", s_style))
    elements.append(Spacer(1, 6))
    
    # Energy Metrics
    elements.append(Paragraph("Energy Metrics", heading_style))
    energy_data = [
        ['Metric', 'Value'],
        ['Total Energy', f"{run_dict.get('total_joules', 0):.4f} J"],
        ['Energy (Wh)', f"{run_dict.get('total_wh', 0):.6f} Wh"],
        ['Estimated Cost', f"₹{run_dict.get('cost_usd', 0):.6f}"],
        ['CO2 Emissions', f"{run_dict.get('co2_grams', 0):.4f} g"],
        ['Carbon Intensity', f"{run_dict.get('carbon_intensity', 0)} gCO2/kWh"],
    ]
    energy_table = Table(energy_data, colWidths=[180, 290])
    energy_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), HexColor('#58A6FF')),
        ('TEXTCOLOR', (0, 0), (-1, 0), white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#CCCCCC')),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [HexColor('#F8F8F8'), white]),
    ]))
    elements.append(energy_table)
    elements.append(Spacer(1, 10))
    
    # Function Breakdown
    fb_raw = run_dict.get('function_breakdown', '[]')
    if isinstance(fb_raw, str):
        try:
            fb = json.loads(fb_raw)
        except json.JSONDecodeError:
            fb = []
    else:
        fb = fb_raw
    
    if fb:
        elements.append(Paragraph("Function Breakdown", heading_style))
        fb_header = [['Function', 'Calls', 'Time (ms)', 'Joules', '% Total', 'Grade']]
        for f in fb[:10]:
            fb_header.append([
                str(f.get('function_name', '')),
                str(f.get('calls', 0)),
                f"{f.get('time_ms', 0):.2f}",
                f"{f.get('joules', 0):.4f}",
                f"{f.get('percent_of_total', 0):.1f}%",
                str(f.get('grade', '')),
            ])
        fb_table = Table(fb_header, colWidths=[130, 50, 70, 70, 60, 50])
        fb_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#00CC6A')),
            ('TEXTCOLOR', (0, 0), (-1, 0), HexColor('#0D1117')),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#CCCCCC')),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [HexColor('#F8F8F8'), white]),
        ]))
        elements.append(fb_table)
        elements.append(Spacer(1, 10))
    
    # AI Refactor Summary
    if run_dict.get('ai_refactor_available'):
        elements.append(Paragraph("AI Green Refactor Summary", heading_style))
        ai_summary = run_dict.get('ai_summary', 'No summary available.')
        elements.append(Paragraph(ai_summary, body_style))
        reduction = run_dict.get('ai_energy_reduction_percent')
        if reduction:
            elements.append(Paragraph(f"Estimated Energy Reduction: -{reduction}%", body_style))
        elements.append(Spacer(1, 10))
    
    # Footer
    elements.append(HRFlowable(width="100%", thickness=0.5, color=HexColor('#CCCCCC')))
    gen_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    elements.append(Paragraph(f"Generated by JouleLens v1.0 on {gen_time}", footer_style))
    elements.append(Paragraph("Making Every Joule Count", footer_style))
    
    doc.build(elements)
    buffer.seek(0)
    return buffer


def generate_json_report(run_dict):
    """Generate a JSON report string for a profiling run."""
    report = dict(run_dict)
    
    # Parse function_breakdown from JSON string back to dict
    fb = report.get('function_breakdown', '[]')
    if isinstance(fb, str):
        try:
            report['function_breakdown'] = json.loads(fb)
        except json.JSONDecodeError:
            report['function_breakdown'] = []
    
    return json.dumps(report, indent=2, default=str)
