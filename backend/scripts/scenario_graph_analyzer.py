"""
Scenario Graph Analyzer

Analyzes dependency graphs in scenarios for:
- Circular dependencies (cycles)
- Orphaned tasks (unreachable)
- Dead-end tasks (don't lead to completion)
- Critical path analysis
- Parallel task opportunities

Usage:
    from scenario_graph_analyzer import ScenarioGraphAnalyzer
    analyzer = ScenarioGraphAnalyzer(tasks)
    cycles = analyzer.find_cycles()
    orphans = analyzer.find_orphaned_tasks()
"""

from typing import Dict, List, Set, Tuple, Optional
from dataclasses import dataclass
from collections import defaultdict, deque


@dataclass
class Task:
    """Simplified task representation for graph analysis"""
    id: str
    prerequisites: List[Dict[str, str]]  # [{type: task|outcome|item, id: xxx}]
    type: str  # minigame, npc_llm, search, etc.


@dataclass
class GraphAnalysisResult:
    """Results from graph analysis"""
    cycles: List[List[str]] = None  # List of cycles (each cycle is a list of task IDs)
    orphaned_tasks: List[str] = None  # Tasks with no path from start
    dead_end_tasks: List[str] = None  # Tasks that don't lead to anything
    critical_path: List[str] = None  # Longest path through the graph
    start_tasks: List[str] = None  # Tasks with no prerequisites
    
    def __post_init__(self):
        if self.cycles is None:
            self.cycles = []
        if self.orphaned_tasks is None:
            self.orphaned_tasks = []
        if self.dead_end_tasks is None:
            self.dead_end_tasks = []
        if self.critical_path is None:
            self.critical_path = []
        if self.start_tasks is None:
            self.start_tasks = []


