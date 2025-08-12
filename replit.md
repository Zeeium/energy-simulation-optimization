# Overview

This is a Python-based energy demand simulation and microreactor optimization system with both a Streamlit web interface and a standalone simple version. The application simulates dynamic energy demand patterns across different zones (residential, commercial, industrial) and optimizes the placement of microreactors to meet demand during both normal operations and disaster scenarios. The system uses mathematical optimization via Gurobi to find optimal reactor placements that minimize uncovered demand while considering coverage constraints and capacity limitations.

## Recent Changes (August 11, 2025)

- Created `simple_energy_reactor_optimization.py` - A standalone, command-line version that doesn't require the Streamlit interface
- Added `test_simple_simulation.py` - Non-interactive test script for the simple version
- Successfully implemented and tested the core simulation features:
  - Grid-based zone mapping (empty, residential, commercial, industrial) with proper color-coded legends
  - Disaster simulation (earthquake, flood, power outage) with different impact patterns
  - Gurobi-based optimization for microreactor placement
  - Comprehensive visualization showing zone maps, demand patterns, disaster impacts, and optimal reactor placement
  - Performance metrics calculation (coverage efficiency, demand analysis)
- **Added Interactive Challenge Game Mode:**
  - Dual-mode interface: Simulation Mode + Challenge Game tabs in Streamlit
  - Complete Flask web version with game mode for Vercel deployment
  - Interactive reactor placement competition against optimizer
  - "User Optimization" scoring system (0-100%) comparing user vs optimal solutions
  - Three-phase game flow: Setup → Playing → Results with performance ratings
  - Side-by-side visual comparison of user and optimal reactor placements

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Frontend Architecture
- **Streamlit-based web interface**: Provides an interactive dashboard for configuration and visualization
- **Component-based structure**: Separates concerns into distinct modules for simulation, optimization, and visualization
- **Real-time parameter adjustment**: Uses Streamlit widgets (sliders, selectboxes) for dynamic configuration

## Simulation Engine
- **Grid-based modeling**: Represents geographical areas as discrete grid cells with zone classifications
- **Multi-scenario simulation**: Handles both normal operations and disaster scenarios with different impact patterns
- **Time-dependent demand modeling**: Incorporates seasonal variations, time-of-day patterns, and zone-specific usage profiles
- **Disaster impact simulation**: Models various disaster types (earthquake, storm, flood, power outage) with different geographical impact patterns

## Optimization Framework
- **Mathematical programming approach**: Uses Gurobi optimizer for mixed-integer programming (MIP)
- **Multi-objective optimization**: Supports different optimization objectives like minimizing uncovered demand
- **Constraint-based modeling**: Enforces reactor count limits, coverage requirements, and capacity constraints
- **Scenario-aware optimization**: Considers both normal and disaster scenarios in placement decisions

## Data Management
- **In-memory data structures**: Uses NumPy arrays for efficient grid-based calculations
- **Session state management**: Leverages Streamlit's session state for maintaining simulation data across interactions
- **Real-time data processing**: Processes demand patterns and optimization results on-the-fly

## Visualization System
- **Matplotlib-based plotting**: Creates visual representations of zone maps, demand patterns, and reactor placements
- **Color-coded mapping**: Uses distinct colors for different zone types and reactor coverage areas
- **Interactive charts**: Integrates with Streamlit to provide responsive visualizations

# External Dependencies

## Optimization Engine
- **Gurobi**: Commercial mathematical optimization solver for mixed-integer programming problems
  - Requires Gurobi license for full functionality
  - Used for reactor placement optimization with complex constraints

## Scientific Computing
- **NumPy**: Numerical computing library for array operations and mathematical calculations
- **Matplotlib**: Plotting library for creating visualizations and charts

## Web Framework
- **Streamlit**: Web application framework for creating interactive data science applications
  - Provides the user interface and web serving capabilities
  - Handles real-time updates and user interactions

## Python Standard Library
- **datetime**: For time-based calculations and temporal modeling
- **random**: For stochastic elements in simulation
- **math**: For mathematical operations in distance and coverage calculations

Note: The application architecture is designed to be modular and extensible, allowing for easy addition of new disaster scenarios, optimization objectives, or visualization features.