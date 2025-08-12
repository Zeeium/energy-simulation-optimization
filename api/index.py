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
            
            <div style="display: flex; gap: 1rem; justify-content: center;">
                <button class="run-button" onclick="runSimulation()" style="max-width: 200px;">🚀 Run Simulation</button>
                <button class="run-button" onclick="showGameMode()" style="max-width: 200px; background: linear-gradient(135deg, #e74c3c, #c0392b);">🎮 Challenge Game</button>
            </div>
        </div>
        
        <!-- Game Mode Section (hidden by default) -->
        <div class="card" id="game-mode" style="display: none; margin-top: 2rem;">
            <h2>🎮 Challenge Mode: Beat the Optimizer!</h2>
            <p>Test your reactor placement skills against our mathematical optimizer. Can you match or beat the optimal solution?</p>
            
            <div id="game-setup">
                <h3>🎯 Challenge Setup</h3>
                <div class="controls">
                    <div class="control-group">
                        <label for="game_grid_size">Grid Size</label>
                        <input type="number" id="game_grid_size" value="15" min="10" max="25">
                    </div>
                    <div class="control-group">
                        <label for="game_num_reactors">Number of Reactors</label>
                        <input type="number" id="game_num_reactors" value="3" min="2" max="6">
                    </div>
                    <div class="control-group">
                        <label for="game_reactor_radius">Reactor Coverage Radius</label>
                        <input type="number" id="game_reactor_radius" value="3" min="2" max="6">
                    </div>
                    <div class="control-group">
                        <label for="game_disaster_type">Disaster Type</label>
                        <select id="game_disaster_type">
                            <option value="earthquake">Earthquake</option>
                            <option value="flood">Flood</option>
                            <option value="power_outage">Power Outage</option>
                        </select>
                    </div>
                    <div class="control-group">
                        <label for="game_severity">Disaster Severity (3-8)</label>
                        <input type="number" id="game_severity" value="5" min="3" max="8">
                    </div>
                </div>
                
                <div style="display: flex; gap: 1rem; justify-content: center; margin-top: 2rem;">
                    <button class="run-button" onclick="previewChallenge()" style="max-width: 200px;">🔍 Preview Challenge</button>
                    <button class="run-button" onclick="backToSimulation()" style="max-width: 200px; background: linear-gradient(135deg, #95a5a6, #7f8c8d);">← Back to Simulation</button>
                </div>
            </div>
            
            <div id="challenge-preview" style="display: none;">
                <h3>📋 Challenge Preview</h3>
                <div id="preview-visualization"></div>
                <div style="text-align: center; margin-top: 2rem;">
                    <button class="run-button" onclick="startChallenge()" style="max-width: 300px;">🔒 Lock Parameters & Start Challenge</button>
                </div>
            </div>
            
            <div id="reactor-placement" style="display: none;">
                <h3>🎯 Place Your Reactors!</h3>
                <div id="placement-info" style="background: #f8f9fa; padding: 1rem; border-radius: 8px; margin: 1rem 0;"></div>
                
                <div style="display: grid; grid-template-columns: 2fr 1fr; gap: 2rem; margin: 2rem 0;">
                    <div>
                        <h4>Interactive Grid - Click to place reactors</h4>
                        <div id="placement-grid">
                            <canvas id="grid-canvas" width="400" height="400" style="border: 2px solid #ddd; cursor: crosshair; border-radius: 8px;"></canvas>
                        </div>
                        
                        <div style="margin-top: 1rem;">
                            <h4>Or enter coordinates manually:</h4>
                            <div style="display: flex; gap: 1rem; align-items: end;">
                                <div class="control-group" style="margin: 0;">
                                    <label for="reactor_x">Grid X</label>
                                    <input type="number" id="reactor_x" value="0" min="0" style="width: 80px;">
                                </div>
                                <div class="control-group" style="margin: 0;">
                                    <label for="reactor_y">Grid Y</label>
                                    <input type="number" id="reactor_y" value="0" min="0" style="width: 80px;">
                                </div>
                                <button onclick="addReactor()" style="padding: 0.75rem 1rem; background: #27ae60; color: white; border: none; border-radius: 5px;">➕ Add Reactor</button>
                            </div>
                            
                            <div style="margin-top: 1rem;">
                                <button onclick="autoPlaceReactor()" style="padding: 0.75rem 1rem; background: #3498db; color: white; border: none; border-radius: 5px;">🎯 Auto-place at High Demand</button>
                                <button onclick="clearLastReactor()" style="padding: 0.75rem 1rem; background: #e74c3c; color: white; border: none; border-radius: 5px;">❌ Remove Last</button>
                            </div>
                        </div>
                        
                        <div id="current-placements" style="margin-top: 1rem;"></div>
                    </div>
                    
                    <div>
                        <div id="game-progress"></div>
                        <button class="run-button" id="solve-button" onclick="solveChallenge()" style="display: none; margin-top: 2rem;">🚀 Challenge the Optimizer!</button>
                    </div>
                </div>
            </div>
            
            <div id="challenge-results" style="display: none;">
                <h3>🏆 Challenge Results</h3>
                <div id="score-display" style="text-align: center; margin: 2rem 0;"></div>
                <div id="comparison-metrics"></div>
                <div id="solution-comparison"></div>
                <div style="text-align: center; margin-top: 2rem;">
                    <button class="run-button" onclick="newChallenge()" style="max-width: 200px;">🎮 New Challenge</button>
                </div>
            </div>
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

        // Game Mode Functions
        let gameState = {
            phase: 'setup',
            scenario: null,
            userPlacements: [],
            optimalSolution: null
        };

        function showGameMode() {
            document.getElementById('game-mode').style.display = 'block';
            document.querySelector('.card:first-of-type').style.display = 'none';
            document.getElementById('results').style.display = 'none';
        }

        function backToSimulation() {
            document.getElementById('game-mode').style.display = 'none';
            document.querySelector('.card:first-of-type').style.display = 'block';
            resetGame();
        }

        function resetGame() {
            gameState = { phase: 'setup', scenario: null, userPlacements: [], optimalSolution: null };
            document.getElementById('game-setup').style.display = 'block';
            document.getElementById('challenge-preview').style.display = 'none';
            document.getElementById('reactor-placement').style.display = 'none';
            document.getElementById('challenge-results').style.display = 'none';
        }

        async function previewChallenge() {
            const params = {
                grid_size: parseInt(document.getElementById('game_grid_size').value),
                num_reactors: parseInt(document.getElementById('game_num_reactors').value),
                reactor_radius: parseInt(document.getElementById('game_reactor_radius').value),
                reactor_capacity: 12,
                disaster_type: document.getElementById('game_disaster_type').value,
                severity: parseInt(document.getElementById('game_severity').value)
            };

            try {
                const response = await fetch('/api/preview_challenge', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(params)
                });
                
                const data = await response.json();
                
                if (data.success) {
                    gameState.scenario = { ...params, ...data };
                    document.getElementById('preview-visualization').innerHTML = `
                        <img src="data:image/png;base64,${data.preview_plot}" alt="Challenge Preview" style="max-width: 100%; border-radius: 10px;">
                        <p style="margin-top: 1rem;"><strong>Your Mission:</strong> Place ${params.num_reactors} reactors optimally to handle this ${params.disaster_type} scenario!</p>
                    `;
                    document.getElementById('challenge-preview').style.display = 'block';
                }
            } catch (error) {
                alert('Error: ' + error.message);
            }
        }

        function startChallenge() {
            gameState.phase = 'playing';
            gameState.userPlacements = [];
            
            document.getElementById('game-setup').style.display = 'none';
            document.getElementById('challenge-preview').style.display = 'none';
            document.getElementById('reactor-placement').style.display = 'block';
            
            updatePlacementUI();
        }

        function updatePlacementUI() {
            const scenario = gameState.scenario;
            const placementsCount = gameState.userPlacements.length;
            
            document.getElementById('placement-info').innerHTML = `
                <strong>Mission:</strong> Place ${scenario.num_reactors} reactors to optimize coverage during a ${scenario.disaster_type} scenario
            `;
            
            // Update max values for input fields
            const maxVal = scenario.grid_size - 1;
            document.getElementById('reactor_x').max = maxVal;
            document.getElementById('reactor_y').max = maxVal;
            
            // Initialize canvas if not already done
            initializeCanvas();
            
            // Show current placements
            let placementsHTML = '';
            if (placementsCount > 0) {
                placementsHTML = `<h4>Current Placements (${placementsCount}/${scenario.num_reactors}):</h4>`;
                gameState.userPlacements.forEach((placement, i) => {
                    placementsHTML += `
                        <div style="display: flex; justify-content: space-between; align-items: center; padding: 0.5rem; background: #f0f0f0; margin: 0.5rem 0; border-radius: 5px;">
                            <span>Reactor ${i+1}: Grid (${placement[0]}, ${placement[1]})</span>
                            <button onclick="removeReactor(${i})" style="background: #e74c3c; color: white; border: none; padding: 0.25rem 0.5rem; border-radius: 3px; cursor: pointer;">Remove</button>
                        </div>
                    `;
                });
            }
            document.getElementById('current-placements').innerHTML = placementsHTML;
            
            // Update progress
            const progress = (placementsCount / scenario.num_reactors) * 100;
            document.getElementById('game-progress').innerHTML = `
                <div style="background: #f8f9fa; padding: 1rem; border-radius: 8px;">
                    <h4>Challenge Info:</h4>
                    <p><strong>Grid:</strong> ${scenario.grid_size}×${scenario.grid_size}</p>
                    <p><strong>Reactors:</strong> ${scenario.num_reactors}</p>
                    <p><strong>Coverage:</strong> ${scenario.reactor_radius} radius</p>
                    <p><strong>Disaster:</strong> ${scenario.disaster_type}</p>
                    <p><strong>Severity:</strong> ${scenario.severity}/10</p>
                    <div style="margin-top: 1rem;">
                        <div style="background: #e0e0e0; height: 20px; border-radius: 10px; overflow: hidden;">
                            <div style="background: #27ae60; height: 100%; width: ${progress}%; transition: width 0.3s ease;"></div>
                        </div>
                        <p style="text-align: center; margin-top: 0.5rem;">Progress: ${placementsCount}/${scenario.num_reactors} reactors placed</p>
                    </div>
                </div>
            `;
            
            // Show solve button when ready
            if (placementsCount === scenario.num_reactors) {
                document.getElementById('solve-button').style.display = 'block';
            } else {
                document.getElementById('solve-button').style.display = 'none';
            }
        }

        function addReactor() {
            const x = parseInt(document.getElementById('reactor_x').value);
            const y = parseInt(document.getElementById('reactor_y').value);
            
            // Check if already placed
            const exists = gameState.userPlacements.some(placement => placement[0] === x && placement[1] === y);
            
            if (exists) {
                alert('Reactor already placed at this location!');
                return;
            }
            
            if (gameState.userPlacements.length < gameState.scenario.num_reactors) {
                gameState.userPlacements.push([x, y]);
                updatePlacementUI();
            }
        }

        function removeReactor(index) {
            gameState.userPlacements.splice(index, 1);
            updatePlacementUI();
        }

        async function solveChallenge() {
            const scenario = gameState.scenario;
            const challengeData = {
                ...scenario,
                user_placements: gameState.userPlacements
            };

            try {
                const response = await fetch('/api/solve_challenge', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(challengeData)
                });
                
                const data = await response.json();
                
                if (data.success) {
                    showChallengeResults(data);
                }
            } catch (error) {
                alert('Error: ' + error.message);
            }
        }

        function showChallengeResults(data) {
            gameState.phase = 'completed';
            
            document.getElementById('reactor-placement').style.display = 'none';
            document.getElementById('challenge-results').style.display = 'block';
            
            const score = data.user_score;
            let scoreColor, performance;
            
            if (score >= 90) {
                scoreColor = '#27ae60';
                performance = 'EXCELLENT!';
            } else if (score >= 75) {
                scoreColor = '#f39c12';
                performance = 'GOOD!';
            } else if (score >= 50) {
                scoreColor = '#e67e22';
                performance = 'FAIR';
            } else {
                scoreColor = '#e74c3c';
                performance = 'NEEDS IMPROVEMENT';
            }
            
            document.getElementById('score-display').innerHTML = `
                <div style="padding: 2rem; border: 3px solid ${scoreColor}; border-radius: 15px; background: ${scoreColor}20;">
                    <h2 style="color: ${scoreColor}; margin: 0;">User Optimization: ${score.toFixed(1)}%</h2>
                    <h3 style="color: ${scoreColor}; margin: 0.5rem 0 0 0;">${performance}</h3>
                </div>
            `;
            
            document.getElementById('comparison-metrics').innerHTML = `
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 2rem; margin: 2rem 0;">
                    <div>
                        <h4>Your Solution:</h4>
                        <div class="metric"><h3>${data.user_metrics.normal_coverage.toFixed(1)}%</h3><p>Normal Coverage</p></div>
                        <div class="metric"><h3>${data.user_metrics.disaster_coverage.toFixed(1)}%</h3><p>Disaster Coverage</p></div>
                        <div class="metric"><h3>${((data.user_metrics.normal_coverage + data.user_metrics.disaster_coverage)/2).toFixed(1)}%</h3><p>Average Coverage</p></div>
                    </div>
                    <div>
                        <h4>Optimal Solution:</h4>
                        <div class="metric"><h3>${data.optimal_metrics.normal_coverage.toFixed(1)}%</h3><p>Normal Coverage</p></div>
                        <div class="metric"><h3>${data.optimal_metrics.disaster_coverage.toFixed(1)}%</h3><p>Disaster Coverage</p></div>
                        <div class="metric"><h3>${((data.optimal_metrics.normal_coverage + data.optimal_metrics.disaster_coverage)/2).toFixed(1)}%</h3><p>Average Coverage</p></div>
                    </div>
                </div>
            `;
            
            document.getElementById('solution-comparison').innerHTML = `
                <h4>Solution Comparison</h4>
                <img src="data:image/png;base64,${data.comparison_plot}" alt="Solution Comparison" style="max-width: 100%; border-radius: 10px;">
            `;
        }

        function newChallenge() {
            resetGame();
        }

        // Canvas-based interactive grid functionality
        let canvas = null;
        let ctx = null;
        let canvasInitialized = false;

        function initializeCanvas() {
            if (canvasInitialized || !gameState.scenario) return;
            
            canvas = document.getElementById('grid-canvas');
            if (!canvas) return;
            
            ctx = canvas.getContext('2d');
            canvasInitialized = true;
            
            // Add click event listener
            canvas.addEventListener('click', function(event) {
                if (gameState.userPlacements.length >= gameState.scenario.num_reactors) {
                    alert('Maximum reactors placed! Remove some to place new ones.');
                    return;
                }
                
                const rect = canvas.getBoundingClientRect();
                const clickX = event.clientX - rect.left;
                const clickY = event.clientY - rect.top;
                
                // Convert canvas coordinates to grid coordinates
                const gridSize = gameState.scenario.grid_size;
                const cellSize = 400 / gridSize;
                const gridX = Math.floor(clickX / cellSize);
                const gridY = Math.floor(clickY / cellSize);
                
                // Check bounds
                if (gridX >= 0 && gridX < gridSize && gridY >= 0 && gridY < gridSize) {
                    // Check if position already occupied
                    const exists = gameState.userPlacements.some(placement => 
                        placement[0] === gridY && placement[1] === gridX
                    );
                    
                    if (!exists) {
                        gameState.userPlacements.push([gridY, gridX]);
                        updatePlacementUI();
                    } else {
                        alert('Reactor already placed at this location!');
                    }
                }
            });
            
            drawGrid();
        }

        function drawGrid() {
            if (!ctx || !gameState.scenario) return;
            
            const gridSize = gameState.scenario.grid_size;
            const cellSize = 400 / gridSize;
            
            // Clear canvas
            ctx.clearRect(0, 0, 400, 400);
            
            // Draw background (simulate disaster demand heatmap)
            const disasterDemand = gameState.scenario.simulator_data?.disaster_demand;
            if (disasterDemand) {
                for (let i = 0; i < gridSize; i++) {
                    for (let j = 0; j < gridSize; j++) {
                        const demand = disasterDemand[i][j];
                        const intensity = Math.min(demand / 20, 1); // Normalize to 0-1
                        
                        // Color based on demand intensity (heatmap)
                        const red = Math.floor(255 * intensity);
                        const green = Math.floor(255 * (1 - intensity * 0.5));
                        const blue = 0;
                        
                        ctx.fillStyle = `rgb(${red}, ${green}, ${blue})`;
                        ctx.globalAlpha = 0.7;
                        ctx.fillRect(j * cellSize, i * cellSize, cellSize, cellSize);
                    }
                }
                ctx.globalAlpha = 1;
            }
            
            // Draw grid lines
            ctx.strokeStyle = '#ddd';
            ctx.lineWidth = 1;
            for (let i = 0; i <= gridSize; i++) {
                ctx.beginPath();
                ctx.moveTo(i * cellSize, 0);
                ctx.lineTo(i * cellSize, 400);
                ctx.stroke();
                
                ctx.beginPath();
                ctx.moveTo(0, i * cellSize);
                ctx.lineTo(400, i * cellSize);
                ctx.stroke();
            }
            
            // Draw reactor placements
            gameState.userPlacements.forEach((placement, index) => {
                const [gridY, gridX] = placement;
                const centerX = gridX * cellSize + cellSize / 2;
                const centerY = gridY * cellSize + cellSize / 2;
                
                // Draw coverage circle
                const radius = gameState.scenario.reactor_radius * cellSize;
                ctx.beginPath();
                ctx.arc(centerX, centerY, radius, 0, 2 * Math.PI);
                ctx.strokeStyle = '#00ff00';
                ctx.lineWidth = 2;
                ctx.setLineDash([5, 5]);
                ctx.stroke();
                ctx.setLineDash([]);
                
                // Draw reactor marker
                ctx.fillStyle = '#ff0000';
                ctx.beginPath();
                ctx.arc(centerX, centerY, 8, 0, 2 * Math.PI);
                ctx.fill();
                
                // Draw reactor label
                ctx.fillStyle = '#ffffff';
                ctx.font = 'bold 12px Arial';
                ctx.textAlign = 'center';
                ctx.fillText(`R${index + 1}`, centerX, centerY + 4);
            });
        }

        function autoPlaceReactor() {
            if (gameState.userPlacements.length >= gameState.scenario.num_reactors) {
                alert('Maximum reactors already placed!');
                return;
            }
            
            const gridSize = gameState.scenario.grid_size;
            const disasterDemand = gameState.scenario.simulator_data?.disaster_demand;
            
            if (!disasterDemand) {
                alert('Disaster demand data not available');
                return;
            }
            
            // Find high demand locations not yet occupied
            let bestLocation = null;
            let maxDemand = 0;
            
            for (let i = 0; i < gridSize; i++) {
                for (let j = 0; j < gridSize; j++) {
                    const demand = disasterDemand[i][j];
                    const occupied = gameState.userPlacements.some(placement => 
                        placement[0] === i && placement[1] === j
                    );
                    
                    if (!occupied && demand > maxDemand) {
                        maxDemand = demand;
                        bestLocation = [i, j];
                    }
                }
            }
            
            if (bestLocation) {
                gameState.userPlacements.push(bestLocation);
                updatePlacementUI();
            } else {
                alert('No suitable high-demand location found!');
            }
        }

        function clearLastReactor() {
            if (gameState.userPlacements.length > 0) {
                gameState.userPlacements.pop();
                updatePlacementUI();
            }
        }

        // Update the existing updatePlacementUI function to include canvas drawing
        const originalUpdatePlacementUI = updatePlacementUI;
        updatePlacementUI = function() {
            originalUpdatePlacementUI();
            drawGrid();
        };
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
        
        # Add legend for zone map
        from matplotlib.patches import Patch
        legend_elements = [
            Patch(facecolor=[0.9, 0.9, 0.9], label='Empty'),
            Patch(facecolor=[0.5, 1.0, 0.5], label='Residential'),
            Patch(facecolor=[1.0, 0.7, 0.7], label='Commercial'), 
            Patch(facecolor=[0.7, 0.7, 1.0], label='Industrial')
        ]
        axes[0, 0].legend(handles=legend_elements, loc='upper right')
        
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

