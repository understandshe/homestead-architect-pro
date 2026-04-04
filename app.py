"""
Homestead Architect Pro 2026 â€” v3 FINAL (Optimized for Plotly 3D)
Cleaned & Integrated for smooth mobile/web experience.
"""

import streamlit as st
import sys, io
import json
from pathlib import Path

# Path configuration
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

# Page Configuration
st.set_page_config(
    page_title='Homestead Architect Pro 2026',
    page_icon='ðŸ¡', 
    layout='wide'
)

# Custom Styling
st.markdown("""
<style>
.main-header{font-size:2.4rem;font-weight:bold;color:#2E7D32;text-align:center;}
.sub-header{font-size:1.05rem;color:#666;text-align:center;margin-bottom:1rem;}
[data-testid="stMetricValue"] {font-size: 1.8rem;}
</style>""", unsafe_allow_html=True)

def main():
    st.markdown('<p class="main-header">ðŸ¡ Homestead Architect Pro</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Design Your Dream Homestead | Global Edition 2026</p>', unsafe_allow_html=True)

    with st.sidebar:
        st.title('âš™ï¸ Settings')
        watermark_enabled = st.checkbox('â˜‘ï¸ Watermark (chundalgardens.com)', value=True)
        st.divider()
        st.markdown('Made by: **Chundal Gardens**')
        st.markdown('ðŸŒ chundalgardens.com')

    # Tabs Navigation
    tabs = st.tabs(['ðŸŽ¨ Design', 'ðŸŒ 3D View', 'ðŸ‘ Livestock', 'ðŸ’° Costs', 'ðŸ“¥ Download'])
    
    with tabs[0]: design_tab(watermark_enabled)
    with tabs[1]: view_3d_tab()
    with tabs[2]: livestock_tab()
    with tabs[3]: costs_tab()
    with tabs[4]: download_tab(watermark_enabled)

def design_tab(watermark_enabled):
    st.header('ðŸŽ¨ Smart Homestead Designer')
    interview = UserInterview()
    answers = interview.run()
    
    if not answers:
        return

    st.success('âœ… Generating your homestead design...')
    col1, col2 = st.columns([2, 1])

    with col1:
        with st.spinner('Rendering site plan...'):
            engine = LayoutEngine()
            layout = engine.generate(answers)

            viz = Visualizer2D()
            raw_map = viz.create(layout, answers)

            # Save raw (no watermark) for PDF
            raw_map.seek(0)
            st.session_state['raw_map'] = io.BytesIO(raw_map.read())

            raw_map.seek(0)
            if watermark_enabled:
                display_map = WatermarkEngine.apply_visible_watermark(raw_map)
            else:
                display_map = WatermarkEngine.apply_protection_watermark(raw_map)

            st.image(display_map, use_column_width=True)
            st.session_state['current_map'] = display_map
            st.session_state['layout_data'] = layout
            st.session_state['answers'] = answers

    with col2:
        if 'layout_data' in st.session_state:
            ld = st.session_state['layout_data']
            st.metric('Total Area',   f"{ld.get('total_sqft', 0):,} sq.ft.")
            st.metric('Acres',        f"{ld.get('acres', 0):.2f}")
            st.metric('Category',     ld.get('category', '').title())
            
            lv = [x for x in ld.get('livestock', []) if x != 'None']
            if lv:
                st.info('ðŸ¾ Animals: ' + ', '.join(lv))
            
            if answers.get('location'):
                climate = ClimateEngine().get_data(answers['location'])
                st.info(f"â›… Climate: **{climate['zone']}**")

def view_3d_tab():
    st.header('ðŸŒ Interactive 3D Cinematic View')
    
    if 'layout_data' not in st.session_state:
        st.info('ðŸ‘ˆ Please generate a design in the Design tab first to see it in 3D.')
        # Default empty call to show the tool even without data
        viz3d = Visualizer3D()
        viz3d.create({}) 
        return

    # Pass the generated layout data to the 3D Engine
    with st.container():
        viz3d = Visualizer3D()
        # This will render your complex Plotly HTML with sidebar and layers
        viz3d.create(st.session_state['layout_data'])

