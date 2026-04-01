"""
Professional 2D Map Visualizer
Generates publication-quality site plans
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, Circle, Rectangle, Polygon, Arc, Wedge
import numpy as np
from io import BytesIO
from typing import Dict, Any

class Visualizer2D:
    """Creates professional 2D homestead maps"""
    
    COLOR_SCHEMES = {
        'small': {
            'z0': '#FFF8E1', 'z1': '#FFECB3', 'z2': '#FFE082',
            'z3': '#FFD54F', 'z4': '#FFCA28',
            'house': '#8D6E63', 'water': '#4FC3F7', 'accent': '#FF8F00'
        },
        'medium': {
            'z0': '#E8F5E9', 'z1': '#C8E6C9', 'z2': '#A5D6A7',
            'z3': '#81C784', 'z4': '#66BB6A',
            'house': '#5D4037', 'water': '#29B6F6', 'accent': '#2E7D32'
        },
        'large': {
            'z0': '#E3F2FD', 'z1': '#BBDEFB', 'z2': '#90CAF9',
            'z3': '#64B5F6', 'z4': '#42A5F5',
            'house': '#37474F', 'water': '#0288D1', 'accent': '#1565C0'
        }
    }
    
    def create(self, layout: Dict[str, Any], answers: Dict[str, Any]) -> BytesIO:
        """Generate complete 2D visualization"""
        
        L = layout['dimensions']['L']
        W = layout['dimensions']['W']
        category = layout['category']
        colors = self.COLOR_SCHEMES[category]
        
        fig, ax = plt.subplots(1, 1, figsize=(14, 14))
        
        # Background
        ax.set_facecolor('#FAFAFA')
        
        # Plot boundary
        boundary = Rectangle((0, 0), L, W, linewidth=4, 
                            edgecolor='#1B5E20', facecolor='white', linestyle='-')
        ax.add_patch(boundary)
        
        # Draw zones
        self._draw_zones(ax, layout, colors)
        
        # Draw house
        self._draw_house(ax, layout, colors)
        
        # Draw features
        self._draw_features(ax, layout, colors)
        
        # Draw livestock areas
        self._draw_livestock_areas(ax, layout, colors)
        
        # Annotations
        self._add_dimensions(ax, L, W)
        self._add_compass(ax, L, W)
        self._add_title(ax, layout, L, W)
        self._add_legend(ax, colors, L, W)
        
        # Set limits
        margin = max(L, W) * 0.12
        ax.set_xlim(-margin, L + margin + L*0.25)
        ax.set_ylim(-margin, W + margin)
        ax.set_aspect('equal')
        ax.axis('off')
        
        plt.tight_layout()
        
        buf = BytesIO()
        plt.savefig(buf, format='png', dpi=200, bbox_inches='tight',
                   facecolor='white', edgecolor='none', pad_inches=0.2)
        buf.seek(0)
        plt.close(fig)
        
        return buf
    
    def _draw_zones(self, ax, layout, colors):
        """Draw permaculture zones"""
        zone_names = {
            'z0': 'Residential', 'z1': 'Kitchen Garden',
            'z2': 'Food Forest', 'z3': 'Pasture/Crops', 'z4': 'Buffer'
        }
        
        for zone_id, pos in layout['zone_positions'].items():
            rect = FancyBboxPatch(
                (pos['x'], pos['y']), pos['width'], pos['height'],
                boxstyle="round,pad=0.01,rounding_size=0.02",
                facecolor=colors[zone_id], edgecolor='#2E7D32',
                linewidth=2, alpha=0.8
            )
            ax.add_patch(rect)
            
            # Label
            cx = pos['x'] + pos['width']/2
            cy = pos['y'] + pos['height']/2
            area = pos['width'] * pos['height']
            
            ax.text(cx, cy, f"{zone_names[zone_id]}\n{int(area)} sq.ft.",
                   ha='center', va='center', fontsize=9, fontweight='bold',
                   color='#1B5E20',
                   bbox=dict(boxstyle='round,pad=0.3', facecolor='white',
                            edgecolor='none', alpha=0.8))
    
    def _draw_house(self, ax, layout, colors):
        """Draw detailed house"""
        house_pos = layout['house_position']
        L, W = layout['dimensions']['L'], layout['dimensions']['W']
        
        # Default house position
        if house_pos == 'North':
            hx, hy, hw, hh = L*0.3, W*0.82, L*0.4, W*0.15
        elif house_pos == 'South':
            hx, hy, hw, hh = L*0.3, W*0.03, L*0.4, W*0.15
        elif house_pos == 'East':
            hx, hy, hw, hh = L*0.75, W*0.35, L*0.2, W*0.3
        elif house_pos == 'West':
            hx, hy, hw, hh = L*0.05, W*0.35, L*0.2, W*0.3
        else:  # Center
            hx, hy, hw, hh = L*0.35, W*0.4, L*0.3, W*0.2
        
        # Main building
        house = FancyBboxPatch(
            (hx, hy), hw, hh,
            boxstyle="round,pad=0.01,rounding_size=0.02",
            facecolor=colors['house'], edgecolor='#3E2723', linewidth=3
        )
        ax.add_patch(house)
        
        # Roof triangle
        roof = Polygon([
            [hx-hw*0.05, hy+hh], [hx+hw/2, hy+hh*1.25], [hx+hw*1.05, hy+hh]
        ], facecolor='#BF360C', edgecolor='#3E2723', linewidth=2)
        ax.add_patch(roof)
        
        # Door
        door = Rectangle((hx+hw*0.4, hy), hw*0.2, hh*0.3,
                        facecolor='#5D4037', edgecolor='#3E2723')
        ax.add_patch(door)
        
        # Windows
        for wx in [hx+hw*0.15, hx+hw*0.65]:
            window = Rectangle((wx, hy+hh*0.5), hw*0.15, hh*0.2,
                             facecolor='#B3E5FC', edgecolor='#3E2723')
            ax.add_patch(window)
        
        ax.text(hx+hw/2, hy+hh*1.3, '🏠 HOUSE',
               ha='center', fontsize=10, fontweight='bold', color='#BF360C')
    
    def _draw_features(self, ax, layout, colors):
        """Draw water, solar, greenhouse, etc."""
        features = layout.get('features', {})
        L, W = layout['dimensions']['L'], layout['dimensions']['W']
        
        # Borewell
        if 'borewell' in features:
            f = features['borewell']
            well = Circle((f['x'], f['y']), f['radius'],
                         facecolor=colors['water'], edgecolor='#01579B', linewidth=3)
            ax.add_patch(well)
            # Ripple effect
            for r in [1.3, 1.6]:
                ripple = Circle((f['x'], f['y']), f['radius']*r,
                              facecolor='none', edgecolor=colors['water'],
                              linewidth=1, alpha=0.3, linestyle='--')
                ax.add_patch(ripple)
            ax.text(f['x'], f['y'], 'W', ha='center', va='center',
                   fontsize=8, fontweight='bold', color='white')
        
        # Pond
        if 'pond' in features:
            f = features['pond']
            # Irregular shape
            theta = np.linspace(0, 2*np.pi, 20)
            r = f['radius'] * (1 + 0.2 * np.sin(4*theta))
            x_pond = f['x'] + r * np.cos(theta)
            y_pond = f['y'] + r * np.sin(theta)
            pond = Polygon(list(zip(x_pond, y_pond)),
                          facecolor='#E1F5FE', edgecolor='#0288D1',
                          linewidth=2, alpha=0.9)
            ax.add_patch(pond)
            ax.text(f['x'], f['y'], '💧 POND', ha='center', va='center',
                   fontsize=8, color='#01579B')
        
        # Solar
        if 'solar' in features:
            f = features['solar']
            panel = Rectangle((f['x'], f['y']), f['width'], f['height'],
                            facecolor='#FFF3E0', edgecolor='#E65100', linewidth=2)
            ax.add_patch(panel)
            # Grid
            for i in range(1, 4):
                ax.plot([f['x']+f['width']*i/4, f['x']+f['width']*i/4],
                       [f['y'], f['y']+f['height']], 'orange', linewidth=1)
            ax.text(f['x']+f['width']/2, f['y']+f['height']/2, '☀️',
                   ha='center', va='center', fontsize=16)
        
        # Greenhouse
        if 'greenhouse' in features:
            f = features['greenhouse']
            gh = Rectangle((f['x'], f['y']), f['width'], f['height'],
                          facecolor='#F1F8E9', edgecolor='#33691E',
                          linewidth=2, linestyle='--')
            ax.add_patch(gh)
            # Arched roof
            arc = Arc((f['x']+f['width']/2, f['y']+f['height']),
                     f['width'], f['height']*0.4,
                     angle=0, theta1=0, theta2=180, color='#33691E', linewidth=2)
            ax.add_patch(arc)
            ax.text(f['x']+f['width']/2, f['y']+f['height']/2, '🌱 GH',
                   ha='center', va='center', fontsize=9, color='#33691E')
        
        # Compost
        if 'compost' in features:
            for i, comp in enumerate(features['compost']):
                c = Circle((comp['x'], comp['y']), comp['size'],
                          facecolor='#3E2723', edgecolor='black')
                ax.add_patch(c)
                ax.text(comp['x'], comp['y'], f'C{i+1}',
                       ha='center', va='center', fontsize=7, color='white')
    
    def _draw_livestock_areas(self, ax, layout, colors):
        """Draw animal housing"""
        features = layout.get('features', {})
        L, W = layout['dimensions']['L'], layout['dimensions']['W']
        
        # Goat shed
        if 'goat_shed' in features:
            f = features['goat_shed']
            shed = Rectangle((f['x'], f['y']), f['width'], f['height'],
                           facecolor='#D7CCC8', edgecolor='#5D4037', linewidth=2)
            ax.add_patch(shed)
            ax.text(f['x']+f['width']/2, f['y']+f['height']/2, '🐐 GOATS',
                   ha='center', va='center', fontsize=9, fontweight='bold')
        
        # Chicken coop
        if 'chicken_coop' in features:
            f = features['chicken_coop']
            coop = Rectangle((f['x'], f['y']), f['width'], f['height'],
                           facecolor='#FFF8E1', edgecolor='#F57F17', linewidth=2)
            ax.add_patch(coop)
            ax.text(f['x']+f['width']/2, f['y']+f['height']/2, '🐔',
                   ha='center', va='center', fontsize=14)
        
        # Piggery
        if 'piggery' in features:
            f = features['piggery']
            pig = Rectangle((f['x'], f['y']), f['width'], f['height'],
                          facecolor='#FFCCBC', edgecolor='#BF360C', linewidth=2)
            ax.add_patch(pig)
            ax.text(f['x']+f['width']/2, f['y']+f['height']/2, '🐷 PIGS',
                   ha='center', va='center', fontsize=9, fontweight='bold')
    
    def _add_dimensions(self, ax, L, W):
        """Add dimension lines"""
        # Horizontal
        ax.annotate('', xy=(0, -W*0.05), xytext=(L, -W*0.05),
                   arrowprops=dict(arrowstyle='<->', color='#424242', lw=2))
        ax.text(L/2, -W*0.08, f'{int(L)} ft', ha='center', fontsize=11,
               fontweight='bold', color='#424242')
        
        # Vertical
        ax.annotate('', xy=(-L*0.05, 0), xytext=(-L*0.05, W),
                   arrowprops=dict(arrowstyle='<->', color='#424242', lw=2))
        ax.text(-L*0.08, W/2, f'{int(W)} ft', ha='center', fontsize=11,
               fontweight='bold', color='#424242', rotation=90)
    
    def _add_compass(self, ax, L, W):
        """Add compass rose"""
        cx, cy = L * 0.92, W * 0.08
        
        # Circle
        compass = Circle((cx, cy), L*0.035, facecolor='white',
                        edgecolor='#424242', linewidth=2)
        ax.add_patch(compass)
        
        # North arrow
        ax.annotate('N', xy=(cx, cy + L*0.04), fontsize=14,
                   ha='center', fontweight='bold', color='#D32F2F')
        ax.annotate('', xy=(cx, cy + L*0.03), xytext=(cx, cy - L*0.02),
                   arrowprops=dict(arrowstyle='->', color='#D32F2F', lw=3))
    
    def _add_title(self, ax, layout, L, W):
        """Add title block"""
        title = f"{layout.get('acres', 0):.2f} Acre Homestead\n"
        title += f"{int(layout['total_sqft']):,} sq.ft. | {layout['category'].title()} Scale"
        
        ax.text(L/2, W*1.05, title, ha='center', va='bottom',
               fontsize=14, fontweight='bold', color='#1B5E20',
               bbox=dict(boxstyle='round,pad=0.5', facecolor='#E8F5E9',
                        edgecolor='#2E7D32', linewidth=2))
    
    def _add_legend(self, ax, colors, L, W):
        """Add legend"""
        legend_elements = [
            patches.Patch(facecolor=colors['z0'], edgecolor='black', label='Zone 0: House'),
            patches.Patch(facecolor=colors['z1'], edgecolor='black', label='Zone 1: Kitchen'),
            patches.Patch(facecolor=colors['z2'], edgecolor='black', label='Zone 2: Forest'),
            patches.Patch(facecolor=colors['z3'], edgecolor='black', label='Zone 3: Crops'),
            patches.Patch(facecolor=colors['z4'], edgecolor='black', label='Zone 4: Buffer'),
            patches.Patch(facecolor=colors['water'], edgecolor='black', label='Water'),
        ]
        ax.legend(handles=legend_elements, loc='upper left',
                 bbox_to_anchor=(1.02, 1), fontsize=9, frameon=True)
