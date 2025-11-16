from flask import request, jsonify, send_file
from app.utils.decorators import conditional_jwt_required
from app.analytics import analytics
from app.models import Employee
from app import cache
import pandas as pd
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors

@analytics.route('/api/reports/export', methods=['GET'])
@conditional_jwt_required()
@cache.cached(timeout=300)
def export_report():
    format = request.args.get('format', 'csv')
    
    employees = Employee.query.all()
    employee_data = [{
        'id': emp.id,
        'first_name': emp.first_name,
        'last_name': emp.last_name,
        'email': emp.email,
        'department': emp.department,
        'position': emp.position,
        'hire_date': emp.hire_date,
        'is_active': emp.is_active,
        'status': emp.status
    } for emp in employees]
    df = pd.DataFrame(employee_data)

    if format == 'csv':
        buffer = BytesIO()
        df.to_csv(buffer, index=False)
        buffer.seek(0)
        return buffer.getvalue(), 200, {'Content-Type': 'text/csv', 'Content-Disposition': 'attachment; filename=report.csv'}
    
    elif format == 'excel':
        buffer = BytesIO()
        df.to_excel(buffer, index=False)
        buffer.seek(0)
        return buffer.getvalue(), 200, {'Content-Type': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 'Content-Disposition': 'attachment; filename=report.xlsx'}

    elif format == 'pdf':
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        elements = []
        
        data = [df.columns.to_list()] + df.values.tolist()
        
        table = Table(data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        elements.append(table)
        doc.build(elements)
        
        buffer.seek(0)
        return buffer.getvalue(), 200, {'Content-Type': 'application/pdf', 'Content-Disposition': 'attachment; filename=report.pdf'}

    else:
        return jsonify({'error': 'Invalid format specified'}), 400
