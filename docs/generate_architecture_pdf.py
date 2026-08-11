from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, ListFlowable, ListItem, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.graphics.shapes import Drawing, String, Rect, Line, PolyLine

output_path = "docs/AI_Opportunity_Hub_Architecture_Reference.pdf"

styles = getSampleStyleSheet()
if 'ClientTitle' not in styles.byName:
    styles.add(ParagraphStyle(name='ClientTitle', parent=styles['Title'], fontName='Helvetica-Bold', fontSize=20, leading=24, spaceAfter=12, textColor=colors.HexColor('#0f4c81')))
if 'ClientHeading' not in styles.byName:
    styles.add(ParagraphStyle(name='ClientHeading', parent=styles['Heading2'], fontName='Helvetica-Bold', fontSize=13, leading=16, spaceAfter=8, textColor=colors.HexColor('#0f4c81')))
if 'ClientBody' not in styles.byName:
    styles.add(ParagraphStyle(name='ClientBody', parent=styles['BodyText'], fontName='Helvetica', fontSize=10, leading=13, spaceAfter=6, textColor=colors.HexColor('#1f2937')))
if 'ClientBullet' not in styles.byName:
    styles.add(ParagraphStyle(name='ClientBullet', parent=styles['BodyText'], fontName='Helvetica', fontSize=10, leading=13, leftIndent=12, spaceAfter=4, textColor=colors.HexColor('#1f2937')))
if 'ClientCaption' not in styles.byName:
    styles.add(ParagraphStyle(name='ClientCaption', parent=styles['BodyText'], fontName='Helvetica-Oblique', fontSize=9, leading=11, textColor=colors.HexColor('#4b5563')))

story = []
story.append(Paragraph("AI Opportunity Hub\nReference Architecture", styles['ClientTitle']))
story.append(Paragraph("Client-ready architecture overview for solution evaluation, implementation planning, and reuse.", styles['ClientBody']))
story.append(Spacer(1, 0.3 * cm))

story.append(Paragraph("1. Solution Overview", styles['ClientHeading']))
story.append(Paragraph("AI Opportunity Hub is a reference solution that helps organizations capture ideas, evaluate technical feasibility, generate architecture packages, and prepare implementation guidance for AI initiatives.", styles['ClientBody']))
story.append(Spacer(1, 0.2 * cm))

story.append(Paragraph("2. Logical Layers", styles['ClientHeading']))
logical_items = [
    "Presentation Layer: React + Vite experience for idea intake and review",
    "Application Layer: FastAPI endpoints for validation, orchestration, and package generation",
    "Intelligence Layer: context evaluation and architecture decision logic",
    "Data Layer: local persistence, document storage, and artifact management",
    "Integration Layer: deployment readiness for Azure services, authentication, and future enterprise connectors"
]
story.append(ListFlowable([ListItem(Paragraph(item, styles['ClientBullet'])) for item in logical_items], bulletType='bullet'))
story.append(Spacer(1, 0.3 * cm))

story.append(Paragraph("3. Core Runtime Flow", styles['ClientHeading']))
flow_data = [
    ["User", "Frontend", "Idea capture"],
    ["API", "FastAPI", "Validation + orchestration"],
    ["Context Engine", "Domain Logic", "Business/technical assessment"],
    ["Architecture Package", "Output", "Components, risks, deployment steps"]
]
flow_table = Table(flow_data, colWidths=[3.2 * cm, 3.2 * cm, 6.4 * cm], repeatRows=1)
flow_table.setStyle(TableStyle([
    ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0f4c81')),
    ('TEXTCOLOR', (0,0), (-1,0), colors.white),
    ('ALIGN', (0,0), (-1,-1), 'LEFT'),
    ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
    ('FONTSIZE', (0,0), (-1,-1), 9),
    ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#d1d5db')),
    ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.HexColor('#f9fafb'), colors.white]),
]))
story.append(flow_table)
story.append(Spacer(1, 0.3 * cm))

story.append(Paragraph("4. Reference Deployment Model", styles['ClientHeading']))
story.append(Paragraph("The architecture supports a local MVP deployment and a cloud-aligned Azure deployment path. The current implementation is optimized for rapid demonstration, while the structure is prepared for enterprise evolution.", styles['ClientBody']))
story.append(Spacer(1, 0.2 * cm))

