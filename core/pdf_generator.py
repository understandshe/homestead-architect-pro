"""
Professional PDF Report Generator â€” v3 FINAL
Homestead Architect Pro 2026

Fixes:
  - Currency symbols (Rs, NGN) rendered via DejaVu TTF font (no square boxes)
  - Cover page via closure (no global variable NameError)
  - 3D screenshot can be embedded as extra page
  - All en-dashes use ASCII hyphen to avoid encoding issues in Helvetica
  - Spacer size fixed (no LayoutError)
"""

from io import BytesIO
from datetime import date
from typing import Dict, Any, Optional

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, HRFlowable, Image as RLImage, KeepTogether,
)
from reportlab.platypus.flowables import Flowable
from reportlab.pdfgen import canvas as rl_canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# Register Unicode fonts once
_FONTS_REGISTERED = False
def _ensure_fonts():
    global _FONTS_REGISTERED
    if _FONTS_REGISTERED:
        return
    try:
        pdfmetrics.registerFont(TTFont('DejaVu',
            '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'))
        pdfmetrics.registerFont(TTFont('DejaVuBold',
            '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'))
        pdfmetrics.registerFont(TTFont('DejaVuItalic',
            '/usr/share/fonts/truetype/dejavu/DejaVuSans-Oblique.ttf'))
        _FONTS_REGISTERED = True
    except Exception:
        pass  # fallback to Helvetica silently

# Colours
GREEN_DARK   = colors.HexColor('#1B5E20')
GREEN_MID    = colors.HexColor('#2E7D32')
GREEN_LIGHT  = colors.HexColor('#E8F5E9')
GOLD         = colors.HexColor('#F9A825')
GREY_DARK    = colors.HexColor('#37474F')
GREY_MID     = colors.HexColor('#78909C')
GREY_LIGHT   = colors.HexColor('#ECEFF1')
WHITE        = colors.white

ZONE_COLORS = {
    'Z0': colors.HexColor('#F5F5DC'),
    'Z1': colors.HexColor('#C8E6C9'),
    'Z2': colors.HexColor('#A5D6A7'),
    'Z3': colors.HexColor('#FFF9C4'),
    'Z4': colors.HexColor('#E1BEE7'),
}
PAGE_W, PAGE_H = A4


class _ColorRule(Flowable):
    def __init__(self, color=GREEN_MID, height=1.5):
        super().__init__()
        self._color = color
        self._h = height
        self.width = 0
        self.height = height + 2

    def draw(self):
        self.canv.setFillColor(self._color)
        w = getattr(self, '_available_width', PAGE_W - 30*mm)
        self.canv.rect(0, 0, w, self._h, fill=True, stroke=False)

    def wrap(self, avail_w, avail_h):
        self._available_width = avail_w
        return avail_w, self.height


def _styles(use_dejavu=True):
    _ensure_fonts()
    base = getSampleStyleSheet()
    body_font = 'DejaVu' if use_dejavu and _FONTS_REGISTERED else 'Helvetica'
    bold_font = 'DejaVuBold' if use_dejavu and _FONTS_REGISTERED else 'Helvetica-Bold'
    ital_font = 'DejaVuItalic' if use_dejavu and _FONTS_REGISTERED else 'Helvetica-Oblique'

    def ps(name, **kw):
        return ParagraphStyle(name, parent=base['Normal'], **kw)

    return {
        'section_title': ps('section_title', fontSize=15, leading=20, textColor=GREEN_DARK,
                            fontName=bold_font, spaceBefore=14, spaceAfter=4),
        'sub_title':     ps('sub_title',     fontSize=11, leading=14, textColor=GREEN_MID,
                            fontName=bold_font, spaceBefore=8, spaceAfter=3),
        'body':          ps('body',          fontSize=9.5, leading=14, textColor=GREY_DARK,
                            fontName=body_font, alignment=TA_JUSTIFY),
        'body_center':   ps('body_center',   fontSize=9.5, leading=14, textColor=GREY_DARK,
                            fontName=body_font, alignment=TA_CENTER),
        'kv_key':        ps('kv_key',        fontSize=9, leading=13, textColor=GREY_MID,
                            fontName=bold_font),
        'kv_val':        ps('kv_val',        fontSize=9, leading=13, textColor=GREY_DARK,
                            fontName=body_font),
        'bullet':        ps('bullet',        fontSize=9.5, leading=14, textColor=GREY_DARK,
                            fontName=body_font, leftIndent=12),
        'caption':       ps('caption',       fontSize=8, leading=11, textColor=GREY_MID,
                            fontName=body_font, alignment=TA_CENTER, spaceAfter=6),
        'disclaimer':    ps('disclaimer',    fontSize=7.5, leading=11, textColor=GREY_MID,
                            fontName=ital_font, alignment=TA_CENTER),
        'table_body':    ps('table_body',    fontSize=8.5, leading=12, textColor=GREY_DARK,
                            fontName=body_font),
    }


