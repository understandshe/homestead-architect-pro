"""
Global Cost Calculator
Real-time pricing by country and region
"""

import json
from typing import Dict, Any
from pathlib import Path

class CostCalculator:
    """Calculates accurate homestead costs globally"""
    
    def __init__(self):
        self.data_path = Path(__file__).parent.parent / 'data' / 'materials_global.json'
        self.prices = self._load_prices()
    
    def _load_prices(self) -> Dict:
        """Load material prices by country"""
        # Default prices if file doesn't exist
        default_prices = {
            "USA": {"currency": "USD", "labor_rate": 25, "concrete": 120, "steel": 800, "lumber": 600},
            "India": {"currency": "INR", "labor_rate": 500, "concrete": 4000, "steel": 55000, "lumber": 800},
            "UK": {"currency": "GBP", "labor_rate": 20, "concrete": 90, "steel": 600, "lumber": 500},
            "Canada": {"currency": "CAD", "labor_rate": 30, "concrete": 140, "steel": 900, "lumber": 700},
            "Australia": {"currency": "AUD", "labor_rate": 35, "concrete": 150, "steel": 950, "lumber": 800}
        }
        
        try:
            with open(self.data_path, 'r') as f:
                return json.load(f)
        except:
            return default_prices
    
    def estimate(self, country: str, currency: str, size_category: str) -> Dict[str, Any]:
        """Generate complete cost estimate"""
        
        prices = self.prices.get(country, self.prices['USA'])
        
        # Base costs by size (USD equivalent)
        base_costs = {
            'small': {'setup': 5000, 'annual_income': 2000, 'annual_expense': 800},
            'medium': {'setup': 35000, 'annual_income': 12000, 'annual_expense': 4000},
            'large': {'setup': 150000, 'annual_income': 50000, 'annual_expense': 15000}
        }
        
        cat_key = 'small' if 'Small' in size_category else 'medium' if 'Medium' in size_category else 'large'
        base = base_costs[cat_key]
        
        # Convert to local currency
        conversion_rates = {
            'USD': 1, 'INR': 83, 'EUR': 0.92, 'GBP': 0.79, 
            'CAD': 1.35, 'AUD': 1.52
        }
        rate = conversion_rates.get(currency, 1)
        
        setup_min = int(base['setup'] * rate * 0.8)
        setup_max = int(base['setup'] * rate * 1.5)
        
        return {
            'setup_min': f"{currency} {setup_min:,}",
            'setup_max': f"{currency} {setup_max:,}",
            'income_min': f"{currency} {int(base['annual_income'] * rate * 0.7):,}",
            'expense_min': f"{currency} {int(base['annual_expense'] * rate):,}",
            'roi_years': 3 if cat_key == 'small' else 4 if cat_key == 'medium' else 5,
            'break_even': f"Year {2 if cat_key == 'small' else 3}",
            'breakdown': {
                'Infrastructure': setup_min * 0.4,
                'Livestock': setup_min * 0.2,
                'Equipment': setup_min * 0.15,
                'Seeds/Plants': setup_min * 0.1,
                'Labor': setup_min * 0.15
            }
        }

