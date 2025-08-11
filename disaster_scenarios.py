import numpy as np
import random
import math

class DisasterScenarios:
    def __init__(self):
        self.disaster_types = {
            'earthquake': {
                'description': 'Seismic activity affecting infrastructure',
                'impact_pattern': 'radial',
                'base_multiplier': 0.3,  # Reduces demand due to damage
                'max_radius': 8
            },
            'storm': {
                'description': 'Severe weather affecting power lines',
                'impact_pattern': 'regional',
                'base_multiplier': 0.2,  # Severe demand reduction
                'max_radius': 12
            },
            'power_outage': {
                'description': 'Grid failure causing blackouts',
                'impact_pattern': 'sector',
                'base_multiplier': 0.1,  # Almost complete demand loss
                'max_radius': 6
            },
            'flood': {
                'description': 'Flooding affecting low-lying areas',
                'impact_pattern': 'linear',
                'base_multiplier': 0.4,  # Moderate demand reduction
                'max_radius': 10
            }
        }
    
    def simulate_disaster(self, disaster_type, severity, zone_map):
        """
        Simulate disaster impact on the grid
        
        Args:
            disaster_type: Type of disaster ('earthquake', 'storm', etc.)
            severity: Severity level (1-10)
            zone_map: Grid zone map
            
        Returns:
            impact_map: Multiplier map for demand modification
        """
        rows, cols = zone_map.shape
        impact_map = np.ones((rows, cols))
        
        if disaster_type not in self.disaster_types:
            return impact_map
        
        disaster_config = self.disaster_types[disaster_type]
        impact_pattern = disaster_config['impact_pattern']
        base_multiplier = disaster_config['base_multiplier']
        max_radius = disaster_config['max_radius']
        
        # Severity affects the intensity and spread
        severity_factor = severity / 10.0
        effective_multiplier = base_multiplier + (1 - base_multiplier) * (1 - severity_factor)
        effective_radius = max_radius * severity_factor
        
        if impact_pattern == 'radial':
            # Earthquake-like radial impact
            center_x = random.randint(rows//4, 3*rows//4)
            center_y = random.randint(cols//4, 3*cols//4)
            impact_map = self._apply_radial_impact(
                impact_map, center_x, center_y, effective_radius, effective_multiplier
            )
        
        elif impact_pattern == 'regional':
            # Storm-like regional impact
            num_regions = random.randint(1, 3)
            for _ in range(num_regions):
                center_x = random.randint(0, rows-1)
                center_y = random.randint(0, cols-1)
                region_radius = effective_radius * random.uniform(0.5, 1.0)
                impact_map = self._apply_radial_impact(
                    impact_map, center_x, center_y, region_radius, effective_multiplier
                )
        
        elif impact_pattern == 'sector':
            # Power outage-like sector impact
            # Randomly select a rectangular region
            start_x = random.randint(0, rows//2)
            start_y = random.randint(0, cols//2)
            end_x = min(rows, start_x + int(effective_radius))
            end_y = min(cols, start_y + int(effective_radius))
            
            impact_map[start_x:end_x, start_y:end_y] *= effective_multiplier
        
        elif impact_pattern == 'linear':
            # Flood-like linear impact
            # Create a flood path
            if random.random() < 0.5:  # Horizontal flood
                flood_row = random.randint(0, rows-1)
                flood_width = int(effective_radius / 2)
                start_row = max(0, flood_row - flood_width)
                end_row = min(rows, flood_row + flood_width)
                impact_map[start_row:end_row, :] *= effective_multiplier
            else:  # Vertical flood
                flood_col = random.randint(0, cols-1)
                flood_width = int(effective_radius / 2)
                start_col = max(0, flood_col - flood_width)
                end_col = min(cols, flood_col + flood_width)
                impact_map[:, start_col:end_col] *= effective_multiplier
        
        # Add some random noise to make it more realistic
        noise = np.random.normal(1.0, 0.1, (rows, cols))
        noise = np.clip(noise, 0.5, 1.5)
        impact_map *= noise
        
        # Ensure impact doesn't make demand negative or unrealistically high
        impact_map = np.clip(impact_map, 0.05, 2.0)
        
        return impact_map
    
    def _apply_radial_impact(self, impact_map, center_x, center_y, radius, multiplier):
        """Apply radial impact pattern"""
        rows, cols = impact_map.shape
        
        for i in range(rows):
            for j in range(cols):
                distance = math.sqrt((i - center_x)**2 + (j - center_y)**2)
                if distance <= radius:
                    # Impact decreases with distance from center
                    impact_strength = 1 - (distance / radius) * 0.7
                    current_multiplier = multiplier + (1 - multiplier) * (1 - impact_strength)
                    impact_map[i, j] *= current_multiplier
        
        return impact_map
    
    def get_disaster_description(self, disaster_type, severity):
        """Get human-readable description of disaster"""
        if disaster_type not in self.disaster_types:
            return "Unknown disaster type"
        
        config = self.disaster_types[disaster_type]
        severity_desc = {
            1: "Minor", 2: "Minor", 3: "Moderate", 4: "Moderate",
            5: "Moderate", 6: "Severe", 7: "Severe", 8: "Major",
            9: "Major", 10: "Catastrophic"
        }
        
        severity_level = severity_desc.get(severity, "Unknown")
        return f"{severity_level} {disaster_type.title()}: {config['description']}"
    
    def simulate_recovery(self, impact_map, recovery_hours):
        """Simulate recovery over time"""
        # Recovery is gradual - exponential recovery towards normal
        recovery_rate = 0.1  # 10% recovery per hour
        recovery_factor = 1 - math.exp(-recovery_rate * recovery_hours)
        
        # Move impact multipliers towards 1.0 (normal operation)
        recovered_map = impact_map + (1.0 - impact_map) * recovery_factor
        return np.clip(recovered_map, 0.1, 1.0)
