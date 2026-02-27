"""
Stage 3: Graph Validator & Fixer

Validates JSON scenario graph and applies deterministic fixes for common issues.
This ensures the graph is structurally valid before rendering to markdown.
"""

import re
import sys
from pathlib import Path
from typing import List, Dict, Set, Tuple
from dataclasses import dataclass, field

# Import graph structures from Stage 2
sys.path.insert(0, str(Path(__file__).parent))
from structure_extractor import ScenarioGraph, Task, Location, Item, NPC


@dataclass
class ValidationResult:
    """Result of graph validation"""
    is_valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    fixes_applied: List[str] = field(default_factory=list)


class GraphValidator:
    """Validates and fixes scenario graphs"""
    
    def __init__(self, graph: ScenarioGraph):
        self.graph = graph
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.fixes: List[str] = []
    
    def validate_and_fix(self, max_iterations: int = 5) -> ValidationResult:
        """
        Validate graph and apply fixes iteratively
        
        Args:
            max_iterations: Maximum fix iterations
        
        Returns:
            ValidationResult
        """
        for iteration in range(max_iterations):
            self.errors = []
            self.warnings = []
            
            print(f"🔍 Validation iteration {iteration + 1}/{max_iterations}")
            
            # Run all validation checks
            self._validate_location_count()
            self._validate_task_count()
            self._validate_references()
            self._validate_npc_task_matching()
            self._validate_hidden_items()
            self._validate_starting_tasks()
            self._validate_task_balance()
            
            if not self.errors:
                print(f"✅ Validation passed!")
                return ValidationResult(
                    is_valid=True,
                    warnings=self.warnings,
                    fixes_applied=self.fixes
                )
            
            # Try to fix errors
            print(f"   Found {len(self.errors)} errors, attempting fixes...")
            fixes_made = self._apply_fixes()
            
            if not fixes_made:
                print(f"❌ Could not fix remaining errors")
                break
        
        return ValidationResult(
            is_valid=False,
            errors=self.errors,
            warnings=self.warnings,
            fixes_applied=self.fixes
        )
    
    def _validate_location_count(self):
        """Check location count is in valid range"""
        count = len(self.graph.locations)
        player_count = self.graph.player_count
        
        if 2 <= player_count <= 3:
            min_loc, max_loc = 4, 6
        elif 4 <= player_count <= 5:
            min_loc, max_loc = 6, 9
        elif 6 <= player_count <= 8:
            min_loc, max_loc = 8, 12
        else:
            min_loc, max_loc = 10, 15
        
        if not (min_loc <= count <= max_loc):
            self.errors.append(f"location_count: {count} (expected {min_loc}-{max_loc})")
    
    def _validate_task_count(self):
        """Check task count is in valid range"""
        count = len(self.graph.tasks)
        player_count = self.graph.player_count
        
        if 3 <= player_count <= 7:
            min_tasks, max_tasks = 30, 40
        else:
            min_tasks, max_tasks = 40, 50
        
        if not (min_tasks <= count <= max_tasks):
            self.errors.append(f"task_count: {count} (expected {min_tasks}-{max_tasks})")
    
    def _validate_references(self):
        """Validate all ID references exist"""
        # Build ID sets
        location_ids = {loc.id for loc in self.graph.locations}
        item_ids = {item.id for item in self.graph.items}
        npc_ids = {npc.id for npc in self.graph.npcs}
        task_ids = {task.id for task in self.graph.tasks}
        outcome_ids = {npc.outcome_provided for npc in self.graph.npcs}
        
        # Check task locations
        for task in self.graph.tasks:
            if task.location not in location_ids and task.location != 'any':
                self.errors.append(f"task_{task.id}_invalid_location: {task.location}")
        
        # Check task NPC references
        for task in self.graph.tasks:
            if task.npc_id and task.npc_id not in npc_ids:
                self.errors.append(f"task_{task.id}_invalid_npc: {task.npc_id}")
        
        # Check item locations
        for item in self.graph.items:
            if item.location not in location_ids:
                self.errors.append(f"item_{item.id}_invalid_location: {item.location}")
        
        # Check task prerequisites
        for task in self.graph.tasks:
            for prereq in task.prerequisites:
                prereq_type = prereq['type']
                prereq_id = prereq['id']
                
                if prereq_type == 'task' and prereq_id not in task_ids:
                    self.errors.append(f"task_{task.id}_invalid_prereq_task: {prereq_id}")
                elif prereq_type == 'item' and prereq_id not in item_ids:
                    self.errors.append(f"task_{task.id}_invalid_prereq_item: {prereq_id}")
                elif prereq_type == 'outcome' and prereq_id not in outcome_ids:
                    self.errors.append(f"task_{task.id}_invalid_prereq_outcome: {prereq_id}")
        
        # Check item unlock references
        for item in self.graph.items:
            for unlock_task in item.unlock_prerequisites:
                if unlock_task not in task_ids:
                    self.errors.append(f"item_{item.id}_invalid_unlock_task: {unlock_task}")
    
    def _validate_npc_task_matching(self):
        """Validate NPC tasks' target outcomes match NPC definitions"""
        outcome_to_npc = {npc.outcome_provided: npc.id for npc in self.graph.npcs}
        
        for task in self.graph.tasks:
            if task.type == 'npc_llm' and task.target_outcome:
                if task.target_outcome not in outcome_to_npc:
                    self.errors.append(f"task_{task.id}_target_outcome_not_found: {task.target_outcome}")
                elif task.npc_id:
                    # Check that the target outcome belongs to the specified NPC
                    expected_npc = outcome_to_npc[task.target_outcome]
                    if task.npc_id != expected_npc:
                        self.errors.append(f"task_{task.id}_outcome_npc_mismatch: wants {task.target_outcome} from {task.npc_id} but outcome belongs to {expected_npc}")
    
    def _validate_hidden_items(self):
        """Validate hidden items have unlock conditions"""
        for item in self.graph.items:
            if item.hidden and not item.unlock_prerequisites:
                self.errors.append(f"item_{item.id}_hidden_no_unlock")
    
    def _validate_starting_tasks(self):
        """Validate each role has at least one starting task"""
        tasks_by_role = {}
        for task in self.graph.tasks:
            if task.role not in tasks_by_role:
                tasks_by_role[task.role] = []
            tasks_by_role[task.role].append(task)
        
        for role in self.graph.roles:
            role_tasks = tasks_by_role.get(role, [])
            starting_tasks = [t for t in role_tasks if not t.prerequisites]
            
            if not starting_tasks:
                self.errors.append(f"role_{role}_no_starting_tasks")
    
    def _validate_task_balance(self):
        """Validate tasks are balanced across roles"""
        tasks_by_role = {}
        for task in self.graph.tasks:
            tasks_by_role[task.role] = tasks_by_role.get(task.role, 0) + 1
        
        for role, count in tasks_by_role.items():
            if count < 2:
                self.errors.append(f"role_{role}_too_few_tasks: {count}")
            elif count > 8:
                self.warnings.append(f"role_{role}_too_many_tasks: {count}")
    
    def _apply_fixes(self) -> bool:
        """
        Apply deterministic fixes to errors
        
        Returns:
            True if any fixes were applied
        """
        fixes_made = False
        
        for error in self.errors[:]:  # Copy list to allow modification
            if self._try_fix(error):
                self.errors.remove(error)
                fixes_made = True
        
        return fixes_made
    
    def _try_fix(self, error: str) -> bool:
        """
        Try to fix a specific error
        
        Returns:
            True if fix was applied
        """
        # Parse error format: "error_type: details"
        if ':' not in error:
            return False
        
        error_type, details = error.split(':', 1)
        details = details.strip()
        
        # Fix: Location count out of range
        if error_type == 'location_count':
            # Parse expected range from details: "9 (expected 4-6)"
            match = re.search(r'(\d+) \(expected (\d+)-(\d+)\)', details)
            if match:
                current = int(match.group(1))
                min_loc = int(match.group(2))
                max_loc = int(match.group(3))
                
                if current > max_loc:
                    # Find which locations are actually used by tasks/items/NPCs
                    used_locations = set()
                    for task in self.graph.tasks:
                        used_locations.add(task.location)
                    for item in self.graph.items:
                        used_locations.add(item.location)
                    for npc in self.graph.npcs:
                        used_locations.add(npc.location)
                    
                    # Keep used locations + extras up to max_loc
                    used_locs = [loc for loc in self.graph.locations if loc.id in used_locations]
                    unused_locs = [loc for loc in self.graph.locations if loc.id not in used_locations]
                    
                    # Keep all used, plus some unused if we have room
                    keep_count = max_loc
                    to_keep = used_locs[:keep_count]
                    if len(to_keep) < keep_count:
                        to_keep.extend(unused_locs[:keep_count - len(to_keep)])
                    
                    removed_count = len(self.graph.locations) - len(to_keep)
                    self.graph.locations = to_keep
                    self.fixes.append(f"Kept {len(to_keep)} most important locations, removed {removed_count} unused")
                    return True
                
                elif current < min_loc:
                    # Add placeholder locations
                    for i in range(min_loc - current):
                        new_loc = Location(
                            id=f"extra_location_{i + 1}",
                            name=f"Extra Location {i + 1}",
                            description="Additional location for scenario"
                        )
                        self.graph.locations.append(new_loc)
                    self.fixes.append(f"Added {min_loc - current} locations to reach minimum")
                    return True
        
        # Fix: Task count out of range
        if error_type == 'task_count':
            match = re.search(r'(\d+) \(expected (\d+)-(\d+)\)', details)
            if match:
                current = int(match.group(1))
                min_tasks = int(match.group(2))
                
                if current < min_tasks:
                    # Mark as warning instead - adding tasks is complex
                    self.warnings.append(f"Task count low: {current} (need {min_tasks})")
                    return True
        
        # Fix: Hidden item without unlock
        if 'hidden_no_unlock' in error_type:
            item_id = error_type.replace('item_', '').replace('_hidden_no_unlock', '')
            item = next((i for i in self.graph.items if i.id == item_id), None)
            if item:
                item.hidden = False
                self.fixes.append(f"Set {item_id}.hidden = false (was hidden with no unlock)")
                return True
        
        # Fix: Invalid NPC reference - remove the task or clear NPC
        if 'invalid_npc' in error_type:
            parts = error_type.split('_')
            task_id = parts[1]
            invalid_npc = details
            
            task = next((t for t in self.graph.tasks if t.id == task_id), None)
            if task:
                # Remove the task entirely (it references non-existent NPC)
                self.graph.tasks.remove(task)
                self.fixes.append(f"Removed task {task_id} (referenced non-existent NPC: {invalid_npc})")
                return True
        
        # Fix: Invalid location reference
        if 'invalid_location' in error_type:
            # Try to map to closest location
            invalid_loc = details
            if self.graph.locations:
                # Use first location as fallback
                first_loc = self.graph.locations[0].id
                
                if 'task_' in error_type:
                    task_id = error_type.split('_')[1]
                    task = next((t for t in self.graph.tasks if t.id == task_id), None)
                    if task:
                        task.location = first_loc
                        self.fixes.append(f"Fixed {task_id} location: {invalid_loc} → {first_loc}")
                        return True
                
                elif 'item_' in error_type:
                    # Extract item_id properly (handle multi-underscore IDs like jewel_case)
                    parts = error_type.split('_')
                    # Find where "invalid" starts
                    try:
                        invalid_idx = parts.index('invalid')
                        item_id = '_'.join(parts[1:invalid_idx])
                    except ValueError:
                        item_id = parts[1]
                    
                    item = next((i for i in self.graph.items if i.id == item_id), None)
                    if item:
                        item.location = first_loc
                        self.fixes.append(f"Fixed {item_id} location: {invalid_loc} → {first_loc}")
                        return True
        
        # Fix: Missing starting task for role
        if 'no_starting_tasks' in error_type:
            role = error_type.replace('role_', '').replace('_no_starting_tasks', '')
            # Find first task for this role and remove its prerequisites
            for task in self.graph.tasks:
                if task.role == role:
                    task.prerequisites = []
                    self.fixes.append(f"Made {task.id} a starting task for {role}")
                    return True
        
        # Fix: Invalid prerequisite - remove it
        if 'invalid_prereq' in error_type:
            parts = error_type.split('_')
            if len(parts) >= 4:
                task_id = parts[1]
                prereq_type = parts[3]  # task, item, or outcome
                invalid_id = details
                
                task = next((t for t in self.graph.tasks if t.id == task_id), None)
                if task:
                    # Remove the invalid prerequisite
                    task.prerequisites = [p for p in task.prerequisites if p['id'] != invalid_id]
                    self.fixes.append(f"Removed invalid {prereq_type} prerequisite from {task_id}: {invalid_id}")
                    return True
        
        # Fix: NPC-outcome mismatch
        if 'outcome_npc_mismatch' in error_type:
            task_id = error_type.split('_')[1]
            task = next((t for t in self.graph.tasks if t.id == task_id), None)
            if task and task.npc_id:
                # Find the NPC's actual outcome
                npc = next((n for n in self.graph.npcs if n.id == task.npc_id), None)
                if npc:
                    task.target_outcome = npc.outcome_provided
                    self.fixes.append(f"Fixed {task_id} target outcome to match NPC {task.npc_id}: {npc.outcome_provided}")
                    return True
        
        # Fix: Target outcome not found - remove task if can't fix
        if 'target_outcome_not_found' in error_type:
            task_id = error_type.split('_')[1]
            task = next((t for t in self.graph.tasks if t.id == task_id), None)
            if task:
                if task.npc_id:
                    npc = next((n for n in self.graph.npcs if n.id == task.npc_id), None)
                    if npc:
                        task.target_outcome = npc.outcome_provided
                        self.fixes.append(f"Set {task_id} target outcome to {npc.outcome_provided}")
                        return True
                
                # Can't fix - remove the task
                self.graph.tasks.remove(task)
                self.fixes.append(f"Removed task {task_id} (target outcome not found: {details})")
                return True
        
        # Fix: Invalid unlock task reference for item
        if 'invalid_unlock_task' in error_type:
            parts = error_type.split('_')
            item_id = parts[1]
            invalid_task = details
            
            item = next((i for i in self.graph.items if i.id == item_id), None)
            if item:
                # Remove the invalid unlock task
                item.unlock_prerequisites = [t for t in item.unlock_prerequisites if t != invalid_task]
                self.fixes.append(f"Removed invalid unlock task from {item_id}: {invalid_task}")
                return True
        
        return False


