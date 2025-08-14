# Energy Demand Simulation & Microreactor Optimization

A Python-based simulation system that models energy demand across different zones and optimizes microreactor placement for both normal operations and disaster scenarios using mathematical optimization.
- Disclaimer, Majority of the code is created using generative AI. This was to create a visual representation of the task we are trying to accomplish.
## Features

- **Grid-based zone mapping** with residential, commercial, and industrial areas
- **Dynamic energy demand simulation** with time-of-day and seasonal variations
- **Disaster scenario modeling** (earthquake, flood, power outage) with realistic impact patterns
- **Mathematical optimization** using Gurobi to find optimal microreactor placement
- **Comprehensive visualizations** showing zone maps, demand patterns, and reactor placement
- **Both web interface and standalone versions** for different use cases

## Quick Start

### Standalone Version (Recommended)

Run the simple command-line version:

```bash
python simple_energy_reactor_optimization.py
```

Or run the automated test:

```bash
python test_simple_simulation.py
```

### Web Interface

For the interactive Streamlit dashboard:

```bash
streamlit run app.py --server.port 5000
```

## Requirements

- Python 3.11+
- gurobipy (Gurobi optimization library)
- matplotlib (visualization)
- numpy (numerical computing)
- streamlit (web interface)

Install dependencies:

```bash
pip install gurobipy matplotlib numpy streamlit
```

## How It Works

1. **Map Generation**: Creates a grid with clustered zones (residential, commercial, industrial)
2. **Demand Calculation**: Simulates realistic energy demand patterns for each zone
3. **Disaster Simulation**: Applies various disaster scenarios that modify demand patterns
4. **Optimization**: Uses Gurobi to find optimal microreactor placement that minimizes uncovered demand
5. **Visualization**: Displays comprehensive results showing zones, demand, disasters, and optimal reactor placement

## Example Results

The system generates visualizations showing:
- Zone distribution map
- Normal and post-disaster energy demand heat maps
- Disaster impact patterns
- Optimal microreactor placement with coverage areas
- Performance metrics (coverage efficiency, total capacity)

## File Structure

```
├── simple_energy_reactor_optimization.py  # Main standalone simulator
├── test_simple_simulation.py             # Automated test script
├── app.py                                # Streamlit web interface
├── energy_simulation.py                  # Energy demand modeling
├── disaster_scenarios.py                 # Disaster simulation logic
├── optimization.py                       # Gurobi optimization engine
├── visualization.py                      # Plotting and visualization
└── README.md                            # This file
```

## Parameters

Key simulation parameters you can adjust:

- **Grid size**: Size of the simulation area (default: 20x20)
- **Number of reactors**: How many microreactors to place (default: 3)
- **Reactor radius**: Coverage area of each reactor (default: 4 cells)
- **Reactor capacity**: Power output per reactor (default: 15 MW)
- **Disaster type**: earthquake, flood, or power_outage
- **Disaster severity**: Scale from 1-10

## License

This project uses Gurobi optimization which requires a license for commercial use. Academic licenses are available for free.

## Contributing

Feel free to fork this repository and submit pull requests for improvements or additional features.