class ScenarioGraphAnalyzer:
    """Analyzes scenario dependency graphs"""
    
    def __init__(self, tasks: Dict[str, Task]):
        """
        Initialize with parsed tasks
        
        Args:
            tasks: Dict mapping task_id -> Task object
        """
        self.tasks = tasks
        
        # Build adjacency lists
        self.dependencies: Dict[str, Set[str]] = defaultdict(set)  # task_id -> set of prerequisite task IDs
        self.dependents: Dict[str, Set[str]] = defaultdict(set)  # task_id -> set of tasks that depend on it
        
        self._build_graph()
    
    def _build_graph(self):
        """Build dependency and dependent adjacency lists from tasks"""
        for task_id, task in self.tasks.items():
            for prereq in task.prerequisites:
                if prereq['type'] == 'task':
                    prereq_id = prereq['id']
                    self.dependencies[task_id].add(prereq_id)
                    self.dependents[prereq_id].add(task_id)
    
    def find_start_tasks(self) -> List[str]:
        """Find tasks with no prerequisites (starting points)"""
        return [
            task_id for task_id, task in self.tasks.items()
            if len([p for p in task.prerequisites if p['type'] == 'task']) == 0
        ]
    
    def find_cycles(self) -> List[List[str]]:
        """
        Find all cycles in the dependency graph using DFS
        
        Returns:
            List of cycles, where each cycle is a list of task IDs
        """
        cycles = []
        visited = set()
        rec_stack = set()
        path = []
        
        def dfs(node: str) -> bool:
            """DFS to detect cycles. Returns True if cycle found."""
            visited.add(node)
            rec_stack.add(node)
            path.append(node)
            
            # Visit all dependencies (nodes this task depends on)
            for prereq in self.dependencies.get(node, []):
                if prereq not in visited:
                    if dfs(prereq):
                        return True
                elif prereq in rec_stack:
                    # Found a cycle!
                    cycle_start = path.index(prereq)
                    cycle = path[cycle_start:] + [prereq]
                    cycles.append(cycle)
                    return True
            
            path.pop()
            rec_stack.remove(node)
            return False
        
        # Run DFS from each unvisited node
        for task_id in self.tasks.keys():
            if task_id not in visited:
                dfs(task_id)
        
        return cycles
    
    def find_orphaned_tasks(self) -> List[str]:
        """
        Find tasks that are unreachable from any start task
        
        Returns:
            List of orphaned task IDs
        """
        start_tasks = self.find_start_tasks()
        if not start_tasks:
            # If no start tasks, all tasks are orphaned (or there's a cycle of all tasks)
            return list(self.tasks.keys())
        
        # BFS from all start tasks
        reachable = set()
        queue = deque(start_tasks)
        reachable.update(start_tasks)
        
        while queue:
            current = queue.popleft()
            
            # Visit all dependents (tasks that depend on current task)
            for dependent in self.dependents.get(current, []):
                if dependent not in reachable:
                    reachable.add(dependent)
                    queue.append(dependent)
        
        # Orphaned tasks are those not reachable
        orphaned = [task_id for task_id in self.tasks.keys() if task_id not in reachable]
        return orphaned
    
    def find_dead_end_tasks(self, exclude_optional: bool = True) -> List[str]:
        """
        Find tasks that don't contribute to unlocking other tasks
        
        Args:
            exclude_optional: If True, don't flag tasks that are clearly optional (flavor)
        
        Returns:
            List of dead-end task IDs
        """
        dead_ends = []
        
        for task_id in self.tasks.keys():
            # A task is a dead-end if no other task depends on it
            if len(self.dependents.get(task_id, [])) == 0:
                dead_ends.append(task_id)
        
        return dead_ends
    
    def find_critical_path(self) -> Tuple[List[str], int]:
        """
        Find the longest path through the dependency graph (critical path)
        
        Uses dynamic programming with memoization.
        
        Returns:
            Tuple of (path as list of task IDs, path length)
        """
        memo = {}
        
        def longest_path_from(node: str) -> Tuple[List[str], int]:
            """Find longest path starting from this node"""
            if node in memo:
                return memo[node]
            
            # Base case: no dependents, path is just this node
            if len(self.dependents.get(node, [])) == 0:
                result = ([node], 1)
                memo[node] = result
                return result
            
            # Recursive case: try all dependents, take the longest
            max_path = []
            max_length = 0
            
            for dependent in self.dependents.get(node, []):
                sub_path, sub_length = longest_path_from(dependent)
                if sub_length > max_length:
                    max_length = sub_length
                    max_path = sub_path
            
            result = ([node] + max_path, max_length + 1)
            memo[node] = result
            return result
        
        # Try starting from each start task
        start_tasks = self.find_start_tasks()
        if not start_tasks:
            return ([], 0)
        
        max_path = []
        max_length = 0
        
        for start_task in start_tasks:
            path, length = longest_path_from(start_task)
            if length > max_length:
                max_length = length
                max_path = path
        
        return (max_path, max_length)
    
    def analyze_all(self) -> GraphAnalysisResult:
        """
        Run all graph analyses
        
        Returns:
            GraphAnalysisResult with all findings
        """
        result = GraphAnalysisResult()
        
        result.start_tasks = self.find_start_tasks()
        result.cycles = self.find_cycles()
        result.orphaned_tasks = self.find_orphaned_tasks()
        result.dead_end_tasks = self.find_dead_end_tasks()
        result.critical_path, _ = self.find_critical_path()
        
        return result
    
    def get_parallel_opportunities(self) -> List[Set[str]]:
        """
        Identify sets of tasks that can be done in parallel
        (same depth in dependency tree, no interdependencies)
        
        Returns:
            List of sets, where each set contains task IDs that can be done in parallel
        """
        # Calculate depth of each task (distance from start)
        depths = {}
        start_tasks = self.find_start_tasks()
        
        queue = deque([(task_id, 0) for task_id in start_tasks])
        while queue:
            task_id, depth = queue.popleft()
            
            if task_id not in depths or depth < depths[task_id]:
                depths[task_id] = depth
                
                for dependent in self.dependents.get(task_id, []):
                    queue.append((dependent, depth + 1))
        
        # Group by depth
        by_depth = defaultdict(set)
        for task_id, depth in depths.items():
            by_depth[depth].add(task_id)
        
        # Return groups that have 2+ tasks (parallel opportunities)
        parallel_groups = [tasks for tasks in by_depth.values() if len(tasks) >= 2]
        return parallel_groups
    
    def get_task_depth(self, task_id: str) -> int:
        """
        Get the minimum depth of a task in the dependency tree
        (how many tasks must be completed before this one is available)
        
        Returns:
            Depth (0 for start tasks, -1 if unreachable)
        """
        start_tasks = self.find_start_tasks()
        if task_id in start_tasks:
            return 0
        
        # BFS to find shortest path
        queue = deque([(start, 0) for start in start_tasks])
        visited = set(start_tasks)
        
        while queue:
            current, depth = queue.popleft()
            
            for dependent in self.dependents.get(current, []):
                if dependent == task_id:
                    return depth + 1
                
                if dependent not in visited:
                    visited.add(dependent)
                    queue.append((dependent, depth + 1))
        
        return -1  # Unreachable
    
    def print_analysis(self, result: GraphAnalysisResult):
        """Print formatted analysis results"""
        print("\n" + "="*80)
        print("DEPENDENCY GRAPH ANALYSIS")
        print("="*80)
        
        print(f"\n📊 Overview:")
        print(f"  Total tasks: {len(self.tasks)}")
        print(f"  Start tasks: {len(result.start_tasks)}")
        print(f"  Critical path length: {len(result.critical_path)}")
        
        if result.start_tasks:
            print(f"\n🚀 Start Tasks ({len(result.start_tasks)}):")
            for task_id in result.start_tasks:
                print(f"  • {task_id}")
        
        if result.cycles:
            print(f"\n🔄 CYCLES DETECTED ({len(result.cycles)}):")
            for i, cycle in enumerate(result.cycles, 1):
                print(f"  {i}. {' → '.join(cycle)}")
            print(f"  ⚠️  These circular dependencies make tasks impossible to complete!")
        else:
            print(f"\n✅ No cycles detected")
        
        if result.orphaned_tasks:
            print(f"\n🏝️  ORPHANED TASKS ({len(result.orphaned_tasks)}):")
            for task_id in result.orphaned_tasks:
                print(f"  • {task_id} (unreachable from start)")
            print(f"  ⚠️  These tasks can never be unlocked!")
        else:
            print(f"\n✅ No orphaned tasks")
        
        if result.dead_end_tasks:
            print(f"\n🚫 DEAD-END TASKS ({len(result.dead_end_tasks)}):")
            for task_id in result.dead_end_tasks:
                print(f"  • {task_id} (doesn't unlock anything)")
            print(f"  ℹ️  These tasks don't contribute to unlocking other tasks")
        
        if result.critical_path:
            print(f"\n🎯 Critical Path ({len(result.critical_path)} tasks):")
            print(f"  {' → '.join(result.critical_path)}")
        
        # Parallel opportunities
        parallel = self.get_parallel_opportunities()
        if parallel:
            print(f"\n⚡ Parallel Opportunities ({len(parallel)} groups):")
            for i, group in enumerate(parallel, 1):
                if len(group) >= 3:  # Only show significant parallel groups
                    print(f"  {i}. {len(group)} tasks can be done in parallel: {', '.join(sorted(group))}")
        
        print("\n" + "="*80 + "\n")


def main():
    """Example usage"""
    # Example tasks for testing
    example_tasks = {
        "MM1": Task("MM1", [], "npc_llm"),
        "MM2": Task("MM2", [], "search"),
        "MM3": Task("MM3", [{"type": "task", "id": "MM1"}, {"type": "task", "id": "MM2"}], "info"),
        "SC1": Task("SC1", [], "search"),
        "SC2": Task("SC2", [{"type": "task", "id": "MM3"}, {"type": "task", "id": "SC1"}], "minigame"),
        "H1": Task("H1", [{"type": "task", "id": "SC2"}], "minigame"),
    }
    
    analyzer = ScenarioGraphAnalyzer(example_tasks)
    result = analyzer.analyze_all()
    analyzer.print_analysis(result)


if __name__ == '__main__':
    main()
