#!/usr/bin/env python3
"""
Custom scenario example showing how to create specific simulation conditions
"""

from simple_energy_reactor_optimization import SimpleEnergySimulator
import numpy as np
import matplotlib.pyplot as plt

def create_custom_scenario():
    """Create a custom scenario with specific zone layout and disaster"""
    print("Custom Scenario: City with Industrial District")
    print("=" * 50)
    
    # Create simulator
    sim = SimpleEnergySimulator(grid_size=16)
    
    # Create custom zone map instead of random generation
    print("Creating custom city layout...")
    sim.zone_map = np.zeros((16, 16), dtype=int)
    
    # Create industrial district (bottom-left)
    sim.zone_map[0:6, 0:6] = 3  # Industrial
    
    # Create commercial downtown (center)
    sim.zone_map[6:10, 6:10] = 2  # Commercial
    
    # Create residential suburbs (scattered)
    residential_coords = [
        (2, 8), (3, 8), (4, 8), (2, 9), (3, 9),  # Residential cluster 1
        (8, 2), (9, 2), (10, 2), (8, 3), (9, 3), # Residential cluster 2
        (12, 12), (13, 12), (14, 12), (12, 13), (13, 13), (14, 13)  # Residential cluster 3
    ]
    
    for x, y in residential_coords:
        if 0 <= x < 16 and 0 <= y < 16:
            sim.zone_map[x, y] = 1
    
    # Calculate demand for custom layout
    sim.base_demand = np.zeros((16, 16))
    for i in range(16):
        for j in range(16):
            zone_type = sim.zone_map[i, j]
            base_demand = sim.zone_types[zone_type]['demand']
            # Add some variation
            variation = np.random.uniform(0.8, 1.2)
            sim.base_demand[i, j] = base_demand * variation
    
    print("Custom city created:")
    print(f"  Industrial district: {np.sum(sim.zone_map == 3)} cells")
    print(f"  Commercial downtown: {np.sum(sim.zone_map == 2)} cells") 
    print(f"  Residential areas: {np.sum(sim.zone_map == 1)} cells")
    print(f"  Total demand: {np.sum(sim.base_demand):.1f} MW")
    
    # Simulate targeted power outage affecting industrial district
    print("\nSimulating power outage in industrial district...")
    disaster_demand, disaster_map = sim.simulate_disaster("power_outage", severity=8)
    
    # Try different optimization strategies
    strategies = [
        {"reactors": 2, "radius": 4, "capacity": 20},
        {"reactors": 3, "radius": 3, "capacity": 15},
        {"reactors": 4, "radius": 2, "capacity": 12}
    ]
    
    results = []
    
    for i, strategy in enumerate(strategies):
        print(f"\nTesting strategy {i+1}: {strategy['reactors']} reactors, radius {strategy['radius']}")
        
        locations, metrics = sim.optimize_reactors(
            sim.base_demand, disaster_demand,
            strategy["reactors"], strategy["radius"], strategy["capacity"]
        )
        
        if locations:
            efficiency = (metrics['normal_coverage'] + metrics['disaster_coverage']) / 2
            total_capacity = len(locations) * strategy["capacity"]
            
            results.append({
                'strategy': i+1,
                'locations': locations,
                'metrics': metrics,
                'efficiency': efficiency,
                'total_capacity': total_capacity,
                'config': strategy
            })
            
            print(f"  Efficiency: {efficiency:.1f}%")
            print(f"  Total capacity: {total_capacity} MW")
    
    # Find best strategy
    if results:
        best = max(results, key=lambda x: x['efficiency'])
        print(f"\nBest strategy: Strategy {best['strategy']} with {best['efficiency']:.1f}% efficiency")
        
        # Visualize best strategy
        fig, axes = plt.subplots(2, 2, figsize=(12, 10))
        
        # Zone map
        zone_colors = np.zeros((16, 16, 3))
        for i in range(16):
            for j in range(16):
                zone_type = sim.zone_map[i, j]
                if zone_type == 0:  # Empty
                    zone_colors[i, j] = [0.9, 0.9, 0.9]
                elif zone_type == 1:  # Residential
                    zone_colors[i, j] = [0.5, 1.0, 0.5]
                elif zone_type == 2:  # Commercial
                    zone_colors[i, j] = [1.0, 0.7, 0.7]
                elif zone_type == 3:  # Industrial
                    zone_colors[i, j] = [0.7, 0.7, 1.0]
        
        axes[0, 0].imshow(zone_colors, origin='lower')
        axes[0, 0].set_title('Custom City Layout')
        
        # Normal demand
        im1 = axes[0, 1].imshow(sim.base_demand, cmap='YlOrRd', origin='lower')
        axes[0, 1].set_title('Normal Demand')
        plt.colorbar(im1, ax=axes[0, 1])
        
        # Disaster impact
        im2 = axes[1, 0].imshow(disaster_map, cmap='RdYlBu_r', origin='lower', vmin=0, vmax=1)
        axes[1, 0].set_title('Power Outage Impact')
        plt.colorbar(im2, ax=axes[1, 0])
        
        # Best reactor placement
        axes[1, 1].imshow(sim.base_demand, cmap='YlOrRd', origin='lower', alpha=0.7)
        for i, (x, y) in enumerate(best['locations']):
            circle = plt.Circle((y, x), best['config']['radius'], fill=False, color='lime', linewidth=2)
            axes[1, 1].add_patch(circle)
            axes[1, 1].plot(y, x, '*', color='red', markersize=15)
            axes[1, 1].text(y, x, str(i+1), ha='center', va='center', color='white', fontweight='bold')
        
        axes[1, 1].set_title(f'Best Strategy: {best["strategy"]}')
        
        plt.tight_layout()
        plt.savefig('custom_scenario_result.png', dpi=150, bbox_inches='tight')
        print("Visualization saved as 'custom_scenario_result.png'")
    
    print("\nCustom scenario completed!")

if __name__ == "__main__":
    create_custom_scenario()