@app.route('/api/preview_challenge', methods=['POST'])
def preview_challenge():
    try:
        data = request.json
        grid_size = int(data.get('grid_size', 15))
        disaster_type = data.get('disaster_type', 'earthquake')
        severity = int(data.get('severity', 5))
        
        # Create simulation for preview
        sim = SimpleEnergySimulator(grid_size)
        sim.create_map()
        
        disaster_demand, disaster_map = sim.simulate_disaster(disaster_type, severity)
        
        # Create preview visualization (3 panels)
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
        preview_plot = plot_to_base64(fig)
        
        return jsonify({
            'success': True,
            'preview_plot': preview_plot,
            'simulator_data': {
                'base_demand': sim.base_demand.tolist(),
                'zone_map': sim.zone_map.tolist(),
                'disaster_demand': disaster_demand.tolist(),
                'disaster_map': disaster_map.tolist()
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/solve_challenge', methods=['POST'])
def solve_challenge():
    try:
        data = request.json
        grid_size = int(data.get('grid_size', 15))
        num_reactors = int(data.get('num_reactors', 3))
        reactor_radius = int(data.get('reactor_radius', 3))
        reactor_capacity = int(data.get('reactor_capacity', 12))
        disaster_type = data.get('disaster_type', 'earthquake')
        severity = int(data.get('severity', 5))
        user_placements = data.get('user_placements', [])
        
        # Recreate simulation
        sim = SimpleEnergySimulator(grid_size)
        sim.create_map()
        disaster_demand, disaster_map = sim.simulate_disaster(disaster_type, severity)
        
        # Calculate user solution performance
        user_metrics = calculate_user_performance(
            user_placements, sim.base_demand, disaster_demand, reactor_radius
        )
        
        # Get optimal solution
        optimal_locations, optimal_metrics = sim.optimize_reactors(
            sim.base_demand, disaster_demand, num_reactors, reactor_radius, reactor_capacity
        )
        
        # Calculate user optimization score
        user_coverage = (user_metrics['normal_coverage'] + user_metrics['disaster_coverage']) / 2
        optimal_coverage = (optimal_metrics['normal_coverage'] + optimal_metrics['disaster_coverage']) / 2
        
        if optimal_coverage > 0:
            optimization_score = min(100, (user_coverage / optimal_coverage) * 100)
            
            # Bonus for exact location matches
            location_bonus = 0
            for user_loc in user_placements:
                if tuple(user_loc) in optimal_locations:
                    location_bonus += 10
            
            final_score = min(100, optimization_score + location_bonus)
        else:
            final_score = 50
        
        # Create comparison visualization
        fig, axes = plt.subplots(1, 2, figsize=(16, 8))
        
        # User solution
        axes[0].imshow(disaster_demand, cmap='YlOrRd', origin='lower', alpha=0.7)
        for i, (x, y) in enumerate(user_placements):
            circle = plt.Circle((y, x), reactor_radius, fill=False, color='lime', linewidth=2, linestyle='--')
            axes[0].add_patch(circle)
            axes[0].plot(y, x, '*', color='red', markersize=12)
        axes[0].set_title(f'Your Solution (Score: {final_score:.1f}%)')
        axes[0].set_xlabel('Grid X')
        axes[0].set_ylabel('Grid Y')
        
        # Optimal solution
        axes[1].imshow(disaster_demand, cmap='YlOrRd', origin='lower', alpha=0.7)
        for i, (x, y) in enumerate(optimal_locations):
            circle = plt.Circle((y, x), reactor_radius, fill=False, color='lime', linewidth=2, linestyle='--')
            axes[1].add_patch(circle)
            axes[1].plot(y, x, '*', color='blue', markersize=12)
        axes[1].set_title('Optimal Solution')
        axes[1].set_xlabel('Grid X')
        axes[1].set_ylabel('Grid Y')
        
        plt.tight_layout()
        comparison_plot = plot_to_base64(fig)
        
        return jsonify({
            'success': True,
            'user_score': final_score,
            'user_metrics': user_metrics,
            'optimal_metrics': optimal_metrics,
            'comparison_plot': comparison_plot
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

def calculate_user_performance(user_locations, normal_demand, disaster_demand, reactor_radius):
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

if __name__ == '__main__':
    app.run(debug=True)