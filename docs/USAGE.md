# Usage Guide

## Running the Simulation

### Option 1: Simple Command Line (Recommended)

The easiest way to run the simulation:

```bash
python simple_energy_reactor_optimization.py
```

You'll be prompted to enter:
- Grid size (default: 20)
- Number of reactors (default: 3)
- Reactor coverage radius (default: 4)
- Reactor capacity in MW (default: 15)
- Disaster type (earthquake/flood/power_outage)
- Disaster severity (1-10)

### Option 2: Automated Test

Run a pre-configured test without any input prompts:

```bash
python test_simple_simulation.py
```

This will automatically run with sensible defaults and save a visualization.

### Option 3: Web Interface

For an interactive dashboard with real-time parameter adjustment:

```bash
streamlit run app.py --server.port 5000
```

Then open your browser to `http://localhost:5000`

## Understanding the Output

### Console Output

The simulation provides detailed feedback:

```
Creating energy demand map...
Map created with 15x15 grid
  Empty: 127 cells, 62.7 MW total
  Residential: 29 cells, 84.3 MW total
  Commercial: 33 cells, 200.0 MW total
  Industrial: 36 cells, 346.2 MW total

Simulating earthquake disaster (severity 6/10)...
  Earthquake epicenter at (7, 3)
  Total demand changed by -43.6%

Optimizing placement of 2 reactors...
  Reactor specs: 12 MW capacity, 3 cell radius
  Optimization successful! Found 2 reactor locations:
    Reactor 1: (3, 3)
    Reactor 2: (3, 8)
  Performance:
    Normal scenario coverage: 56.4%
    Disaster scenario coverage: 55.8%
    Total capacity: 24 MW
```

### Visualization

The system generates a 6-panel visualization showing:

1. **Zone Map**: Color-coded areas (residential=green, commercial=pink, industrial=blue, empty=gray)
2. **Normal Energy Demand**: Heat map of baseline energy consumption
3. **Disaster Impact**: Shows how the disaster affected different areas (blue=most affected)
4. **Post-Disaster Demand**: Energy demand after the disaster
5. **Reactor Placement (Normal)**: Optimal reactor locations with coverage circles
6. **Reactor Placement (Disaster)**: Same placement showing disaster scenario coverage

### Performance Metrics

- **Coverage Efficiency**: Average percentage of demand covered across both scenarios
- **Normal/Disaster Coverage**: Percentage of demand covered in each scenario
- **Total Capacity**: Combined power output of all reactors
- **Redundancy Factor**: Average number of reactors covering each demand point

## Customizing the Simulation

### Disaster Types

1. **Earthquake**: Radial damage from a random epicenter
   - Higher severity = larger affected radius
   - Damage decreases with distance from epicenter

2. **Flood**: Linear flooding pattern
   - Can be horizontal or vertical
   - Severity affects the width of flooded area

3. **Power Outage**: Rectangular sector blackout
   - Severity affects the size of affected area
   - Causes severe demand reduction (90% loss)

### Zone Types

- **Empty** (0.5 MW/cell): Minimal demand areas
- **Residential** (3.0 MW/cell): Housing areas with moderate demand
- **Commercial** (6.0 MW/cell): Business districts with higher demand
- **Industrial** (10.0 MW/cell): Factories with highest demand

### Optimization Objectives

The system minimizes uncovered demand by:
- Weighing disaster scenarios 2x more heavily than normal scenarios
- Considering reactor coverage radius and capacity constraints
- Finding mathematically optimal placement using mixed-integer programming

## Tips for Best Results

1. **Grid Size**: Start with 15-20 for quick results, use 30+ for detailed simulations
2. **Reactor Count**: Use 2-5 reactors for most scenarios
3. **Coverage Radius**: 3-5 cells typically provides good coverage without overlap
4. **Capacity**: Match total capacity to roughly 20-40% of total demand for realistic scenarios
5. **Disaster Severity**: Use 5-7 for moderate impact, 8-10 for severe scenarios