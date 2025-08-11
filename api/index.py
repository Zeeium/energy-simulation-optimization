from flask import Flask, render_template_string, jsonify, request
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
import base64
import random
import math

app = Flask(__name__)

# HTML template embedded in the Python file
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Energy Simulation & Reactor Optimization</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh; color: #333;
        }
        .container { max-width: 1200px; margin: 0 auto; padding: 2rem; }
        .header { text-align: center; color: white; margin-bottom: 2rem; }
        .header h1 { font-size: 2.5rem; margin-bottom: 0.5rem; }
        .header p { font-size: 1.2rem; opacity: 0.9; }
        .card {
            background: white; border-radius: 15px; padding: 2rem; margin: 1rem 0;
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        }
        .controls {
            display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 1.5rem; margin-bottom: 2rem;
        }
        .control-group { display: flex; flex-direction: column; }
        .control-group label { font-weight: bold; margin-bottom: 0.5rem; color: #2c3e50; }
        .control-group input, .control-group select {
            padding: 0.75rem; border: 2px solid #e0e0e0; border-radius: 8px;
            font-size: 1rem; transition: border-color 0.3s ease;
        }
        .control-group input:focus, .control-group select:focus {
            outline: none; border-color: #3498db;
        }
        .run-button {
            background: linear-gradient(135deg, #3498db, #2980b9); color: white;
            border: none; padding: 1rem 2rem; font-size: 1.1rem; font-weight: bold;
            border-radius: 10px; cursor: pointer; transition: all 0.3s ease;
            width: 100%; max-width: 300px; margin: 0 auto; display: block;
        }
        .run-button:hover { transform: translateY(-2px); box-shadow: 0 8px 20px rgba(52, 152, 219, 0.3); }
        .run-button:disabled { background: #95a5a6; cursor: not-allowed; transform: none; }
        .loading { text-align: center; padding: 2rem; display: none; }
        .spinner {
            border: 4px solid #f3f3f3; border-top: 4px solid #3498db; border-radius: 50%;
            width: 50px; height: 50px; animation: spin 1s linear infinite; margin: 0 auto 1rem;
        }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
        .results { display: none; }
        .metrics {
            display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem; margin: 1.5rem 0;
        }
        .metric {
            text-align: center; padding: 1rem; background: #f8f9fa;
            border-radius: 10px; border-left: 4px solid #3498db;
        }
        .metric h3 { font-size: 1.8rem; color: #2c3e50; margin-bottom: 0.5rem; }
        .metric p { color: #7f8c8d; font-weight: 500; }
        .visualization { text-align: center; margin: 2rem 0; }
        .visualization img { max-width: 100%; border-radius: 10px; box-shadow: 0 4px 20px rgba(0,0,0,0.1); }
        .error { background: #e74c3c; color: white; padding: 1rem; border-radius: 8px; margin: 1rem 0; display: none; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>⚡ Energy Simulation & Reactor Optimization</h1>
            <p>Advanced microreactor placement using mathematical optimization</p>
        </div>

        <div class="card">
            <h2>🎛️ Simulation Parameters</h2>
            <div class="controls">
                <div class="control-group">
                    <label for="grid_size">Grid Size</label>
                    <input type="number" id="grid_size" value="15" min="10" max="30">
                </div>
                <div class="control-group">
                    <label for="num_reactors">Number of Reactors</label>
                    <input type="number" id="num_reactors" value="2" min="1" max="8">
                </div>
                <div class="control-group">
                    <label for="reactor_radius">Reactor Coverage Radius</label>
                    <input type="number" id="reactor_radius" value="3" min="1" max="8">
                </div>
                <div class="control-group">
                    <label for="reactor_capacity">Reactor Capacity (MW)</label>
                    <input type="number" id="reactor_capacity" value="12" min="5" max="30">
                </div>
                <div class="control-group">
                    <label for="disaster_type">Disaster Type</label>
                    <select id="disaster_type">
                        <option value="earthquake">Earthquake</option>
                        <option value="flood">Flood</option>
                        <option value="power_outage">Power Outage</option>
                    </select>
                </div>
                <div class="control-group">
                    <label for="severity">Disaster Severity (1-10)</label>
                    <input type="number" id="severity" value="5" min="1" max="10">
                </div>
            </div>
            <button class="run-button" onclick="runSimulation()">🚀 Run Simulation</button>
        </div>

        <div class="loading">
            <div class="spinner"></div>
            <p>Running optimization... This may take a few moments.</p>
        </div>

        <div class="error" id="error-message"></div>

        <div class="results" id="results">
            <div class="card">
                <h2>📊 Simulation Results</h2>
                <div class="metrics" id="metrics"></div>
                <div class="visualization" id="visualization"></div>
            </div>
        </div>
    </div>

    <script>
        async function runSimulation() {
            const button = document.querySelector('.run-button');
            const loading = document.querySelector('.loading');
            const results = document.querySelector('.results');
            const errorDiv = document.getElementById('error-message');
            
            button.disabled = true;
            loading.style.display = 'block';
            results.style.display = 'none';
            errorDiv.style.display = 'none';
            
            try {
                const params = {
                    grid_size: parseInt(document.getElementById('grid_size').value),
                    num_reactors: parseInt(document.getElementById('num_reactors').value),
                    reactor_radius: parseInt(document.getElementById('reactor_radius').value),
                    reactor_capacity: parseInt(document.getElementById('reactor_capacity').value),
                    disaster_type: document.getElementById('disaster_type').value,
                    severity: parseInt(document.getElementById('severity').value)
                };
                
                const response = await fetch('/api/simulate', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(params)
                });
                
                const data = await response.json();
                
                if (data.success) {
                    displayResults(data);
                } else {
                    throw new Error(data.error || 'Simulation failed');
                }
                
            } catch (error) {
                errorDiv.textContent = 'Error: ' + error.message;
                errorDiv.style.display = 'block';
            } finally {
                button.disabled = false;
                loading.style.display = 'none';
            }
        }
        
        function displayResults(data) {
            const metrics = data.metrics;
            const metricsDiv = document.getElementById('metrics');
            const visualizationDiv = document.getElementById('visualization');
            const resultsDiv = document.getElementById('results');
            
            metricsDiv.innerHTML = `
                <div class="metric"><h3>${metrics.total_normal_demand}</h3><p>Normal Demand (MW)</p></div>
                <div class="metric"><h3>${metrics.total_disaster_demand}</h3><p>Disaster Demand (MW)</p></div>
                <div class="metric"><h3>${metrics.impact_percent > 0 ? '+' : ''}${metrics.impact_percent}%</h3><p>Demand Change</p></div>
                <div class="metric"><h3>${metrics.efficiency}%</h3><p>Coverage Efficiency</p></div>
                <div class="metric"><h3>${metrics.reactor_count}</h3><p>Reactors Placed</p></div>
                <div class="metric"><h3>${metrics.total_capacity}</h3><p>Total Capacity (MW)</p></div>
            `;
            
            visualizationDiv.innerHTML = `
                <h3>📈 Simulation Visualization</h3>
                <img src="data:image/png;base64,${data.plot}" alt="Simulation Results">
            `;
            
            resultsDiv.style.display = 'block';
        }
    </script>
</body>
</html>
'''

class SimpleEnergySimulator:
    def __init__(self, grid_size=15):
        self.grid_size = grid_size
        self.zone_map = None
        self.base_demand = None
        
    def create_map(self):
        self.zone_map = np.zeros((self.grid_size, self.grid_size))
        self.base_demand = np.zeros((self.grid_size, self.grid_size))
        
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                rand_val = random.random()
                if rand_val < 0.3:
                    self.zone_map[i, j] = 0
                    self.base_demand[i, j] = 0
                elif rand_val < 0.7:
                    self.zone_map[i, j] = 1
                    self.base_demand[i, j] = random.uniform(2, 6)
                elif rand_val < 0.9:
                    self.zone_map[i, j] = 2
                    self.base_demand[i, j] = random.uniform(4, 10)
                else:
                    self.zone_map[i, j] = 3
                    self.base_demand[i, j] = random.uniform(8, 15)
    
    def simulate_disaster(self, disaster_type, severity):
        disaster_map = np.zeros((self.grid_size, self.grid_size))
        center_x, center_y = self.grid_size // 2, self.grid_size // 2
        
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                distance = math.sqrt((i - center_x)**2 + (j - center_y)**2)
                
                if disaster_type == 'earthquake':
                    impact = max(0, 1 - distance / (severity * 2))
                elif disaster_type == 'flood':
                    if i < center_x + severity and j < center_y + severity:
                        impact = 0.8 * (severity / 10)
                    else:
                        impact = 0
                else:
                    if distance < severity:
                        impact = 0.9
                    else:
                        impact = 0
                
                disaster_map[i, j] = impact
        
        disaster_demand = self.base_demand * (1 + disaster_map * severity / 5)
        return disaster_demand, disaster_map
    
    def optimize_reactors(self, normal_demand, disaster_demand, num_reactors, radius, capacity):
        locations = []
        coverage_map = np.zeros((self.grid_size, self.grid_size))
        
        for _ in range(num_reactors):
            best_score = 0
            best_pos = (0, 0)
            
            for i in range(self.grid_size):
                for j in range(self.grid_size):
                    if (i, j) in locations:
                        continue
                    
                    score = 0
                    for di in range(-radius, radius + 1):
                        for dj in range(-radius, radius + 1):
                            ni, nj = i + di, j + dj
                            if 0 <= ni < self.grid_size and 0 <= nj < self.grid_size:
                                if di*di + dj*dj <= radius*radius:
                                    if coverage_map[ni, nj] == 0:
                                        score += disaster_demand[ni, nj]
                    
                    if score > best_score:
                        best_score = score
                        best_pos = (i, j)
            
            locations.append(best_pos)
            
            i, j = best_pos
            for di in range(-radius, radius + 1):
                for dj in range(-radius, radius + 1):
                    ni, nj = i + di, j + dj
                    if 0 <= ni < self.grid_size and 0 <= nj < self.grid_size:
                        if di*di + dj*dj <= radius*radius:
                            coverage_map[ni, nj] = 1
        
        total_normal = np.sum(normal_demand)
        total_disaster = np.sum(disaster_demand)
        covered_normal = np.sum(normal_demand * coverage_map)
        covered_disaster = np.sum(disaster_demand * coverage_map)
        
        metrics = {
            'normal_coverage': (covered_normal / total_normal) * 100 if total_normal > 0 else 0,
            'disaster_coverage': (covered_disaster / total_disaster) * 100 if total_disaster > 0 else 0
        }
        
        return locations, metrics

def plot_to_base64(fig):
    img = io.BytesIO()
    fig.savefig(img, format='png', bbox_inches='tight', dpi=100)
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode()
    plt.close(fig)
    return plot_url

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

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
        
        sim = SimpleEnergySimulator(grid_size)
        sim.create_map()
        
        disaster_demand, disaster_map = sim.simulate_disaster(disaster_type, severity)
        reactor_locations, metrics = sim.optimize_reactors(
            sim.base_demand, disaster_demand, num_reactors, reactor_radius, reactor_capacity
        )
        
        fig, axes = plt.subplots(2, 3, figsize=(15, 10))
        
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
        
        im1 = axes[0, 1].imshow(sim.base_demand, cmap='YlOrRd', origin='lower')
        axes[0, 1].set_title('Normal Demand')
        plt.colorbar(im1, ax=axes[0, 1])
        
        im2 = axes[0, 2].imshow(disaster_map, cmap='RdYlBu_r', origin='lower', vmin=0, vmax=1)
        axes[0, 2].set_title('Disaster Impact')
        plt.colorbar(im2, ax=axes[0, 2])
        
        im3 = axes[1, 0].imshow(disaster_demand, cmap='YlOrRd', origin='lower')
        axes[1, 0].set_title('Post-Disaster Demand')
        plt.colorbar(im3, ax=axes[1, 0])
        
        axes[1, 1].imshow(sim.base_demand, cmap='YlOrRd', origin='lower', alpha=0.7)
        for i, (x, y) in enumerate(reactor_locations):
            circle = plt.Circle((y, x), reactor_radius, fill=False, color='lime', linewidth=2)
            axes[1, 1].add_patch(circle)
            axes[1, 1].plot(y, x, '*', color='red', markersize=12)
        axes[1, 1].set_title('Optimal Placement')
        
        if metrics:
            categories = ['Normal Coverage', 'Disaster Coverage']
            values = [metrics['normal_coverage'], metrics['disaster_coverage']]
            axes[1, 2].bar(categories, values, color=['green', 'red'], alpha=0.7)
            axes[1, 2].set_ylabel('Coverage (%)')
            axes[1, 2].set_title('Performance Metrics')
            axes[1, 2].set_ylim(0, 100)
        
        plt.tight_layout()
        plot_url = plot_to_base64(fig)
        
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
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True)