story.append(Paragraph("5. Recommended Reuse Scenarios", styles['ClientHeading']))
reuse_items = [
    "Use the frontend and API layout as a foundation for a custom innovation portal",
    "Reuse the validation workflow for internal AI opportunity review programs",
    "Adapt the storage abstraction to enterprise databases and document services",
    "Replace demo authentication with Microsoft Entra ID for production rollout"
]
story.append(ListFlowable([ListItem(Paragraph(item, styles['ClientBullet'])) for item in reuse_items], bulletType='bullet'))
story.append(Spacer(1, 0.3 * cm))

story.append(Paragraph("6. Architecture Summary", styles['ClientHeading']))
story.append(Paragraph("A visual summary of the solution follows.", styles['ClientCaption']))

# Overview diagram
overview = Drawing(16 * cm, 6 * cm)
overview.add(Rect(0.2 * cm, 0.2 * cm, 15.6 * cm, 5.6 * cm, fillColor=colors.HexColor('#f8fbff'), strokeColor=colors.HexColor('#d7e7f7'), strokeWidth=1))
box_style = dict(fillColor=colors.HexColor('#e8f2ff'), strokeColor=colors.HexColor('#0f4c81'), strokeWidth=1.2)
overview.add(Rect(1.0 * cm, 3.5 * cm, 3.0 * cm, 1.2 * cm, **box_style))
overview.add(String(1.4 * cm, 3.95 * cm, 'Users / Clients'))
overview.add(Rect(5.0 * cm, 3.5 * cm, 3.0 * cm, 1.2 * cm, **box_style))
overview.add(String(5.45 * cm, 3.95 * cm, 'Frontend'))
overview.add(Rect(9.0 * cm, 3.5 * cm, 3.0 * cm, 1.2 * cm, **box_style))
overview.add(String(9.35 * cm, 3.95 * cm, 'API / Orchestrator'))
overview.add(Rect(5.0 * cm, 1.0 * cm, 3.0 * cm, 1.2 * cm, **box_style))
overview.add(String(5.25 * cm, 1.45 * cm, 'Data / Storage'))
for x1, y1, x2, y2 in [(4.0, 4.1, 5.0, 4.1), (8.0, 4.1, 9.0, 4.1), (6.5, 3.5, 6.5, 2.2)]:
    overview.add(Line(x1 * cm, y1 * cm, x2 * cm, y2 * cm, strokeColor=colors.HexColor('#0f4c81'), strokeWidth=1.2))
overview.add(PolyLine([(3.5*cm, 4.1*cm),(3.8*cm, 4.1*cm)], strokeColor=colors.HexColor('#0f4c81'), strokeWidth=1.2))
overview.add(PolyLine([(8.2*cm, 4.1*cm),(8.8*cm, 4.1*cm)], strokeColor=colors.HexColor('#0f4c81'), strokeWidth=1.2))
overview.add(PolyLine([(6.5*cm, 3.5*cm),(6.5*cm, 2.2*cm)], strokeColor=colors.HexColor('#0f4c81'), strokeWidth=1.2))
story.append(overview)
story.append(Spacer(1, 0.3 * cm))
story.append(Paragraph("This document is intended as a client-facing reference for architecture understanding, reuse, and implementation planning.", styles['ClientCaption']))

story.append(PageBreak())
story.append(Paragraph("Tab 1 - System Flow Diagram", styles['ClientHeading']))
story.append(Paragraph("This view illustrates how a request moves through the platform from user interaction to generated architecture output.", styles['ClientBody']))
story.append(Spacer(1, 0.25 * cm))

flow_diagram = Drawing(16 * cm, 8 * cm)
flow_diagram.add(Rect(0.2 * cm, 0.2 * cm, 15.6 * cm, 7.6 * cm, fillColor=colors.HexColor('#fcfeff'), strokeColor=colors.HexColor('#d7e7f7'), strokeWidth=1))
flow_boxes = [
    (1.0, 5.8, 3.2, 1.2, 'User / Client'),
    (5.0, 5.8, 3.2, 1.2, 'Frontend'),
    (9.0, 5.8, 3.2, 1.2, 'API Layer'),
    (5.0, 3.4, 3.2, 1.2, 'Validation Logic'),
    (5.0, 1.0, 3.2, 1.2, 'Architecture Output'),
    (11.0, 3.4, 3.2, 1.2, 'Storage / Artifacts')
]
for x, y, w, h, label in flow_boxes:
    flow_diagram.add(Rect(x * cm, y * cm, w * cm, h * cm, fillColor=colors.HexColor('#edf6ff'), strokeColor=colors.HexColor('#0f4c81'), strokeWidth=1.1))
    flow_diagram.add(String((x + 0.4) * cm, (y + 0.5) * cm, label))
