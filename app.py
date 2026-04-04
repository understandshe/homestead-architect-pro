"""
Homestead Architect Pro 2026 — APP (Fixed for ULTRA EDITION Visualizer)
Connects to: visualizer_3d.py (your ULTRA EDITION with HTML download)
"""

import streamlit as st
import sys
import io
import subprocess
from pathlib import Path

# Path setup
BASE_DIR = Path(__file__).parent
sys.path.insert(0, str(BASE_DIR))
sys.path.insert(0, str(BASE_DIR / 'core'))

# Core imports
try:
    from core.user_interview import UserInterview
    from core.layout_engine import LayoutEngine
    from core.livestock_designer import LivestockDesigner
    from core.cost_calculator import CostCalculator
    from core.climate_engine import ClimateEngine
    from core.visualizer_2d import Visualizer2D
    from core.watermark_system import WatermarkEngine
    from core.pdf_generator import PDFGenerator
except ImportError as e:
    st.error(f"Core module error: {e}")
    st.stop()

# 3D Visualizer import - tries multiple locations
try:
    # Try root folder first (your file is here)
    from visualizer_3d import Visualizer3D
except ImportError:
    try:
        # Try core folder
        from core.visualizer_3d import Visualizer3D
    except ImportError as e:
        st.error("visualizer_3d.py not found.")
        st.error("Expected: visualizer_3d.py in root or core/ folder")
        st.stop()

# Page config
st.set_page_config(
    page_title='Homestead Architect Pro 2026',
    page_icon='H',
    layout='wide'
)

# Styling
st.markdown("""
<style>
.main-header {font-size:2.5rem; font-weight:bold; color:#2E7D32; text-align:center;}
.sub-header {font-size:1.1rem; color:#666; text-align:center; margin-bottom:1rem;}
.success-box {background:#C8E6C9; padding:15px; border-radius:10px; border-left:5px solid #2E7D32;}
</style>
""", unsafe_allow_html=True)

def _build_version() -> str:
    """Return deploy build marker to verify latest release on Streamlit Cloud."""
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"], text=True
        ).strip()
    except Exception:
        return "unknown"


def main():
    build_id = _build_version()
    st.markdown('<p class="main-header">Homestead Architect Pro</p>', unsafe_allow_html=True)
    st.markdown(
        f'<p class="sub-header">ULTRA EDITION with 3D Labels & HTML Export | Build: {build_id}</p>',
        unsafe_allow_html=True
    )
    
    with st.sidebar:
        st.title('Settings')
        watermark_enabled = st.checkbox('Watermark (chundalgardens.com)', value=True)
        st.divider()
        st.markdown('Made by: **Chundal Gardens**')
        st.markdown('chundalgardens.com')
        st.caption(f"Build: {build_id}")
    
    # Tabs
    tabs = st.tabs(['Design', '3D View', 'Livestock', 'Costs', 'Download'])
    
    with tabs[0]: design_tab(watermark_enabled)
    with tabs[1]: view_3d_tab()
    with tabs[2]: livestock_tab()
    with tabs[3]: costs_tab()
    with tabs[4]: download_tab(watermark_enabled)


