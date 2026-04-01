"""
PDF Report Generator - FIXED VERSION
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from io import BytesIO
from typing import Dict, Any, List

from core.watermark_system import PDFWatermark


class PDFGenerator:
    """Generates comprehensive PDF reports"""
    
    def create(self, layout_data: Dict[str, Any], watermark_enabled: bool, 
               affiliate_products: List[Dict] = None) -> BytesIO:
        """Generate complete PDF report"""
        
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer, pagesize=A4,
            rightMargin=72, leftMargin=72,
            topMargin=72, bottomMargin=18
        )
        
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle', parent=styles['Heading1'],
            fontSize=24, textColor=HexColor('#2E7D32'),
            spaceAfter=30, alignment=TA_CENTER
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading', parent=styles['Heading2'],
            fontSize=16, textColor=HexColor('#388E3C'),
            spaceAfter=12
        )
        
        body_style = ParagraphStyle(
            'CustomBody', parent=styles['BodyText'],
            fontSize=11, alignment=TA_JUSTIFY, spaceAfter=12
        )
        
        warning_style = ParagraphStyle(
            'WarningStyle', parent=styles['BodyText'],
            fontSize=10, textColor=HexColor('#D32F2F'),
            alignment=TA_JUSTIFY, spaceAfter=12,
            borderWidth=1, borderColor=HexColor('#D32F2F'),
            borderPadding=10, backColor=HexColor('#FFEBEE')
        )
        
        story = []
        
        # PAGE 1: Title & Disclaimer
        story.append(Paragraph("HOMESTEAD SITE PLAN REPORT", title_style))
        story.append(Spacer(1, 0.3*inch))
        story.append(Paragraph(f"<b>Project:</b> {layout_data.get('project_name', 'My Homestead')}", styles['Heading2']))
        story.append(Spacer(1, 0.2*inch))
        
        # Disclaimer
        disclaimer = (
            "<b>IMPORTANT DISCLAIMER:</b> This report is generated for informational purposes only. "
            "All cost estimates, income projections, and recommendations are approximate and may vary "
            "based on local conditions, market rates, and individual circumstances. Before making any "
            "financial commitments or beginning construction/development on your property, please consult "
            "with qualified agricultural experts, financial advisors, and local authorities. "
            "chundalgardens.com assumes no liability for decisions made based on this report."
        )
        story.append(Paragraph(disclaimer, warning_style))
        story.append(Spacer(1, 0.2*inch))
        
        # Project details
        data = [
            ['Parameter', 'Value'],
            ['Total Area', f"{layout_data.get('total_sqft', 0):,} sq.ft."],
            ['Total Area', f"{layout_data.get('acres', 0):.2f} acres"],
            ['Plot Dimensions', f"{layout_data['dimensions']['L']:.0f}' × {layout_data['dimensions']['W']:.0f}'"],
            ['Category', layout_data.get('category', 'Unknown').title()],
            ['House Position', layout_data.get('house_position', 'Unknown')],
            ['Water Source', layout_data.get('water_source', 'Unknown')],
            ['Slope', layout_data.get('slope', 'Unknown')],
        ]
        
        t = Table(data, colWidths=[3*inch, 3*inch])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#4CAF50')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), HexColor('#E8F5E9')),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        story.append(t)
        
        # PAGE 2: Zone Breakdown
        story.append(PageBreak())
        story.append(Paragraph("Zone Analysis", heading_style))
        
        zone_data = [['Zone', 'Description', 'Percentage', 'Area (sq.ft.)']]
        zone_names = {
            'z0': 'Residential', 'z1': 'Kitchen Garden',
            'z2': 'Food Forest', 'z3': 'Pasture/Crops', 'z4': 'Buffer'
        }
        
        total = layout_data.get('total_sqft', 0)
        for zid, ratio in layout_data.get('zones', {}).items():
            zone_data.append([
                zid.upper(), zone_names.get(zid, zid),
                f"{ratio*100:.0f}%", f"{int(total * ratio):,}"
            ])
        
        zt = Table(zone_data, colWidths=[1*inch, 2.5*inch, 1.5*inch, 1.5*inch])
        zt.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#2E7D32')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BACKGROUND', (0, 1), (-1, -1), HexColor('#C8E6C9')),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        story.append(zt)
        
        # PAGE 3-4: Affiliate Products
        if affiliate_products:
            story.append(PageBreak())
            story.append(Paragraph("Recommended Products", title_style))
            story.append(Paragraph("Based on your homestead size and needs:", body_style))
            story.append(Spacer(1, 0.2*inch))
            
            for i, product in enumerate(affiliate_products[:6], 1):
                story.append(Paragraph(f"<b>{i}. {product.get('name', 'Product')}</b>", heading_style))
                story.append(Paragraph(product.get('description', ''), body_style))
                story.append(Paragraph(f"<b>Why we recommend:</b> {product.get('reason', '')}", body_style))
                
                cta_level = product.get('cta_level', 'medium')
                if cta_level == 'high':
                    cta_text = f"<font color='red'><b>⭐ HIGHLY RECOMMENDED:</b></font> <a href='{product.get('url', '#')}' color='blue'>Get it now - Special Discount</a>"
                elif cta_level == 'medium':
                    cta_text = f"<b>Recommended:</b> <a href='{product.get('url', '#')}' color='blue'>Check price on Amazon</a>"
                else:
                    cta_text = f"<a href='{product.get('url', '#')}' color='blue'>Learn more</a>"
                
                story.append(Paragraph(cta_text, body_style))
                story.append(Spacer(1, 0.15*inch))
        
        # Build PDF with appropriate watermark
        def get_watermark_func():
            if watermark_enabled:
                return PDFWatermark.add_visible_watermark
            else:
                return PDFWatermark.add_protection_watermark
        
        watermark_func = get_watermark_func()
        doc.build(story, onFirstPage=watermark_func, onLaterPages=watermark_func)
        
        buffer.seek(0)
        return buffer
