"""
🏡 Homestead Architect Pro 2026
ALL FEATURES INCLUDED - Stable Version
"""

import streamlit as st
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent))

# All imports
from core.user_interview import UserInterview
from core.layout_engine import LayoutEngine
from core.livestock_designer import LivestockDesigner
from core.cost_calculator import CostCalculator
from core.climate_engine import ClimateEngine
from core.visualizer_2d import Visualizer2D
from core.watermark_system import WatermarkEngine, PDFWatermark
from core.pdf_generator import PDFGenerator

# Page config
st.set_page_config(
    page_title="Homestead Architect Pro 2026",
    page_icon="🏡",
    layout="wide"
)

# CSS
st.markdown("""
<style>
.main-header {font-size: 2.5rem; font-weight: bold; color: #2E7D32; text-align: center;}
.sub-header {font-size: 1.1rem; color: #666; text-align: center; margin-bottom: 1rem;}
</style>
""", unsafe_allow_html=True)

def main():
    st.markdown('<p class="main-header">🏡 Homestead Architect Pro</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Design Your Dream Homestead | 2026 Edition</p>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.title("⚙️ Settings")
        
        watermark_enabled = st.checkbox(
            "☑️ Add Watermark (chundalgardens.com)",
            value=True
        )
        
        st.divider()
        st.markdown("Made by: **Chundal Gardens**")
    
    # Tabs
    tabs = st.tabs(["🎨 Design", "🐐 Livestock", "💰 Costs", "📥 Download"])
    
    with tabs[0]:
        design_tab(watermark_enabled)
    with tabs[1]:
        livestock_tab()
    with tabs[2]:
        costs_tab()
    with tabs[3]:
        download_tab(watermark_enabled)

def design_tab(watermark_enabled):
    st.header("🎨 Smart Homestead Designer")
    
    interview = UserInterview()
    answers = interview.run()
    
    if answers:
        st.success("✅ Design ready!")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            with st.spinner("Generating..."):
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
                
                st.session_state['current_map'] = final_buffer
                st.session_state['layout_data'] = layout
        
        with col2:
            if 'layout_data' in st.session_state:
                stats = st.session_state['layout_data']
                st.metric("Area", f"{stats.get('total_sqft', 0):,} sq.ft.")
                st.metric("Category", stats.get('category', '').title())

def livestock_tab():
    st.header("🐐 Livestock Housing Designer")
    
    designer = LivestockDesigner()
    
    animal = st.selectbox("Animal", ["Goats", "Chickens", "Pigs"])
    count = st.number_input("Count", 1, 1000, 10)
    climate = st.selectbox("Climate", ["Tropical", "Dry", "Temperate", "Cold"])
    budget = st.selectbox("Budget", ["Basic", "Standard", "Premium"])
    
    if st.button("Generate Housing Plan"):
        with st.spinner("Creating..."):
            design = designer.create_housing(animal, count, climate, budget)
            st.image(design['floor_plan'], use_column_width=True)
            
            st.subheader("Specifications")
            for k, v in design['specs'].items():
                st.write(f"**{k}:** {v}")

def costs_tab():
    st.header("💰 Cost Calculator")
    
    calc = CostCalculator()
    
    country = st.selectbox("Country", ["USA", "India", "UK", "Canada", "Australia"])
    currency = st.selectbox("Currency", ["USD", "INR", "EUR", "GBP", "CAD", "AUD"])
    size = st.selectbox("Size", ["Small", "Medium", "Large"])
    
    if st.button("Calculate Costs"):
        costs = calc.estimate(country, currency, size)
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Setup (Min)", costs['setup_min'])
        col2.metric("Setup (Max)", costs['setup_max'])
        col3.metric("ROI", f"{costs['roi_years']} years")

def download_tab(watermark_enabled):
    st.header("📥 Download")
    
    if 'current_map' not in st.session_state:
        st.warning("Generate design first!")
        return
    
    st.download_button(
        "Download Map (PNG)",
        st.session_state['current_map'],
        "homestead_map.png",
        "image/png"
    )
    
    if st.button("Generate PDF Report"):
        with st.spinner("Creating PDF..."):
            pdf_gen = PDFGenerator()
            pdf_buffer = pdf_gen.create(
                st.session_state['layout_data'],
                watermark_enabled
            )
            st.download_button(
                "Download PDF",
                pdf_buffer,
                "homestead_report.pdf",
                "application/pdf"
            )

if __name__ == "__main__":
    main()
