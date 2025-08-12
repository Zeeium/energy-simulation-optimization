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
    
    # Create tabs for different modes
    tab1, tab2 = st.tabs(["🔬 Simulation Mode", "🎮 Challenge Game"])
    
    with tab1:
        simulation_mode()
    
    with tab2:
        game_mode()

def simulation_mode():
    
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

def game_mode():
    """Interactive game mode where users compete against the optimizer"""
    st.markdown("### 🎮 Challenge Mode: Beat the Optimizer!")
    st.markdown("Test your reactor placement skills against our mathematical optimizer. Can you match or beat the optimal solution?")
    
    # Initialize game state
    if 'game_state' not in st.session_state:
        st.session_state.game_state = {
            'phase': 'setup',  # setup, playing, completed
            'user_placements': [],
            'locked_params': None,
            'challenge_scenario': None,
            'optimal_solution': None,
            'user_score': 0
        }
    
    game_state = st.session_state.game_state
    
    if game_state['phase'] == 'setup':
        setup_challenge_game()
    elif game_state['phase'] == 'playing':
        play_challenge_game()
    elif game_state['phase'] == 'completed':
        show_challenge_results()

def setup_challenge_game():
    """Setup phase: User configures challenge parameters"""
    st.subheader("🎯 Challenge Setup")
    st.markdown("Configure your challenge parameters. Once locked, you can't change them!")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("**Grid & Reactors**")
        grid_size = st.slider("Grid Size", 10, 25, 15, key="game_grid")
        num_reactors = st.slider("Number of Reactors", 2, 6, 3, key="game_reactors")
        reactor_radius = st.slider("Reactor Coverage Radius", 2, 6, 3, key="game_radius")
        reactor_capacity = st.slider("Reactor Capacity (MW)", 8, 20, 12, key="game_capacity")
        
    with col2:
        st.markdown("**Disaster Scenario**")
        disaster_type = st.selectbox("Disaster Type", 
                                   ["earthquake", "flood", "power_outage"], key="game_disaster")
        disaster_severity = st.slider("Disaster Severity", 3, 8, 5, key="game_severity")
        
        difficulty = st.selectbox("Difficulty Level",
                                ["Easy", "Medium", "Hard"], key="game_difficulty")
    
    # Preview scenario
    if st.button("🔍 Preview Challenge", key="preview_challenge"):
        # Generate challenge scenario
        from simple_energy_reactor_optimization import SimpleEnergySimulator
        sim = SimpleEnergySimulator(grid_size)
        sim.create_map()
        
        disaster_demand, disaster_map = sim.simulate_disaster(disaster_type, disaster_severity)
        
        # Store scenario
        challenge_scenario = {
            'simulator': sim,
            'grid_size': grid_size,
            'num_reactors': num_reactors,
            'reactor_radius': reactor_radius, 
            'reactor_capacity': reactor_capacity,
            'disaster_type': disaster_type,
            'disaster_severity': disaster_severity,
            'difficulty': difficulty,
            'disaster_demand': disaster_demand,
            'disaster_map': disaster_map
        }
        
        st.session_state.game_state['challenge_scenario'] = challenge_scenario
        
        # Show preview
        st.subheader("📋 Challenge Preview")
        fig, axes = plt.subplots(1, 3, figsize=(15, 5))
        
        # Zone map
        zone_colors = np.zeros((grid_size, grid_size, 3))
        for i in range(grid_size):
            for j in range(grid_size):
                zone_type = sim.zone_map[i, j]
                if zone_type == 0:
                    zone_colors[i, j] = [0.9, 0.9, 0.9]
                elif zone_type == 1:
                    zone_colors[i, j] = [0.5, 1.0, 0.5]
                elif zone_type == 2:
                    zone_colors[i, j] = [1.0, 0.7, 0.7]
                elif zone_type == 3:
                    zone_colors[i, j] = [0.7, 0.7, 1.0]
        
        axes[0].imshow(zone_colors, origin='lower')
        axes[0].set_title('Zone Map')
        
        # Normal demand
        im1 = axes[1].imshow(sim.base_demand, cmap='YlOrRd', origin='lower')
        axes[1].set_title('Normal Demand')
        plt.colorbar(im1, ax=axes[1])
        
        # Disaster impact
        im2 = axes[2].imshow(disaster_map, cmap='RdYlBu_r', origin='lower', vmin=0, vmax=1)
        axes[2].set_title(f'{disaster_type.title()} Impact')
        plt.colorbar(im2, ax=axes[2])
        
        plt.tight_layout()
        st.pyplot(fig)
        
        st.info(f"**Your Mission:** Place {num_reactors} reactors optimally to handle this {disaster_type} scenario!")
    
    # Lock parameters button
    if st.session_state.game_state.get('challenge_scenario'):
        if st.button("🔒 Lock Parameters & Start Challenge", type="primary", key="lock_params"):
            st.session_state.game_state['phase'] = 'playing'
            st.session_state.game_state['locked_params'] = True
            st.rerun()