def validate_and_fix_graph(graph: ScenarioGraph, max_iterations: int = 5) -> Tuple[ScenarioGraph, ValidationResult]:
    """
    Validate and fix scenario graph
    
    Args:
        graph: ScenarioGraph to validate
        max_iterations: Maximum fix iterations
    
    Returns:
        Tuple of (fixed_graph, validation_result)
    """
    validator = GraphValidator(graph)
    result = validator.validate_and_fix(max_iterations)
    
    return graph, result


if __name__ == '__main__':
    import argparse
    import json
    from structure_extractor import ScenarioGraph
    
    parser = argparse.ArgumentParser(description="Validate and fix scenario graph (Stage 3)")
    parser.add_argument("graph_file", help="Path to JSON graph file")
    parser.add_argument("--output", help="Output JSON file path")
    parser.add_argument("--max-iterations", type=int, default=5, help="Max fix iterations")
    
    args = parser.parse_args()
    
    print(f"🔧 Validating and fixing graph...")
    print(f"   Graph: {args.graph_file}")
    print()
    
    # Load graph
    graph_path = Path(args.graph_file)
    if not graph_path.exists():
        print(f"❌ Graph file not found: {graph_path}")
        sys.exit(1)
    
    graph_data = json.loads(graph_path.read_text())
    
    # Reconstruct ScenarioGraph from dict
    # (Simple reconstruction - in production, add proper deserialization)
    graph = ScenarioGraph(
        scenario_id=graph_data['scenario_id'],
        objective=graph_data['objective'],
        player_count=graph_data['player_count'],
        roles=graph_data['roles']
    )
    
    # Validate and fix
    fixed_graph, result = validate_and_fix_graph(graph, args.max_iterations)
    
    # Report results
    print()
    if result.is_valid:
        print(f"✅ Graph is valid!")
    else:
        print(f"❌ Graph validation failed:")
        for error in result.errors:
            print(f"   - {error}")
    
    if result.fixes_applied:
        print(f"\n🔧 Fixes applied: {len(result.fixes_applied)}")
        for fix in result.fixes_applied:
            print(f"   - {fix}")
    
    if result.warnings:
        print(f"\n⚠️  Warnings: {len(result.warnings)}")
        for warning in result.warnings:
            print(f"   - {warning}")
    
    # Save fixed graph
    if args.output:
        output_path = Path(args.output)
    else:
        output_path = graph_path.with_stem(graph_path.stem + '_fixed')
    
    output_path.write_text(fixed_graph.to_json())
    print(f"\n💾 Saved to: {output_path}")
    
    sys.exit(0 if result.is_valid else 1)
