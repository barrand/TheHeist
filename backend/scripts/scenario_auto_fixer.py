"""
Scenario Auto-Fixer

Provides automatic fix suggestions for common scenario issues.
Can generate:
- Suggested prerequisite removals to fix cycles
- Suggested prerequisite additions to connect orphaned tasks
- Task redistribution suggestions for balance
- Parallel task suggestions

Note: This tool suggests fixes but does NOT automatically modify files.
Human review is required before applying changes.

Usage:
    from scenario_auto_fixer import AutoFixer
    fixer = AutoFixer(tasks, graph_analysis, playability_result)
    suggestions = fixer.generate_fixes()
"""

from typing import Dict, List, Set, Tuple, Optional
from dataclasses import dataclass, field
from collections import defaultdict


@dataclass
class Fix:
    """A suggested fix"""
    type: str  # cycle_fix, orphan_fix, balance_fix, etc.
    severity: str  # critical, important, advisory
    description: str
    action: str  # Human-readable action
    details: Dict = field(default_factory=dict)  # Machine-readable details
    
    def to_string(self) -> str:
        """Format fix as readable string"""
        return f"[{self.severity.upper()}] {self.type}: {self.description}\n  Action: {self.action}"


@dataclass
class FixSuggestions:
    """Collection of all fix suggestions"""
    critical_fixes: List[Fix] = field(default_factory=list)
    important_fixes: List[Fix] = field(default_factory=list)
    advisory_fixes: List[Fix] = field(default_factory=list)
    
    def add_fix(self, fix: Fix):
        """Add a fix to appropriate list"""
        if fix.severity == "critical":
            self.critical_fixes.append(fix)
        elif fix.severity == "important":
            self.important_fixes.append(fix)
        else:
            self.advisory_fixes.append(fix)
    
    def get_all_fixes(self) -> List[Fix]:
        """Get all fixes in priority order"""
        return self.critical_fixes + self.important_fixes + self.advisory_fixes
    
    def print_suggestions(self):
        """Print all fix suggestions"""
        print("\n" + "="*80)
        print("AUTO-FIX SUGGESTIONS")
        print("="*80)
        
        total = len(self.critical_fixes) + len(self.important_fixes) + len(self.advisory_fixes)
        print(f"\nTotal suggestions: {total}")
        print(f"  Critical: {len(self.critical_fixes)}")
        print(f"  Important: {len(self.important_fixes)}")
        print(f"  Advisory: {len(self.advisory_fixes)}")
        
        if self.critical_fixes:
            print(f"\n🚨 CRITICAL FIXES ({len(self.critical_fixes)}):")
            print("-" * 80)
            for i, fix in enumerate(self.critical_fixes, 1):
                print(f"\n{i}. {fix.description}")
                print(f"   💡 {fix.action}")
        
        if self.important_fixes:
            print(f"\n⚠️  IMPORTANT FIXES ({len(self.important_fixes)}):")
            print("-" * 80)
            for i, fix in enumerate(self.important_fixes, 1):
                print(f"\n{i}. {fix.description}")
                print(f"   💡 {fix.action}")
        
        if self.advisory_fixes:
            print(f"\n💭 ADVISORY SUGGESTIONS ({len(self.advisory_fixes)}):")
            print("-" * 80)
            for i, fix in enumerate(self.advisory_fixes, 1):
                print(f"\n{i}. {fix.description}")
                print(f"   💡 {fix.action}")
        
        print("\n" + "="*80)
        print("\n⚠️  IMPORTANT: These are SUGGESTIONS only. Human review required.")
        print("Review each suggestion and manually apply appropriate fixes.\n")


