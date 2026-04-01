"""
Professional PDF Report Generator
Homestead Architect Pro 2026 — Global Edition
NO affiliate content. Zero spam. Pure value.
"""

from io import BytesIO
from datetime import date
from typing import Dict, Any, Optional

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm, cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, HRFlowable, Image as RLImage, KeepTogether,
)
from reportlab.platypus.flowables import Flowable
from reportlab.pdfgen import canvas


# ── Colour palette ────────────────────────────────────────────────────────────
GREEN_DARK   = colors.HexColor("#1B5E20")
GREEN_MID    = colors.HexColor("#2E7D32")
GREEN_LIGHT  = colors.HexColor("#E8F5E9")
GREEN_ACCENT = colors.HexColor("#4CAF50")
GOLD         = colors.HexColor("#F9A825")
GREY_DARK    = colors.HexColor("#37474F")
GREY_MID     = colors.HexColor("#78909C")
GREY_LIGHT   = colors.HexColor("#ECEFF1")
WHITE        = colors.white
BLACK        = colors.black

ZONE_COLORS = {
    "Z0": colors.HexColor("#F5F5DC"),
    "Z1": colors.HexColor("#C8E6C9"),
    "Z2": colors.HexColor("#A5D6A7"),
    "Z3": colors.HexColor("#FFF9C4"),
    "Z4": colors.HexColor("#E1BEE7"),
}

PAGE_W, PAGE_H = A4

# ── Header / Footer canvas callback ──────────────────────────────────────────
class _HeaderFooter:
    def __init__(self, brand: str = "chundalgardens.com"):
        self.brand = brand

    def __call__(self, canv: canvas.Canvas, doc):
        canv.saveState()
        w, h = PAGE_W, PAGE_H

        # ── Header bar
        canv.setFillColor(GREEN_DARK)
        canv.rect(0, h - 18*mm, w, 18*mm, fill=True, stroke=False)
        canv.setFillColor(WHITE)
        canv.setFont("Helvetica-Bold", 10)
        canv.drawString(15*mm, h - 12*mm, "HOMESTEAD ARCHITECT PRO  ·  Professional Site Plan")
        canv.setFont("Helvetica", 9)
        canv.drawRightString(w - 15*mm, h - 12*mm, self.brand)

        # ── Footer bar
        canv.setFillColor(GREY_LIGHT)
        canv.rect(0, 0, w, 14*mm, fill=True, stroke=False)
        canv.setFillColor(GREY_DARK)
        canv.setFont("Helvetica", 8)
        canv.drawString(15*mm, 5*mm,
            "This report is for planning purposes only. "
            "Consult licensed professionals before construction.")
        canv.setFont("Helvetica-Bold", 8)
        canv.drawRightString(w - 15*mm, 5*mm, f"Page {doc.page}")

        canv.restoreState()


# ── Thin coloured rule Flowable ───────────────────────────────────────────────
class _ColorRule(Flowable):
    def __init__(self, color=GREEN_MID, height=1.5, width_frac=1.0):
        super().__init__()
        self._color = color
        self._h = height
        self._wf = width_frac
        self.width = 0
        self.height = height + 2

    def draw(self):
        self.canv.setFillColor(self._color)
        w = (self._available_width if hasattr(self, "_available_width")
             else PAGE_W - 30*mm) * self._wf
        self.canv.rect(0, 0, w, self._h, fill=True, stroke=False)

    def wrap(self, avail_w, avail_h):
        self._available_width = avail_w
        return avail_w, self.height


