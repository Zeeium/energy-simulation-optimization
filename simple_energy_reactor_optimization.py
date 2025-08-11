#!/usr/bin/env python3
"""
Simple Energy Demand Simulation with Microreactor Optimization
Creates a map, simulates energy demand, applies disaster effects, and finds optimal reactor placement
"""

import random
import numpy as np
import matplotlib.pyplot as plt
import gurobipy as gp
from gurobipy import GRB
import math

class SimpleEnergySimulator:
    def __init__(self, grid_size=20):
        self.grid_size = grid_size
        self.zone_map = None
        self.base_demand = None
        
        # Zone types and their energy demands (MW per cell)
        self.zone_types = {
            0: {'name': 'Empty', 'demand': 0.5, 'color': 'lightgray'},
            1: {'name': 'Residential', 'demand': 3.0, 'color': 'lightgreen'},
            2: {'name': 'Commercial', 'demand': 6.0, 'color': 'lightcoral'},
            3: {'name': 'Industrial', 'demand': 10.0, 'color': 'lightblue'}
        }
    
    def create_map(self):
        """Create a random map with different zones"""
        print("Creating energy demand map...")
        
        # Initialize with empty zones
        self.zone_map = np.zeros((self.grid_size, self.grid_size), dtype=int)
        
        # Create clusters of different zone types
        for zone_type in [1, 2, 3]:  # Residential, Commercial, Industrial
            num_clusters = random.randint(2, 4)
            
            for _ in range(num_clusters):
                # Pick random center for cluster
                center_x = random.randint(2, self.grid_size - 3)
                center_y = random.randint(2, self.grid_size - 3)
                cluster_size = random.randint(2, 5)
                
                # Fill cluster area
                for dx in range(-cluster_size//2, cluster_size//2 + 1):
                    for dy in range(-cluster_size//2, cluster_size//2 + 1):
                        x, y = center_x + dx, center_y + dy
                        if (0 <= x < self.grid_size and 0 <= y < self.grid_size):
                            if random.random() < 0.7:  # 70% chance to place zone
                                self.zone_map[x, y] = zone_type
        
        # Calculate base demand for each cell
        self.base_demand = np.zeros((self.grid_size, self.grid_size))
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                zone_type = self.zone_map[i, j]
                base_demand = self.zone_types[zone_type]['demand']
                # Add some random variation (±20%)
                variation = random.uniform(0.8, 1.2)
                self.base_demand[i, j] = base_demand * variation
        
        print(f"Map created with {self.grid_size}x{self.grid_size} grid")
        self.print_zone_statistics()
    
    def print_zone_statistics(self):
        """Print statistics about the zones"""
        for zone_type, info in self.zone_types.items():
            count = np.sum(self.zone_map == zone_type)
            total_demand = np.sum(self.base_demand[self.zone_map == zone_type])
            print(f"  {info['name']}: {count} cells, {total_demand:.1f} MW total")
    
    def simulate_disaster(self, disaster_type="earthquake", severity=5):
        """Simulate disaster impact on energy demand"""
        print(f"\nSimulating {disaster_type} disaster (severity {severity}/10)...")
        
        disaster_map = np.ones((self.grid_size, self.grid_size))
        
        if disaster_type == "earthquake":
            # Radial impact from random epicenter
            epicenter_x = random.randint(self.grid_size//4, 3*self.grid_size//4)
            epicenter_y = random.randint(self.grid_size//4, 3*self.grid_size//4)
            max_radius = severity * 1.5
            
            for i in range(self.grid_size):
                for j in range(self.grid_size):
                    distance = math.sqrt((i - epicenter_x)**2 + (j - epicenter_y)**2)
                    if distance <= max_radius:
                        # Demand reduction based on distance from epicenter
                        impact = 0.2 + 0.6 * (distance / max_radius)  # 20-80% of original
                        disaster_map[i, j] = impact
            
            print(f"  Earthquake epicenter at ({epicenter_x}, {epicenter_y})")
        
        elif disaster_type == "flood":
            # Linear flooding pattern
            if random.random() < 0.5:  # Horizontal flood
                flood_row = random.randint(0, self.grid_size - 1)
                flood_width = severity
                start_row = max(0, flood_row - flood_width//2)
                end_row = min(self.grid_size, flood_row + flood_width//2)
                disaster_map[start_row:end_row, :] *= 0.3  # 30% of original demand
                print(f"  Horizontal flood affecting rows {start_row}-{end_row}")
            else:  # Vertical flood
                flood_col = random.randint(0, self.grid_size - 1)
                flood_width = severity
                start_col = max(0, flood_col - flood_width//2)
                end_col = min(self.grid_size, flood_col + flood_width//2)
                disaster_map[:, start_col:end_col] *= 0.3
                print(f"  Vertical flood affecting columns {start_col}-{end_col}")
        
        elif disaster_type == "power_outage":
            # Sector-based outage
            sector_size = severity * 2
            start_x = random.randint(0, self.grid_size - sector_size)
            start_y = random.randint(0, self.grid_size - sector_size)
            end_x = min(self.grid_size, start_x + sector_size)
            end_y = min(self.grid_size, start_y + sector_size)
            disaster_map[start_x:end_x, start_y:end_y] *= 0.1  # 10% of original (emergency power only)
            print(f"  Power outage in sector ({start_x}:{end_x}, {start_y}:{end_y})")
        
        # Apply disaster impact to demand
        affected_demand = self.base_demand * disaster_map
        
        original_total = np.sum(self.base_demand)
        affected_total = np.sum(affected_demand)
        impact_percent = ((affected_total - original_total) / original_total) * 100
        print(f"  Total demand changed by {impact_percent:+.1f}%")
        
        return affected_demand, disaster_map
    
    def optimize_reactors(self, normal_demand, disaster_demand, num_reactors=3, reactor_radius=4, reactor_capacity=15):
        """Find optimal placement for microreactors using Gurobi"""
        print(f"\nOptimizing placement of {num_reactors} reactors...")
        print(f"  Reactor specs: {reactor_capacity} MW capacity, {reactor_radius} cell radius")
        
        try:
            # Create optimization model
            model = gp.Model("ReactorPlacement")
            model.setParam('OutputFlag', 0)  # Suppress Gurobi output
            model.setParam('TimeLimit', 30)  # 30 second time limit
            
            # Decision variables
            reactor = model.addVars(self.grid_size, self.grid_size, vtype=GRB.BINARY, name="reactor")
            
            # Coverage variables for each scenario (normal and disaster)
            coverage_normal = model.addVars(self.grid_size, self.grid_size, vtype=GRB.BINARY, name="coverage_normal")
            coverage_disaster = model.addVars(self.grid_size, self.grid_size, vtype=GRB.BINARY, name="coverage_disaster")
            
            # Constraint: Maximum number of reactors
            model.addConstr(reactor.sum() <= num_reactors, "max_reactors")
            
            # Coverage constraints
            for i in range(self.grid_size):
                for j in range(self.grid_size):
                    if normal_demand[i, j] > 1.0:  # Only consider cells with significant demand
                        # Find all reactor positions that can cover this cell
                        covering_reactors = []
                        for rx in range(self.grid_size):
                            for ry in range(self.grid_size):
                                distance = math.sqrt((i - rx)**2 + (j - ry)**2)
                                if distance <= reactor_radius:
                                    covering_reactors.append((rx, ry))
                        
                        if covering_reactors:
                            # Normal scenario coverage
                            model.addConstr(
                                gp.quicksum(reactor[rx, ry] for rx, ry in covering_reactors) >= coverage_normal[i, j],
                                f"coverage_normal_{i}_{j}"
                            )
                            
                            # Disaster scenario coverage
                            model.addConstr(
                                gp.quicksum(reactor[rx, ry] for rx, ry in covering_reactors) >= coverage_disaster[i, j],
                                f"coverage_disaster_{i}_{j}"
                            )
            
            # Objective: Minimize uncovered demand (weighted by scenario importance)
            uncovered_normal = gp.quicksum(
                normal_demand[i, j] * (1 - coverage_normal[i, j])
                for i in range(self.grid_size) for j in range(self.grid_size)
                if normal_demand[i, j] > 1.0
            )
            
            uncovered_disaster = gp.quicksum(
                disaster_demand[i, j] * (1 - coverage_disaster[i, j])
                for i in range(self.grid_size) for j in range(self.grid_size)
                if disaster_demand[i, j] > 1.0
            )
            
            # Weight disaster scenario more heavily (2x)
            model.setObjective(uncovered_normal + 2.0 * uncovered_disaster, GRB.MINIMIZE)
            
            # Solve
            model.optimize()
            
            if model.status == GRB.OPTIMAL:
                # Extract reactor locations
                reactor_locations = []
                for i in range(self.grid_size):
                    for j in range(self.grid_size):
                        if reactor[i, j].X > 0.5:
                            reactor_locations.append((i, j))
                
                # Calculate performance metrics
                metrics = self.calculate_metrics(reactor_locations, normal_demand, disaster_demand, reactor_radius)
                
                print(f"  Optimization successful! Found {len(reactor_locations)} reactor locations:")
                for i, (x, y) in enumerate(reactor_locations):
                    print(f"    Reactor {i+1}: ({x}, {y})")
                
                print(f"  Performance:")
                print(f"    Normal scenario coverage: {metrics['normal_coverage']:.1f}%")
                print(f"    Disaster scenario coverage: {metrics['disaster_coverage']:.1f}%")
                print(f"    Total capacity: {len(reactor_locations) * reactor_capacity} MW")
                
                return reactor_locations, metrics
            
            else:
                print(f"  Optimization failed: {model.status}")
                return [], {}
        
        except Exception as e:
            print(f"  Error during optimization: {e}")
            return [], {}
    
    def calculate_metrics(self, reactor_locations, normal_demand, disaster_demand, reactor_radius):
        """Calculate coverage and performance metrics"""
        def calculate_coverage(demand_map):
            total_demand = 0
            covered_demand = 0
            
            for i in range(self.grid_size):
                for j in range(self.grid_size):
                    demand = demand_map[i, j]
                    if demand > 1.0:
                        total_demand += demand
                        
                        # Check if covered by any reactor
                        covered = False
                        for rx, ry in reactor_locations:
                            distance = math.sqrt((i - rx)**2 + (j - ry)**2)
                            if distance <= reactor_radius:
                                covered = True
                                break
                        
                        if covered:
                            covered_demand += demand
            
            return (covered_demand / total_demand * 100) if total_demand > 0 else 0
        
        return {
            'normal_coverage': calculate_coverage(normal_demand),
            'disaster_coverage': calculate_coverage(disaster_demand)
        }
    
    def visualize_results(self, normal_demand, disaster_demand, disaster_map, reactor_locations, reactor_radius):
        """Create visualizations of the results"""
        fig, axes = plt.subplots(2, 3, figsize=(18, 12))
        
        # 1. Zone map
        zone_colors = np.zeros((self.grid_size, self.grid_size, 3))
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                zone_type = self.zone_map[i, j]
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
        im1 = axes[0, 1].imshow(normal_demand, cmap='YlOrRd', origin='lower')
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
        axes[1, 1].imshow(normal_demand, cmap='YlOrRd', origin='lower', alpha=0.7)
        self.plot_reactors(axes[1, 1], reactor_locations, reactor_radius)
        axes[1, 1].set_title('Reactor Placement (Normal)')
        
        # 6. Reactor placement on disaster demand
        axes[1, 2].imshow(disaster_demand, cmap='YlOrRd', origin='lower', alpha=0.7)
        self.plot_reactors(axes[1, 2], reactor_locations, reactor_radius)
        axes[1, 2].set_title('Reactor Placement (Disaster)')
        
        plt.tight_layout()
        plt.show()
    
    def plot_reactors(self, ax, reactor_locations, reactor_radius):
        """Add reactor markers and coverage circles to a plot"""
        for i, (x, y) in enumerate(reactor_locations):
            # Coverage circle
            circle = plt.Circle((y, x), reactor_radius, fill=False, color='lime', linewidth=2, alpha=0.8)
            ax.add_patch(circle)
            
            # Reactor marker
            ax.plot(y, x, '*', color='red', markersize=15, markeredgecolor='black', markeredgewidth=1)
            ax.text(y, x, str(i+1), ha='center', va='center', color='white', fontweight='bold', fontsize=8)


def main():
    print("=" * 60)
    print("SIMPLE ENERGY DEMAND SIMULATION & REACTOR OPTIMIZATION")
    print("=" * 60)
    
    # Get user input
    try:
        grid_size = int(input("Grid size (default 20): ") or 20)
        num_reactors = int(input("Number of reactors (default 3): ") or 3)
        reactor_radius = int(input("Reactor coverage radius (default 4): ") or 4)
        reactor_capacity = int(input("Reactor capacity in MW (default 15): ") or 15)
        
        print(f"\nDisaster types available:")
        print("1. earthquake - Radial damage from epicenter")
        print("2. flood - Linear flooding pattern") 
        print("3. power_outage - Sector blackout")
        
        disaster_choice = input("Choose disaster type (1-3, default 1): ") or "1"
        disaster_types = {"1": "earthquake", "2": "flood", "3": "power_outage"}
        disaster_type = disaster_types.get(disaster_choice, "earthquake")
        
        severity = int(input("Disaster severity (1-10, default 5): ") or 5)
        
    except ValueError:
        print("Invalid input, using defaults...")
        grid_size, num_reactors, reactor_radius, reactor_capacity = 20, 3, 4, 15
        disaster_type, severity = "earthquake", 5
    
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
        
        # Step 5: Visualize results
        print("\nGenerating visualizations...")
        sim.visualize_results(sim.base_demand, disaster_demand, disaster_map, reactor_locations, reactor_radius)
    
    print("\nSimulation complete!")


if __name__ == "__main__":
    main()