class AutoFixer:
    """Generates automatic fix suggestions for scenario issues"""
    
    def __init__(self, tasks: Dict, graph_analysis=None, playability_result=None):
        """
        Initialize auto-fixer
        
        Args:
            tasks: Dict mapping task_id -> Task
            graph_analysis: Optional GraphAnalysisResult from graph analyzer
            playability_result: Optional PlayabilityResult from simulator
        """
        self.tasks = tasks
        self.graph_analysis = graph_analysis
        self.playability_result = playability_result
        self.suggestions = FixSuggestions()
    
    def generate_fixes(self) -> FixSuggestions:
        """Generate all fix suggestions"""
        if self.graph_analysis:
            self._fix_cycles()
            self._fix_orphaned_tasks()
            self._fix_dead_ends()
        
        if self.playability_result:
            self._fix_early_engagement()
            self._fix_dead_time()
            self._fix_workload_distribution()
        
        return self.suggestions
    
    def _fix_cycles(self):
        """Suggest fixes for circular dependencies"""
        if not self.graph_analysis or not self.graph_analysis.cycles:
            return
        
        for i, cycle in enumerate(self.graph_analysis.cycles, 1):
            # Suggest breaking the weakest link
            # Heuristic: break dependency between last and first task (simplest)
            task_a = cycle[-1]
            task_b = cycle[0]
            
            fix = Fix(
                type="cycle_fix",
                severity="critical",
                description=f"Circular dependency detected: {' → '.join(cycle)}",
                action=f"Remove prerequisite: Task {task_b} should NOT depend on {task_a}",
                details={
                    "cycle": cycle,
                    "suggested_removal": {"from_task": task_b, "remove_prereq": task_a}
                }
            )
            self.suggestions.add_fix(fix)
    
    def _fix_orphaned_tasks(self):
        """Suggest fixes for unreachable tasks"""
        if not self.graph_analysis or not self.graph_analysis.orphaned_tasks:
            return
        
        start_tasks = self.graph_analysis.start_tasks
        
        for orphan_id in self.graph_analysis.orphaned_tasks:
            orphan = self.tasks[orphan_id]
            
            # Suggest either:
            # 1. Remove all prerequisites (make it a start task)
            # 2. Add a prerequisite from an existing reachable task
            
            if orphan.prerequisites:
                # Has prerequisites but unreachable - suggest removing them
                fix = Fix(
                    type="orphan_fix",
                    severity="critical",
                    description=f"Task {orphan_id} is unreachable (orphaned)",
                    action=f"Option 1: Remove all prerequisites to make it a starting task. Option 2: Connect it to an existing task in the main flow.",
                    details={
                        "task_id": orphan_id,
                        "current_prereqs": orphan.prerequisites
                    }
                )
            else:
                # No prerequisites but still orphaned? Shouldn't happen
                fix = Fix(
                    type="orphan_fix",
                    severity="critical",
                    description=f"Task {orphan_id} is unreachable (should be a start task but isn't)",
                    action=f"Verify task definition - this shouldn't happen",
                    details={"task_id": orphan_id}
                )
            
            self.suggestions.add_fix(fix)
    
    def _fix_dead_ends(self):
        """Suggest making dead-end tasks contribute to the heist"""
        if not self.graph_analysis or not self.graph_analysis.dead_end_tasks:
            return
        
        # Only flag non-optional dead ends
        for dead_end_id in self.graph_analysis.dead_end_tasks:
            dead_end = self.tasks[dead_end_id]
            
            # Skip if it looks like an optional/flavor task (search, info_share)
            if dead_end.type in ['search', 'info']:
                continue
            
            fix = Fix(
                type="dead_end_fix",
                severity="advisory",
                description=f"Task {dead_end_id} doesn't unlock any other tasks (dead end)",
                action=f"Consider making another task depend on {dead_end_id}, or mark it as optional",
                details={"task_id": dead_end_id, "task_type": dead_end.type}
            )
            self.suggestions.add_fix(fix)
    
    def _fix_early_engagement(self):
        """Suggest fixes for roles that start late"""
        if not self.playability_result or not self.playability_result.role_timeline:
            return
        
        for role, timeline in self.playability_result.role_timeline.items():
            if not timeline:
                # No tasks at all
                fix = Fix(
                    type="engagement_fix",
                    severity="critical",
                    description=f"Role {role} has NO tasks assigned",
                    action=f"Add 3-5 tasks for {role} role",
                    details={"role": role}
                )
                self.suggestions.add_fix(fix)
            elif timeline[0] > 3:
                # First task too late
                task_ids = [tid for tid, t in self.tasks.items() if t.role == role]
                
                fix = Fix(
                    type="engagement_fix",
                    severity="important",
                    description=f"Role {role} doesn't get first task until turn {timeline[0]}",
                    action=f"Remove prerequisites from one of {role}'s early tasks to enable earlier start: {', '.join(task_ids[:3])}",
                    details={"role": role, "first_turn": timeline[0], "early_tasks": task_ids[:3]}
                )
                self.suggestions.add_fix(fix)
    
    def _fix_dead_time(self):
        """Suggest fixes for extended idle periods"""
        if not self.playability_result or not self.playability_result.role_max_idle:
            return
        
        for role, max_idle in self.playability_result.role_max_idle.items():
            if max_idle > 3:
                # Suggest adding parallel tasks
                fix = Fix(
                    type="dead_time_fix",
                    severity="important",
                    description=f"Role {role} has {max_idle} consecutive idle turns",
                    action=f"Add parallel tasks for {role} or reduce prerequisites on existing tasks to reduce wait time",
                    details={"role": role, "max_idle_turns": max_idle}
                )
                self.suggestions.add_fix(fix)
    
    def _fix_workload_distribution(self):
        """Suggest fixes for uneven task distribution across timeline"""
        if not self.playability_result or not self.playability_result.role_timeline:
            return
        
        total_turns = self.playability_result.total_turns
        if total_turns == 0:
            return
        
        for role, timeline in self.playability_result.role_timeline.items():
            if not timeline or len(timeline) < 3:
                continue
            
            # Check if >50% of tasks are in final 25%
            final_quarter_start = int(total_turns * 0.75)
            tasks_in_final = sum(1 for t in timeline if t >= final_quarter_start)
            total_tasks = len(timeline)
            
            if tasks_in_final > total_tasks * 0.5:
                pct = (tasks_in_final / total_tasks) * 100
                
                fix = Fix(
                    type="workload_fix",
                    severity="important",
                    description=f"Role {role} has {pct:.0f}% of tasks concentrated in final 25% of game",
                    action=f"Redistribute {role}'s task prerequisites to spread them across early, mid, and late game",
                    details={"role": role, "late_task_pct": pct}
                )
                self.suggestions.add_fix(fix)