def play_challenge_game():
    """Playing phase: User places reactors interactively"""
    scenario = st.session_state.game_state['challenge_scenario']
    
    st.subheader("🎯 Place Your Reactors!")
    st.markdown(f"**Mission:** Place {scenario['num_reactors']} reactors to optimize coverage during a {scenario['disaster_type']} scenario")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("**Click on the grid to place reactors:**")
        
        # Interactive grid for reactor placement
        grid_size = scenario['grid_size']
        user_placements = st.session_state.game_state.get('user_placements', [])
        
        # Display current placements
        if user_placements:
            st.markdown(f"**Current Placements ({len(user_placements)}/{scenario['num_reactors']}):**")
            for i, (x, y) in enumerate(user_placements):
                col_a, col_b = st.columns([3, 1])
                with col_a:
                    st.write(f"Reactor {i+1}: Grid ({x}, {y})")
                with col_b:
                    if st.button(f"Remove", key=f"remove_{i}"):
                        user_placements.pop(i)
                        st.session_state.game_state['user_placements'] = user_placements
                        st.rerun()
        
        # Simple grid input (since streamlit doesn't support click events on plots)
        if len(user_placements) < scenario['num_reactors']:
            st.markdown("**Add Reactor:**")
            col_x, col_y, col_add = st.columns([1, 1, 1])
            with col_x:
                new_x = st.number_input("Grid X", 0, grid_size-1, 0, key="new_reactor_x")
            with col_y:
                new_y = st.number_input("Grid Y", 0, grid_size-1, 0, key="new_reactor_y")
            with col_add:
                st.write("")  # spacing
                if st.button("➕ Add Reactor", key="add_reactor"):
                    if (new_x, new_y) not in user_placements:
                        user_placements.append((new_x, new_y))
                        st.session_state.game_state['user_placements'] = user_placements
                        st.rerun()
                    else:
                        st.warning("Reactor already placed at this location!")
        
        # Show current placement on grid
        if user_placements:
            fig, ax = plt.subplots(figsize=(10, 10))
            
            # Show disaster demand as background
            im = ax.imshow(scenario['disaster_demand'], cmap='YlOrRd', origin='lower', alpha=0.7)
            
            # Show user reactor placements
            for i, (x, y) in enumerate(user_placements):
                # Coverage circle
                circle = plt.Circle((y, x), scenario['reactor_radius'], 
                                  fill=False, color='lime', linewidth=2, linestyle='--')
                ax.add_patch(circle)
                
                # Reactor marker
                ax.plot(y, x, '*', color='red', markersize=15)
                ax.text(y, x+0.5, f'R{i+1}', ha='center', va='bottom', 
                       fontweight='bold', color='white', fontsize=12)
            
            ax.set_title('Your Reactor Placement')
            ax.set_xlabel('Grid X')
            ax.set_ylabel('Grid Y')
            plt.colorbar(im, ax=ax, label='Demand (MW)')
            
            st.pyplot(fig)
    
    with col2:
        st.markdown("**Challenge Info:**")
        st.info(f"""
        **Grid:** {scenario['grid_size']}×{scenario['grid_size']}
        **Reactors:** {scenario['num_reactors']}
        **Coverage:** {scenario['reactor_radius']} radius
        **Disaster:** {scenario['disaster_type'].title()}
        **Severity:** {scenario['disaster_severity']}/10
        """)
        
        # Progress
        progress = len(user_placements) / scenario['num_reactors']
        st.progress(progress)
        st.write(f"Progress: {len(user_placements)}/{scenario['num_reactors']} reactors placed")
        
        # Solve button
        if len(user_placements) == scenario['num_reactors']:
            if st.button("🚀 Challenge the Optimizer!", type="primary", key="solve_challenge"):
                solve_challenge()

def solve_challenge():
    """Solve the challenge and compare user vs optimal solution"""
    scenario = st.session_state.game_state['challenge_scenario']
    user_placements = st.session_state.game_state['user_placements']
    
    # Calculate user solution performance
    user_metrics = calculate_placement_performance(
        user_placements, 
        scenario['simulator'].base_demand,
        scenario['disaster_demand'],
        scenario['reactor_radius']
    )
    
    # Get optimal solution using greedy algorithm
    optimal_locations, optimal_metrics = scenario['simulator'].optimize_reactors(
        scenario['simulator'].base_demand,
        scenario['disaster_demand'],
        scenario['num_reactors'],
        scenario['reactor_radius'],
        scenario['reactor_capacity']
    )
    
    # Calculate user optimization score
    user_coverage = (user_metrics['normal_coverage'] + user_metrics['disaster_coverage']) / 2
    optimal_coverage = (optimal_metrics['normal_coverage'] + optimal_metrics['disaster_coverage']) / 2
    
    # Score calculation (with some bonus for exact matches)
    if optimal_coverage > 0:
        optimization_score = min(100, (user_coverage / optimal_coverage) * 100)
        
        # Bonus for exact location matches
        location_bonus = 0
        for user_loc in user_placements:
            if user_loc in optimal_locations:
                location_bonus += 10
        
        final_score = min(100, optimization_score + location_bonus)
    else:
        final_score = 50  # Fallback score
    
    # Store results
    st.session_state.game_state['user_score'] = final_score
    st.session_state.game_state['optimal_solution'] = {
        'locations': optimal_locations,
        'metrics': optimal_metrics
    }
    st.session_state.game_state['user_metrics'] = user_metrics
    st.session_state.game_state['phase'] = 'completed'
    st.rerun()

