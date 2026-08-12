import os
import io
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

DISCLAIMER_TEXT = "This prediction is based solely on historical data patterns and should not be interpreted as a forecast of future real-world events."

def create_pdf_briefing(narrative, kpis, chart_img_path=None, output_path=None):
    """
    Generate a professional ReportLab PDF briefing containing KPIs, Narrative, Chart, and Disclaimer Footer.
    Returns bytes or writes to file.
    """
    buffer = io.BytesIO() if output_path is None else output_path
    
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=54
    )
    
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=colors.HexColor('#0F172A')
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#64748B')
    )
    
    section_heading = ParagraphStyle(
        'SectionHeading',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=16,
        textColor=colors.HexColor('#1E293B'),
        spaceBefore=12,
        spaceAfter=6
    )
    
    body_style = ParagraphStyle(
        'BodyTextCustom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=15,
        textColor=colors.HexColor('#334155'),
        spaceAfter=10
    )
    
    disclaimer_style = ParagraphStyle(
        'DisclaimerText',
        parent=styles['Italic'],
        fontName='Helvetica-Oblique',
        fontSize=8,
        leading=11,
        textColor=colors.HexColor('#64748B'),
        alignment=1  # Centered
    )
    
    elements = []
    
    # Header Title
    elements.append(Paragraph("SCOPE | Strategic Crime Observation & Prediction Engine", title_style))
    elements.append(Paragraph("AUTOMATED STRATEGIC THREAT BRIEFING", subtitle_style))
    elements.append(Spacer(1, 10))
    elements.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#3B82F6'), spaceAfter=15))
    
    # KPI Table
    kpi_data = [
        [
            Paragraph("<b>Total Incidents</b>", subtitle_style),
            Paragraph("<b>Total Fatalities</b>", subtitle_style),
            Paragraph("<b>Primary Threat Driver</b>", subtitle_style),
            Paragraph("<b>Region Covered</b>", subtitle_style)
        ],
        [
            Paragraph(f"<font size=14 color='#0F172A'><b>{kpis.get('total_incidents', 'N/A')}</b></font>", body_style),
            Paragraph(f"<font size=14 color='#EF4444'><b>{kpis.get('total_fatalities', 'N/A')}</b></font>", body_style),
            Paragraph(f"<font size=12 color='#0F172A'><b>{kpis.get('primary_driver', 'N/A')}</b></font>", body_style),
            Paragraph(f"<font size=12 color='#0F172A'><b>{kpis.get('region', 'Global')}</b></font>", body_style)
        ]
    ]
    
    t = Table(kpi_data, colWidths=[130, 130, 150, 130])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F8FAFC')),
        ('PADDING', (0, 0), (-1, -1), 8),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LINEBELOW', (0, 0), (-1, 0), 1, colors.HexColor('#E2E8F0')),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#CBD5E1'))
    ]))
    elements.append(t)
    elements.append(Spacer(1, 15))
    
    # Narrative Section
    elements.append(Paragraph("Strategic Intelligence Assessment", section_heading))
    for paragraph in narrative.split('\n\n'):
        elements.append(Paragraph(paragraph.replace('\n', '<br/>'), body_style))
    elements.append(Spacer(1, 10))
    
    # Embedded Chart Image
    if chart_img_path and os.path.exists(chart_img_path):
        elements.append(Paragraph("Trend & Threat Distribution Analysis", section_heading))
        img = Image(chart_img_path, width=500, height=230)
        elements.append(img)
        elements.append(Spacer(1, 15))
        
    elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#CBD5E1'), spaceBefore=15, spaceAfter=10))
    elements.append(Paragraph(DISCLAIMER_TEXT, disclaimer_style))
    
    doc.build(elements)
    
    if output_path is None:
        buffer.seek(0)
        return buffer.getvalue()
    return output_path