def main():
    """Example usage"""
    from scenario_graph_analyzer import Task as GraphTask, ScenarioGraphAnalyzer
    from scenario_playability_simulator import Task as SimTask, PlayabilitySimulator
    
    # Example with issues
    tasks_graph = {
        "MM1": GraphTask("MM1", [], "npc_llm"),
        "MM2": GraphTask("MM2", [{"type": "task", "id": "MM1"}], "search"),
        "MM3": GraphTask("MM3", [{"type": "task", "id": "SC2"}], "info"),  # Orphaned (depends on non-existent SC2)
        "SC1": GraphTask("SC1", [], "search"),
        "SC2": GraphTask("SC2", [{"type": "task", "id": "MM2"}], "minigame"),
    }
    
    tasks_sim = {
        "MM1": SimTask("MM1", "mastermind", [], "npc_llm"),
        "MM2": SimTask("MM2", "mastermind", [{"type": "task", "id": "MM1"}], "search"),
        "MM3": SimTask("MM3", "mastermind", [{"type": "task", "id": "SC2"}], "info"),
        "SC1": SimTask("SC1", "safe_cracker", [], "search"),
        "SC2": SimTask("SC2", "safe_cracker", [{"type": "task", "id": "MM2"}], "minigame"),
    }
    
    # Run analyses
    graph_analyzer = ScenarioGraphAnalyzer(tasks_graph)
    graph_result = graph_analyzer.analyze_all()
    
    sim = PlayabilitySimulator(tasks_sim, ["mastermind", "safe_cracker", "hacker"])
    play_result = sim.simulate()
    
    # Generate fixes
    fixer = AutoFixer(tasks_graph, graph_result, play_result)
    suggestions = fixer.generate_fixes()
    suggestions.print_suggestions()


if __name__ == '__main__':
    main()
