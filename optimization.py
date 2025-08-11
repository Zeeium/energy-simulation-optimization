import gurobipy as gp
from gurobipy import GRB
import numpy as np
import math

class MicroreactorOptimizer:
    def __init__(self):
        self.model = None
        self.reactor_vars = None
        self.coverage_vars = None
    
    def optimize_placement(self, normal_demand, disaster_demand, num_reactors, 
                          reactor_radius, reactor_capacity, objective_type="minimize uncovered demand"):
        """
        Optimize microreactor placement using Gurobi
        
        Args:
            normal_demand: Normal demand map (2D array)
            disaster_demand: Post-disaster demand map (2D array)
            num_reactors: Maximum number of reactors to place
            reactor_radius: Coverage radius of each reactor
            reactor_capacity: Power capacity of each reactor (MW)
            objective_type: Optimization objective
            
        Returns:
            Dictionary with optimization results
        """
        try:
            rows, cols = normal_demand.shape
            
            # Create optimization model
            model = gp.Model("MicroreactorPlacement")
            model.setParam('OutputFlag', 0)  # Suppress output
            model.setParam('TimeLimit', 60)  # 60 second time limit
            
            # Decision variables
            # reactor[i,j] = 1 if reactor is placed at (i,j)
            reactor = model.addVars(rows, cols, vtype=GRB.BINARY, name="reactor")
            
            # coverage[i,j,s] = 1 if demand at (i,j) is covered in scenario s
            # s=0: normal scenario, s=1: disaster scenario
            coverage = model.addVars(rows, cols, 2, vtype=GRB.BINARY, name="coverage")
            
            # Constraints
            
            # 1. Maximum number of reactors
            model.addConstr(reactor.sum() <= num_reactors, "max_reactors")
            
            # 2. Coverage constraints for each scenario
            for scenario in [0, 1]:  # 0=normal, 1=disaster
                demand_map = normal_demand if scenario == 0 else disaster_demand
                
                for i in range(rows):
                    for j in range(cols):
                        if demand_map[i, j] > 0.1:  # Only consider significant demand points
                            # A point is covered if there's at least one reactor within radius
                            # and total capacity is sufficient
                            
                            # Find all reactor positions that can cover this point
                            covering_reactors = []
                            for rx in range(rows):
                                for ry in range(cols):
                                    distance = math.sqrt((i - rx)**2 + (j - ry)**2)
                                    if distance <= reactor_radius:
                                        covering_reactors.append((rx, ry))
                            
                            if covering_reactors:
                                # Coverage constraint: sum of covering reactors >= coverage variable
                                model.addConstr(
                                    gp.quicksum(reactor[rx, ry] for rx, ry in covering_reactors) >= coverage[i, j, scenario],
                                    f"coverage_{i}_{j}_{scenario}"
                                )
            
            # 3. Capacity constraints (simplified - assume adequate capacity if covered)
            # In practice, you might want more sophisticated capacity modeling
            
            # Objective function
            if "minimize uncovered demand" in objective_type.lower():
                # Minimize total uncovered demand across both scenarios
                uncovered_normal = gp.quicksum(
                    normal_demand[i, j] * (1 - coverage[i, j, 0])
                    for i in range(rows) for j in range(cols)
                    if normal_demand[i, j] > 0.1
                )
                uncovered_disaster = gp.quicksum(
                    disaster_demand[i, j] * (1 - coverage[i, j, 1])
                    for i in range(rows) for j in range(cols)
                    if disaster_demand[i, j] > 0.1
                )
                # Weight disaster scenario more heavily
                model.setObjective(uncovered_normal + 2.0 * uncovered_disaster, GRB.MINIMIZE)
                
            elif "maximize coverage" in objective_type.lower():
                # Maximize total coverage
                total_coverage = gp.quicksum(
                    coverage[i, j, s] for i in range(rows) for j in range(cols) for s in [0, 1]
                )
                model.setObjective(total_coverage, GRB.MAXIMIZE)
                
            elif "disaster resilience" in objective_type.lower():
                # Focus on disaster scenario coverage
                disaster_coverage = gp.quicksum(
                    coverage[i, j, 1] for i in range(rows) for j in range(cols)
                )
                model.setObjective(disaster_coverage, GRB.MAXIMIZE)
            
            # Optimize
            model.optimize()
            
            # Extract results
            if model.status == GRB.OPTIMAL:
                # Get reactor locations
                reactor_locations = []
                for i in range(rows):
                    for j in range(cols):
                        if reactor[i, j].X > 0.5:
                            reactor_locations.append((i, j))
                
                # Calculate performance metrics
                metrics = self._calculate_metrics(
                    reactor_locations, normal_demand, disaster_demand, 
                    reactor_radius, reactor_capacity
                )
                
                return {
                    'status': 'optimal',
                    'reactor_locations': reactor_locations,
                    'metrics': metrics,
                    'objective_value': model.objVal
                }
            else:
                return {
                    'status': 'infeasible' if model.status == GRB.INFEASIBLE else 'error',
                    'reactor_locations': [],
                    'metrics': {},
                    'objective_value': None
                }
                
        except Exception as e:
            return {
                'status': f'error: {str(e)}',
                'reactor_locations': [],
                'metrics': {},
                'objective_value': None
            }
    
    def _calculate_metrics(self, reactor_locations, normal_demand, disaster_demand, 
                          reactor_radius, reactor_capacity):
        """Calculate performance metrics for the placement solution"""
        rows, cols = normal_demand.shape
        
        # Calculate coverage for each scenario
        normal_coverage = self._calculate_coverage(
            reactor_locations, normal_demand, reactor_radius
        )
        disaster_coverage = self._calculate_coverage(
            reactor_locations, disaster_demand, reactor_radius
        )
        
        # Calculate redundancy (average number of reactors covering each point)
        redundancy = self._calculate_redundancy(
            reactor_locations, normal_demand, reactor_radius
        )
        
        # Total capacity
        total_capacity = len(reactor_locations) * reactor_capacity
        
        # Coverage efficiency (considering both scenarios)
        coverage_efficiency = (normal_coverage + disaster_coverage) / 2
        
        return {
            'normal_coverage': normal_coverage,
            'disaster_coverage': disaster_coverage,
            'coverage_efficiency': coverage_efficiency,
            'redundancy': redundancy,
            'total_capacity': total_capacity,
            'num_reactors': len(reactor_locations)
        }
    
    def _calculate_coverage(self, reactor_locations, demand_map, reactor_radius):
        """Calculate percentage of demand covered"""
        rows, cols = demand_map.shape
        covered_demand = 0
        total_demand = 0
        
        for i in range(rows):
            for j in range(cols):
                demand = demand_map[i, j]
                if demand > 0.1:  # Only consider significant demand
                    total_demand += demand
                    
                    # Check if this point is covered by any reactor
                    covered = False
                    for rx, ry in reactor_locations:
                        distance = math.sqrt((i - rx)**2 + (j - ry)**2)
                        if distance <= reactor_radius:
                            covered = True
                            break
                    
                    if covered:
                        covered_demand += demand
        
        return (covered_demand / total_demand * 100) if total_demand > 0 else 0
    
    def _calculate_redundancy(self, reactor_locations, demand_map, reactor_radius):
        """Calculate average redundancy factor"""
        rows, cols = demand_map.shape
        total_redundancy = 0
        demand_points = 0
        
        for i in range(rows):
            for j in range(cols):
                if demand_map[i, j] > 0.1:  # Only consider significant demand
                    demand_points += 1
                    
                    # Count how many reactors cover this point
                    covering_reactors = 0
                    for rx, ry in reactor_locations:
                        distance = math.sqrt((i - rx)**2 + (j - ry)**2)
                        if distance <= reactor_radius:
                            covering_reactors += 1
                    
                    total_redundancy += covering_reactors
        
        return total_redundancy / demand_points if demand_points > 0 else 0
    
    def analyze_placement_strategies(self, normal_demand, disaster_demand, num_reactors, 
                                   reactor_radius, reactor_capacity):
        """Compare different placement strategies"""
        strategies = [
            "minimize uncovered demand",
            "maximize coverage", 
            "disaster resilience"
        ]
        
        results = {}
        
        for strategy in strategies:
            result = self.optimize_placement(
                normal_demand, disaster_demand, num_reactors,
                reactor_radius, reactor_capacity, strategy
            )
            results[strategy] = result
        
        return results
