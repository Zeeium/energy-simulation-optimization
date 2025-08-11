#!/usr/bin/env python3
"""
Basic example showing how to use the energy simulation system
This example creates a small simulation and runs optimization
"""

from simple_energy_reactor_optimization import SimpleEnergySimulator
import matplotlib.pyplot as plt

def run_basic_example():
    """Run a basic simulation example with predefined parameters"""
    print("Running Basic Energy Simulation Example")
    print("=" * 50)
    
    # Create simulator with a small grid for quick testing
    sim = SimpleEnergySimulator(grid_size=12)
    
    # Step 1: Create the map
    print("1. Creating energy demand map...")
    sim.create_map()
    
    # Step 2: Simulate a moderate earthquake
    print("\n2. Simulating earthquake disaster...")
    disaster_demand, disaster_map = sim.simulate_disaster("earthquake", severity=5)
    
    # Step 3: Optimize reactor placement
    print("\n3. Optimizing reactor placement...")
    reactor_locations, metrics = sim.optimize_reactors(
        normal_demand=sim.base_demand,
        disaster_demand=disaster_demand,
        num_reactors=2,
        reactor_radius=3,
        reactor_capacity=10
    )
    
    # Step 4: Show results
    print("\n4. Results Summary:")
    print("-" * 30)
    if reactor_locations:
        print(f"   Reactors placed: {len(reactor_locations)}")
        print(f"   Normal coverage: {metrics['normal_coverage']:.1f}%")
        print(f"   Disaster coverage: {metrics['disaster_coverage']:.1f}%")
        print(f"   Reactor locations: {reactor_locations}")
        
        # Create a simple visualization
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
        
        # Plot normal demand with reactors
        im1 = ax1.imshow(sim.base_demand, cmap='YlOrRd', origin='lower')
        for i, (x, y) in enumerate(reactor_locations):
            circle = plt.Circle((y, x), 3, fill=False, color='lime', linewidth=2)
            ax1.add_patch(circle)
            ax1.plot(y, x, '*', color='red', markersize=12)
            ax1.text(y, x, str(i+1), ha='center', va='center', color='white', fontweight='bold')
        
        ax1.set_title('Normal Demand + Reactors')
        plt.colorbar(im1, ax=ax1, label='MW')
        
        # Plot disaster demand with reactors
        im2 = ax2.imshow(disaster_demand, cmap='YlOrRd', origin='lower')
        for i, (x, y) in enumerate(reactor_locations):
            circle = plt.Circle((y, x), 3, fill=False, color='lime', linewidth=2)
            ax2.add_patch(circle)
            ax2.plot(y, x, '*', color='red', markersize=12)
            ax2.text(y, x, str(i+1), ha='center', va='center', color='white', fontweight='bold')
        
        ax2.set_title('Disaster Demand + Reactors')
        plt.colorbar(im2, ax=ax2, label='MW')
        
        plt.tight_layout()
        plt.savefig('basic_example_result.png', dpi=150, bbox_inches='tight')
        print("   Visualization saved as 'basic_example_result.png'")
        
    else:
        print("   Optimization failed!")
    
    print("\nBasic example completed!")

if __name__ == "__main__":
    run_basic_example()