for x1, y1, x2, y2 in [(4.2, 6.4, 5.0, 6.4), (8.2, 6.4, 9.0, 6.4), (6.6, 5.8, 6.6, 4.6), (8.2, 4.0, 11.0, 4.0), (11.0, 3.4, 10.2, 2.2)]:
    flow_diagram.add(Line(x1 * cm, y1 * cm, x2 * cm, y2 * cm, strokeColor=colors.HexColor('#0f4c81'), strokeWidth=1.1))
flow_diagram.add(PolyLine([(6.6*cm, 3.4*cm),(6.6*cm, 2.2*cm)], strokeColor=colors.HexColor('#0f4c81'), strokeWidth=1.1))
flow_diagram.add(PolyLine([(8.2*cm, 6.4*cm),(8.8*cm, 6.4*cm)], strokeColor=colors.HexColor('#0f4c81'), strokeWidth=1.1))
story.append(flow_diagram)
story.append(Spacer(1, 0.3 * cm))
story.append(Paragraph("Flow summary: capture idea → validate feasibility → generate architecture package → persist outputs and share results.", styles['ClientCaption']))

story.append(PageBreak())
story.append(Paragraph("Tab 2 - Component Diagram", styles['ClientHeading']))
story.append(Paragraph("This view shows the main software components and their interaction boundaries for implementation and extension.", styles['ClientBody']))
story.append(Spacer(1, 0.25 * cm))

component_diagram = Drawing(16 * cm, 8 * cm)
component_diagram.add(Rect(0.2 * cm, 0.2 * cm, 15.6 * cm, 7.6 * cm, fillColor=colors.HexColor('#fcfeff'), strokeColor=colors.HexColor('#d7e7f7'), strokeWidth=1))
component_boxes = [
    (1.0, 6.0, 3.2, 1.2, 'Frontend UI'),
    (5.0, 6.0, 3.2, 1.2, 'API Services'),
    (9.0, 6.0, 3.2, 1.2, 'Authentication'),
    (3.0, 3.6, 3.2, 1.2, 'Validation Engine'),
    (7.0, 3.6, 3.2, 1.2, 'Context Engine'),
    (5.0, 1.2, 3.2, 1.2, 'Persistence / Blob'),
]
for x, y, w, h, label in component_boxes:
    component_diagram.add(Rect(x * cm, y * cm, w * cm, h * cm, fillColor=colors.HexColor('#f2f8ff'), strokeColor=colors.HexColor('#2563eb'), strokeWidth=1.1))
    component_diagram.add(String((x + 0.3) * cm, (y + 0.5) * cm, label))
for x1, y1, x2, y2 in [(4.2, 6.6, 5.0, 6.6), (8.2, 6.6, 9.0, 6.6), (4.6, 3.6, 5.0, 2.4), (8.6, 3.6, 7.0, 2.4), (6.6, 3.6, 6.6, 2.4)]:
    component_diagram.add(Line(x1 * cm, y1 * cm, x2 * cm, y2 * cm, strokeColor=colors.HexColor('#2563eb'), strokeWidth=1.1))
component_diagram.add(PolyLine([(6.6*cm, 3.6*cm),(6.6*cm, 2.4*cm)], strokeColor=colors.HexColor('#2563eb'), strokeWidth=1.1))
story.append(component_diagram)
story.append(Spacer(1, 0.3 * cm))
story.append(Paragraph("Component summary: UI, API, validation, context, storage and identity layers can evolve independently for future enterprise deployments.", styles['ClientCaption']))

story.append(PageBreak())
story.append(Paragraph("Tab 3 - Frontend Flow Diagram", styles['ClientHeading']))
story.append(Paragraph("This view shows how the user interface drives the ideation and review experience end-to-end.", styles['ClientBody']))
story.append(Spacer(1, 0.25 * cm))