def show_challenge_results():
    """Show challenge results and comparison"""
    scenario = st.session_state.game_state['challenge_scenario']
    user_placements = st.session_state.game_state['user_placements']
    user_score = st.session_state.game_state['user_score']
    optimal_solution = st.session_state.game_state['optimal_solution']
    user_metrics = st.session_state.game_state['user_metrics']
    
    st.subheader("🏆 Challenge Results")
    
    # Score display
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        # Score with color coding
        if user_score >= 90:
            score_color = "🟢"
            performance = "EXCELLENT!"
        elif user_score >= 75:
            score_color = "🟡" 
            performance = "GOOD!"
        elif user_score >= 50:
            score_color = "🟠"
            performance = "FAIR"
        else:
            score_color = "🔴"
            performance = "NEEDS IMPROVEMENT"
            
        st.markdown(f"""
        <div style="text-align: center; padding: 20px; border: 2px solid #ddd; border-radius: 10px;">
            <h2>{score_color} User Optimization: {user_score:.1f}%</h2>
            <h3>{performance}</h3>
        </div>
        """, unsafe_allow_html=True)
    
    # Detailed comparison
    st.subheader("📊 Performance Comparison")
    
    comparison_col1, comparison_col2 = st.columns(2)
    
    with comparison_col1:
        st.markdown("**Your Solution:**")
        st.metric("Normal Coverage", f"{user_metrics['normal_coverage']:.1f}%")
        st.metric("Disaster Coverage", f"{user_metrics['disaster_coverage']:.1f}%")
        st.metric("Average Coverage", f"{(user_metrics['normal_coverage'] + user_metrics['disaster_coverage'])/2:.1f}%")
    
    with comparison_col2:
        st.markdown("**Optimal Solution:**")
        optimal_metrics = optimal_solution['metrics']
        st.metric("Normal Coverage", f"{optimal_metrics['normal_coverage']:.1f}%")
        st.metric("Disaster Coverage", f"{optimal_metrics['disaster_coverage']:.1f}%") 
        st.metric("Average Coverage", f"{(optimal_metrics['normal_coverage'] + optimal_metrics['disaster_coverage'])/2:.1f}%")
    
    # Visual comparison
    st.subheader("🗺️ Solution Comparison")
    fig, axes = plt.subplots(1, 2, figsize=(16, 8))
    
    # User solution
    axes[0].imshow(scenario['disaster_demand'], cmap='YlOrRd', origin='lower', alpha=0.7)
    for i, (x, y) in enumerate(user_placements):
        circle = plt.Circle((y, x), scenario['reactor_radius'], 
                          fill=False, color='lime', linewidth=2, linestyle='--')
        axes[0].add_patch(circle)
        axes[0].plot(y, x, '*', color='red', markersize=12)
    axes[0].set_title(f'Your Solution (Score: {user_score:.1f}%)')
    
    # Optimal solution  
    axes[1].imshow(scenario['disaster_demand'], cmap='YlOrRd', origin='lower', alpha=0.7)
    for i, (x, y) in enumerate(optimal_solution['locations']):
        circle = plt.Circle((y, x), scenario['reactor_radius'], 
                          fill=False, color='lime', linewidth=2, linestyle='--')
        axes[1].add_patch(circle)
        axes[1].plot(y, x, '*', color='blue', markersize=12)
    axes[1].set_title('Optimal Solution')
    
    plt.tight_layout()
    st.pyplot(fig)
    
    # New challenge button
    if st.button("🎮 New Challenge", type="primary", key="new_challenge"):
        st.session_state.game_state = {
            'phase': 'setup',
            'user_placements': [],
            'locked_params': None,
            'challenge_scenario': None,
            'optimal_solution': None,
            'user_score': 0
        }
        st.rerun()

def calculate_placement_performance(user_locations, normal_demand, disaster_demand, reactor_radius):
    """Calculate performance metrics for user reactor placement"""
    def calculate_coverage(demand_map):
        total_demand = 0
        covered_demand = 0
        grid_size = demand_map.shape[0]
        
        for i in range(grid_size):
            for j in range(grid_size):
                demand = demand_map[i, j]
                if demand > 1.0:
                    total_demand += demand
                    
                    # Check if covered by any reactor
                    covered = False
                    for rx, ry in user_locations:
                        distance = ((i - rx)**2 + (j - ry)**2)**0.5
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

if __name__ == "__main__":
    main()
