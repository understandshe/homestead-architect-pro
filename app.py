"""
🏡 Homestead Architect Pro 2026 — FIXED VERSION
All features working:
  - 2D map with all animals in correct positions
  - 3D interactive view
  - PDF with map embedded and no errors
  - Livestock housing designer
  - Cost calculator
  - Watermark system
"""

import streamlit as st
import sys
from pathlib import Path
import io

sys.path.append(str(Path(__file__).parent))

from core.user_interview import UserInterview
from core.layout_engine import LayoutEngine
from core.livestock_designer import LivestockDesigner
from core.cost_calculator import CostCalculator
from core.climate_engine import ClimateEngine
from core.visualizer_2d import Visualizer2D
from core.visualizer_3d import Visualizer3D
from core.watermark_system import WatermarkEngine
from core.pdf_generator import PDFGenerator

st.set_page_config(
    page_title='Homestead Architect Pro 2026',
    page_icon='🏡',
    layout='wide',
)

st.markdown("""
<style>
.main-header {font-size:2.5rem; font-weight:bold; color:#2E7D32; text-align:center;}
.sub-header  {font-size:1.1rem; color:#666; text-align:center; margin-bottom:1rem;}
.stTabs [data-baseweb="tab"] {font-size:1rem; font-weight:600;}
</style>
""", unsafe_allow_html=True)


def main():
    st.markdown('<p class="main-header">🏡 Homestead Architect Pro</p>',
                unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Design Your Dream Homestead | 2026 Edition</p>',
                unsafe_allow_html=True)

    with st.sidebar:
        st.title('⚙️ Settings')
        watermark_enabled = st.checkbox(
            '☑️ Add Watermark (chundalgardens.com)', value=True)
        st.divider()
        st.markdown('Made by: **Chundal Gardens**')
        st.markdown('🌐 chundalgardens.com')

    tabs = st.tabs(['🎨 Design', '🌐 3D View', '🐐 Livestock', '💰 Costs', '📥 Download'])

    with tabs[0]:
        design_tab(watermark_enabled)
    with tabs[1]:
        view_3d_tab()
    with tabs[2]:
        livestock_tab()
    with tabs[3]:
        costs_tab()
    with tabs[4]:
        download_tab(watermark_enabled)


# ── Tab: 2D Design ────────────────────────────────────────────────────────────
def design_tab(watermark_enabled):
    st.header('🎨 Smart Homestead Designer')

    interview = UserInterview()
    answers = interview.run()

    if answers:
        st.success('✅ Generating your homestead design...')

        col1, col2 = st.columns([2, 1])

        with col1:
            with st.spinner('Rendering 2D site plan...'):
                engine = LayoutEngine()
                layout = engine.generate(answers)

                viz = Visualizer2D()
                map_buffer = viz.create(layout, answers)

                # Apply watermark
                if watermark_enabled:
                    final_buffer = WatermarkEngine.apply_visible_watermark(map_buffer)
                else:
                    final_buffer = WatermarkEngine.apply_protection_watermark(map_buffer)

                st.image(final_buffer, use_column_width=True)

                # Save to session
                st.session_state['current_map'] = final_buffer
                st.session_state['layout_data'] = layout
                st.session_state['answers'] = answers

                # Also save raw map (without watermark re-applied) for PDF
                map_buffer.seek(0)
                st.session_state['raw_map'] = io.BytesIO(map_buffer.read())

        with col2:
            if 'layout_data' in st.session_state:
                ld = st.session_state['layout_data']
                st.metric('Total Area', f"{ld.get('total_sqft', 0):,} sq.ft.")
                st.metric('Acres', f"{ld.get('acres', 0):.2f}")
                st.metric('Category', ld.get('category', '').title())

                livestock = ld.get('livestock', [])
                real = [x for x in livestock if x != 'None']
                if real:
                    st.metric('Livestock', ', '.join(real))

                # Climate info
                if answers.get('location'):
                    climate = ClimateEngine().get_data(answers['location'])
                    st.info(f"🌤 Climate Zone: **{climate['zone']}**\n\n"
                            f"Challenges: {', '.join(climate.get('challenges', []))}")

        # Show features placed
        if 'layout_data' in st.session_state:
            ld = st.session_state['layout_data']
            features = ld.get('features', {})
            with st.expander('📍 Features placed on map'):
                feature_labels = {
                    'well':        '🌊 Borewell/Well',
                    'pond':        '🐟 Pond/Aquaculture',
                    'solar':       '☀️ Solar Array',
                    'greenhouse':  '🌿 Greenhouse',
                    'goat_shed':   '🐐 Goat Shed',
                    'chicken_coop':'🐔 Chicken Coop',
                    'piggery':     '🐷 Piggery',
                    'cow_shed':    '🐄 Cow Shed',
                    'fish_tanks':  '🐟 Fish Tanks',
                    'bee_hives':   '🐝 Bee Hives',
                    'compost':     '🌱 Compost Bins',
                    'rain_tank':   '💧 Rain Tank',
                    'swales':      '〰️ Swales',
                }
                placed = [feature_labels[k] for k in features if k in feature_labels]
                if placed:
                    for item in placed:
                        st.write(f'✅ {item}')
                else:
                    st.write('No special features added.')