frontend_diagram = Drawing(16 * cm, 8 * cm)
frontend_diagram.add(Rect(0.2 * cm, 0.2 * cm, 15.6 * cm, 7.6 * cm, fillColor=colors.HexColor('#fcfeff'), strokeColor=colors.HexColor('#d7e7f7'), strokeWidth=1))
frontend_boxes = [
    (1.0, 6.0, 3.0, 1.2, 'Login / Session'),
    (4.8, 6.0, 3.0, 1.2, 'Idea Capture'),
    (8.6, 6.0, 3.0, 1.2, 'Context Review'),
    (4.8, 3.6, 3.0, 1.2, 'Technical Validation'),
    (4.8, 1.2, 3.0, 1.2, 'Results / Actions')
]
for x, y, w, h, label in frontend_boxes:
    frontend_diagram.add(Rect(x * cm, y * cm, w * cm, h * cm, fillColor=colors.HexColor('#eef7ff'), strokeColor=colors.HexColor('#0f4c81'), strokeWidth=1.1))
    frontend_diagram.add(String((x + 0.3) * cm, (y + 0.5) * cm, label))
for x1, y1, x2, y2 in [(4.0, 6.6, 4.8, 6.6), (7.8, 6.6, 8.6, 6.6), (6.3, 3.6, 6.3, 2.4), (6.3, 3.6, 6.3, 2.4)]:
    frontend_diagram.add(Line(x1 * cm, y1 * cm, x2 * cm, y2 * cm, strokeColor=colors.HexColor('#0f4c81'), strokeWidth=1.1))
frontend_diagram.add(PolyLine([(6.3*cm, 3.6*cm),(6.3*cm, 2.4*cm)], strokeColor=colors.HexColor('#0f4c81'), strokeWidth=1.1))
story.append(frontend_diagram)
story.append(Spacer(1, 0.3 * cm))
story.append(Paragraph("Frontend flow: session → capture idea → review context → validate and present guidance.", styles['ClientCaption']))

story.append(PageBreak())
story.append(Paragraph("Tab 4 - Backend and API Layer Flow", styles['ClientHeading']))
story.append(Paragraph("This view describes the backend orchestration and API interactions behind the experience.", styles['ClientBody']))
story.append(Spacer(1, 0.25 * cm))

backend_diagram = Drawing(16 * cm, 8 * cm)
backend_diagram.add(Rect(0.2 * cm, 0.2 * cm, 15.6 * cm, 7.6 * cm, fillColor=colors.HexColor('#fcfeff'), strokeColor=colors.HexColor('#d7e7f7'), strokeWidth=1))
backend_boxes = [
    (1.0, 6.0, 3.2, 1.2, 'Client Request'),
    (4.8, 6.0, 3.2, 1.2, 'API Router'),
    (8.8, 6.0, 3.2, 1.2, 'Auth / Session'),
    (4.8, 3.6, 3.2, 1.2, 'Business Services'),
    (8.8, 3.6, 3.2, 1.2, 'Validation + Context'),
    (6.8, 1.2, 3.2, 1.2, 'Storage / Output')
]
for x, y, w, h, label in backend_boxes:
    backend_diagram.add(Rect(x * cm, y * cm, w * cm, h * cm, fillColor=colors.HexColor('#f5f9ff'), strokeColor=colors.HexColor('#2563eb'), strokeWidth=1.1))
    backend_diagram.add(String((x + 0.3) * cm, (y + 0.5) * cm, label))
for x1, y1, x2, y2 in [(4.2, 6.6, 4.8, 6.6), (8.0, 6.6, 8.8, 6.6), (6.4, 3.6, 6.8, 2.4), (9.6, 3.6, 8.8, 2.4)]:
    backend_diagram.add(Line(x1 * cm, y1 * cm, x2 * cm, y2 * cm, strokeColor=colors.HexColor('#2563eb'), strokeWidth=1.1))
backend_diagram.add(PolyLine([(6.8*cm, 3.6*cm),(6.8*cm, 2.4*cm)], strokeColor=colors.HexColor('#2563eb'), strokeWidth=1.1))
story.append(backend_diagram)
story.append(Spacer(1, 0.3 * cm))
story.append(Paragraph("Backend flow: route request → authenticate → invoke services → persist artifacts and return response.", styles['ClientCaption']))

# Build pdf
pdf = SimpleDocTemplate(output_path, pagesize=A4, rightMargin=2.2 * cm, leftMargin=2.2 * cm, topMargin=2.0 * cm, bottomMargin=2.0 * cm)
pdf.build(story)
print(output_path)