def _tbl_style(header_color=GREEN_DARK):
    return TableStyle([
        ('BACKGROUND',    (0, 0), (-1, 0),  header_color),
        ('TEXTCOLOR',     (0, 0), (-1, 0),  WHITE),
        ('FONTNAME',      (0, 0), (-1, 0),  'DejaVuBold' if _FONTS_REGISTERED else 'Helvetica-Bold'),
        ('FONTSIZE',      (0, 0), (-1, 0),  9),
        ('BOTTOMPADDING', (0, 0), (-1, 0),  7),
        ('TOPPADDING',    (0, 0), (-1, 0),  7),
        ('FONTNAME',      (0, 1), (-1, -1), 'DejaVu' if _FONTS_REGISTERED else 'Helvetica'),
        ('FONTSIZE',      (0, 1), (-1, -1), 8.5),
        ('TOPPADDING',    (0, 1), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 5),
        ('ROWBACKGROUNDS',(0, 1), (-1, -1), [WHITE, GREY_LIGHT]),
        ('GRID',          (0, 0), (-1, -1), 0.4, colors.HexColor('#B0BEC5')),
        ('ALIGN',         (1, 1), (-1, -1), 'CENTER'),
        ('VALIGN',        (0, 0), (-1, -1), 'MIDDLE'),
    ])


