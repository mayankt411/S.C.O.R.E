import json
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
import io

class DataManager:
    """Handles clinical reporting, PDF generation, and FHIR integration"""
    
    def __init__(self):
        self.export_dir = "exports/"
        
    def generate_pdf_report(self, patient_data: dict, prediction: dict, responses: list) -> io.BytesIO:
        """Generate a clinical PDF report and return as a byte stream"""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []
        
        # Header
        story.append(Paragraph("NeuroCognitive AI Assessment Report", styles['Title']))
        story.append(Spacer(1, 12))
        
        # Patient & Test Info
        story.append(Paragraph(f"<b>Session ID:</b> {patient_data.get('session_id', 'N/A')}", styles['Normal']))
        story.append(Paragraph(f"<b>Date:</b> {datetime.now().strftime('%Y-%m-%d %H:%M')}", styles['Normal']))
        story.append(Spacer(1, 12))
        
        # Disease Prediction Summary
        story.append(Paragraph("AI Diagnostic Summary", styles['Heading2']))
        story.append(Paragraph(f"<b>Predicted Condition:</b> {prediction.get('disease_type', 'N/A')}", styles['Normal']))
        story.append(Paragraph(f"<b>Severity Stage:</b> {prediction.get('severity', 'N/A')}", styles['Normal']))
        story.append(Paragraph(f"<b>Confidence:</b> {prediction.get('confidence', 0):.1f}%", styles['Normal']))
        story.append(Paragraph(f"<b>Risk Level:</b> {prediction.get('risk_level', 'N/A')}", styles['Normal']))
        story.append(Spacer(1, 12))
        
        # Table of Results
        story.append(Paragraph("Individual Task Performance", styles['Heading2']))
        data = [["Domain", "Question", "Score", "Status"]]
        for r in responses:
            data.append([r['domain'], r['question_text'][:30] + "...", f"{r['earned']}/{r['max_points']}", r['status']])
            
        t = Table(data, colWidths=[80, 200, 60, 60])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ]))
        story.append(t)
        
        # Build PDF
        doc.build(story)
        buffer.seek(0)
        return buffer

    def export_fhir_json(self, prediction: dict, responses: list) -> str:
        """Generate a FHIR-compliant DiagnosticReport JSON"""
        fhir_bundle = {
            "resourceType": "DiagnosticReport",
            "status": "final",
            "category": [{
                "coding": [{
                    "system": "http://terminology.hl7.org/CodeSystem/v2-0074",
                    "code": "GE",
                    "display": "General"
                }]
            }],
            "code": {
                "coding": [{
                    "system": "http://loinc.org",
                    "code": "72133-2",
                    "display": "Mini-Mental State Examination"
                }]
            },
            "conclusion": f"{prediction.get('disease_type')} - {prediction.get('severity')}",
            "issued": datetime.now().isoformat(),
            "resultsInterpreter": ["AI-Model-v2.0"],
            "result": []
        }
        
        # Map responses to Observations
        for r in responses:
            fhir_bundle['result'].append({
                "resourceType": "Observation",
                "status": "final",
                "code": {"text": r['question_text']},
                "valueQuantity": {
                    "value": float(r['earned']),
                    "unit": "points"
                }
            })
            
        return json.dumps(fhir_bundle, indent=2)

    def mock_ehr_push(self, fhir_data: str) -> bool:
        """Simulate pushing data to Epic/Cerner EHR APIs"""
        print(f"DEBUG: Pushing FHIR data to EHR interface...")
        # In a real scenario, this would use OAuth2 and a POST request to a FHIR server
        return True
