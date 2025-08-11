#!/usr/bin/env python3
"""
Test script for the simple energy simulation without interactive input
"""

import numpy as np
import matplotlib.pyplot as plt
from simple_energy_reactor_optimization import SimpleEnergySimulator

def test_simulation():
    print("=" * 60)
    print("TESTING ENERGY DEMAND SIMULATION & REACTOR OPTIMIZATION")
    print("=" * 60)
    
    # Use fixed parameters for testing
    grid_size = 15
    num_reactors = 2
    reactor_radius = 3
    reactor_capacity = 12
    disaster_type = "earthquake"
    severity = 6
    
    print(f"Parameters:")
    print(f"  Grid size: {grid_size}x{grid_size}")
    print(f"  Reactors: {num_reactors} units")
    print(f"  Reactor radius: {reactor_radius} cells")
    print(f"  Reactor capacity: {reactor_capacity} MW each")
    print(f"  Disaster: {disaster_type} (severity {severity}/10)")
    
    # Initialize simulator
    sim = SimpleEnergySimulator(grid_size)
    
    # Step 1: Create the map and base demand
    sim.create_map()
    
    # Step 2: Simulate disaster
    disaster_demand, disaster_map = sim.simulate_disaster(disaster_type, severity)
    
    # Step 3: Optimize reactor placement
    reactor_locations, metrics = sim.optimize_reactors(
        sim.base_demand, disaster_demand, num_reactors, reactor_radius, reactor_capacity
    )
    
    if reactor_locations:
        # Step 4: Show results
        print("\n" + "="*50)
        print("FINAL RESULTS:")
        print("="*50)
        print(f"Total normal demand: {np.sum(sim.base_demand):.1f} MW")
        print(f"Total disaster demand: {np.sum(disaster_demand):.1f} MW")
        print(f"Total reactor capacity: {len(reactor_locations) * reactor_capacity} MW")
        print(f"Coverage efficiency: {(metrics['normal_coverage'] + metrics['disaster_coverage'])/2:.1f}%")
        
        # Step 5: Create visualizations (save instead of show)
        print("\nGenerating visualizations...")
        fig, axes = plt.subplots(2, 3, figsize=(18, 12))
        
        # 1. Zone map
        zone_colors = np.zeros((grid_size, grid_size, 3))
        for i in range(grid_size):
            for j in range(grid_size):
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
        axes[0, 0].set_title('Zone Map')
        axes[0, 0].set_xlabel('Grid X')
        axes[0, 0].set_ylabel('Grid Y')
        
        # 2. Normal demand
        im1 = axes[0, 1].imshow(sim.base_demand, cmap='YlOrRd', origin='lower')
        axes[0, 1].set_title('Normal Energy Demand')
        plt.colorbar(im1, ax=axes[0, 1], label='MW')
        
        # 3. Disaster impact
        im2 = axes[0, 2].imshow(disaster_map, cmap='RdYlBu_r', origin='lower', vmin=0, vmax=1)
        axes[0, 2].set_title('Disaster Impact')
        plt.colorbar(im2, ax=axes[0, 2], label='Demand Multiplier')
        
        # 4. Disaster demand
        im3 = axes[1, 0].imshow(disaster_demand, cmap='YlOrRd', origin='lower')
        axes[1, 0].set_title('Post-Disaster Demand')
        plt.colorbar(im3, ax=axes[1, 0], label='MW')
        
        # 5. Reactor placement on normal demand
        axes[1, 1].imshow(sim.base_demand, cmap='YlOrRd', origin='lower', alpha=0.7)
        for i, (x, y) in enumerate(reactor_locations):
            # Coverage circle
            circle = plt.Circle((y, x), reactor_radius, fill=False, color='lime', linewidth=2, alpha=0.8)
            axes[1, 1].add_patch(circle)
            
            # Reactor marker
            axes[1, 1].plot(y, x, '*', color='red', markersize=15, markeredgecolor='black', markeredgewidth=1)
            axes[1, 1].text(y, x, str(i+1), ha='center', va='center', color='white', fontweight='bold', fontsize=8)
        
        axes[1, 1].set_title('Reactor Placement (Normal)')
        
        # 6. Reactor placement on disaster demand
        axes[1, 2].imshow(disaster_demand, cmap='YlOrRd', origin='lower', alpha=0.7)
        for i, (x, y) in enumerate(reactor_locations):
            # Coverage circle
            circle = plt.Circle((y, x), reactor_radius, fill=False, color='lime', linewidth=2, alpha=0.8)
            axes[1, 2].add_patch(circle)
            
            # Reactor marker
            axes[1, 2].plot(y, x, '*', color='red', markersize=15, markeredgecolor='black', markeredgewidth=1)
            axes[1, 2].text(y, x, str(i+1), ha='center', va='center', color='white', fontweight='bold', fontsize=8)
        
        axes[1, 2].set_title('Reactor Placement (Disaster)')
        
        plt.tight_layout()
        plt.savefig('energy_simulation_results.png', dpi=150, bbox_inches='tight')
        print("Visualization saved as 'energy_simulation_results.png'")
        
        return True
    else:
        print("Optimization failed!")
        return False

if __name__ == "__main__":
    success = test_simulation()
    if success:
        print("\nSimulation completed successfully!")
    else:
        print("\nSimulation failed!")