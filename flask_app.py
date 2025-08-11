from flask import Flask, render_template, jsonify, request
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import io
import base64
import json
from simple_energy_reactor_optimization import SimpleEnergySimulator

app = Flask(__name__)

# Store simulation results
sim_results = {}

def plot_to_base64(fig):
    """Convert matplotlib figure to base64 string for web display"""
    img = io.BytesIO()
    fig.savefig(img, format='png', bbox_inches='tight', dpi=100)
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode()
    plt.close(fig)
    return plot_url

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/simulate', methods=['POST'])
def simulate():
    try:
        data = request.json
        grid_size = int(data.get('grid_size', 15))
        num_reactors = int(data.get('num_reactors', 2))
        reactor_radius = int(data.get('reactor_radius', 3))
        reactor_capacity = int(data.get('reactor_capacity', 12))
        disaster_type = data.get('disaster_type', 'earthquake')
        severity = int(data.get('severity', 5))
        
        # Create simulation
        sim = SimpleEnergySimulator(grid_size)
        sim.create_map()
        
        # Simulate disaster
        disaster_demand, disaster_map = sim.simulate_disaster(disaster_type, severity)
        
        # Optimize reactors
        reactor_locations, metrics = sim.optimize_reactors(
            sim.base_demand, disaster_demand, num_reactors, reactor_radius, reactor_capacity
        )
        
        # Create visualizations
        fig, axes = plt.subplots(2, 3, figsize=(15, 10))
        
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
        
        axes[0, 0].imshow(zone_colors, origin='lower')
        axes[0, 0].set_title('Zone Map')
        
        # Normal demand
        im1 = axes[0, 1].imshow(sim.base_demand, cmap='YlOrRd', origin='lower')
        axes[0, 1].set_title('Normal Demand')
        plt.colorbar(im1, ax=axes[0, 1])
        
        # Disaster impact
        im2 = axes[0, 2].imshow(disaster_map, cmap='RdYlBu_r', origin='lower', vmin=0, vmax=1)
        axes[0, 2].set_title('Disaster Impact')
        plt.colorbar(im2, ax=axes[0, 2])
        
        # Disaster demand
        im3 = axes[1, 0].imshow(disaster_demand, cmap='YlOrRd', origin='lower')
        axes[1, 0].set_title('Post-Disaster Demand')
        plt.colorbar(im3, ax=axes[1, 0])
        
        # Reactor placement (normal)
        axes[1, 1].imshow(sim.base_demand, cmap='YlOrRd', origin='lower', alpha=0.7)
        for i, (x, y) in enumerate(reactor_locations):
            circle = plt.Circle((y, x), reactor_radius, fill=False, color='lime', linewidth=2)
            axes[1, 1].add_patch(circle)
            axes[1, 1].plot(y, x, '*', color='red', markersize=12)
        axes[1, 1].set_title('Optimal Placement')
        
        # Performance metrics chart
        if metrics:
            categories = ['Normal Coverage', 'Disaster Coverage']
            values = [metrics['normal_coverage'], metrics['disaster_coverage']]
            axes[1, 2].bar(categories, values, color=['green', 'red'], alpha=0.7)
            axes[1, 2].set_ylabel('Coverage (%)')
            axes[1, 2].set_title('Performance Metrics')
            axes[1, 2].set_ylim(0, 100)
        
        plt.tight_layout()
        plot_url = plot_to_base64(fig)
        
        # Calculate summary stats
        total_normal = float(np.sum(sim.base_demand))
        total_disaster = float(np.sum(disaster_demand))
        impact_percent = ((total_disaster - total_normal) / total_normal) * 100
        
        return jsonify({
            'success': True,
            'plot': plot_url,
            'metrics': {
                'total_normal_demand': round(total_normal, 1),
                'total_disaster_demand': round(total_disaster, 1),
                'impact_percent': round(impact_percent, 1),
                'normal_coverage': round(metrics.get('normal_coverage', 0), 1),
                'disaster_coverage': round(metrics.get('disaster_coverage', 0), 1),
                'efficiency': round((metrics.get('normal_coverage', 0) + metrics.get('disaster_coverage', 0))/2, 1),
                'reactor_count': len(reactor_locations),
                'total_capacity': len(reactor_locations) * reactor_capacity
            },
            'reactor_locations': reactor_locations
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

if __name__ == '__main__':
    app.run(debug=True)