# ── Tab: 3D View ──────────────────────────────────────────────────────────────
def view_3d_tab():
    st.header('🌐 Interactive 3D View')

    if 'layout_data' not in st.session_state:
        st.info('👈 Generate a design in the **Design** tab first.')
        return

    with st.spinner('Building 3D model...'):
        viz3d = Visualizer3D()
        fig = viz3d.create(st.session_state['layout_data'])
        st.plotly_chart(fig, use_container_width=True)

    st.caption('💡 Drag to rotate · Scroll to zoom · Double-click to reset')


# ── Tab: Livestock ────────────────────────────────────────────────────────────
def livestock_tab():
    st.header('🐐 Livestock Housing Designer')
    designer = LivestockDesigner()

    col1, col2 = st.columns(2)
    with col1:
        animal  = st.selectbox('Animal', ['Goats', 'Chickens', 'Pigs'])
        count   = st.number_input('Count', 1, 1000, 10)
    with col2:
        climate = st.selectbox('Climate', ['Tropical', 'Dry', 'Temperate', 'Cold'])
        budget  = st.selectbox('Budget', ['Basic', 'Standard', 'Premium'])

    if st.button('🏗️ Generate Housing Plan', use_container_width=True):
        with st.spinner('Designing housing...'):
            try:
                design = designer.create_housing(animal, count, climate, budget)
                st.image(design['floor_plan'], use_column_width=True)

                col_s, col_m = st.columns(2)
                with col_s:
                    st.subheader('📐 Specifications')
                    for k, v in design['specs'].items():
                        st.write(f'**{k}:** {v}')
                with col_m:
                    st.subheader('🧱 Materials')
                    for k, v in design['materials'].items():
                        st.write(f'**{k}:** {v}')

                st.success(f"💰 Estimated Cost: **{design['estimated_cost']}**")
            except Exception as e:
                st.error(f'Error generating housing plan: {e}')


# ── Tab: Cost Calculator ──────────────────────────────────────────────────────
def costs_tab():
    st.header('💰 Global Cost Calculator')
    calc = CostCalculator()

    col1, col2, col3 = st.columns(3)
    with col1:
        country  = st.selectbox('Country', ['USA', 'India', 'UK', 'Canada', 'Australia'])
    with col2:
        currency = st.selectbox('Currency', ['USD', 'INR', 'EUR', 'GBP', 'CAD', 'AUD'])
    with col3:
        size = st.selectbox('Size', [
            'Small (< 0.5 acre)', 'Medium (0.5-5 acres)', 'Large (5+ acres)'])

    if st.button('💵 Calculate Costs', use_container_width=True):
        with st.spinner('Calculating...'):
            try:
                costs = calc.estimate(country, currency, size)

                c1, c2, c3 = st.columns(3)
                c1.metric('Setup (Min)',   costs['setup_min'])
                c2.metric('Setup (Max)',   costs['setup_max'])
                c3.metric('ROI Period',   f"{costs['roi_years']} years")

                c4, c5 = st.columns(2)
                c4.metric('Annual Income', costs.get('income_min', 'N/A'))
                c5.metric('Break Even',    costs.get('break_even', 'N/A'))

                # Cost breakdown
                if 'breakdown' in costs:
                    st.subheader('Cost Breakdown')
                    breakdown = costs['breakdown']
                    bd_data = {k: f"{currency} {v:,.0f}" for k, v in breakdown.items()}
                    for k, v in bd_data.items():
                        st.write(f'**{k}:** {v}')
            except Exception as e:
                st.error(f'Error calculating costs: {e}')


# ── Tab: Download ─────────────────────────────────────────────────────────────
def download_tab(watermark_enabled):
    st.header('📥 Download Your Plan')

    if 'current_map' not in st.session_state:
        st.warning('⚠️ Please generate a design in the **Design** tab first.')
        return

    col1, col2 = st.columns(2)

    with col1:
        st.subheader('🗺️ Download Map (PNG)')
        map_buf = st.session_state['current_map']
        map_buf.seek(0)
        st.download_button(
            label='⬇️ Download Site Map (PNG)',
            data=map_buf,
            file_name='homestead_site_plan.png',
            mime='image/png',
            use_container_width=True,
        )

    with col2:
        st.subheader('📄 Download Full PDF Report')
        if st.button('📑 Generate PDF Report', use_container_width=True):
            with st.spinner('Creating professional PDF report...'):
                try:
                    pdf_gen = PDFGenerator()

                    # Get raw map for PDF (seek to start)
                    raw_map = st.session_state.get('raw_map')
                    if raw_map:
                        raw_map.seek(0)

                    pdf_buffer = pdf_gen.create(
                        layout_data=st.session_state['layout_data'],
                        watermark_enabled=watermark_enabled,
                        map_image_buffer=raw_map,
                    )

                    st.success('✅ PDF ready!')
                    st.download_button(
                        label='⬇️ Download PDF Report',
                        data=pdf_buffer,
                        file_name='homestead_report.pdf',
                        mime='application/pdf',
                        use_container_width=True,
                    )
                except Exception as e:
                    st.error(f'PDF generation error: {e}')
                    import traceback
                    st.code(traceback.format_exc())

    # Preview
    if 'current_map' in st.session_state:
        st.divider()
        st.subheader('Preview')
        buf = st.session_state['current_map']
        buf.seek(0)
        st.image(buf, caption='Your Homestead Site Plan', use_column_width=True)


if __name__ == '__main__':
    main()
