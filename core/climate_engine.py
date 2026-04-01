"""
Climate Intelligence Engine
Auto-suggests based on weather patterns
"""

from typing import Dict, Any

class ClimateEngine:
    """Analyzes climate data for optimal design"""
    
    CLIMATE_ZONES = {
        'Tropical': {
            'rainfall': '2000+ mm',
            'temp_range': '20-35Â°C',
            'growing_days': 365,
            'challenges': ['Heavy rain', 'Pests', 'Heat'],
            'solutions': ['Elevated structures', 'Good drainage', 'Shade nets']
        },
        'Dry': {
            'rainfall': '< 500 mm',
            'temp_range': '10-40Â°C',
            'growing_days': 240,
            'challenges': ['Water scarcity', 'Heat', 'Dust'],
            'solutions': ['Water harvesting', 'Drought crops', 'Mulching']
        },
        'Temperate': {
            'rainfall': '500-1500 mm',
            'temp_range': '-5 to 30Â°C',
            'growing_days': 200,
            'challenges': ['Winter frost', 'Variable weather'],
            'solutions': ['Greenhouses', 'Seasonal planning', 'Cold storage']
        },
        'Cold': {
            'rainfall': '300-800 mm',
            'temp_range': '-20 to 20Â°C',
            'growing_days': 120,
            'challenges': ['Snow', 'Frozen ground', 'Short season'],
            'solutions': ['Heated greenhouses', 'Root cellar', 'Hardy breeds']
        }
    }
    
    def get_data(self, location: str) -> Dict[str, Any]:
        """Get climate data for location"""
        # Simplified - in production would use API
        location_lower = location.lower()
        
        if any(x in location_lower for x in ['india', 'thailand', 'brazil', 'kenya', 'florida']):
            zone = 'Tropical'
        elif any(x in location_lower for x in ['arizona', 'egypt', 'saudi', 'rajasthan']):
            zone = 'Dry'
        elif any(x in location_lower for x in ['canada', 'germany', 'uk', 'new york']):
            zone = 'Temperate'
        elif any(x in location_lower for x in ['alaska', 'norway', 'siberia']):
            zone = 'Cold'
        else:
            zone = 'Temperate'  # Default
        
        return {
            'zone': zone,
            **self.CLIMATE_ZONES[zone]
        }
    
    def get_recommendations(self, climate: str, features: list) -> list:
        """Get specific recommendations"""
        data = self.CLIMATE_ZONES.get(climate, self.CLIMATE_ZONES['Temperate'])
        return data['solutions']
