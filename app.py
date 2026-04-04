"""
Homestead Architect Pro 2026 — v3.1 REALISTIC EDITION
Fixed imports + Realistic 3D Visualizer Integration
"""

import streamlit as st
import sys
import io
import json
from pathlib import Path

# Path configuration — ensure core is accessible
BASE_DIR = Path(__file__).parent
sys.path.insert(0, str(BASE_DIR))
sys.path.insert(0, str(BASE_DIR / 'core'))

# Try imports with fallback
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
    st.error(f"Core module import error: {e}")
    st.stop()

# 3D Visualizer import with multiple fallbacks
visualizer_3d = None
try:
    # Try realistic visualizer first (new)
    from realistic_visualizer_3d import RealisticVisualizer3D
    visualizer_3d = RealisticVisualizer3D
    VISUALIZER_MODE = "REALISTIC"
except ImportError:
    try:
        # Fallback to core.visualizer_3d (original)
        from core.visualizer_3d import Visualizer3D
        visualizer_3d = Visualizer3D
        VISUALIZER_MODE = "STANDARD"
    except ImportError:
        try:
            # Fallback to visualizer_3d in root
            from visualizer_3d import Visualizer3D
            visualizer_3d = Visualizer3D
            VISUALIZER_MODE = "STANDARD"
        except ImportError as e:
            st.error(f"3D Visualizer not found: {e}")
            st.error("Please ensure visualizer_3d.py or realistic_visualizer_3d.py exists")
            VISUALIZER_MODE = "NONE"
            visualizer_3d = None

# Page Configuration
st.set_page_config(
    page_title='Homestead Architect Pro 2026',
    page_icon='🏡',
    layout='wide',
    initial_sidebar_state='expanded'
)

# Custom Styling
st.markdown("""
<style>
.main-header {
    font-size: 2.8rem;
    font-weight: 800;
    color: #1B5E20;
    text-align: center;
    text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    margin-bottom: 0.5rem;
}
.sub-header {
    font-size: 1.2rem;
    color: #555;
    text-align: center;
    margin-bottom: 2rem;
    font-weight: 400;
}
[data-testid="stMetricValue"] {
    font-size: 2rem !important;
    font-weight: 700 !important;
    color: #2E7D32 !important;
}
[data-testid="stMetricLabel"] {
    font-size: 1rem !important;
    color: #666 !important;
}
.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
}
.stTabs [data-baseweb="tab"] {
    height: 50px;
    padding-left: 20px;
    padding-right: 20px;
    font-weight: 600;
    font-size: 1.1rem;
}
.success-box {
    background: linear-gradient(135deg, #C8E6C9 0%, #A5D6A7 100%);
    padding: 20px;
    border-radius: 15px;
    border-left: 5px solid #2E7D32;
    margin: 10px 0;
}
.info-badge {
    background: #E3F2FD;
    padding: 10px 15px;
    border-radius: 8px;
    border-left: 4px solid #1976D2;
    margin: 5px 0;
}
</style>
""", unsafe_allow_html=True)


