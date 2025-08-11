# Contributing to Energy Simulation Project

Thank you for your interest in contributing to this energy demand simulation and microreactor optimization project!

## Project Structure

```
energy-simulation/
├── README.md                              # Main project documentation
├── LICENSE                                # MIT license
├── dependencies.txt                       # Python package requirements
├── .gitignore                            # Git ignore patterns
├── 
├── # Core simulation files
├── simple_energy_reactor_optimization.py  # Standalone simulator (main entry point)
├── test_simple_simulation.py             # Automated test script
├── 
├── # Web interface components
├── app.py                                # Streamlit web dashboard
├── energy_simulation.py                  # Energy demand modeling
├── disaster_scenarios.py                 # Disaster simulation logic
├── optimization.py                       # Gurobi optimization engine
├── visualization.py                      # Plotting and charts
├── 
├── # Documentation
├── docs/
│   └── USAGE.md                          # Detailed usage instructions
├── 
├── # Examples and tutorials
├── examples/
│   ├── basic_example.py                  # Simple usage example
│   └── custom_scenario.py               # Advanced custom scenarios
└── 
```

## Getting Started for Development

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd energy-simulation
   ```

2. **Install dependencies**
   ```bash
   pip install -r dependencies.txt
   ```

3. **Test the installation**
   ```bash
   python test_simple_simulation.py
   ```

## Development Guidelines

### Code Style
- Follow PEP 8 Python style guidelines
- Use descriptive variable names
- Add docstrings to all functions and classes
- Keep functions focused and modular

### Testing
- Test your changes with `test_simple_simulation.py`
- Verify both standalone and web interface work
- Check that visualizations generate correctly

### Documentation
- Update README.md for major feature changes
- Add examples for new functionality
- Document any new parameters or options

## Areas for Contribution

### 1. New Disaster Scenarios
Add new disaster types in `disaster_scenarios.py`:
- Wildfire with wind patterns
- Hurricane with compound effects
- Cyber attacks on grid infrastructure
- Climate change long-term impacts

### 2. Enhanced Optimization
Improve the optimization engine in `optimization.py`:
- Multi-objective optimization (cost vs. coverage)
- Dynamic reactor sizing
- Time-dependent optimization
- Uncertainty modeling

### 3. Advanced Visualizations
Extend visualization capabilities in `visualization.py`:
- 3D terrain visualization
- Animated time series
- Interactive plots
- Real-time updates

### 4. Web Interface Features
Enhance the Streamlit app in `app.py`:
- Parameter sensitivity analysis
- Scenario comparison tools
- Export/import configurations
- Real-time collaboration

### 5. Performance Improvements
- Optimization algorithm speedups
- Memory usage optimization
- Parallel processing for large grids
- GPU acceleration for simulations

## Submission Process

1. **Fork** the repository
2. **Create a feature branch**: `git checkout -b feature-name`
3. **Make your changes** following the guidelines above
4. **Test thoroughly** with existing test scripts
5. **Add documentation** for new features
6. **Submit a pull request** with:
   - Clear description of changes
   - Screenshots of new visualizations (if applicable)
   - Performance impact assessment
   - Test results

## Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Help others learn and grow
- Maintain project quality standards

## Questions?

Feel free to open an issue for:
- Bug reports
- Feature requests
- Documentation improvements
- General questions about the project

## License

By contributing, you agree that your contributions will be licensed under the MIT License.