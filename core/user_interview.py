"""
Smart Interview System with Tree Slider
Homestead Architect Pro 2026 - Global Edition
"""

import streamlit as st
from typing import Dict, Any

class UserInterview:
    """Interactive questionnaire with tree count control"""

    QUESTIONS = [
        {
            "id": "location",
            "question": "Where is your homestead located?",
            "type": "text",
            "placeholder": "City, Country (e.g., Austin, USA or Pune, India)",
            "help": "We use this to determine climate, rainfall, and growing season"
        },
        {
            "id": "dimensions",
            "question": "What are your plot dimensions?",
            "type": "dimensions",
            "help": "Length and width in feet or meters"
        },
        {
            "id": "house_position",
            "question": "Where is/will be your house located?",
            "type": "select",
            "options": ["North", "South", "East", "West", "Center", "Not built yet"],
            "help": "Affects sun exposure and zone placement"
        },
        {
            "id": "slope",
            "question": "What is the slope direction?",
            "type": "select",
            "options": ["Flat", "North", "South", "East", "West", "Mixed/Undulating"],
            "help": "Critical for water management and drainage"
        },
        {
            "id": "water_source",
            "question": "What is your primary water source?",
            "type": "select",
            "options": ["Borewell/Well", "Municipal Supply", "Rainwater", "River/Pond", "None yet"],
            "help": "Determines irrigation system design"
        },
        {
            "id": "livestock",
            "question": "Which animals do you plan to keep?",
            "type": "multiselect",
            "options": ["None", "Chickens", "Goats", "Pigs", "Cows", "Bees", "Fish"],
            "help": "Select all that apply"
        },
        {
            "id": "tree_count",
            "question": "How many fruit/nut trees do you want in your Food Forest?",
            "type": "slider",
            "min": 5,
            "max": 50,
            "default": 15,
            "help": "More trees = more income but needs more space"
        },
        {
            "id": "budget",
            "question": "What is your budget range?",
            "type": "select",
            "options": ["Under $5,000", "$5,000 - $25,000", "$25,000 - $100,000", "$100,000+", "Not sure"],
            "help": "Helps us recommend appropriate solutions"
        }
    ]

    def run(self) -> Dict[str, Any]:
        """Run the interview and return answers"""
        answers = {}

        st.subheader("Design Your Homestead")
        st.caption("Answer these questions for your custom permaculture design")

        with st.form("homestead_interview"):
            for q in self.QUESTIONS:
                answers[q['id']] = self._render_question(q)

            submitted = st.form_submit_button(
                "Generate My Homestead Design",
                use_container_width=True,
                type="primary"
            )

        if submitted:
            if not answers.get('location'):
                st.error("Please enter your location")
                return None

            st.session_state['project_name'] = answers['location'].replace(',', '_').replace(' ', '_')
            return answers

        return None

    def _render_question(self, q: Dict) -> Any:
        """Render a single question based on type"""
        st.markdown(f"**{q['question']}**")

        if q['type'] == 'text':
            return st.text_input(
                label=q['id'],
                placeholder=q.get('placeholder', ''),
                help=q.get('help', ''),
                label_visibility="collapsed"
            )

        elif q['type'] == 'dimensions':
            col1, col2 = st.columns(2)
            with col1:
                length = st.number_input("Length (ft)", 10, 10000, 100, help="feet or meters")
            with col2:
                width = st.number_input("Width (ft)", 10, 10000, 100, help="feet or meters")
            return {"length": length, "width": width}

        elif q['type'] == 'select':
            return st.selectbox(
                label=q['id'],
                options=q['options'],
                help=q.get('help', ''),
                label_visibility="collapsed"
            )

        elif q['type'] == 'multiselect':
            return st.multiselect(
                label=q['id'],
                options=q['options'],
                default=["None"],
                help=q.get('help', ''),
                label_visibility="collapsed"
            )

        elif q['type'] == 'slider':
            return st.slider(
                label=q['id'],
                min_value=q.get('min', 5),
                max_value=q.get('max', 50),
                value=q.get('default', 15),
                help=q.get('help', ''),
                label_visibility="collapsed"
            )

        return None
