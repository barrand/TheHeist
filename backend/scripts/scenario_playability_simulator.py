"""
Scenario Playability Simulator

Simulates actual gameplay to validate:
- All players have tasks available throughout the game
- No extended dead time (players waiting with nothing to do)
- Workload is distributed across game timeline
- Concurrent task availability for parallelism

Usage:
    from scenario_playability_simulator import PlayabilitySimulator
    sim = PlayabilitySimulator(tasks, roles)
    result = sim.simulate()
    sim.print_report(result)
"""

from typing import Dict, List, Set, Tuple, Optional
from dataclasses import dataclass, field
from collections import defaultdict
import random


@dataclass
class Task:
    """Task representation for simulation"""
    id: str
    role: str
    prerequisites: List[Dict[str, str]]  # [{type: task|outcome|item, id: xxx}]
    type: str
    target_outcomes: List[str] = field(default_factory=list)
    search_items: List[str] = field(default_factory=list)


@dataclass
class PlayerState:
    """Tracks a player's state during simulation"""
    role: str
    completed_tasks: Set[str] = field(default_factory=set)
    available_tasks: List[str] = field(default_factory=list)
    tasks_completed_count: int = 0
    idle_turns: int = 0  # Consecutive turns with no available tasks
    max_idle_streak: int = 0  # Longest idle period
    
    def is_idle(self) -> bool:
        return len(self.available_tasks) == 0
    
    def has_work(self) -> bool:
        return len(self.available_tasks) > 0


@dataclass
class SimulationTurn:
    """State of one simulation turn"""
    turn_number: int
    completed_task_id: str
    completed_by_role: str
    player_states: Dict[str, PlayerState]
    idle_players: List[str]
    active_players: List[str]
    available_task_count: int


@dataclass
class PlayabilityResult:
    """Results from playability simulation"""
    success: bool
    total_turns: int
    turns: List[SimulationTurn] = field(default_factory=list)
    
    # Per-role metrics
    role_task_counts: Dict[str, int] = field(default_factory=dict)
    role_max_idle: Dict[str, int] = field(default_factory=dict)
    role_timeline: Dict[str, List[int]] = field(default_factory=dict)  # role -> [turn_nums when tasks completed]
    
    # Issues found
    issues: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    
    def add_issue(self, message: str):
        """Add a critical issue"""
        self.issues.append(message)
        self.success = False
    
    def add_warning(self, message: str):
        """Add a warning (non-critical)"""
        self.warnings.append(message)


