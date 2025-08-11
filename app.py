import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import random
from energy_simulation import EnergySimulation
from disaster_scenarios import DisasterScenarios
from optimization import MicroreactorOptimizer
from visualization import Visualizer

st.set_page_config(
    page_title="Energy Demand Simulation & Microreactor Optimization",
    page_icon="⚡",
    layout="wide"
)

def main():
    st.title("⚡ Dynamic Energy Demand Simulation with Disaster Scenarios")
    st.markdown("**Microreactor Placement Optimization using Gurobi**")
    
    # Sidebar for configuration
    st.sidebar.header("Configuration Parameters")
    
    # Grid and reactor parameters
    st.sidebar.subheader("Grid Configuration")
    grid_rows = st.sidebar.slider("Grid Rows", 10, 50, 20)
    grid_cols = st.sidebar.slider("Grid Columns", 10, 50, 20)
    
    st.sidebar.subheader("Microreactor Parameters")
    num_reactors = st.sidebar.slider("Number of Microreactors", 1, 10, 3)
    reactor_radius = st.sidebar.slider("Reactor Coverage Radius", 1, 10, 5)
    reactor_capacity = st.sidebar.slider("Reactor Capacity (MW)", 1, 20, 10)
    
    # Zone distribution
    st.sidebar.subheader("Zone Distribution")
    residential_pct = st.sidebar.slider("Residential %", 0, 100, 60)
    commercial_pct = st.sidebar.slider("Commercial %", 0, 100, 25)
    industrial_pct = 100 - residential_pct - commercial_pct
    st.sidebar.write(f"Industrial: {industrial_pct}%")
    
    # Time parameters
    st.sidebar.subheader("Simulation Parameters")
    season = st.sidebar.selectbox("Season", ["Spring", "Summer", "Fall", "Winter"])
    time_of_day = st.sidebar.slider("Hour of Day", 0, 23, 12)
    simulation_hours = st.sidebar.slider("Simulation Duration (hours)", 1, 168, 24)
    
    # Initialize simulation
    if 'energy_sim' not in st.session_state:
        st.session_state.energy_sim = EnergySimulation(grid_rows, grid_cols)
        st.session_state.disaster_sim = DisasterScenarios()
        st.session_state.optimizer = MicroreactorOptimizer()
        st.session_state.visualizer = Visualizer()
    
    # Update parameters if changed
    if (st.session_state.energy_sim.grid_rows != grid_rows or 
        st.session_state.energy_sim.grid_cols != grid_cols):
        st.session_state.energy_sim = EnergySimulation(grid_rows, grid_cols)
    
    energy_sim = st.session_state.energy_sim
    disaster_sim = st.session_state.disaster_sim
    optimizer = st.session_state.optimizer
    visualizer = st.session_state.visualizer
    
    # Generate zones
    if st.sidebar.button("Generate New Map"):
        energy_sim.generate_zones(residential_pct/100, commercial_pct/100, industrial_pct/100)
        st.rerun()
    
    if not hasattr(energy_sim, 'zone_map') or energy_sim.zone_map is None:
        energy_sim.generate_zones(residential_pct/100, commercial_pct/100, industrial_pct/100)
    
    # Main content area
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("🗺️ Zone Map")
        zone_fig = visualizer.plot_zone_map(energy_sim.zone_map)
        st.pyplot(zone_fig)
        
        # Current demand
        current_demand = energy_sim.calculate_demand(season, time_of_day)
        st.subheader("⚡ Current Energy Demand")
        demand_fig = visualizer.plot_demand_heatmap(current_demand, "Current Demand")
        st.pyplot(demand_fig)
    
    with col2:
        st.subheader("📊 Demand Statistics")
        total_demand = np.sum(current_demand)
        avg_demand = np.mean(current_demand)
        max_demand = np.max(current_demand)
        
        col2a, col2b, col2c = st.columns(3)
        with col2a:
            st.metric("Total Demand", f"{total_demand:.1f} MW")
        with col2b:
            st.metric("Average Demand", f"{avg_demand:.1f} MW")
        with col2c:
            st.metric("Peak Demand", f"{max_demand:.1f} MW")
        
        # Zone-wise statistics
        st.subheader("📈 Zone-wise Demand")
        zone_stats = energy_sim.get_zone_statistics(current_demand)
        for zone_type, stats in zone_stats.items():
            st.write(f"**{zone_type.title()}:** {stats['total']:.1f} MW (Avg: {stats['avg']:.1f} MW)")
    
    # Disaster scenario section
    st.header("🌪️ Disaster Scenarios")
    
    col3, col4 = st.columns([1, 1])
    
    with col3:
        disaster_type = st.selectbox("Disaster Type", 
                                   ["None", "Earthquake", "Storm", "Power Outage", "Flood"])
        severity = st.slider("Disaster Severity", 1, 10, 5)
        
        if disaster_type != "None":
            if st.button("Apply Disaster Scenario"):
                disaster_impact = disaster_sim.simulate_disaster(
                    disaster_type.lower(), severity, energy_sim.zone_map
                )
                affected_demand = energy_sim.apply_disaster_impact(current_demand, disaster_impact)
                st.session_state.affected_demand = affected_demand
                st.session_state.disaster_impact = disaster_impact
                st.rerun()
    
    with col4:
        if hasattr(st.session_state, 'affected_demand'):
            st.subheader("🚨 Post-Disaster Demand")
            disaster_fig = visualizer.plot_demand_heatmap(
                st.session_state.affected_demand, 
                f"Post-{disaster_type} Demand"
            )
            st.pyplot(disaster_fig)
            
            # Impact statistics
            original_total = np.sum(current_demand)
            affected_total = np.sum(st.session_state.affected_demand)
            impact_pct = ((affected_total - original_total) / original_total) * 100
            st.metric("Demand Change", f"{impact_pct:+.1f}%")
    
    # Optimization section
    st.header("🔧 Microreactor Placement Optimization")
    
    optimization_objective = st.selectbox(
        "Optimization Objective",
        ["Minimize Uncovered Demand", "Maximize Coverage", "Disaster Resilience"]
    )
    
    if st.button("Optimize Reactor Placement"):
        with st.spinner("Running Gurobi optimization..."):
            # Prepare demand scenarios
            normal_demand = current_demand
            disaster_demand = getattr(st.session_state, 'affected_demand', current_demand)
            
            # Run optimization
            result = optimizer.optimize_placement(
                normal_demand,
                disaster_demand,
                num_reactors,
                reactor_radius,
                reactor_capacity,
                optimization_objective.lower()
            )
            
            if result['status'] == 'optimal':
                st.session_state.optimization_result = result
                st.success("Optimization completed successfully!")
                st.rerun()
            else:
                st.error(f"Optimization failed: {result['status']}")
    
    # Display optimization results
    if hasattr(st.session_state, 'optimization_result'):
        result = st.session_state.optimization_result
        
        st.subheader("🎯 Optimization Results")
        
        col5, col6 = st.columns([1, 1])
        
        with col5:
            # Reactor placement visualization
            placement_fig = visualizer.plot_reactor_placement(
                energy_sim.zone_map,
                current_demand,
                result['reactor_locations'],
                reactor_radius
            )
            st.pyplot(placement_fig)
            
            # Reactor locations
            st.subheader("📍 Reactor Locations")
            for i, (x, y) in enumerate(result['reactor_locations']):
                st.write(f"Reactor {i+1}: ({x}, {y})")
        
        with col6:
            # Performance metrics
            st.subheader("📊 Performance Metrics")
            metrics = result['metrics']
            
            st.metric("Coverage Efficiency", f"{metrics['coverage_efficiency']:.1f}%")
            st.metric("Normal Scenario Coverage", f"{metrics['normal_coverage']:.1f}%")
            st.metric("Disaster Scenario Coverage", f"{metrics['disaster_coverage']:.1f}%")
            st.metric("Redundancy Factor", f"{metrics['redundancy']:.2f}")
            st.metric("Total Capacity", f"{metrics['total_capacity']:.1f} MW")
            
            # Coverage comparison
            st.subheader("📈 Coverage Analysis")
            coverage_data = {
                'Normal': metrics['normal_coverage'],
                'Disaster': metrics['disaster_coverage'],
                'Average': (metrics['normal_coverage'] + metrics['disaster_coverage']) / 2
            }
            
            fig, ax = plt.subplots(figsize=(8, 4))
            bars = ax.bar(coverage_data.keys(), coverage_data.values(), 
                         color=['green', 'red', 'blue'], alpha=0.7)
            ax.set_ylabel('Coverage (%)')
            ax.set_title('Coverage Comparison')
            ax.set_ylim(0, 100)
            
            # Add value labels on bars
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height + 1,
                       f'{height:.1f}%', ha='center', va='bottom')
            
            st.pyplot(fig)
    
    # Time series simulation
    st.header("📅 Time Series Simulation")
    
    if st.button("Run Time Series Analysis"):
        with st.spinner("Running time series simulation..."):
            # Generate time series data
            hours = list(range(simulation_hours))
            demands = []
            
            for hour in hours:
                current_hour = (time_of_day + hour) % 24
                demand = energy_sim.calculate_demand(season, current_hour)
                demands.append(np.sum(demand))
            
            # Plot time series
            fig, ax = plt.subplots(figsize=(12, 6))
            ax.plot(hours, demands, linewidth=2, color='blue', label='Total Demand')
            ax.set_xlabel('Hours from Start')
            ax.set_ylabel('Total Demand (MW)')
            ax.set_title(f'Energy Demand Over {simulation_hours} Hours')
            ax.grid(True, alpha=0.3)
            ax.legend()
            
            # Add reactor capacity line if optimization result exists
            if hasattr(st.session_state, 'optimization_result'):
                total_capacity = st.session_state.optimization_result['metrics']['total_capacity']
                ax.axhline(y=total_capacity, color='red', linestyle='--', 
                          label=f'Total Reactor Capacity ({total_capacity:.1f} MW)')
                ax.legend()
            
            st.pyplot(fig)
            
            # Statistics
            col7, col8, col9 = st.columns(3)
            with col7:
                st.metric("Average Demand", f"{np.mean(demands):.1f} MW")
            with col8:
                st.metric("Peak Demand", f"{np.max(demands):.1f} MW")
            with col9:
                st.metric("Min Demand", f"{np.min(demands):.1f} MW")

if __name__ == "__main__":
    main()
