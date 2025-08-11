import numpy as np
import random
from datetime import datetime, timedelta

class EnergySimulation:
    def __init__(self, grid_rows=20, grid_cols=20):
        self.grid_rows = grid_rows
        self.grid_cols = grid_cols
        self.zone_map = None
        
        # Base demand profiles (MW per unit area)
        self.base_demands = {
            'residential': 2.0,
            'commercial': 5.0,
            'industrial': 8.0,
            'empty': 0.1
        }
        
        # Time-of-day multipliers
        self.time_multipliers = {
            0: 0.6, 1: 0.5, 2: 0.4, 3: 0.4, 4: 0.4, 5: 0.5,
            6: 0.7, 7: 0.9, 8: 1.0, 9: 1.1, 10: 1.2, 11: 1.3,
            12: 1.4, 13: 1.3, 14: 1.2, 15: 1.1, 16: 1.0, 17: 1.1,
            18: 1.3, 19: 1.4, 20: 1.3, 21: 1.1, 22: 0.9, 23: 0.7
        }
        
        # Seasonal multipliers
        self.seasonal_multipliers = {
            'spring': 1.0,
            'summer': 1.3,  # Higher due to AC usage
            'fall': 1.1,
            'winter': 1.2   # Higher due to heating
        }
        
        # Zone-specific time patterns
        self.zone_time_patterns = {
            'residential': {
                'peak_hours': [7, 8, 18, 19, 20],
                'low_hours': [2, 3, 4, 5],
                'multiplier': 1.0
            },
            'commercial': {
                'peak_hours': [9, 10, 11, 12, 13, 14, 15, 16],
                'low_hours': [22, 23, 0, 1, 2, 3, 4, 5, 6],
                'multiplier': 1.2
            },
            'industrial': {
                'peak_hours': [8, 9, 10, 11, 12, 13, 14, 15, 16, 17],
                'low_hours': [0, 1, 2, 3, 4, 5, 6],
                'multiplier': 0.8  # More consistent demand
            }
        }
    
    def generate_zones(self, residential_pct=0.6, commercial_pct=0.25, industrial_pct=0.15):
        """Generate a realistic zone map with clustered zones"""
        self.zone_map = np.full((self.grid_rows, self.grid_cols), 'empty', dtype=object)
        
        # Create zone clusters
        zones = ['residential', 'commercial', 'industrial']
        zone_probs = [residential_pct, commercial_pct, industrial_pct]
        
        # Generate cluster centers
        num_clusters = random.randint(3, 8)
        cluster_centers = []
        
        for _ in range(num_clusters):
            center_x = random.randint(2, self.grid_rows - 3)
            center_y = random.randint(2, self.grid_cols - 3)
            zone_type = np.random.choice(zones, p=zone_probs)
            cluster_size = random.randint(2, 6)
            cluster_centers.append((center_x, center_y, zone_type, cluster_size))
        
        # Fill clusters
        for center_x, center_y, zone_type, cluster_size in cluster_centers:
            for dx in range(-cluster_size//2, cluster_size//2 + 1):
                for dy in range(-cluster_size//2, cluster_size//2 + 1):
                    x, y = center_x + dx, center_y + dy
                    if (0 <= x < self.grid_rows and 0 <= y < self.grid_cols):
                        # Probability decreases with distance from center
                        distance = abs(dx) + abs(dy)
                        prob = max(0.1, 1.0 - distance * 0.2)
                        if random.random() < prob:
                            self.zone_map[x, y] = zone_type
        
        # Add some random scattered zones
        for _ in range(self.grid_rows * self.grid_cols // 10):
            x = random.randint(0, self.grid_rows - 1)
            y = random.randint(0, self.grid_cols - 1)
            if self.zone_map[x, y] == 'empty':
                zone_type = np.random.choice(zones, p=zone_probs)
                self.zone_map[x, y] = zone_type
    
    def calculate_demand(self, season='spring', hour=12):
        """Calculate energy demand for given season and time"""
        if self.zone_map is None:
            self.generate_zones()
        
        demand_map = np.zeros((self.grid_rows, self.grid_cols))
        
        season_mult = self.seasonal_multipliers.get(season.lower(), 1.0)
        time_mult = self.time_multipliers.get(hour, 1.0)
        
        for i in range(self.grid_rows):
            for j in range(self.grid_cols):
                zone_type = self.zone_map[i, j]
                base_demand = self.base_demands.get(zone_type, 0.1)
                
                # Apply zone-specific time patterns
                zone_mult = 1.0
                if zone_type in self.zone_time_patterns:
                    pattern = self.zone_time_patterns[zone_type]
                    if hour in pattern['peak_hours']:
                        zone_mult = pattern['multiplier'] * 1.2
                    elif hour in pattern['low_hours']:
                        zone_mult = pattern['multiplier'] * 0.6
                    else:
                        zone_mult = pattern['multiplier']
                
                # Add random variation (±10%)
                random_mult = random.uniform(0.9, 1.1)
                
                demand_map[i, j] = base_demand * season_mult * time_mult * zone_mult * random_mult
        
        return demand_map
    
    def apply_disaster_impact(self, base_demand, disaster_impact):
        """Apply disaster impact to base demand"""
        return base_demand * disaster_impact
    
    def get_zone_statistics(self, demand_map):
        """Get statistics for each zone type"""
        stats = {}
        
        for zone_type in ['residential', 'commercial', 'industrial', 'empty']:
            mask = self.zone_map == zone_type
            zone_demands = demand_map[mask]
            
            if len(zone_demands) > 0:
                stats[zone_type] = {
                    'total': np.sum(zone_demands),
                    'avg': np.mean(zone_demands),
                    'max': np.max(zone_demands),
                    'count': len(zone_demands)
                }
            else:
                stats[zone_type] = {
                    'total': 0, 'avg': 0, 'max': 0, 'count': 0
                }
        
        return stats
    
    def get_demand_coordinates(self):
        """Get coordinates of all demand points for optimization"""
        coords = []
        for i in range(self.grid_rows):
            for j in range(self.grid_cols):
                if self.zone_map[i, j] != 'empty':
                    coords.append((i, j))
        return coords