def main():
    # Header
    st.markdown('<p class="main-header">🏡 Homestead Architect Pro</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Design Your Dream Homestead with Realistic 3D Visualization | 2026 Edition</p>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.title('⚙️ Configuration')
        
        watermark_enabled = st.checkbox(
            '☑️ Enable Watermark (chundalgardens.com)', 
            value=True,
            help="Adds watermark to protect your designs"
        )
        
        # Visualizer mode indicator
        if VISUALIZER_MODE == "REALISTIC":
            st.success("🎨 3D Mode: REALISTIC (Real-world scale)")
        elif VISUALIZER_MODE == "STANDARD":
            st.info("🎨 3D Mode: STANDARD")
        else:
            st.warning("🎨 3D Mode: NOT AVAILABLE")
        
        st.divider()
        
        st.markdown("### 📊 Quick Stats")
        if 'layout_data' in st.session_state:
            ld = st.session_state['layout_data']
            st.metric("Area", f"{ld.get('acres', 0):.2f} acres")
            st.metric("Category", ld.get('category', 'N/A'))
        else:
            st.info("Generate a design to see stats")
        
        st.divider()
        st.markdown("**Made by: Chundal Gardens**")
        st.markdown("🌐 [chundalgardens.com](https://chundalgardens.com)")
    
    # Tabs
    tabs = st.tabs([
        '🎨 Design Studio', 
        '🌐 Realistic 3D View', 
        '🐑 Livestock Designer', 
        '💰 Cost Calculator', 
        '📥 Export & Download'
    ])
    
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


def design_tab(watermark_enabled):
    """Design tab with 2D visualization"""
    st.header('🎨 Smart Homestead Designer')
    
    interview = UserInterview()
    answers = interview.run()
    
    if not answers:
        st.info("👆 Fill out the interview questions above to generate your design")
        return
    
    st.markdown('<div class="success-box">✅ Generating your custom homestead design...</div>', 
                unsafe_allow_html=True)
    
    col1, col2 = st.columns([3, 2])
    
    with col1:
        with st.spinner('🎨 Rendering professional site plan...'):
            try:
                engine = LayoutEngine()
                layout = engine.generate(answers)
                
                viz = Visualizer2D()
                raw_map = viz.create(layout, answers)
                
                # Save raw for PDF
                raw_map.seek(0)
                st.session_state['raw_map'] = io.BytesIO(raw_map.read())
                
                raw_map.seek(0)
                if watermark_enabled:
                    display_map = WatermarkEngine.apply_visible_watermark(raw_map)
                else:
                    display_map = WatermarkEngine.apply_protection_watermark(raw_map)
                
                st.image(display_map, use_column_width=True, caption="2D Site Plan")
                st.session_state['current_map'] = display_map
                st.session_state['layout_data'] = layout
                st.session_state['answers'] = answers
                
            except Exception as e:
                st.error(f"Design generation error: {e}")
                st.exception(e)
    
    with col2:
        if 'layout_data' in st.session_state:
            ld = st.session_state['layout_data']
            
            st.subheader("📐 Site Metrics")
            m1, m2 = st.columns(2)
            with m1:
                st.metric('Total Area', f"{ld.get('total_sqft', 0):,} sq.ft.")
                st.metric('Acres', f"{ld.get('acres', 0):.2f}")
            with m2:
                st.metric('Dimensions', f"{int(ld.get('dimensions', {}).get('L', 0))} × {int(ld.get('dimensions', {}).get('W', 0))} ft")
                st.metric('Category', ld.get('category', 'N/A').title())
            
            # Livestock info
            lv = [x for x in ld.get('livestock', []) if x and x != 'None']
            if lv:
                st.markdown('<div class="info-badge">🐾 Animals: ' + ', '.join(lv) + '</div>', 
                          unsafe_allow_html=True)
            
            # Climate info
            if answers.get('location'):
                try:
                    climate = ClimateEngine().get_data(answers['location'])
                    st.markdown(f'<div class="info-badge">⛅ Climate Zone: <b>{climate.get("zone", "Unknown")}</b></div>', 
                              unsafe_allow_html=True)
                except:
                    pass
            
            st.info("💡 Tip: Switch to 'Realistic 3D View' tab to see your design in 3D!")


def view_3d_tab():
    """3D visualization tab with realistic rendering"""
    st.header('🌐 Realistic 3D Cinematic View')
    
    if visualizer_3d is None:
        st.error("❌ 3D Visualizer not available. Please check installation.")
        st.info("Expected files: realistic_visualizer_3d.py or core/visualizer_3d.py")
        return
    
    if 'layout_data' not in st.session_state:
        st.warning("👈 Please generate a design in the 'Design Studio' tab first!")
        
        # Show empty state with demo
        with st.expander("ℹ️ What you'll see here"):
            st.markdown("""
            **Features of Realistic 3D View:**
            - 🏠 **Real-world scale**: 1 unit = 1 foot
            - 🌳 **Botanically accurate trees** with proper heights
            - 🐄 **Real barn dimensions** (no oversized sheds)
            - 📐 **Dynamic scaling**: Works for 1-1000 acres
            - 🎥 **Multiple camera angles**: Isometric, Top, North, South, etc.
            - 💧 **Realistic water features** with depth
            """)
        
        # Try to show empty visualizer
        try:
            viz = visualizer_3d()
            viz.create({})
        except:
            pass
        return
    
    # Real 3D rendering
    layout_data = st.session_state['layout_data']
    
    # Info banner
    acres = layout_data.get('acres', 0)
    st.markdown(f'<div class="success-box">🎯 Rendering {acres:.2f} acres in REALISTIC 3D | Scale: 1 unit = 1 foot</div>', 
                unsafe_allow_html=True)
    
    with st.container():
        with st.spinner('🎬 Generating cinematic 3D view...'):
            try:
                viz = visualizer_3d()
                
                # Check if it's realistic visualizer (has user_models param)
                import inspect
                sig = inspect.signature(viz.create)
                if 'user_models' in sig.parameters:
                    # Realistic visualizer
                    user_models = st.session_state.get('user_models', [])
                    viz.create(layout_data, user_models=user_models)
                else:
                    # Standard visualizer
                    viz.create(layout_data)
                    
            except Exception as e:
                st.error(f"3D rendering error: {e}")
                st.exception(e)
                st.info("💡 Try refreshing or check the layout data")


def livestock_tab():
    """Livestock housing designer"""
    st.header('🐑 Professional Livestock Housing Designer')
    
    designer = LivestockDesigner()
    
    col1, col2 = st.columns(2)
    with col1:
        animal = st.selectbox(
            '🐾 Animal Type',
            ['Goats', 'Chickens', 'Pigs', 'Cows', 'Sheep', 'Rabbits'],
            help="Select animal for housing design"
        )
        count = st.number_input('📊 Total Count', 1, 1000, 10, 
                               help="Number of animals to house")
    with col2:
        climate = st.selectbox(
            '🌍 Regional Climate',
            ['Tropical', 'Dry/Arid', 'Temperate', 'Cold', 'Highland'],
            help="Climate affects ventilation and insulation"
        )
        budget = st.selectbox(
            '💰 Project Budget',
            ['Basic/Economy', 'Standard', 'Premium', 'Luxury'],
            help="Budget level determines materials"
        )
    
    if st.button('🏗️ Generate Housing Plan', use_container_width=True, type='primary'):
        with st.spinner('🔨 Designing optimal housing...'):
            try:
                design = designer.create_housing(animal, count, climate, budget)
                
                if 'floor_plan' in design:
                    st.image(design['floor_plan'], use_column_width=True, 
                            caption=f"{animal} Housing Floor Plan")
                
                c1, c2 = st.columns(2)
                with c1:
                    st.subheader('📋 Specifications')
                    for k, v in design.get('specs', {}).items():
                        st.write(f'**{k}:** {v}')
                with c2:
                    st.subheader('🔧 Materials List')
                    for k, v in design.get('materials', {}).items():
                        st.write(f'**{k}:** {v}')
                
                cost = design.get('estimated_cost', 'N/A')
                st.success(f"💵 Estimated Investment: **{cost}**")
                
            except Exception as e:
                st.error(f'Design error: {e}')
                st.exception(e)


def costs_tab():
    """Cost estimation tab"""
    st.header('💰 Global Investment Calculator')
    
    calc = CostCalculator()
    
    c1, c2, c3 = st.columns(3)
    with c1:
        country = st.selectbox(
            '🌍 Country',
            ['USA', 'India', 'UK', 'Canada', 'Australia', 'Germany', 'France', 'Brazil']
        )
    with c2:
        currency = st.selectbox(
            '💱 Currency',
            ['USD', 'INR', 'EUR', 'GBP', 'CAD', 'AUD', 'BRL']
        )
    with c3:
        size = st.selectbox(
            '📐 Farm Size',
            ['Small (< 0.5 acre)', 'Medium (0.5-5 acres)', 'Large (5-20 acres)', 'Estate (20+ acres)']
        )
    
    if st.button('💵 Calculate Investment', use_container_width=True, type='primary'):
        with st.spinner('💰 Analyzing costs...'):
            try:
                costs = calc.estimate(country, currency, size)
                
                c1, c2, c3, c4 = st.columns(4)
                with c1:
                    st.metric('Minimum Setup', costs.get('setup_min', 'N/A'))
                with c2:
                    st.metric('Maximum Setup', costs.get('setup_max', 'N/A'))
                with c3:
                    st.metric('Annual Operating', costs.get('annual_operating', 'N/A'))
                with c4:
                    st.metric('ROI Period', f"{costs.get('roi_years', 'N/A')} years")
                
                # Breakdown
                if 'breakdown' in costs:
                    with st.expander("📊 Detailed Breakdown"):
                        for category, amount in costs['breakdown'].items():
                            st.write(f"**{category}:** {amount}")
                            
            except Exception as e:
                st.error(f'Calculation error: {e}')


def download_tab(watermark_enabled):
    """Export and download tab"""
    st.header('📥 Export Your Professional Plan')
    
    if 'current_map' not in st.session_state:
        st.warning('⚠️ Please generate a design in the Design Studio tab first.')
        return
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader('🗺️ Site Map (PNG)')
        buf = st.session_state['current_map']
        buf.seek(0)
        st.download_button(
            '⬇️ Download Site Map (PNG)',
            data=buf,
            file_name='homestead_site_plan.png',
            mime='image/png',
            use_container_width=True,
            help="High-resolution 2D site plan"
        )
    
    with col2:
        st.subheader('📄 Professional PDF Report')
        
        include_3d = st.checkbox('Include 3D view in PDF', value=True)
        
        if st.button('📑 Generate PDF Report', use_container_width=True, type='primary'):
            with st.spinner('📄 Creating comprehensive PDF report...'):
                try:
                    pdf_gen = PDFGenerator()
                    
                    # Get buffers
                    raw = st.session_state.get('raw_map')
                    if raw:
                        raw.seek(0)
                    
                    # Try to get 3D snapshot if available
                    three_d_buf = None
                    if include_3d and 'layout_data' in st.session_state:
                        # Note: 3D to image conversion would need additional setup
                        pass
                    
                    pdf_buf = pdf_gen.create(
                        layout_data=st.session_state['layout_data'],
                        watermark_enabled=watermark_enabled,
                        map_image_buffer=raw,
                        threed_image_buffer=three_d_buf
                    )
                    
                    st.success('✅ Professional PDF Report Ready!')
                    st.download_button(
                        '⬇️ Download PDF Report',
                        data=pdf_buf,
                        file_name=f"homestead_plan_{st.session_state.get('answers', {}).get('name', 'design')}.pdf",
                        mime='application/pdf',
                        use_container_width=True
                    )
                    
                except Exception as e:
                    st.error(f'PDF generation error: {e}')
                    st.exception(e)


if __name__ == '__main__':
    main()