def design_tab(watermark_enabled):
    """Design tab - generates layout"""
    st.header('Smart Homestead Designer')
    
    interview = UserInterview()
    answers = interview.run()
    
    if not answers:
        return
    
    st.markdown('<div class="success-box">Generating your design...</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        with st.spinner('Rendering...'):
            engine = LayoutEngine()
            layout = engine.generate(answers)
            # Preserve user context for premium map/PDF personalization.
            layout['location'] = answers.get('location', layout.get('location', 'Custom Location'))
            layout['water_source'] = answers.get('water_source', layout.get('water_source', ''))
            layout['slope'] = answers.get('slope', layout.get('slope', 'Flat'))
            
            viz = Visualizer2D()
            raw_map = viz.create(layout, answers)
            
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
            st.metric('Total Area', f"{ld.get('total_sqft', 0):,} sq.ft.")
            st.metric('Acres', f"{ld.get('acres', 0):.2f}")
            st.metric('Category', ld.get('category', '').title())
            
            lv = [x for x in ld.get('livestock', []) if x and x != 'None']
            if lv:
                st.info('Animals: ' + ', '.join(lv))
            
            if answers.get('location'):
                try:
                    climate = ClimateEngine().get_data(answers['location'])
                    st.info(f"Climate: **{climate['zone']}**")
                except:
                    pass


def view_3d_tab():
    """3D View tab - uses YOUR ULTRA EDITION visualizer"""
    st.header('Interactive 3D Cinematic View')
    
    if 'layout_data' not in st.session_state:
        st.info('Please generate a design in the Design tab first.')
        # Empty call to show the tool
        viz3d = Visualizer3D()
        viz3d.create({})
        return
    
    # Use YOUR visualizer with all features
    with st.container():
        viz3d = Visualizer3D()
        viz3d.create(st.session_state['layout_data'])
        
        # Note: HTML download button is already inside your visualizer_3d.py!


def livestock_tab():
    """Livestock tab"""
    st.header('Livestock Housing Designer')
    designer = LivestockDesigner()
    
    col1, col2 = st.columns(2)
    with col1:
        animal = st.selectbox('Animal Type', ['Goats', 'Chickens', 'Pigs'])
        count = st.number_input('Total Count', 1, 1000, 10)
    with col2:
        climate = st.selectbox('Climate', ['Tropical', 'Dry', 'Temperate', 'Cold'])
        budget = st.selectbox('Budget', ['Basic', 'Standard', 'Premium'])
    
    if st.button('Generate Housing Plan', use_container_width=True):
        with st.spinner('Designing...'):
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


def costs_tab():
    """Costs tab"""
    st.header('Global Cost Calculator')
    calc = CostCalculator()
    
    c1, c2, c3 = st.columns(3)
    with c1:
        country = st.selectbox('Country', ['USA', 'India', 'UK', 'Canada', 'Australia'])
    with c2:
        currency = st.selectbox('Currency', ['USD', 'INR', 'EUR', 'GBP', 'CAD', 'AUD'])
    with c3:
        size = st.selectbox('Farm Size', ['Small (< 0.5 acre)', 'Medium (0.5-5 acres)', 'Large (5+ acres)'])
    
    if st.button('Calculate Investment', use_container_width=True):
        with st.spinner('Calculating...'):
            costs = calc.estimate(country, currency, size)
            c1, c2, c3 = st.columns(3)
            c1.metric('Min Setup', costs['setup_min'])
            c2.metric('Max Setup', costs['setup_max'])
            c3.metric('ROI Period', f"{costs['roi_years']} years")


def download_tab(watermark_enabled):
    """Download tab"""
    st.header('Download Your Professional Plan')
    
    if 'current_map' not in st.session_state:
        st.warning('Please generate a design first.')
        return
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader('Site Map (PNG)')
        buf = st.session_state['current_map']
        buf.seek(0)
        st.download_button(
            'Download Site Map',
            data=buf,
            file_name='homestead_site_plan.png',
            mime='image/png',
            use_container_width=True
        )
    
    with col2:
        st.subheader('Full PDF Report')
        if st.button('Generate PDF Report', use_container_width=True):
            with st.spinner('Creating PDF...'):
                pdf_gen = PDFGenerator()
                raw = st.session_state.get('raw_map')
                if raw:
                    raw.seek(0)
                
                pdf_buf = pdf_gen.create(
                    layout_data=st.session_state['layout_data'],
                    watermark_enabled=watermark_enabled,
                    map_image_buffer=raw,
                    threed_image_buffer=None
                )
                st.success('PDF Ready')
                st.download_button(
                    'Download PDF Report',
                    data=pdf_buf,
                    file_name='homestead_report.pdf',
                    mime='application/pdf',
                    use_container_width=True
                )


if __name__ == '__main__':
    main()