class PlayabilitySimulator:
    """Simulates gameplay to validate scenario playability"""
    
    def __init__(self, tasks: Dict[str, Task], roles: List[str]):
        """
        Initialize simulator
        
        Args:
            tasks: Dict mapping task_id -> Task
            roles: List of role names in this scenario
        """
        self.tasks = tasks
        self.roles = roles
        
        # Group tasks by role
        self.tasks_by_role: Dict[str, List[str]] = defaultdict(list)
        for task_id, task in tasks.items():
            self.tasks_by_role[task.role].append(task_id)
    
    def _check_prerequisites(self, task: Task, player_state: PlayerState, 
                            global_completed: Set[str], 
                            global_outcomes: Set[str],
                            global_items: Set[str]) -> bool:
        """Check if all prerequisites for a task are met"""
        for prereq in task.prerequisites:
            if prereq['type'] == 'task':
                if prereq['id'] not in global_completed:
                    return False
            elif prereq['type'] == 'outcome':
                if prereq['id'] not in global_outcomes:
                    return False
            elif prereq['type'] == 'item':
                if prereq['id'] not in global_items:
                    return False
        return True
    
    def _update_available_tasks(self, players: Dict[str, PlayerState], 
                                global_completed: Set[str],
                                global_outcomes: Set[str],
                                global_items: Set[str]):
        """Update available tasks for all players based on current state"""
        for role, player in players.items():
            player.available_tasks = []
            
            for task_id in self.tasks_by_role[role]:
                if task_id in global_completed:
                    continue  # Already completed
                
                task = self.tasks[task_id]
                if self._check_prerequisites(task, player, global_completed, global_outcomes, global_items):
                    player.available_tasks.append(task_id)
    
    def simulate(self, strategy: str = "round_robin", max_turns: int = 1000) -> PlayabilityResult:
        """
        Simulate gameplay
        
        Args:
            strategy: Task selection strategy:
                - "round_robin": Players take turns
                - "random": Random player selection
                - "greedy": Always pick player with most available tasks
            max_turns: Maximum simulation turns (safety limit)
        
        Returns:
            PlayabilityResult with simulation data
        """
        result = PlayabilityResult(success=True, total_turns=0)
        
        # Initialize player states
        players = {role: PlayerState(role=role) for role in self.roles}
        
        # Global game state
        global_completed: Set[str] = set()
        global_outcomes: Set[str] = set()  # Outcomes achieved from NPCs
        global_items: Set[str] = set()  # Items collected
        
        # Simulation loop
        turn = 0
        consecutive_idle_all = 0
        
        while len(global_completed) < len(self.tasks) and turn < max_turns:
            turn += 1
            
            # Update available tasks for all players
            self._update_available_tasks(players, global_completed, global_outcomes, global_items)
            
            # Check if anyone has work
            active_players = [role for role, p in players.items() if p.has_work()]
            idle_players = [role for role, p in players.items() if p.is_idle()]
            
            if not active_players:
                consecutive_idle_all += 1
                if consecutive_idle_all > 3:
                    result.add_issue(f"Deadlock at turn {turn}: No players have available tasks but {len(self.tasks) - len(global_completed)} tasks remain")
                    break
                continue
            else:
                consecutive_idle_all = 0
            
            # Select a player to complete a task
            if strategy == "round_robin":
                # Pick player with work in round-robin order
                current_player_role = active_players[turn % len(active_players)]
            elif strategy == "random":
                current_player_role = random.choice(active_players)
            elif strategy == "greedy":
                # Pick player with most tasks available
                current_player_role = max(active_players, key=lambda r: len(players[r].available_tasks))
            else:
                current_player_role = active_players[0]
            
            current_player = players[current_player_role]
            
            # Pick a task for this player to complete
            task_id = current_player.available_tasks[0]  # Could be randomized
            task = self.tasks[task_id]
            
            # Complete the task
            global_completed.add(task_id)
            current_player.completed_tasks.add(task_id)
            current_player.tasks_completed_count += 1
            current_player.idle_turns = 0
            
            # Simulate outcomes/items from task completion
            if task.type == 'npc_llm':
                # Add the real outcome IDs this task unlocks
                for outcome_id in getattr(task, 'target_outcomes', []):
                    global_outcomes.add(outcome_id)
            if task.type == 'search':
                # Add items discovered by this search task
                for item_id in getattr(task, 'search_items', []):
                    global_items.add(item_id)
            
            # Track idle turns for other players
            for role, player in players.items():
                if role != current_player_role and player.is_idle():
                    player.idle_turns += 1
                    player.max_idle_streak = max(player.max_idle_streak, player.idle_turns)
            
            # Record turn
            turn_data = SimulationTurn(
                turn_number=turn,
                completed_task_id=task_id,
                completed_by_role=current_player_role,
                player_states={r: PlayerState(
                    role=p.role,
                    completed_tasks=p.completed_tasks.copy(),
                    available_tasks=p.available_tasks.copy(),
                    tasks_completed_count=p.tasks_completed_count,
                    idle_turns=p.idle_turns,
                    max_idle_streak=p.max_idle_streak
                ) for r, p in players.items()},
                idle_players=idle_players.copy(),
                active_players=active_players.copy(),
                available_task_count=sum(len(p.available_tasks) for p in players.values())
            )
            result.turns.append(turn_data)
        
        result.total_turns = turn
        
        # Build role metrics
        for role, player in players.items():
            result.role_task_counts[role] = player.tasks_completed_count
            result.role_max_idle[role] = player.max_idle_streak
            
            # Build timeline (which turns each role completed tasks)
            timeline = []
            for turn_data in result.turns:
                if turn_data.completed_by_role == role:
                    timeline.append(turn_data.turn_number)
            result.role_timeline[role] = timeline
        
        # Validate results against rules
        self._validate_results(result, players)
        
        return result
    
    def _validate_results(self, result: PlayabilityResult, players: Dict[str, PlayerState]):
        """Validate simulation results against playability rules"""
        
        # Rule 19: Early game engagement (all roles have ≥1 task in first 3 turns)
        for role, timeline in result.role_timeline.items():
            if not timeline:
                result.add_issue(f"Rule 19: {role} has NO tasks (cannot participate)")
            elif timeline[0] > 3:
                result.add_warning(f"Rule 19: {role}'s first task is at turn {timeline[0]} (should be within first 3)")
        
        # Rule 20: No extended dead time (>3 consecutive turns idle)
        for role, max_idle in result.role_max_idle.items():
            if max_idle > 3:
                result.add_warning(f"Rule 20: {role} had {max_idle} consecutive idle turns (max 3 recommended)")
        
        # Rule 21: Distributed workload (check if >50% of tasks are in final 25%)
        for role, timeline in result.role_timeline.items():
            if not timeline:
                continue
            
            total_tasks = len(timeline)
            final_quarter_start = int(result.total_turns * 0.75)
            tasks_in_final_quarter = sum(1 for t in timeline if t >= final_quarter_start)
            
            if tasks_in_final_quarter > total_tasks * 0.5:
                pct = (tasks_in_final_quarter / total_tasks) * 100
                result.add_warning(f"Rule 21: {role} has {pct:.0f}% of tasks in final 25% of game (uneven pacing)")
        
        # Rule 22: Concurrent task availability (≥50% of turns should have tasks for ≥50% of players)
        active_player_counts = [len(turn.active_players) for turn in result.turns]
        turns_with_good_concurrency = sum(1 for count in active_player_counts if count >= len(self.roles) * 0.5)
        concurrency_pct = (turns_with_good_concurrency / len(result.turns)) * 100 if result.turns else 0
        
        if concurrency_pct < 50:
            result.add_warning(f"Rule 22: Only {concurrency_pct:.0f}% of turns had ≥50% of players with available tasks (target: ≥50%)")
    
    def print_report(self, result: PlayabilityResult):
        """Print formatted playability report"""
        print("\n" + "="*80)
        print("PLAYABILITY SIMULATION REPORT")
        print("="*80)
        
        status = "✅ PLAYABLE" if result.success and not result.issues else "❌ NOT PLAYABLE"
        print(f"\n{status}")
        print(f"Total turns: {result.total_turns}")
        print(f"Issues: {len(result.issues)}")
        print(f"Warnings: {len(result.warnings)}")
        
        # Per-role summary
        print(f"\n📊 Per-Role Summary:")
        print(f"{'Role':<20} {'Tasks':<10} {'Max Idle':<12} {'Timeline'}")
        print("-" * 80)
        for role in self.roles:
            task_count = result.role_task_counts.get(role, 0)
            max_idle = result.role_max_idle.get(role, 0)
            timeline = result.role_timeline.get(role, [])
            timeline_str = ', '.join(map(str, timeline[:10]))
            if len(timeline) > 10:
                timeline_str += f", ... ({len(timeline)} total)"
            
            print(f"{role:<20} {task_count:<10} {max_idle:<12} {timeline_str}")
        
        # Issues
        if result.issues:
            print(f"\n❌ CRITICAL ISSUES ({len(result.issues)}):")
            for i, issue in enumerate(result.issues, 1):
                print(f"  {i}. {issue}")
        
        # Warnings
        if result.warnings:
            print(f"\n⚠️  WARNINGS ({len(result.warnings)}):")
            for i, warning in enumerate(result.warnings, 1):
                print(f"  {i}. {warning}")
        
        # Concurrency analysis
        if result.turns:
            avg_active = sum(len(t.active_players) for t in result.turns) / len(result.turns)
            print(f"\n⚡ Concurrency:")
            print(f"  Average players with available tasks: {avg_active:.1f} / {len(self.roles)}")
            
            # Show bottleneck turns (only 1 player active)
            bottlenecks = [t for t in result.turns if len(t.active_players) == 1]
            if bottlenecks:
                print(f"  Bottleneck turns (only 1 player active): {len(bottlenecks)}")
        
        print("\n" + "="*80 + "\n")


def main():
    """Example usage"""
    # Example tasks
    example_tasks = {
        "MM1": Task("MM1", "mastermind", [], "npc_llm"),
        "MM2": Task("MM2", "mastermind", [{"type": "task", "id": "MM1"}], "search"),
        "SC1": Task("SC1", "safe_cracker", [], "search"),
        "SC2": Task("SC2", "safe_cracker", [{"type": "task", "id": "MM2"}, {"type": "task", "id": "SC1"}], "minigame"),
        "H1": Task("H1", "hacker", [], "minigame"),
        "H2": Task("H2", "hacker", [{"type": "task", "id": "SC2"}, {"type": "task", "id": "H1"}], "minigame"),
    }
    
    roles = ["mastermind", "safe_cracker", "hacker"]
    
    sim = PlayabilitySimulator(example_tasks, roles)
    result = sim.simulate(strategy="round_robin")
    sim.print_report(result)


if __name__ == '__main__':
    main()