# ── Style factory ─────────────────────────────────────────────────────────────
def _styles():
    base = getSampleStyleSheet()
    custom = {}

    def add(name, **kw):
        custom[name] = ParagraphStyle(name, parent=base["Normal"], **kw)

    add("cover_title",
        fontSize=28, leading=34, textColor=WHITE,
        fontName="Helvetica-Bold", alignment=TA_CENTER)
    add("cover_sub",
        fontSize=13, leading=17, textColor=colors.HexColor("#B9F6CA"),
        fontName="Helvetica", alignment=TA_CENTER)
    add("cover_meta",
        fontSize=10, leading=14, textColor=colors.HexColor("#CFD8DC"),
        fontName="Helvetica", alignment=TA_CENTER)

    add("section_title",
        fontSize=15, leading=20, textColor=GREEN_DARK,
        fontName="Helvetica-Bold", spaceBefore=14, spaceAfter=4)
    add("sub_title",
        fontSize=11, leading=14, textColor=GREEN_MID,
        fontName="Helvetica-Bold", spaceBefore=8, spaceAfter=3)
    add("body",
        fontSize=9.5, leading=14, textColor=GREY_DARK,
        fontName="Helvetica", alignment=TA_JUSTIFY)
    add("body_center",
        fontSize=9.5, leading=14, textColor=GREY_DARK,
        fontName="Helvetica", alignment=TA_CENTER)
    add("kv_key",
        fontSize=9, leading=13, textColor=GREY_MID,
        fontName="Helvetica-Bold")
    add("kv_val",
        fontSize=9, leading=13, textColor=GREY_DARK,
        fontName="Helvetica")
    add("bullet",
        fontSize=9.5, leading=14, textColor=GREY_DARK,
        fontName="Helvetica", leftIndent=12, bulletIndent=0,
        bulletFontName="Helvetica", bulletFontSize=9.5)
    add("caption",
        fontSize=8, leading=11, textColor=GREY_MID,
        fontName="Helvetica", alignment=TA_CENTER, spaceAfter=6)
    add("disclaimer",
        fontSize=7.5, leading=11, textColor=GREY_MID,
        fontName="Helvetica-Oblique", alignment=TA_CENTER)

    return custom