def livestock_tab():
    st.header('ðŸ‘ Livestock Housing Designer')
    designer = LivestockDesigner()

    col1, col2 = st.columns(2)
    with col1:
        animal  = st.selectbox('Animal Type', ['Goats', 'Chickens', 'Pigs'])
        count   = st.number_input('Total Count', 1, 1000, 10)
    with col2:
        climate = st.selectbox('Regional Climate', ['Tropical', 'Dry', 'Temperate', 'Cold'])
        budget  = st.selectbox('Project Budget', ['Basic', 'Standard', 'Premium'])

    if st.button('ðŸ—ï¸ Generate Housing Plan', use_container_width=True):
        with st.spinner('Designing...'):
            try:
                design = designer.create_housing(animal, count, climate, budget)
                st.image(design['floor_plan'], use_column_width=True)
                
                c1, c2 = st.columns(2)
                with c1:
                    st.subheader('Specifications')
                    for k, v in design['specs'].items():
                        st.write(f'**{k}:** {v}')
                with c2:
                    st.subheader('Materials')
                    for k, v in design['materials'].items():
                        st.write(f'**{k}:** {v}')
                st.success(f"Estimated Cost: **{design['estimated_cost']}**")
            except Exception as e:
                st.error(f'Error: {e}')

def costs_tab():
    st.header('ðŸ’° Global Cost Calculator')
    calc = CostCalculator()
    c1, c2, c3 = st.columns(3)
    with c1:
        country  = st.selectbox('Country', ['USA', 'India', 'UK', 'Canada', 'Australia'])
    with c2:
        currency = st.selectbox('Currency', ['USD', 'INR', 'EUR', 'GBP', 'CAD', 'AUD'])
    with c3:
        size = st.selectbox('Farm Size', ['Small (< 0.5 acre)', 'Medium (0.5-5 acres)', 'Large (5+ acres)'])

    if st.button('ðŸ’µ Calculate Investment', use_container_width=True):
        with st.spinner('Calculating...'):
            try:
                costs = calc.estimate(country, currency, size)
                c1, c2, c3 = st.columns(3)
                c1.metric('Min Setup', costs['setup_min'])
                c2.metric('Max Setup', costs['setup_max'])
                c3.metric('ROI Period', f"{costs['roi_years']} years")
            except Exception as e:
                st.error(f'Error: {e}')

def download_tab(watermark_enabled):
    st.header('ðŸ“¥ Download Your Professional Plan')
    if 'current_map' not in st.session_state:
        st.warning('Please generate a design in the Design tab first.')
        return

    col1, col2 = st.columns(2)
    with col1:
        st.subheader('ðŸ—ºï¸ Site Map (PNG)')
        buf = st.session_state['current_map']
        buf.seek(0)
        st.download_button(
            'â¬‡ï¸ Download Site Map',
            data=buf, file_name='homestead_site_plan.png',
            mime='image/png', use_container_width=True)

    with col2:
        st.subheader('ðŸ“„ Full PDF Report')
        if st.button('ðŸ“‘ Generate PDF Report', use_container_width=True):
            with st.spinner('Creating 7-Page PDF...'):
                try:
                    pdf_gen = PDFGenerator()
                    raw = st.session_state.get('raw_map')
                    if raw: raw.seek(0)

                    pdf_buf = pdf_gen.create(
                        layout_data=st.session_state['layout_data'],
                        watermark_enabled=watermark_enabled,
                        map_image_buffer=raw,
                        threed_image_buffer=None 
                    )
                    st.success('âœ… PDF Ready for download!')
                    st.download_button(
                        'â¬‡ï¸ Download PDF Report',
                        data=pdf_buf, file_name='homestead_report.pdf',
                        mime='application/pdf', use_container_width=True)
                except Exception as e:
                    st.error(f'PDF error: {e}')

if __name__ == '__main__':
    main()
