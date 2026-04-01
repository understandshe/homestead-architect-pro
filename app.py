"""
🏡 Homestead Architect Pro 2026
Main Application Entry Point
"""

import streamlit as st
import sys
from pathlib import Path

# Add core to path
sys.path.append(str(Path(__file__).parent))

from core.user_interview import UserInterview
from core.layout_engine import LayoutEngine
from core.livestock_designer import LivestockDesigner
from core.cost_calculator import CostCalculator
from core.climate_engine import ClimateEngine
from core.visualizer_2d import Visualizer2D
from core.visualizer_3d import Visualizer3D
from core.watermark_system import WatermarkEngine, PDFWatermark
from core.pdf_generator import PDFGenerator

# Page Config
st.set_page_config(
    page_title="Homestead Architect Pro 2026",
    page_icon="🏡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #2E7D32;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .stButton>button {
        background-color: #2E7D32;
        color: white;
        font-weight: bold;
        padding: 1rem 2rem;
        border-radius: 10px;
    }
    .feature-card {
        background-color: #F1F8E9;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #2E7D32;
    }
</style>
""", unsafe_allow_html=True)

def main():
    # Header
    st.markdown('<p class="main-header">🏡 Homestead Architect Pro</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Design Your Dream Homestead in 60 Seconds | 2026 Edition</p>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.image("https://via.placeholder.com/150x150/2E7D32/FFFFFF?text=HA+Pro", width=150)
        st.title("⚙️ Settings")
        
        # Watermark Toggle (YOUR SPEC)
        watermark_enabled = st.checkbox(
            "☑️ Add Watermark (chundalgardens.com)",
            value=True,
            help="Checked: Large diagonal watermark | Unchecked: Small protected watermarks"
        )
        
        if watermark_enabled:
            st.info("✓ Visible watermark mode")
        else:
            st.warning("⚠️ Protection mode active")
        
        st.divider()
        st.markdown("**Made by:** [Chundal Gardens](https://chundalgardens.com)")
        st.markdown("**Version:** 2026.1.0")
    
    # Main Content Tabs
    tab1, tab2, tab3, tab4 = st.tabs(["🎨 Design", "🐐 Livestock", "💰 Costs", "📥 Download"])
    
    with tab1:
        design_tab(watermark_enabled)
    
    with tab2:
        livestock_tab()
    
    with tab3:
        costs_tab()
    
    with tab4:
        download_tab(watermark_enabled)

def design_tab(watermark_enabled):
    st.header("🎨 Smart Homestead Designer")
    
    # 7-Question Interview
    interview = UserInterview()
    answers = interview.run()
    
    if answers:
        st.success("✅ All questions answered!")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("📐 Your Layout")
            
            # Generate Layout
            with st.spinner("🤖 AI is designing your homestead..."):
                engine = LayoutEngine()
                layout = engine.generate(answers)
                
                # Visualize
                viz = Visualizer2D()
                map_buffer = viz.create(layout, answers)
                
                # Apply Watermark
                if watermark_enabled:
                    final_buffer = WatermarkEngine.apply_visible_watermark(map_buffer)
                    st.info("📌 Visible watermark applied")
                else:
                    final_buffer = WatermarkEngine.apply_protection_watermark(map_buffer)
                    st.info("🔒 Protection watermarks applied")
                
                # Display
                st.image(final_buffer, use_column_width=True)
                
                # Store in session for download
                st.session_state['current_map'] = final_buffer
                st.session_state['layout_data'] = layout
        
        with col2:
            st.subheader("📊 Quick Stats")
            if 'layout_data' in st.session_state:
                stats = st.session_state['layout_data']
                st.metric("Total Area", f"{stats.get('total_sqft', 0):,} sq.ft.")
                st.metric("Zones", len(stats.get('zones', {})))
                st.metric("Features", len([f for f in stats.get('features', {}).values() if f]))
                
                st.divider()
                st.subheader("🌍 Climate")
                climate = ClimateEngine()
                data = climate.get_data(answers.get('location', 'Unknown'))
                st.write(f"**Zone:** {data.get('zone', 'N/A')}")
                st.write(f"**Rainfall:** {data.get('rainfall', 'N/A')} mm/year")
                st.write(f"**Growing Season:** {data.get('growing_days', 'N/A')} days")

def livestock_tab():
    st.header("🐐 Professional Livestock Housing")
    
    designer = LivestockDesigner()
    
    animal_type = st.selectbox(
        "Select Animal",
        ["Goats", "Chickens", "Pigs", "Mixed System"]
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        count = st.number_input(f"Number of {animal_type.lower()}", 1, 1000, 10)
        climate = st.selectbox("Climate", ["Tropical", "Dry", "Temperate", "Cold"])
        budget = st.select_slider("Budget Tier", ["Basic", "Standard", "Premium"])
    
    with col2:
        if st.button("🏗️ Generate Housing Design"):
            with st.spinner("Creating 3D housing plan..."):
                design = designer.create_housing(animal_type, count, climate, budget)
                
                st.subheader("📐 Floor Plan")
                st.image(design['floor_plan'], use_column_width=True)
                
                st.subheader("🔧 Specifications")
                for spec, value in design['specs'].items():
                    st.write(f"**{spec}:** {value}")
                
                st.subheader("📦 Materials Needed")
                for material, qty in design['materials'].items():
                    st.write(f"- {material}: {qty}")

def costs_tab():
    st.header("💰 Global Cost Calculator")
    
    calc = CostCalculator()
    
    col1, col2, col3 = st.columns(3)
    with col1:
        country = st.selectbox("Country", ["USA", "India", "UK", "Canada", "Australia", "Other"])
    with col2:
        currency = st.selectbox("Currency", ["USD", "INR", "EUR", "GBP", "CAD", "AUD"])
    with col3:
        size_category = st.selectbox("Homestead Size", ["Small (< 0.5 acre)", "Medium (0.5-5 acres)", "Large (> 5 acres)"])
    
    if st.button("💵 Calculate Costs"):
        with st.spinner("Fetching latest prices..."):
            costs = calc.estimate(country, currency, size_category)
            
            st.subheader("💰 Investment Breakdown")
            
            col_a, col_b, col_c = st.columns(3)
            with col_a:
                st.metric("Setup Cost (Min)", costs['setup_min'])
                st.metric("Annual Income", costs['income_min'])
            with col_b:
                st.metric("Setup Cost (Max)", costs['setup_max'])
                st.metric("Annual Expense", costs['expense_min'])
            with col_c:
                st.metric("ROI Timeline", f"{costs['roi_years']} years")
                st.metric("Break-even", costs['break_even'])
            
            st.subheader("📊 Detailed Breakdown")
            st.bar_chart(costs['breakdown'])

def download_tab(watermark_enabled):
    st.header("📥 Download Your Plans")
    
    if 'current_map' not in st.session_state:
        st.warning("⚠️ Please generate a design first in the 'Design' tab")
        return
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🖼️ Site Plan (PNG)")
        st.download_button(
            label="📥 Download HD Map",
            data=st.session_state['current_map'],
            file_name=f"homestead_plan_{st.session_state.get('project_name', 'myfarm')}.png",
            mime="image/png"
        )
        
        # 3D View option
        if st.button("🎲 Generate 3D View"):
            with st.spinner("Rendering 3D..."):
                viz3d = Visualizer3D()
                scene = viz3d.create(st.session_state['layout_data'])
                st.plotly_chart(scene, use_container_width=True)
    
    with col2:
        st.subheader("📄 Full Report (PDF)")
        
        if st.button("📑 Generate PDF Report"):
            with st.spinner("Creating professional report..."):
                pdf_gen = PDFGenerator()
                pdf_buffer = pdf_gen.create(
                    st.session_state['layout_data'],
                    watermark_enabled
                )
                
                st.download_button(
                    label="📥 Download PDF Report",
                    data=pdf_buffer,
                    file_name=f"homestead_report_{st.session_state.get('project_name', 'myfarm')}.pdf",
                    mime="application/pdf"
                )
                
                st.success("✅ PDF includes affiliate products on pages 6-7!")

if __name__ == "__main__":
    main()