class PDFGenerator:

    ZONE_META = {
        'Z0': {'name': 'Residential',    'desc': 'Core living area - house, storage, immediate surroundings.',
               'tips': ['Maximise passive solar gain (south-facing windows in northern hemisphere).',
                        'Install rainwater collection from roof.',
                        'Keep emergency vegetable patch within 10 m of kitchen door.']},
        'Z1': {'name': 'Kitchen Garden', 'desc': 'Daily-harvest vegetables, herbs, and medicinal plants.',
               'tips': ['Use raised beds for intensive planting and weed control.',
                        'Companion plant tomatoes with basil; beans with corn and squash.',
                        'Mulch 3-4 inches to retain moisture and suppress weeds.']},
        'Z2': {'name': 'Food Forest',    'desc': 'Multi-layer perennial food production - trees, shrubs, ground covers.',
               'tips': ['Plant in guilds: fruit tree + nitrogen-fixer + dynamic accumulator.',
                        'Minimum 7 layers: canopy, sub-canopy, shrub, herb, ground, vine, root.',
                        'Avoid tilling - use sheet mulch for establishment.']},
        'Z3': {'name': 'Pasture / Crops','desc': 'Annual crops, grazing paddocks, and large-scale production.',
               'tips': ['Rotate livestock paddocks every 21-28 days (mob grazing).',
                        'Use cover crops (clover, rye) between seasons to fix nitrogen.',
                        'Install windbreaks on the prevailing wind side.']},
        'Z4': {'name': 'Buffer Zone',    'desc': 'Wild edges, timber, and biodiversity corridors.',
               'tips': ['Plant native species for wildlife habitat and pest control.',
                        'Maintain a 10-m wildlife corridor along property boundaries.',
                        'Source timber and fuel wood sustainably from this zone.']},
    }

    # Currency symbols that need Unicode font
    COST_REFERENCE = {
        'USA':       {'currency': 'USD', 'symbol': '$',    'low': 0.08, 'high': 0.22},
        'India':     {'currency': 'INR', 'symbol': 'Rs.', 'low': 4.0,  'high': 12.0},
        'UK':        {'currency': 'GBP', 'symbol': 'GBP ', 'low': 0.07, 'high': 0.20},
        'Canada':    {'currency': 'CAD', 'symbol': 'CAD ', 'low': 0.10, 'high': 0.28},
        'Australia': {'currency': 'AUD', 'symbol': 'AUD ', 'low': 0.09, 'high': 0.25},
        'EU':        {'currency': 'EUR', 'symbol': 'EUR ', 'low': 0.07, 'high': 0.19},
        'Brazil':    {'currency': 'BRL', 'symbol': 'BRL ', 'low': 0.25, 'high': 0.70},
        'Nigeria':   {'currency': 'NGN', 'symbol': 'NGN ', 'low': 40,   'high': 120},
    }

    def create(self, layout_data, watermark_enabled=True,
               map_image_buffer=None, threed_image_buffer=None):
        _ensure_fonts()
        buf = BytesIO()
        st = _styles()

        def cover_canvas(canv, doc):
            self._draw_cover(canv, layout_data)

        hf = self._make_hf()

        doc = SimpleDocTemplate(
            buf, pagesize=A4,
            leftMargin=15*mm, rightMargin=15*mm,
            topMargin=22*mm, bottomMargin=18*mm,
            title='Homestead Architect Pro - Site Plan Report',
            author='chundalgardens.com',
        )

        story = []
        story.append(Spacer(1, 20*mm))   # cover page placeholder
        story.append(PageBreak())
        self._executive_summary(story, st, layout_data)
        story.append(PageBreak())

        if map_image_buffer:
            self._map_page(story, st, map_image_buffer, '2D Site Plan Map')
            story.append(PageBreak())

        if threed_image_buffer:
            self._map_page(story, st, threed_image_buffer, '3D Homestead View')
            story.append(PageBreak())

        self._zone_analysis(story, st, layout_data)
        story.append(PageBreak())
        self._livestock_section(story, st, layout_data)
        self._water_management(story, st, layout_data)
        self._implementation_timeline(story, st, layout_data)
        story.append(PageBreak())
        self._global_cost_analysis(story, st, layout_data)
        story.append(PageBreak())
        self._planting_guide(story, st, layout_data)
        self._closing_page(story, st)

        doc.build(story, onFirstPage=cover_canvas, onLaterPages=hf)
        buf.seek(0)
        return buf

    @staticmethod
    def _make_hf():
        class HF:
            def __call__(self, canv, doc):
                canv.saveState()
                w, h = PAGE_W, PAGE_H
                canv.setFillColor(GREEN_DARK)
                canv.rect(0, h - 18*mm, w, 18*mm, fill=True, stroke=False)
                canv.setFillColor(WHITE)
                canv.setFont('Helvetica-Bold', 10)
                canv.drawString(15*mm, h - 12*mm,
                                'HOMESTEAD ARCHITECT PRO  |  Professional Site Plan')
                canv.setFont('Helvetica', 9)
                canv.drawRightString(w - 15*mm, h - 12*mm, 'chundalgardens.com')
                canv.setFillColor(GREY_LIGHT)
                canv.rect(0, 0, w, 14*mm, fill=True, stroke=False)
                canv.setFillColor(GREY_DARK)
                canv.setFont('Helvetica', 8)
                canv.drawString(15*mm, 5*mm,
                    'For planning purposes only. Consult licensed professionals before construction.')
                canv.setFont('Helvetica-Bold', 8)
                canv.drawRightString(w - 15*mm, 5*mm, f'Page {doc.page}')
                canv.restoreState()
        return HF()

    @staticmethod
    def _draw_cover(canv, layout_data):
        canv.saveState()
        w, h = PAGE_W, PAGE_H
        canv.setFillColor(GREEN_DARK)
        canv.rect(0, 0, w, h, fill=True, stroke=False)
        canv.setFillColor(colors.HexColor('#2E7D32'))
        canv.rect(0, h * 0.35, w, h * 0.65, fill=True, stroke=False)

        canv.setStrokeColor(colors.HexColor('#4CAF50'))
        canv.setLineWidth(0.5)
        for r in range(80, 300, 35):
            canv.circle(w * 0.85, h * 0.78, r, fill=False, stroke=True)

        canv.setFillColor(WHITE)
        canv.roundRect(20*mm, h*0.28, w - 40*mm, h*0.44, 8, fill=True, stroke=False)

        canv.setFillColor(colors.HexColor('#B9F6CA'))
        canv.setFont('Helvetica', 11)
        canv.drawCentredString(w/2, h*0.92, 'chundalgardens.com')

        canv.setFillColor(WHITE)
        canv.setFont('Helvetica-Bold', 30)
        canv.drawCentredString(w/2, h*0.83, 'HOMESTEAD ARCHITECT')
        canv.setFont('Helvetica-Bold', 26)
        canv.drawCentredString(w/2, h*0.77, 'PRO  2026')

        canv.setFont('Helvetica', 12)
        canv.setFillColor(colors.HexColor('#C8E6C9'))
        canv.drawCentredString(w/2, h*0.72,
                               'Professional Permaculture Site Plan  |  Global Edition')

        canv.setStrokeColor(GOLD)
        canv.setLineWidth(2)
        canv.line(40*mm, h*0.68, w - 40*mm, h*0.68)

        total = layout_data.get('total_sqft', 0)
        acres = layout_data.get('acres', total / 43560)
        cat   = layout_data.get('category', '').title()
        L     = layout_data.get('dimensions', {}).get('L', 0)
        W_dim = layout_data.get('dimensions', {}).get('W', 0)
        livestock = layout_data.get('livestock', [])
        lv_str = ', '.join(str(x) for x in livestock if x != 'None') or 'None'

        items = [
            ('TOTAL AREA',  f'{total:,.0f} sq.ft.  ({acres:.2f} acres)'),
            ('DIMENSIONS',  f'{int(L)} ft  x  {int(W_dim)} ft'),
            ('SCALE',       cat),
            ('LIVESTOCK',   lv_str),
            ('DATE',        date.today().strftime('%B %d, %Y')),
        ]
        row_h = 9 * mm
        panel_y = h * 0.30
        for i, (k, v) in enumerate(items):
            y = panel_y + (len(items) - 1 - i) * row_h + 14*mm
            canv.setFillColor(GREY_MID)
            canv.setFont('Helvetica-Bold', 9)
            canv.drawString(30*mm, y, k)
            canv.setFillColor(GREY_DARK)
            canv.setFont('Helvetica', 9)
            canv.drawString(82*mm, y, str(v))

        canv.setFont('Helvetica-Oblique', 7)
        canv.setFillColor(colors.HexColor('#90A4AE'))
        canv.drawCentredString(w/2, 10*mm,
            'For planning purposes only. Consult licensed professionals before construction.')
        canv.restoreState()

    def _executive_summary(self, story, st, layout_data):
        story.append(Paragraph('Executive Summary', st['section_title']))
        story.append(_ColorRule())
        story.append(Spacer(1, 4*mm))

        total = layout_data.get('total_sqft', 0)
        acres = layout_data.get('acres', total / 43560)
        cat   = layout_data.get('category', 'medium').title()
        L     = layout_data.get('dimensions', {}).get('L', 0)
        W_dim = layout_data.get('dimensions', {}).get('W', 0)
        hpos  = layout_data.get('house_position', 'Center')
        water = layout_data.get('water_source', 'Borewell/Well')
        slope = layout_data.get('slope', 'Flat')
        lv    = layout_data.get('livestock', [])
        lv_str= ', '.join(str(x) for x in lv if x != 'None') or 'None'

        kv = [
            ['Total Area', f'{total:,.0f} sq.ft. ({acres:.2f} acres)', 'Scale', cat],
            ['Dimensions', f'{int(L)} x {int(W_dim)} ft', 'House', hpos],
            ['Water',      str(water), 'Slope', str(slope)],
            ['Livestock',  lv_str, 'Report Date', date.today().strftime('%d %B %Y')],
        ]
        col_w = [32*mm, 58*mm, 30*mm, 55*mm]
        tbl = Table(
            [[Paragraph(c, st['kv_key'] if i % 2 == 0 else st['kv_val'])
              for i, c in enumerate(row)]
             for row in kv],
            colWidths=col_w,
        )
        tbl.setStyle(TableStyle([
            ('ROWBACKGROUNDS', (0, 0), (-1, -1), [WHITE, GREY_LIGHT]),
            ('GRID',          (0, 0), (-1, -1), 0.3, colors.HexColor('#CFD8DC')),
            ('TOPPADDING',    (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ('LEFTPADDING',   (0, 0), (-1, -1), 6),
        ]))
        story.append(tbl)
        story.append(Spacer(1, 5*mm))

        for pt in [
            'Self-sufficiency target: 60-80% of household food needs within 3 years.',
            'Water harvesting designed for zero external water dependency.',
            'Livestock integration for nutrient cycling and passive income.',
            'Carbon sequestration through food forest (Zone 2) plantings.',
            'Designed to global standards - applicable in any climate zone.',
        ]:
            story.append(Paragraph(f'â€¢ {pt}', st['bullet']))
        story.append(Spacer(1, 3*mm))

    def _map_page(self, story, st, buf, title):
        story.append(Paragraph(title, st['section_title']))
        story.append(_ColorRule())
        story.append(Spacer(1, 3*mm))
        buf.seek(0)
        img = RLImage(buf, width=175*mm, height=130*mm, kind='proportional')
        story.append(img)
        story.append(Spacer(1, 2*mm))
        story.append(Paragraph(
            f'Figure: {title}. North arrow shown on map.',
            st['caption']))

    def _zone_analysis(self, story, st, layout_data):
        story.append(Paragraph('Zone Analysis and Recommendations', st['section_title']))
        story.append(_ColorRule())
        story.append(Spacer(1, 4*mm))

        zones = layout_data.get('zone_positions', {})
        total_sqft = max(layout_data.get('total_sqft', 1), 1)

        zone_uses = {
            'z0': 'House, garden, immediate needs',
            'z1': 'Daily vegetables, herbs, medicinal',
            'z2': 'Perennial food trees, shrubs',
            'z3': 'Annual crops, grazing animals',
            'z4': 'Timber, wildlife, buffer',
        }
        header = ['Zone', 'Name', 'Area (sq.ft.)', '% of Total', 'Primary Use']
        rows = [header]
        for zid in ['z0', 'z1', 'z2', 'z3', 'z4']:
            pos  = zones.get(zid, {})
            area = int(pos.get('width', 0) * pos.get('height', 0))
            pct  = f'{area / total_sqft * 100:.0f}%' if area else '--'
            rows.append([
                zid.upper(), self.ZONE_META[zid.upper()]['name'],
                f'{area:,}', pct, zone_uses.get(zid, ''),
            ])

        col_w = [16*mm, 38*mm, 32*mm, 20*mm, 69*mm]
        tbl = Table(rows, colWidths=col_w, repeatRows=1)
        ts = _tbl_style()
        for i, zid in enumerate(['Z0', 'Z1', 'Z2', 'Z3', 'Z4'], start=1):
            ts.add('BACKGROUND', (0, i), (0, i), ZONE_COLORS[zid])
        tbl.setStyle(ts)
        story.append(tbl)
        story.append(Spacer(1, 5*mm))

        for zid_upper in ['Z0', 'Z1', 'Z2', 'Z3', 'Z4']:
            meta = self.ZONE_META[zid_upper]
            pos  = zones.get(zid_upper.lower(), {})
            area = int(pos.get('width', 0) * pos.get('height', 0))
            story.append(KeepTogether([
                Paragraph(
                    f'{zid_upper} - {meta["name"]}' + (f'  |  {area:,} sq.ft.' if area else ''),
                    st['sub_title']),
                Paragraph(meta['desc'], st['body']),
                Spacer(1, 2*mm),
                *[Paragraph(f'   {tip}', st['bullet']) for tip in meta['tips']],
                Spacer(1, 4*mm),
            ]))

    def _livestock_section(self, story, st, layout_data):
        livestock = layout_data.get('livestock', [])
        real = [x for x in livestock if x != 'None']
        if not real:
            return

        story.append(Paragraph('Livestock Housing Plan', st['section_title']))
        story.append(_ColorRule())
        story.append(Spacer(1, 3*mm))

        specs = {
            'Goats':    ('15 sq.ft./adult indoors', '25 sq.ft. outdoor paddock', 'Elevated floor recommended'),
            'Chickens': ('4 sq.ft./bird free-range', 'Nesting boxes + roosts',   'Ventilation critical'),
            'Pigs':     ('50 sq.ft./sow farrowing',  'Slatted floors + drainage','Biogas integration possible'),
            'Cows':     ('80 sq.ft./cow',            'Covered yard + feed bunk', 'Deep litter or slurry system'),
            'Fish':     ('300-500L tank/100 fish',   'Aeration + filtration',    'Tilapia/catfish suit tropical'),
            'Bees':     ('1 hive per colony',        'Facing east/SE',           '2m+ from pathways'),
        }
        rows = [['Animal', 'Space Needed', 'Key Feature', 'Note']]
        for animal in real:
            if animal in specs:
                s = specs[animal]
                rows.append([animal, s[0], s[1], s[2]])

        if len(rows) > 1:
            col_w = [25*mm, 45*mm, 50*mm, 55*mm]
            tbl = Table(rows, colWidths=col_w, repeatRows=1)
            tbl.setStyle(_tbl_style(header_color=GREEN_MID))
            story.append(tbl)
        story.append(Spacer(1, 4*mm))

    def _water_management(self, story, st, layout_data):
        story.append(Paragraph('Water Management', st['section_title']))
        story.append(_ColorRule())
        story.append(Spacer(1, 3*mm))

        water = str(layout_data.get('water_source', 'Borewell/Well'))
        recommendations = {
            'Borewell/Well': [
                'Install submersible pump with solar (1-2 kW) to cut electricity cost.',
                'Test water quality annually: pH, TDS, coliform bacteria.',
                'Pair with 5,000-10,000 L overhead tank for gravity-fed distribution.',
            ],
            'Rainwater': [
                'Install first-flush diverter on every downpipe before the tank.',
                'Target 1 L storage per sq.ft. of roof area for drought resilience.',
                'Gutters and tanks must be food-grade if used for drinking.',
            ],
            'River/Pond': [
                'Obtain necessary permits before diverting any water course.',
                'Install swales on-contour to slow and sink water.',
                'Maintain 5-10 m riparian buffer with native vegetation.',
            ],
            'Municipal Supply': [
                'Supplement with rainwater harvesting to reduce bill by 40-60%.',
                'Install grey-water recycling for toilet flushing and irrigation.',
                'Plan for independence: municipal supply may fail in extreme events.',
            ],
            'None yet': [
                'Priority: sink a borewell or arrange water delivery before planting.',
                'Design swales first to harvest every drop of rainfall.',
                'Consider a small pond in Zone 3 as primary water storage.',
            ],
        }
        # Find matching key
        tips = None
        for k, v in recommendations.items():
            if k.lower() in water.lower() or water.lower() in k.lower():
                tips = v
                break
        if tips is None:
            tips = recommendations['Borewell/Well']

        for tip in tips:
            story.append(Paragraph(f'â€¢ {tip}', st['bullet']))

        story.append(Spacer(1, 3*mm))
        story.append(Paragraph('General Water Strategy', st['sub_title']))
        for g in [
            'Swales on contour (Zone 3/4) to capture and slow runoff.',
            'Mulch all bare soil to reduce evaporation by up to 70%.',
            'Pond in Zone 3 for aquaculture and emergency irrigation reserve.',
            'Keyline plowing to redistribute water from valleys to ridges.',
        ]:
            story.append(Paragraph(f'â€¢ {g}', st['bullet']))
        story.append(Spacer(1, 4*mm))

    def _implementation_timeline(self, story, st, layout_data):
        story.append(Paragraph('Implementation Timeline', st['section_title']))
        story.append(_ColorRule())
        story.append(Spacer(1, 3*mm))

        phases = [
            ['Phase', 'Timeframe', 'Key Actions', 'Priority'],
            ['1 - Foundation',    'Month 1-3',  'Soil test, Water infrastructure, Fencing, Zone 0 prep', 'CRITICAL'],
            ['2 - Zone 1 Setup',  'Month 3-6',  'Raised beds, Compost, Greenhouse, Herb garden',         'HIGH'],
            ['3 - Food Forest',   'Month 6-18', 'Tree planting guilds, Sheet mulch, Swales, Pond',       'HIGH'],
            ['4 - Zone 3',        'Month 12-24','Livestock housing, Paddock rotation, Annual crops',     'MEDIUM'],
            ['5 - Zone 4 Buffer', 'Month 18-36','Native plantings, Timber, Wildlife corridors',          'LOW'],
            ['6 - Optimise',      'Year 3+',    'Solar upgrade, Seed saving, Income streams',            'ONGOING'],
        ]
        col_w = [38*mm, 28*mm, 97*mm, 20*mm]
        tbl = Table(phases, colWidths=col_w, repeatRows=1)
        ts = _tbl_style()
        priority_colors = {
            'CRITICAL': colors.HexColor('#FFCDD2'),
            'HIGH':     colors.HexColor('#FFF9C4'),
            'MEDIUM':   colors.HexColor('#E8F5E9'),
            'LOW':      GREY_LIGHT,
            'ONGOING':  colors.HexColor('#E3F2FD'),
        }
        for i, row in enumerate(phases[1:], start=1):
            ts.add('BACKGROUND', (3, i), (3, i), priority_colors.get(row[3], WHITE))
        tbl.setStyle(ts)
        story.append(tbl)
        story.append(Spacer(1, 4*mm))

    def _global_cost_analysis(self, story, st, layout_data):
        story.append(Paragraph('Global Cost Analysis', st['section_title']))
        story.append(_ColorRule())
        story.append(Spacer(1, 3*mm))

        total_sqft = layout_data.get('total_sqft', 200000)
        story.append(Paragraph(
            'Estimated setup costs by region. Covers earthworks, infrastructure, '
            'fencing, initial plantings, and basic livestock housing. '
            'Does NOT include land purchase or main dwelling construction.',
            st['body']))
        story.append(Spacer(1, 3*mm))

        header = ['Country / Region', 'Currency', 'Low Estimate', 'High Estimate', 'Note']
        rows = [header]
        for country, ref in self.COST_REFERENCE.items():
            low  = ref['low']  * total_sqft
            high = ref['high'] * total_sqft
            sym  = ref['symbol']
            rows.append([country, ref['currency'],
                         f'{sym}{low:,.0f}', f'{sym}{high:,.0f}', 'DIY saves 30-50%'])

        col_w = [40*mm, 22*mm, 32*mm, 32*mm, 49*mm]
        tbl = Table(rows, colWidths=col_w, repeatRows=1)
        tbl.setStyle(_tbl_style())
        story.append(tbl)
        story.append(Spacer(1, 3*mm))

        story.append(Paragraph('Expected Returns', st['sub_title']))
        income_rows = [
            ['Income Stream',            'Start Year', 'Annual (USD equiv.)', 'Effort'],
            ['Kitchen garden produce',   'Year 1',     '$200 - $800',         'Daily'],
            ['Eggs / poultry',           'Year 1',     '$400 - $1,500',       'Daily'],
            ['Dairy / goat products',    'Year 2',     '$600 - $3,000',       'Daily'],
            ['Fruit and nut harvest',    'Year 3',     '$500 - $5,000',       'Seasonal'],
            ['Fish / aquaculture',       'Year 1',     '$300 - $2,000',       'Weekly'],
            ['Honey / beeswax',          'Year 2',     '$200 - $1,500',       'Seasonal'],
            ['Agri-tourism / workshops', 'Year 3',     '$500 - $8,000',       'Monthly'],
        ]
        col_w2 = [55*mm, 25*mm, 50*mm, 25*mm]
        tbl2 = Table(income_rows, colWidths=col_w2, repeatRows=1)
        tbl2.setStyle(_tbl_style(header_color=GREEN_MID))
        story.append(tbl2)
        story.append(Spacer(1, 4*mm))

    def _planting_guide(self, story, st, layout_data):
        story.append(Paragraph('Quick Planting Reference', st['section_title']))
        story.append(_ColorRule())
        story.append(Spacer(1, 3*mm))

        rows = [
            ['Plant', 'Zone', 'Spacing', 'Yield / plant', 'Notes'],
            ['Tomato',       'Z1', '60 cm',  '4-8 kg/season',   'Stake, water consistently'],
            ['Kale',         'Z1', '45 cm',  'Continuous',       'Frost hardy; cut outer leaves'],
            ['Basil',        'Z1', '30 cm',  'Continuous',       'Companion to tomatoes'],
            ['Banana',       'Z2', '3 m',    '15-40 kg bunch',   'Needs wind protection'],
            ['Mango',        'Z2', '8-10 m', '50-300 kg/yr',     'Full sun; drought tolerant'],
            ['Moringa',      'Z2', '3 m',    'Leaves year-round','Fast-growing, nutritious'],
            ['Sweet potato', 'Z3', '30 cm',  '1-2 kg/plant',     'Excellent ground cover'],
            ['Maize/Corn',   'Z3', '30 cm',  '1-2 cobs',         'Plant in blocks'],
            ['Pigeon pea',   'Z3', '1 m',    '1-2 kg/plant',     'Nitrogen-fixing'],
            ['Bamboo',       'Z4', '2-5 m',  'Timber yr 3+',     'Excellent windbreak'],
            ['Leucaena',     'Z4', '2 m',    'Fodder + N-fix',   'Coppice regularly'],
        ]
        col_w = [32*mm, 14*mm, 20*mm, 30*mm, 79*mm]
        tbl = Table(rows, colWidths=col_w, repeatRows=1)
        tbl.setStyle(_tbl_style(header_color=GREEN_MID))
        story.append(tbl)
        story.append(Spacer(1, 4*mm))
        story.append(Paragraph(
            'Yields are estimates based on optimised conditions. '
            'Actual results depend on soil quality, climate, water, and management.',
            st['disclaimer']))

    def _closing_page(self, story, st):
        story.append(PageBreak())
        story.append(Spacer(1, 20*mm))
        story.append(Paragraph('Thank You for Using Homestead Architect Pro', st['section_title']))
        story.append(_ColorRule(color=GOLD))
        story.append(Spacer(1, 6*mm))
        story.append(Paragraph(
            'We hope this plan helps you build a productive, resilient, and beautiful homestead. '
            'Agriculture is one of humanity\'s most important skills - every garden planted '
            'is a step toward a healthier planet.',
            st['body']))
        story.append(Spacer(1, 4*mm))
        story.append(Paragraph('Share your progress at chundalgardens.com', st['body_center']))
        story.append(Spacer(1, 8*mm))
        story.append(HRFlowable(width='80%', thickness=1, color=GREY_MID,
                                spaceAfter=6*mm, lineCap='round'))
        story.append(Paragraph(
            'DISCLAIMER: This report is for informational and planning purposes only. '
            'All measurements, costs, and yields are estimates. '
            'Always consult qualified agronomists, engineers, and local authorities '
            'before commencing construction or making financial decisions. '
            'chundalgardens.com assumes no liability for decisions made using this report.',
            st['disclaimer']))
