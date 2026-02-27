"""
Graph Validator
Fast structural validation for scenario graphs (no auto-fixing)
"""

from dataclasses import dataclass
from typing import List, Set, Dict, Optional
from collections import deque


@dataclass
class ValidationError:
    """A validation error in the graph"""
    rule: str
    severity: str  # "critical", "error", "warning"
    message: str
    details: List[str] = None
    
    def __post_init__(self):
        if self.details is None:
            self.details = []


@dataclass
class ValidationResult:
    """Result of graph validation"""
    valid: bool
    errors: List[ValidationError]
    
    def __str__(self):
        if self.valid:
            return "✅ Graph is valid"
        
        lines = ["❌ Graph validation failed:\n"]
        for error in self.errors:
            lines.append(f"  [{error.severity.upper()}] {error.rule}: {error.message}")
            for detail in error.details:
                lines.append(f"    - {detail}")
        return "\n".join(lines)


class GraphValidator:
    """Validates scenario graph structure and playability"""
    
    def __init__(self, graph):
        self.graph = graph
        self.errors: List[ValidationError] = []
    
    def validate(self) -> ValidationResult:
        """Run all validation checks"""
        
        self.errors = []
        
        # Structural checks
        self._check_location_references()
        self._check_npc_references()
        self._check_outcome_references()
        self._check_item_references()
        self._check_prerequisite_references()
        
        # Graph integrity checks
        self._check_starting_tasks()
        self._check_reachability()
        self._check_circular_dependencies()
        
        # Balance checks
        self._check_task_balance()
        self._check_hidden_items()
        
        return ValidationResult(
            valid=len(self.errors) == 0,
            errors=self.errors
        )
    
    def _check_location_references(self):
        """Rule 1: All location references are valid"""
        location_ids = {loc.id for loc in self.graph.locations}
        invalid_refs = []
        
        # Check tasks
        for task in self.graph.tasks:
            if task.location not in location_ids:
                invalid_refs.append(f"Task {task.id} references invalid location: {task.location}")
        
        # Check items
        for item in self.graph.items:
            if item.location and item.location not in location_ids:
                invalid_refs.append(f"Item {item.id} references invalid location: {item.location}")
        
        # Check NPCs
        for npc in self.graph.npcs:
            if npc.location not in location_ids:
                invalid_refs.append(f"NPC {npc.id} references invalid location: {npc.location}")
        
        if invalid_refs:
            self.errors.append(ValidationError(
                rule="location_references",
                severity="critical",
                message="Invalid location references found",
                details=invalid_refs
            ))
    
    def _check_npc_references(self):
        """Rule 2: All NPC references are valid"""
        npc_ids = {npc.id for npc in self.graph.npcs}
        invalid_refs = []
        
        for task in self.graph.tasks:
            if task.type == "npc_llm" and task.npc_id:
                if task.npc_id not in npc_ids:
                    invalid_refs.append(f"Task {task.id} references invalid NPC: {task.npc_id}")
        
        if invalid_refs:
            self.errors.append(ValidationError(
                rule="npc_references",
                severity="critical",
                message="Invalid NPC references found",
                details=invalid_refs
            ))
    
    def _check_outcome_references(self):
        """Rule 3: All outcome references exist in NPC definitions"""
        # Build outcome map: outcome_id -> npc_id
        outcome_to_npc = {}
        for npc in self.graph.npcs:
            for info in npc.information_known:
                if info.info_id:
                    outcome_to_npc[info.info_id] = npc.id
            for action in npc.actions_available:
                outcome_to_npc[action.action_id] = npc.id
        
        invalid_refs = []
        
        # Check task target_outcomes
        for task in self.graph.tasks:
            if task.type == "npc_llm":
                for outcome_id in task.target_outcomes:
                    if outcome_id not in outcome_to_npc:
                        invalid_refs.append(
                            f"Task {task.id} targets invalid outcome: {outcome_id}"
                        )
                    elif outcome_to_npc[outcome_id] != task.npc_id:
                        invalid_refs.append(
                            f"Task {task.id} targets outcome {outcome_id} but it belongs to NPC {outcome_to_npc[outcome_id]}, not {task.npc_id}"
                        )
        
        # Check prerequisites
        for task in self.graph.tasks:
            for prereq in task.prerequisites:
                if prereq.type == "outcome" and prereq.id not in outcome_to_npc:
                    invalid_refs.append(
                        f"Task {task.id} has prerequisite for invalid outcome: {prereq.id}"
                    )
        
        if invalid_refs:
            self.errors.append(ValidationError(
                rule="outcome_references",
                severity="critical",
                message="Invalid outcome references found",
                details=invalid_refs
            ))
    
    def _check_item_references(self):
        """Rule 4: All item references are valid"""
        item_ids = {item.id for item in self.graph.items}
        invalid_refs = []
        
        # Check task search_items
        for task in self.graph.tasks:
            if task.type == "search":
                for item_id in task.search_items:
                    if item_id not in item_ids:
                        invalid_refs.append(f"Task {task.id} searches for invalid item: {item_id}")
        
        # Check task handoff_item
        for task in self.graph.tasks:
            if task.type == "handoff" and task.handoff_item:
                if task.handoff_item not in item_ids:
                    invalid_refs.append(f"Task {task.id} hands off invalid item: {task.handoff_item}")
        
        # Check item prerequisites
        for item in self.graph.items:
            for prereq in item.unlock_prerequisites:
                if prereq.type == "item" and prereq.id not in item_ids:
                    invalid_refs.append(f"Item {item.id} has prerequisite for invalid item: {prereq.id}")
        
        if invalid_refs:
            self.errors.append(ValidationError(
                rule="item_references",
                severity="critical",
                message="Invalid item references found",
                details=invalid_refs
            ))
    
    def _check_prerequisite_references(self):
        """Rule 5: All prerequisite references are valid"""
        task_ids = {task.id for task in self.graph.tasks}
        item_ids = {item.id for item in self.graph.items}
        
        # Build outcome set
        outcome_ids = set()
        for npc in self.graph.npcs:
            for info in npc.information_known:
                if info.info_id:
                    outcome_ids.add(info.info_id)
            for action in npc.actions_available:
                outcome_ids.add(action.action_id)
        
        invalid_refs = []
        
        # Check task prerequisites
        for task in self.graph.tasks:
            for prereq in task.prerequisites:
                if prereq.type == "task" and prereq.id not in task_ids:
                    invalid_refs.append(f"Task {task.id} has invalid task prerequisite: {prereq.id}")
                elif prereq.type == "outcome" and prereq.id not in outcome_ids:
                    invalid_refs.append(f"Task {task.id} has invalid outcome prerequisite: {prereq.id}")
                elif prereq.type == "item" and prereq.id not in item_ids:
                    invalid_refs.append(f"Task {task.id} has invalid item prerequisite: {prereq.id}")
        
        # Check item prerequisites
        for item in self.graph.items:
            for prereq in item.unlock_prerequisites:
                if prereq.type == "task" and prereq.id not in task_ids:
                    invalid_refs.append(f"Item {item.id} has invalid task prerequisite: {prereq.id}")
                elif prereq.type == "outcome" and prereq.id not in outcome_ids:
                    invalid_refs.append(f"Item {item.id} has invalid outcome prerequisite: {prereq.id}")
                elif prereq.type == "item" and prereq.id not in item_ids:
                    invalid_refs.append(f"Item {item.id} has invalid item prerequisite: {prereq.id}")
        
        if invalid_refs:
            self.errors.append(ValidationError(
                rule="prerequisite_references",
                severity="critical",
                message="Invalid prerequisite references found",
                details=invalid_refs
            ))
    
    def _check_starting_tasks(self):
        """Rule 6: Each role has at least one starting task"""
        roles = set()
        starting_tasks_by_role = {}
        
        for task in self.graph.tasks:
            roles.add(task.assigned_role)
            if not task.prerequisites:
                if task.assigned_role not in starting_tasks_by_role:
                    starting_tasks_by_role[task.assigned_role] = []
                starting_tasks_by_role[task.assigned_role].append(task.id)
        
        missing_starts = []
        for role in roles:
            if role not in starting_tasks_by_role:
                missing_starts.append(f"Role {role} has no starting tasks")
        
        if missing_starts:
            self.errors.append(ValidationError(
                rule="starting_tasks",
                severity="critical",
                message="Roles without starting tasks",
                details=missing_starts
            ))
    
    def _check_reachability(self):
        """Rule 7: All tasks are reachable from starting tasks"""
        
        # Build dependency graph
        task_map = {task.id: task for task in self.graph.tasks}
        
        # Find starting tasks
        starting_tasks = [task.id for task in self.graph.tasks if not task.prerequisites]
        
        if not starting_tasks:
            self.errors.append(ValidationError(
                rule="reachability",
                severity="critical",
                message="No starting tasks found - graph is unreachable",
                details=[]
            ))
            return
        
        # BFS from starting tasks to find all reachable tasks
        reachable = set(starting_tasks)
        queue = deque(starting_tasks)
        
        # Build reverse dependency map: what each task/outcome/item unlocks
        unlocks: Dict[str, Set[str]] = {}  # prereq_id -> set of task_ids it unlocks
        
        for task in self.graph.tasks:
            for prereq in task.prerequisites:
                key = f"{prereq.type}:{prereq.id}"
                if key not in unlocks:
                    unlocks[key] = set()
                unlocks[key].add(task.id)
        
        # BFS
        while queue:
            current_task_id = queue.popleft()
            
            # This task being completed unlocks other tasks
            task_key = f"task:{current_task_id}"
            if task_key in unlocks:
                for unlocked_task_id in unlocks[task_key]:
                    if unlocked_task_id not in reachable:
                        # Check if all prerequisites are now reachable
                        if self._all_prereqs_reachable(unlocked_task_id, reachable, task_map):
                            reachable.add(unlocked_task_id)
                            queue.append(unlocked_task_id)
            
            # If this is an NPC task, its outcomes unlock other tasks
            task = task_map[current_task_id]
            if task.type == "npc_llm":
                for outcome_id in task.target_outcomes:
                    outcome_key = f"outcome:{outcome_id}"
                    if outcome_key in unlocks:
                        for unlocked_task_id in unlocks[outcome_key]:
                            if unlocked_task_id not in reachable:
                                if self._all_prereqs_reachable(unlocked_task_id, reachable, task_map):
                                    reachable.add(unlocked_task_id)
                                    queue.append(unlocked_task_id)
            
            # If this is a search task, its items unlock other tasks
            if task.type == "search":
                for item_id in task.search_items:
                    item_key = f"item:{item_id}"
                    if item_key in unlocks:
                        for unlocked_task_id in unlocks[item_key]:
                            if unlocked_task_id not in reachable:
                                if self._all_prereqs_reachable(unlocked_task_id, reachable, task_map):
                                    reachable.add(unlocked_task_id)
                                    queue.append(unlocked_task_id)
        
        # Check for unreachable tasks
        all_task_ids = set(task_map.keys())
        unreachable_tasks = all_task_ids - reachable
        
        if unreachable_tasks:
            self.errors.append(ValidationError(
                rule="reachability",
                severity="critical",
                message="Unreachable tasks found (orphaned tasks)",
                details=[f"Task {task_id} cannot be reached from starting tasks" for task_id in unreachable_tasks]
            ))
    
    def _all_prereqs_reachable(
        self,
        task_id: str,
        reachable: Set[str],
        task_map: Dict[str, 'Task']
    ) -> bool:
        """Check if all prerequisites for a task are reachable"""
        task = task_map[task_id]
        
        for prereq in task.prerequisites:
            if prereq.type == "task":
                if prereq.id not in reachable:
                    return False
            elif prereq.type == "outcome":
                # Check if any task providing this outcome is reachable
                found = False
                for other_task in task_map.values():
                    if other_task.type == "npc_llm" and prereq.id in other_task.target_outcomes:
                        if other_task.id in reachable:
                            found = True
                            break
                if not found:
                    return False
            elif prereq.type == "item":
                # Check if any search task providing this item is reachable
                found = False
                for other_task in task_map.values():
                    if other_task.type == "search" and prereq.id in other_task.search_items:
                        if other_task.id in reachable:
                            found = True
                            break
                if not found:
                    return False
        
        return True
    
    def _check_circular_dependencies(self):
        """Rule 8: No circular dependencies"""
        
        task_map = {task.id: task for task in self.graph.tasks}
        
        def has_cycle(task_id: str, visited: Set[str], rec_stack: Set[str]) -> Optional[List[str]]:
            """DFS to detect cycles, returns cycle path if found"""
            visited.add(task_id)
            rec_stack.add(task_id)
            
            task = task_map[task_id]
            
            # Check all task prerequisites
            for prereq in task.prerequisites:
                if prereq.type == "task":
                    next_task_id = prereq.id
                    if next_task_id not in task_map:
                        continue
                    
                    if next_task_id not in visited:
                        cycle = has_cycle(next_task_id, visited, rec_stack)
                        if cycle:
                            return [task_id] + cycle
                    elif next_task_id in rec_stack:
                        return [task_id, next_task_id]
            
            rec_stack.remove(task_id)
            return None
        
        visited = set()
        cycles_found = []
        
        for task_id in task_map.keys():
            if task_id not in visited:
                cycle = has_cycle(task_id, visited, set())
                if cycle:
                    cycles_found.append(" -> ".join(cycle))
        
        if cycles_found:
            self.errors.append(ValidationError(
                rule="circular_dependencies",
                severity="critical",
                message="Circular dependencies detected",
                details=cycles_found
            ))
    
    def _check_task_balance(self):
        """Rule 9: Tasks are reasonably balanced across roles"""
        role_task_counts = {}
        
        for task in self.graph.tasks:
            role = task.assigned_role
            role_task_counts[role] = role_task_counts.get(role, 0) + 1
        
        if not role_task_counts:
            return
        
        avg_tasks = sum(role_task_counts.values()) / len(role_task_counts)
        imbalanced = []
        
        for role, count in role_task_counts.items():
            if count < avg_tasks * 0.5:  # Less than 50% of average
                imbalanced.append(f"Role {role} has only {count} tasks (avg: {avg_tasks:.1f})")
        
        if imbalanced:
            self.errors.append(ValidationError(
                rule="task_balance",
                severity="warning",
                message="Task distribution is imbalanced",
                details=imbalanced
            ))
    
    def _check_hidden_items(self):
        """Rule 10: Hidden items have unlock prerequisites"""
        invalid_items = []
        
        for item in self.graph.items:
            if item.hidden and not item.unlock_prerequisites:
                invalid_items.append(
                    f"Item {item.id} is hidden but has no unlock prerequisites (will be impossible to find)"
                )
        
        if invalid_items:
            self.errors.append(ValidationError(
                rule="hidden_items",
                severity="critical",
                message="Hidden items without unlock prerequisites",
                details=invalid_items
            ))


def validate_graph(graph) -> ValidationResult:
    """Main entry point for graph validation"""
    validator = GraphValidator(graph)
    return validator.validate()
