"""
Test Suite for Homestead Architect Pro
Ensures all modules work correctly
"""

import unittest
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from core.layout_engine import LayoutEngine
from core.livestock_designer import LivestockDesigner
from core.cost_calculator import CostCalculator
from core.climate_engine import ClimateEngine
from core.watermark_system import WatermarkEngine


class TestLayoutEngine(unittest.TestCase):
    """Test AI layout generation"""
    
    def setUp(self):
        self.engine = LayoutEngine()
        self.sample_answers = {
            'dimensions': {'length': 200, 'width': 100},
            'house_position': 'Center',
            'slope': 'Flat',
            'water_source': 'Borewell',
            'livestock': ['Goats', 'Chickens']
        }
    
    def test_layout_generation(self):
        """Test basic layout generation"""
        layout = self.engine.generate(self.sample_answers)
        
        self.assertIn('zones', layout)
        self.assertIn('features', layout)
        self.assertEqual(layout['total_sqft'], 20000)
        self.assertEqual(layout['category'], 'small')
    
    def test_zone_calculation(self):
        """Test zone percentages sum to 100%"""
        layout = self.engine.generate(self.sample_answers)
        total = sum(layout['zones'].values())
        self.assertAlmostEqual(total, 1.0, places=2)
    
    def test_feature_placement(self):
        """Test features are within bounds"""
        layout = self.engine.generate(self.sample_answers)
        L, W = layout['dimensions']['L'], layout['dimensions']['W']
        
        for name, feature in layout['features'].items():
            if 'x' in feature:
                self.assertGreaterEqual(feature['x'], 0)
                self.assertLessEqual(feature['x'], L)
                self.assertGreaterEqual(feature['y'], 0)
                self.assertLessEqual(feature['y'], W)


class TestLivestockDesigner(unittest.TestCase):
    """Test animal housing design"""
    
    def setUp(self):
        self.designer = LivestockDesigner()
    
    def test_goat_house(self):
        """Test goat housing design"""
        design = self.designer.create_housing('Goats', 10, 'Tropical', 'Standard')
        
        self.assertIn('floor_plan', design)
        self.assertIn('specs', design)
        self.assertIn('materials', design)
        self.assertIn('Indoor Area', design['specs'])
    
    def test_chicken_house(self):
        """Test poultry housing design"""
        design = self.designer.create_housing('Chickens', 50, 'Temperate', 'Basic')
        
        self.assertIn('floor_plan', design)
        self.assertIn('Total Area', design['specs'])
    
    def test_piggery(self):
        """Test pig housing design"""
        design = self.designer.create_housing('Pigs', 5, 'Cold', 'Premium')
        
        self.assertIn('floor_plan', design)
        self.assertIn('Farrowing', design['specs'])
    
    def test_space_calculation(self):
        """Test space calculations are reasonable"""
        design = self.designer.create_housing('Goats', 20, 'Dry', 'Standard')
        # 20 goats × 15 sqft = 300 sqft minimum
        indoor = design['specs']['Indoor Area']
        self.assertIn('300', indoor)  # Should contain 300


class TestCostCalculator(unittest.TestCase):
    """Test cost estimation"""
    
    def setUp(self):
        self.calc = CostCalculator()
    
    def test_usa_costs(self):
        """Test USA pricing"""
        costs = self.calc.estimate('USA', 'USD', 'Small (< 0.5 acre)')
        
        self.assertIn('setup_min', costs)
        self.assertIn('USD', costs['setup_min'])
        self.assertIn('roi_years', costs)
    
    def test_india_costs(self):
        """Test India pricing"""
        costs = self.calc.estimate('India', 'INR', 'Medium (0.5-5 acres)')
        
        self.assertIn('INR', costs['setup_min'])
        # India should be cheaper in USD terms
        self.assertIn('breakdown', costs)
    
    def test_currency_conversion(self):
        """Test all currencies work"""
        currencies = ['USD', 'INR', 'EUR', 'GBP', 'CAD', 'AUD']
        for curr in currencies:
            costs = self.calc.estimate('USA', curr, 'Small (< 0.5 acre)')
            self.assertIn(curr, costs['setup_min'])


class TestClimateEngine(unittest.TestCase):
    """Test climate recommendations"""
    
    def setUp(self):
        self.engine = ClimateEngine()
    
    def test_tropical_detection(self):
        """Test tropical climate detection"""
        data = self.engine.get_data('Kerala, India')
        self.assertEqual(data['zone'], 'Tropical')
        self.assertIn('Heavy rainfall erosion', data['challenges'])
    
    def test_dry_detection(self):
        """Test dry climate detection"""
        data = self.engine.get_data('Rajasthan, India')
        self.assertEqual(data['zone'], 'Dry')
        self.assertIn('Water scarcity', data['challenges'])
    
    def test_recommendations(self):
        """Test recommendations exist"""
        data = self.engine.get_data('London, UK')
        self.assertIn('solutions', data)
        self.assertGreater(len(data['solutions']), 0)


class TestWatermarkSystem(unittest.TestCase):
    """Test watermark functionality"""
    
    def setUp(self):
        # Create dummy image
        from PIL import Image
        import io
        
        img = Image.new('RGB', (800, 600), 'white')
        self.buffer = io.BytesIO()
        img.save(self.buffer, 'PNG')
        self.buffer.seek(0)
    
    def test_visible_watermark(self):
        """Test visible watermark mode"""
        result = WatermarkEngine.apply_visible_watermark(self.buffer)
        
        self.assertIsInstance(result, io.BytesIO)
        result.seek(0)
        img = Image.open(result)
        self.assertEqual(img.size, (800, 600))
    
    def test_protection_watermark(self):
        """Test protection watermark mode"""
        self.buffer.seek(0)
        result = WatermarkEngine.apply_protection_watermark(self.buffer)
        
        self.assertIsInstance(result, io.BytesIO)
        result.seek(0)
        img = Image.open(result)
        self.assertEqual(img.size, (800, 600))
    
    def test_watermark_text(self):
        """Test watermark text is correct"""
        self.assertEqual(WatermarkEngine.WATERMARK_TEXT, "chundalgardens.com")


class TestIntegration(unittest.TestCase):
    """Integration tests - full workflow"""
    
    def test_full_workflow(self):
        """Test complete user journey"""
        # 1. Interview
        answers = {
            'location': 'Pune, India',
            'dimensions': {'length': 300, 'width': 200},
            'house_position': 'South',
            'slope': 'Flat',
            'water_source': 'Borewell',
            'livestock': ['Goats', 'Chickens'],
            'budget': '$5,000 - $25,000'
        }
        
        # 2. Generate layout
        engine = LayoutEngine()
        layout = engine.generate(answers)
        self.assertIsNotNone(layout)
        
        # 3. Get climate data
        climate = ClimateEngine()
        climate_data = climate.get_data(answers['location'])
        self.assertIsNotNone(climate_data)
        
        # 4. Calculate costs
        calc = CostCalculator()
        costs = calc.estimate('India', 'INR', 'Medium (0.5-5 acres)')
        self.assertIsNotNone(costs)
        
        # 5. Design livestock housing
        designer = LivestockDesigner()
        goat_design = designer.create_housing('Goats', 10, climate_data['zone'], 'Standard')
        self.assertIsNotNone(goat_design)


def run_tests():
    """Run all tests"""
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromModule(sys.modules[__name__])
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
