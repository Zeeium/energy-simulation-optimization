import matplotlib.pyplot as plt
import numpy as np
import matplotlib.patches as patches

class Visualizer:
    def __init__(self):
        self.zone_colors = {
            'residential': '#90EE90',  # Light green
            'commercial': '#FFB6C1',   # Light pink
            'industrial': '#87CEEB',   # Sky blue
            'empty': '#F5F5DC'         # Beige
        }
        
        self.reactor_color = '#FF4500'  # Orange red
        self.coverage_color = '#32CD32'  # Lime green
    
    def plot_zone_map(self, zone_map):
        """Plot the zone map with different colors for each zone type"""
        fig, ax = plt.subplots(figsize=(10, 8))
        
        rows, cols = zone_map.shape
        
        # Create color map
        colored_map = np.zeros((rows, cols, 3))
        
        for i in range(rows):
            for j in range(cols):
                zone_type = zone_map[i, j]
                color_hex = self.zone_colors.get(zone_type, '#FFFFFF')
                color_rgb = self._hex_to_rgb(color_hex)
                colored_map[i, j] = color_rgb
        
        ax.imshow(colored_map, origin='lower')
        ax.set_title('Zone Map', fontsize=14, fontweight='bold')
        ax.set_xlabel('Grid X')
        ax.set_ylabel('Grid Y')
        
        # Add legend
        legend_elements = []
        for zone_type, color in self.zone_colors.items():
            if zone_type in np.unique(zone_map):
                legend_elements.append(
                    plt.Rectangle((0, 0), 1, 1, facecolor=color, label=zone_type.title())
                )
        
        ax.legend(handles=legend_elements, loc='upper right', bbox_to_anchor=(1.15, 1))
        
        # Add grid
        ax.set_xticks(range(0, cols, max(1, cols//10)))
        ax.set_yticks(range(0, rows, max(1, rows//10)))
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        return fig
    
    def plot_demand_heatmap(self, demand_map, title="Energy Demand"):
        """Plot energy demand as a heatmap"""
        fig, ax = plt.subplots(figsize=(10, 8))
        
        im = ax.imshow(demand_map, cmap='YlOrRd', origin='lower')
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.set_xlabel('Grid X')
        ax.set_ylabel('Grid Y')
        
        # Add colorbar
        cbar = plt.colorbar(im, ax=ax)
        cbar.set_label('Demand (MW)', rotation=270, labelpad=20)
        
        # Add grid
        rows, cols = demand_map.shape
        ax.set_xticks(range(0, cols, max(1, cols//10)))
        ax.set_yticks(range(0, rows, max(1, rows//10)))
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        return fig
    
    def plot_reactor_placement(self, zone_map, demand_map, reactor_locations, reactor_radius):
        """Plot reactor placement with coverage areas"""
        fig, ax = plt.subplots(figsize=(12, 10))
        
        # Plot demand heatmap as background
        im = ax.imshow(demand_map, cmap='YlOrRd', origin='lower', alpha=0.7)
        
        # Plot coverage circles
        for i, (rx, ry) in enumerate(reactor_locations):
            circle = plt.Circle((ry, rx), reactor_radius, 
                              fill=False, color=self.coverage_color, 
                              linewidth=2, alpha=0.6, linestyle='--')
            ax.add_patch(circle)
            
            # Add coverage area fill (very transparent)
            circle_fill = plt.Circle((ry, rx), reactor_radius, 
                                   fill=True, color=self.coverage_color, 
                                   alpha=0.1)
            ax.add_patch(circle_fill)
        
        # Plot reactor locations
        if reactor_locations:
            reactor_x = [ry for rx, ry in reactor_locations]
            reactor_y = [rx for rx, ry in reactor_locations]
            ax.scatter(reactor_x, reactor_y, c=self.reactor_color, 
                      s=200, marker='*', edgecolors='black', linewidth=2,
                      label='Microreactors', zorder=5)
            
            # Add reactor numbers
            for i, (rx, ry) in enumerate(reactor_locations):
                ax.text(ry, rx, str(i+1), ha='center', va='center', 
                       fontweight='bold', fontsize=10, color='white')
        
        ax.set_title('Optimal Microreactor Placement', fontsize=14, fontweight='bold')
        ax.set_xlabel('Grid X')
        ax.set_ylabel('Grid Y')
        
        # Add colorbar for demand
        cbar = plt.colorbar(im, ax=ax)
        cbar.set_label('Demand (MW)', rotation=270, labelpad=20)
        
        # Add legend
        legend_elements = [
            plt.Line2D([0], [0], marker='*', color='w', markerfacecolor=self.reactor_color,
                      markersize=15, label='Microreactors'),
            plt.Line2D([0], [0], color=self.coverage_color, linewidth=2, 
                      linestyle='--', label=f'Coverage (R={reactor_radius})')
        ]
        ax.legend(handles=legend_elements, loc='upper right', bbox_to_anchor=(1.3, 1))
        
        # Add grid
        rows, cols = demand_map.shape
        ax.set_xticks(range(0, cols, max(1, cols//10)))
        ax.set_yticks(range(0, rows, max(1, rows//10)))
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        return fig
    
    def plot_disaster_impact(self, original_demand, affected_demand, disaster_type="Disaster"):
        """Plot before and after disaster comparison"""
        fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(18, 6))
        
        # Original demand
        im1 = ax1.imshow(original_demand, cmap='YlOrRd', origin='lower')
        ax1.set_title('Before Disaster', fontsize=12, fontweight='bold')
        ax1.set_xlabel('Grid X')
        ax1.set_ylabel('Grid Y')
        
        # Affected demand
        im2 = ax2.imshow(affected_demand, cmap='YlOrRd', origin='lower')
        ax2.set_title(f'After {disaster_type}', fontsize=12, fontweight='bold')
        ax2.set_xlabel('Grid X')
        ax2.set_ylabel('Grid Y')
        
        # Difference map
        difference = affected_demand - original_demand
        im3 = ax3.imshow(difference, cmap='RdBu_r', origin='lower', 
                        vmin=np.min(difference), vmax=np.max(difference))
        ax3.set_title('Demand Change', fontsize=12, fontweight='bold')
        ax3.set_xlabel('Grid X')
        ax3.set_ylabel('Grid Y')
        
        # Add colorbars
        plt.colorbar(im1, ax=ax1, label='Demand (MW)')
        plt.colorbar(im2, ax=ax2, label='Demand (MW)')
        plt.colorbar(im3, ax=ax3, label='Change (MW)')
        
        plt.tight_layout()
        return fig
    
    def plot_coverage_comparison(self, metrics_dict):
        """Plot coverage comparison across different strategies"""
        strategies = list(metrics_dict.keys())
        normal_coverage = [metrics_dict[s]['metrics'].get('normal_coverage', 0) for s in strategies]
        disaster_coverage = [metrics_dict[s]['metrics'].get('disaster_coverage', 0) for s in strategies]
        
        fig, ax = plt.subplots(figsize=(12, 6))
        
        x = np.arange(len(strategies))
        width = 0.35
        
        bars1 = ax.bar(x - width/2, normal_coverage, width, label='Normal Scenario', 
                      color='green', alpha=0.7)
        bars2 = ax.bar(x + width/2, disaster_coverage, width, label='Disaster Scenario', 
                      color='red', alpha=0.7)
        
        ax.set_xlabel('Optimization Strategy')
        ax.set_ylabel('Coverage (%)')
        ax.set_title('Coverage Comparison Across Strategies')
        ax.set_xticks(x)
        ax.set_xticklabels([s.replace('_', ' ').title() for s in strategies])
        ax.legend()
        ax.set_ylim(0, 100)
        
        # Add value labels on bars
        for bars in [bars1, bars2]:
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height + 1,
                       f'{height:.1f}%', ha='center', va='bottom')
        
        plt.tight_layout()
        return fig
    
    def _hex_to_rgb(self, hex_color):
        """Convert hex color to RGB tuple (0-1 range)"""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16)/255.0 for i in (0, 2, 4))
    
    def plot_time_series_with_capacity(self, hours, demands, reactor_capacity=None, title="Energy Demand Over Time"):
        """Plot time series with optional reactor capacity line"""
        fig, ax = plt.subplots(figsize=(12, 6))
        
        ax.plot(hours, demands, linewidth=2, color='blue', label='Total Demand')
        
        if reactor_capacity is not None:
            ax.axhline(y=reactor_capacity, color='red', linestyle='--', 
                      linewidth=2, label=f'Total Reactor Capacity ({reactor_capacity:.1f} MW)')
            
            # Shade area where demand exceeds capacity
            over_capacity = np.array(demands) > reactor_capacity
            if np.any(over_capacity):
                ax.fill_between(hours, demands, reactor_capacity, 
                              where=over_capacity, alpha=0.3, color='red',
                              label='Demand Exceeds Capacity')
        
        ax.set_xlabel('Hours from Start')
        ax.set_ylabel('Total Demand (MW)')
        ax.set_title(title)
        ax.grid(True, alpha=0.3)
        ax.legend()
        
        plt.tight_layout()
        return fig