# ── Table style helpers ───────────────────────────────────────────────────────
def _header_table_style(header_color=GREEN_DARK):
    return TableStyle([
        ("BACKGROUND",    (0, 0), (-1, 0), header_color),
        ("TEXTCOLOR",     (0, 0), (-1, 0), WHITE),
        ("FONTNAME",      (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE",      (0, 0), (-1, 0), 9),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 7),
        ("TOPPADDING",    (0, 0), (-1, 0), 7),
        ("FONTNAME",      (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE",      (0, 1), (-1, -1), 8.5),
        ("TOPPADDING",    (0, 1), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 1), (-1, -1), 5),
        ("ROWBACKGROUNDS",(0, 1), (-1, -1), [WHITE, GREY_LIGHT]),
        ("GRID",          (0, 0), (-1, -1), 0.4, colors.HexColor("#B0BEC5")),
        ("ALIGN",         (1, 1), (-1, -1), "CENTER"),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
    ])


# ── Main generator class ──────────────────────────────────────────────────────
class PDFGenerator:

    # Zone metadata used across sections
    ZONE_META = {
        "Z0": {
            "name": "Residential",
            "desc": "Core living area — house, storage, immediate surroundings.",
            "tips": [
                "Maximise passive solar gain (south-facing windows in northern hemisphere).",
                "Install rainwater collection from roof.",
                "Keep emergency vegetable patch within 10 m of kitchen door.",
            ],
        },
        "Z1": {
            "name": "Kitchen Garden",
            "desc": "Daily-harvest vegetables, herbs, and medicinal plants.",
            "tips": [
                "Use raised beds for intensive planting and weed control.",
                "Companion plant tomatoes with basil; beans with corn & squash.",
                "Mulch 3–4 inches to retain moisture and suppress weeds.",
            ],
        },
        "Z2": {
            "name": "Food Forest",
            "desc": "Multi-layer perennial food production — trees, shrubs, ground covers.",
            "tips": [
                "Plant in guilds: fruit tree + nitrogen-fixer + dynamic accumulator.",
                "Minimum 7 layers: canopy, sub-canopy, shrub, herb, ground, vine, root.",
                "Avoid tilling — use sheet mulch for establishment.",
            ],
        },
        "Z3": {
            "name": "Pasture / Crops",
            "desc": "Annual crops, grazing paddocks, and large-scale production.",
            "tips": [
                "Rotate livestock paddocks every 21–28 days (mob grazing).",
                "Use cover crops (clover, rye) between seasons to fix nitrogen.",
                "Install windbreaks on the prevailing wind side.",
            ],
        },
        "Z4": {
            "name": "Buffer Zone",
            "desc": "Wild edges, timber, and biodiversity corridors.",
            "tips": [
                "Plant native species for wildlife habitat and pest control.",
                "Maintain a 10-m wildlife corridor along property boundaries.",
                "Source timber and fuel wood sustainably from this zone.",
            ],
        },
    }

    # Global cost reference (setup per sq.ft.) — very conservative ranges
    COST_REFERENCE = {
        "USA":       {"currency": "USD", "symbol": "$",  "low": 0.08, "high": 0.22},
        "India":     {"currency": "INR", "symbol": "₹",  "low": 4.0,  "high": 12.0},
        "UK":        {"currency": "GBP", "symbol": "£",  "low": 0.07, "high": 0.20},
        "Canada":    {"currency": "CAD", "symbol": "CA$","low": 0.10, "high": 0.28},
        "Australia": {"currency": "AUD", "symbol": "A$", "low": 0.09, "high": 0.25},
        "EU":        {"currency": "EUR", "symbol": "€",  "low": 0.07, "high": 0.19},
        "Brazil":    {"currency": "BRL", "symbol": "R$", "low": 0.25, "high": 0.70},
        "Nigeria":   {"currency": "NGN", "symbol": "₦",  "low": 40,   "high": 120},
    }

    # ── Public API ────────────────────────────────────────────────────────────
    def create(
        self,
        layout_data: Dict[str, Any],
        watermark_enabled: bool = True,
        map_image_buffer: Optional[BytesIO] = None,
    ) -> BytesIO:
        buf = BytesIO()
        hf = _HeaderFooter(brand="chundalgardens.com")

        doc = SimpleDocTemplate(
            buf,
            pagesize=A4,
            leftMargin=15*mm,
            rightMargin=15*mm,
            topMargin=22*mm,
            bottomMargin=18*mm,
            title="Homestead Architect Pro — Site Plan Report",
            author="chundalgardens.com",
            subject="Permaculture Homestead Design",
        )

        st = _styles()
        story = []

        # Pages
        self._cover_page(story, st, layout_data)
        story.append(PageBreak())
        self._executive_summary(story, st, layout_data)
        story.append(PageBreak())
        if map_image_buffer:
            self._site_map_page(story, st, layout_data, map_image_buffer)
            story.append(PageBreak())
        self._zone_analysis(story, st, layout_data)
        story.append(PageBreak())
        self._water_management(story, st, layout_data)
        self._implementation_timeline(story, st, layout_data)
        story.append(PageBreak())
        self._global_cost_analysis(story, st, layout_data)
        story.append(PageBreak())
        self._planting_guide(story, st, layout_data)
        self._closing_page(story, st)

        doc.build(story, onFirstPage=self._cover_canvas,
                  onLaterPages=hf)
        buf.seek(0)
        return buf

    # ── Cover page (full canvas, no header/footer) ────────────────────────────
    @staticmethod
    def _cover_canvas(canv: canvas.Canvas, doc):
        canv.saveState()
        w, h = PAGE_W, PAGE_H

        # Background gradient simulation (two rects)
        canv.setFillColor(GREEN_DARK)
        canv.rect(0, 0, w, h, fill=True, stroke=False)
        canv.setFillColor(colors.HexColor("#2E7D32"))
        canv.rect(0, h * 0.35, w, h * 0.65, fill=True, stroke=False)

        # Decorative arc
        canv.setStrokeColor(colors.HexColor("#4CAF50"))
        canv.setLineWidth(0.5)
        for r in range(80, 300, 35):
            canv.circle(w * 0.85, h * 0.78, r, fill=False, stroke=True)

        # White panel
        canv.setFillColor(WHITE)
        canv.roundRect(20*mm, h*0.30, w - 40*mm, h*0.42, 8, fill=True, stroke=False)

        # Brand
        canv.setFillColor(colors.HexColor("#B9F6CA"))
        canv.setFont("Helvetica", 11)
        canv.drawCentredString(w / 2, h * 0.92, "chundalgardens.com")

        # Title
        canv.setFillColor(WHITE)
        canv.setFont("Helvetica-Bold", 30)
        canv.drawCentredString(w / 2, h * 0.83, "HOMESTEAD ARCHITECT")
        canv.setFont("Helvetica-Bold", 26)
        canv.drawCentredString(w / 2, h * 0.77, "PRO  2026")

        # Sub-line
        canv.setFont("Helvetica", 12)
        canv.setFillColor(colors.HexColor("#C8E6C9"))
        canv.drawCentredString(w / 2, h * 0.72,
                               "Professional Permaculture Site Plan  ·  Global Edition")

        # Gold rule
        rule_y = h * 0.68
        canv.setStrokeColor(GOLD)
        canv.setLineWidth(2)
        canv.line(40*mm, rule_y, w - 40*mm, rule_y)

        # Stats in white panel
        total = layout_data_cover.get("total_sqft", 0)
        acres = layout_data_cover.get("acres", total / 43560)
        cat   = layout_data_cover.get("category", "").title()
        L     = layout_data_cover.get("dimensions", {}).get("L", 0)
        W_dim = layout_data_cover.get("dimensions", {}).get("W", 0)

        panel_y = h * 0.32
        items = [
            ("Total Area",   f"{total:,.0f} sq.ft.  ({acres:.2f} acres)"),
            ("Dimensions",   f"{int(L)} ft  ×  {int(W_dim)} ft"),
            ("Scale",        cat),
            ("Date",         date.today().strftime("%B %d, %Y")),
        ]
        canv.setFont("Helvetica-Bold", 9)
        canv.setFillColor(GREY_MID)
        canv.setFont("Helvetica", 9)
        row_h = 9 * mm
        for i, (k, v) in enumerate(items):
            y = panel_y + (len(items) - 1 - i) * row_h + 14*mm
            canv.setFillColor(GREY_MID)
            canv.setFont("Helvetica-Bold", 9)
            canv.drawString(30*mm, y, k.upper())
            canv.setFillColor(GREY_DARK)
            canv.setFont("Helvetica", 9)
            canv.drawString(80*mm, y, v)

        # Disclaimer
        canv.setFont("Helvetica-Oblique", 7)
        canv.setFillColor(colors.HexColor("#90A4AE"))
        canv.drawCentredString(w / 2, 10*mm,
            "For planning purposes only. Consult licensed professionals before construction.")

        canv.restoreState()

    # ── Story-based pages ─────────────────────────────────────────────────────
    def _cover_page(self, story, st, layout_data):
        # Cover is purely canvas-drawn; we need layout_data accessible in the
        # static callback. We store it in a module-level name (simple approach).
        global layout_data_cover
        layout_data_cover = layout_data
        # Placeholder spacer so SimpleDocTemplate creates the first page
        story.append(Spacer(1, PAGE_H - 30*mm))

    def _executive_summary(self, story, st, layout_data):
        story.append(Paragraph("Executive Summary", st["section_title"]))
        story.append(_ColorRule())
        story.append(Spacer(1, 4*mm))

        total  = layout_data.get("total_sqft", 0)
        acres  = layout_data.get("acres", total / 43560)
        cat    = layout_data.get("category", "medium").title()
        L      = layout_data.get("dimensions", {}).get("L", 0)
        W_dim  = layout_data.get("dimensions", {}).get("W", 0)
        hpos   = layout_data.get("house_position", "Center")
        water  = layout_data.get("water_source", "Borewell")
        slope  = layout_data.get("slope", "Flat")

        # KV grid
        kv = [
            ["Total Area",     f"{total:,.0f} sq.ft.  ({acres:.2f} acres)",
             "Scale Category", cat],
            ["Dimensions",     f"{int(L)} × {int(W_dim)} ft",
             "House Position", hpos],
            ["Water Source",   water,
             "Terrain Slope",  slope],
            ["Report Date",    date.today().strftime("%d %B %Y"),
             "Standard",       "Permaculture Zones 0–4"],
        ]

        col_w = [35*mm, 55*mm, 40*mm, 45*mm]
        tbl = Table(
            [[Paragraph(c, st["kv_key"] if i % 2 == 0 else st["kv_val"])
              for i, c in enumerate(row)]
             for row in kv],
            colWidths=col_w,
        )
        tbl.setStyle(TableStyle([
            ("BACKGROUND",    (0, 0), (-1, -1), GREY_LIGHT),
            ("ROWBACKGROUNDS",(0, 0), (-1, -1), [WHITE, GREY_LIGHT]),
            ("GRID",          (0, 0), (-1, -1), 0.3, colors.HexColor("#CFD8DC")),
            ("TOPPADDING",    (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ("LEFTPADDING",   (0, 0), (-1, -1), 6),
        ]))
        story.append(tbl)
        story.append(Spacer(1, 5*mm))

        # Overview text
        text = (
            f"This report presents a professionally designed permaculture homestead plan "
            f"for a <b>{acres:.2f}-acre ({total:,.0f} sq.ft.)</b> property. "
            f"The design follows established permaculture principles, organising the land "
            f"into five concentric zones (Zone 0–4) radiating outward from the main "
            f"residence. Each zone receives care proportional to the frequency of human "
            f"activity, reducing labour while maximising yield and ecological resilience. "
        )
        story.append(Paragraph(text, st["body"]))
        story.append(Spacer(1, 3*mm))

        key_points = [
            "Self-sufficiency target: 60–80% of household food needs within 3 years.",
            "Water harvesting designed for zero external water dependency.",
            "Livestock integration for nutrient cycling and passive income.",
            "Carbon sequestration through food forest (Zone 2) plantings.",
            "Designed to global standards — applicable in any climate zone.",
        ]
        for pt in key_points:
            story.append(Paragraph(f"• {pt}", st["bullet"]))
        story.append(Spacer(1, 3*mm))

    def _site_map_page(self, story, st, layout_data, map_buf):
        story.append(Paragraph("Site Plan Map", st["section_title"]))
        story.append(_ColorRule())
        story.append(Spacer(1, 3*mm))

        # Embed image
        map_buf.seek(0)
        img = RLImage(map_buf, width=175*mm, height=130*mm, kind="proportional")
        story.append(img)
        story.append(Spacer(1, 2*mm))
        story.append(Paragraph(
            "Figure 1 — Generated site plan. North is indicated by the compass rose.",
            st["caption"]))

    def _zone_analysis(self, story, st, layout_data):
        story.append(Paragraph("Zone Analysis & Recommendations", st["section_title"]))
        story.append(_ColorRule())
        story.append(Spacer(1, 4*mm))

        zones = layout_data.get("zone_positions", {})

        # Summary table
        total_sqft = layout_data.get("total_sqft", 1)
        header = ["Zone", "Name", "Area (sq.ft.)", "% of Total", "Primary Use"]
        rows   = [header]

        zone_uses = {
            "z0": "House, garden, immediate needs",
            "z1": "Daily vegetables, herbs, medicinal",
            "z2": "Perennial food trees, shrubs",
            "z3": "Annual crops, grazing animals",
            "z4": "Timber, wildlife, buffer",
        }
        for zid in ["z0", "z1", "z2", "z3", "z4"]:
            pos  = zones.get(zid, {})
            area = int(pos.get("width", 0) * pos.get("height", 0))
            pct  = f"{area / total_sqft * 100:.0f}%" if area else "—"
            rows.append([
                zid.upper(), self.ZONE_META[zid.upper()]["name"],
                f"{area:,}", pct, zone_uses.get(zid, ""),
            ])

        col_w = [16*mm, 38*mm, 32*mm, 22*mm, 67*mm]
        tbl = Table(rows, colWidths=col_w, repeatRows=1)

        ts = _header_table_style()
        # Zone colour cells
        for i, zid in enumerate(["Z0","Z1","Z2","Z3","Z4"], start=1):
            ts.add("BACKGROUND", (0, i), (0, i), ZONE_COLORS[zid])
        tbl.setStyle(ts)
        story.append(tbl)
        story.append(Spacer(1, 5*mm))

        # Per-zone detailed cards
        for zid_upper in ["Z0","Z1","Z2","Z3","Z4"]:
            zid_lower = zid_upper.lower()
            meta  = self.ZONE_META[zid_upper]
            pos   = zones.get(zid_lower, {})
            area  = int(pos.get("width", 0) * pos.get("height", 0))

            story.append(KeepTogether([
                Paragraph(
                    f"{zid_upper} — {meta['name']}"
                    + (f"  |  {area:,} sq.ft." if area else ""),
                    st["sub_title"]),
                Paragraph(meta["desc"], st["body"]),
                Spacer(1, 2*mm),
                *[Paragraph(f"✓  {tip}", st["bullet"]) for tip in meta["tips"]],
                Spacer(1, 4*mm),
            ]))

    def _water_management(self, story, st, layout_data):
        story.append(Paragraph("Water Management", st["section_title"]))
        story.append(_ColorRule())
        story.append(Spacer(1, 3*mm))

        water = layout_data.get("water_source", "Borewell")
        L     = layout_data.get("dimensions", {}).get("L", 500)
        W_dim = layout_data.get("dimensions", {}).get("W", 400)

        # Estimated rainfall capture
        roof_area = L * W_dim * 0.04  # rough 4 % of total land is roof
        daily_L   = roof_area * 0.6 * 50 / 365  # 50 cm annual, 60% efficiency

        recommendations = {
            "Borewell/Well": [
                "Install submersible pump with solar panel (1–2 kW) to eliminate electricity cost.",
                "Test water quality annually — pH, TDS, coliform bacteria.",
                "Pair with a 5,000–10,000 L overhead tank for gravity-fed distribution.",
            ],
            "Rainwater": [
                f"Estimated roof collection: {daily_L:.0f} L/day (based on 50 cm annual rain, 60% efficiency).",
                "Install first-flush diverter on every downpipe before the tank.",
                "Target 1 L storage per sq.ft. of roof area for drought resilience.",
            ],
            "River/Stream": [
                "Obtain necessary permits before diverting any water course.",
                "Install swales on-contour to slow and sink water before the stream.",
                "Maintain 5–10 m riparian buffer with native vegetation.",
            ],
            "Municipal": [
                "Supplement with rainwater harvesting to reduce bill by 40–60%.",
                "Install grey-water recycling for toilet flushing and irrigation.",
                "Plan for independence: municipal supply may fail in extreme events.",
            ],
        }

        tips = recommendations.get(water, recommendations["Borewell/Well"])
        for tip in tips:
            story.append(Paragraph(f"• {tip}", st["bullet"]))

        # General water strategy
        story.append(Spacer(1, 3*mm))
        story.append(Paragraph("General Water Strategy", st["sub_title"]))
        general = [
            "Swales on contour (Zone 3/4) to capture and slow runoff.",
            "Mulch all bare soil to reduce evaporation by up to 70%.",
            "Pond in Zone 3 for aquaculture and emergency irrigation reservoir.",
            "Keyline plowing to redistribute water from valleys to ridges.",
        ]
        for g in general:
            story.append(Paragraph(f"• {g}", st["bullet"]))
        story.append(Spacer(1, 4*mm))

    def _implementation_timeline(self, story, st, layout_data):
        story.append(Paragraph("Implementation Timeline", st["section_title"]))
        story.append(_ColorRule())
        story.append(Spacer(1, 3*mm))

        phases = [
            ["Phase", "Timeframe", "Key Actions", "Priority"],
            ["1 — Foundation",  "Month 1–3",
             "Soil test · Water infrastructure · Fencing · Zone 0 house prep",
             "CRITICAL"],
            ["2 — Zone 1 Setup", "Month 3–6",
             "Raised beds · Compost system · Greenhouse erection · Herb garden",
             "HIGH"],
            ["3 — Food Forest",  "Month 6–18",
             "Tree planting guilds · Sheet mulch · Swales · Pond excavation",
             "HIGH"],
            ["4 — Zone 3 Production", "Month 12–24",
             "Livestock housing · Paddock rotation · Annual crops · Cover crops",
             "MEDIUM"],
            ["5 — Zone 4 Buffer", "Month 18–36",
             "Native plantings · Timber establishment · Wildlife corridors",
             "LOW"],
            ["6 — Optimise",    "Year 3+",
             "Solar upgrade · Seed saving · Income streams · Community sharing",
             "ONGOING"],
        ]

        col_w = [38*mm, 28*mm, 95*mm, 20*mm]
        tbl = Table(phases, colWidths=col_w, repeatRows=1)
        ts = _header_table_style()
        # Priority colour coding
        priority_colors = {
            "CRITICAL": colors.HexColor("#FFCDD2"),
            "HIGH":     colors.HexColor("#FFF9C4"),
            "MEDIUM":   colors.HexColor("#E8F5E9"),
            "LOW":      GREY_LIGHT,
            "ONGOING":  colors.HexColor("#E3F2FD"),
        }
        for i, row in enumerate(phases[1:], start=1):
            pc = priority_colors.get(row[3], WHITE)
            ts.add("BACKGROUND", (3, i), (3, i), pc)
        tbl.setStyle(ts)
        story.append(tbl)
        story.append(Spacer(1, 4*mm))

    def _global_cost_analysis(self, story, st, layout_data):
        story.append(Paragraph("Global Cost Analysis", st["section_title"]))
        story.append(_ColorRule())
        story.append(Spacer(1, 3*mm))

        total_sqft = layout_data.get("total_sqft", 200000)

        story.append(Paragraph(
            "Estimated setup costs vary significantly by region. "
            "The table below shows conservative ranges based on local material and labour costs. "
            "Costs cover earthworks, infrastructure, fencing, initial plantings, and basic livestock housing. "
            "They do NOT include land purchase or main dwelling construction.",
            st["body"]))
        story.append(Spacer(1, 3*mm))

        header = ["Country / Region", "Currency", "Low Estimate", "High Estimate", "Note"]
        rows = [header]
        for country, ref in self.COST_REFERENCE.items():
            low  = ref["low"]  * total_sqft
            high = ref["high"] * total_sqft
            sym  = ref["symbol"]
            rows.append([
                country, ref["currency"],
                f"{sym}{low:,.0f}", f"{sym}{high:,.0f}",
                "DIY saves 30–50%",
            ])

        col_w = [40*mm, 22*mm, 32*mm, 32*mm, 49*mm]
        tbl = Table(rows, colWidths=col_w, repeatRows=1)
        tbl.setStyle(_header_table_style())
        story.append(tbl)
        story.append(Spacer(1, 3*mm))

        # ROI table
        story.append(Paragraph("Expected Returns", st["sub_title"]))
        income_rows = [
            ["Income Stream",  "Start Year", "Annual Range (USD equiv.)", "Effort"],
            ["Kitchen garden produce",   "Year 1", "$200 – $800",   "Daily"],
            ["Eggs / poultry",           "Year 1", "$400 – $1,500", "Daily"],
            ["Dairy / goat products",    "Year 2", "$600 – $3,000", "Daily"],
            ["Fruit & nut harvest",      "Year 3", "$500 – $5,000", "Seasonal"],
            ["Value-added products",     "Year 2", "$300 – $2,000", "Weekly"],
            ["Agri-tourism / workshops", "Year 3", "$500 – $8,000", "Monthly"],
        ]
        col_w2 = [55*mm, 25*mm, 55*mm, 25*mm]
        tbl2 = Table(income_rows, colWidths=col_w2, repeatRows=1)
        tbl2.setStyle(_header_table_style(header_color=GREEN_MID))
        story.append(tbl2)
        story.append(Spacer(1, 4*mm))

    def _planting_guide(self, story, st, layout_data):
        story.append(Paragraph("Quick Planting Reference", st["section_title"]))
        story.append(_ColorRule())
        story.append(Spacer(1, 3*mm))

        rows = [
            ["Plant", "Zone", "Spacing", "Yield / plant", "Notes"],
            ["Tomato",      "Z1", "60 cm",  "4–8 kg/season", "Stake, water consistently"],
            ["Kale",        "Z1", "45 cm",  "Continuous",    "Cut outer leaves; frost hardy"],
            ["Basil",       "Z1", "30 cm",  "Continuous",    "Companion to tomatoes"],
            ["Banana",      "Z2", "3 m",    "15–40 kg bunch","Needs wind protection"],
            ["Mango",       "Z2", "8–10 m", "50–300 kg/yr",  "Full sun; drought tolerant once established"],
            ["Moringa",     "Z2", "3 m",    "Leaves year-round","Fast-growing, nutritious"],
            ["Sweet potato","Z3", "30 cm",  "1–2 kg/plant",  "Excellent ground cover"],
            ["Maize/Corn",  "Z3", "30 cm",  "1–2 cobs/plant","Plant in blocks for pollination"],
            ["Pigeon pea",  "Z3", "1 m",    "1–2 kg/plant",  "Nitrogen-fixing; drought resistant"],
            ["Bamboo",      "Z4", "2–5 m",  "Timber/year 3+","Excellent windbreak species"],
            ["Leucaena",    "Z4", "2 m",    "Fodder + N-fix", "Fast-growing; coppice regularly"],
        ]
        col_w = [32*mm, 14*mm, 20*mm, 30*mm, 79*mm]
        tbl = Table(rows, colWidths=col_w, repeatRows=1)
        tbl.setStyle(_header_table_style(header_color=GREEN_MID))
        story.append(tbl)
        story.append(Spacer(1, 4*mm))

        story.append(Paragraph(
            "Note: Yields are estimates based on optimised growing conditions. "
            "Actual results depend on soil quality, climate, water availability, "
            "and management practices.",
            st["disclaimer"]))

    def _closing_page(self, story, st):
        story.append(PageBreak())
        story.append(Spacer(1, 20*mm))
        story.append(Paragraph("Thank You for Using Homestead Architect Pro", st["section_title"]))
        story.append(_ColorRule(color=GOLD))
        story.append(Spacer(1, 6*mm))
        story.append(Paragraph(
            "We hope this plan helps you build a productive, resilient, and beautiful homestead. "
            "Agriculture is one of humanity's most important skills — every garden planted "
            "is a step toward a healthier planet.",
            st["body"]))
        story.append(Spacer(1, 4*mm))
        story.append(Paragraph(
            "Share your progress with the community at <b>chundalgardens.com</b>",
            st["body_center"]))
        story.append(Spacer(1, 8*mm))
        story.append(HRFlowable(width="80%", thickness=1, color=GREY_MID,
                                spaceAfter=6*mm, lineCap="round"))
        story.append(Paragraph(
            "DISCLAIMER: This report is generated for informational and planning purposes only. "
            "All measurements, costs, and yields are estimates. "
            "Always consult qualified agronomists, engineers, and local authorities "
            "before commencing construction or making financial decisions based on this report. "
            "chundalgardens.com assumes no liability for decisions made using this report.",
            st["disclaimer"]))
