"""
Scenario Validation Tool

Validates experience/scenario markdown files against all requirements from
design/dependency_tree_design_guide.md (the single source of truth).

Usage:
    python validate_scenario.py <experience_file.md>
    python validate_scenario.py backend/experiences/generated_museum_4players.md
"""

import re
import json
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
from dataclasses import dataclass, field
from enum import Enum
import sys

# Import graph analysis and playability tools
sys.path.insert(0, str(Path(__file__).parent))
from scenario_graph_analyzer import ScenarioGraphAnalyzer, Task as GraphTask
from scenario_playability_simulator import PlayabilitySimulator, Task as SimTask


class ValidationLevel(str, Enum):
    """Severity level of validation issue"""
    CRITICAL = "CRITICAL"  # Must pass - scenario is broken
    IMPORTANT = "IMPORTANT"  # Should pass - scenario has issues
    ADVISORY = "ADVISORY"  # Nice to have - polish issues


@dataclass
class ValidationIssue:
    """A single validation issue"""
    rule_number: int
    level: ValidationLevel
    title: str
    message: str
    details: List[str] = field(default_factory=list)
    fix_suggestion: Optional[str] = None


@dataclass
class ValidationReport:
    """Complete validation report"""
    file_path: str
    passed: bool
    issues: List[ValidationIssue] = field(default_factory=list)
    
    def add_issue(self, issue: ValidationIssue):
        """Add an issue to the report"""
        self.issues.append(issue)
        if issue.level == ValidationLevel.CRITICAL:
            self.passed = False
    
    def get_summary(self) -> str:
        """Generate summary text"""
        critical = sum(1 for i in self.issues if i.level == ValidationLevel.CRITICAL)
        important = sum(1 for i in self.issues if i.level == ValidationLevel.IMPORTANT)
        advisory = sum(1 for i in self.issues if i.level == ValidationLevel.ADVISORY)
        
        status = "✅ PASSED" if self.passed else "❌ FAILED"
        return f"{status} | Critical: {critical} | Important: {important} | Advisory: {advisory}"
    
    def print_report(self):
        """Print formatted validation report"""
        print(f"\n{'='*80}")
        print(f"SCENARIO VALIDATION REPORT: {Path(self.file_path).name}")
        print(f"{'='*80}\n")
        print(self.get_summary())
        print()
        
        if not self.issues:
            print("✨ No issues found! Scenario is perfect.\n")
            return
        
        # Group by level
        for level in [ValidationLevel.CRITICAL, ValidationLevel.IMPORTANT, ValidationLevel.ADVISORY]:
            level_issues = [i for i in self.issues if i.level == level]
            if not level_issues:
                continue
            
            print(f"\n{level.value} ISSUES ({len(level_issues)}):")
            print("-" * 80)
            
            for issue in level_issues:
                print(f"\n[{issue.rule_number}] {issue.title}")
                print(f"  {issue.message}")
                
                if issue.details:
                    print(f"  Details:")
                    for detail in issue.details[:10]:  # Limit to 10 details
                        print(f"    • {detail}")
                    if len(issue.details) > 10:
                        print(f"    ... and {len(issue.details) - 10} more")
                
                if issue.fix_suggestion:
                    print(f"  💡 Fix: {issue.fix_suggestion}")
        
        print(f"\n{'='*80}\n")


@dataclass
class ParsedTask:
    """A parsed task from the markdown file"""
    id: str
    role: str
    type: str  # minigame, npc_llm, search, handoff, info_share
    description: str
    location: str
    prerequisites: List[Dict[str, str]] = field(default_factory=list)  # [{type: task|outcome|item, id: xxx}]
    minigame_id: Optional[str] = None
    npc_id: Optional[str] = None
    target_outcomes: List[str] = field(default_factory=list)
    handoff_item: Optional[str] = None


@dataclass
class ParsedNPC:
    """A parsed NPC from the markdown file"""
    id: str
    name: str
    location: str
    outcomes: List[str] = field(default_factory=list)  # IDs from Information Known and Actions Available
    info_known_ids: List[str] = field(default_factory=list)  # IDs only from Information Known
    action_ids: List[str] = field(default_factory=list)      # IDs only from Actions Available
    has_personality: bool = False
    has_relationships: bool = False
    cover_count: int = 0


@dataclass
class ParsedItem:
    """A parsed item from the markdown file"""
    id: str
    name: str
    location: str
    required_for: str  # Task IDs or "None"
    hidden: bool = False  # Whether item requires thorough search
    unlock_tasks: List[str] = field(default_factory=list)  # Tasks that must complete before item appears


@dataclass
class ParsedLocation:
    """A parsed location from the markdown file"""
    id: str
    name: str


class ScenarioValidator:
    """Validates scenario files against all design guide requirements"""
    
    def __init__(self, experience_file: Path):
        self.experience_file = experience_file
        self.content = experience_file.read_text()
        self.report = ValidationReport(file_path=str(experience_file), passed=True)
        
        # Parsed data
        self.roles: List[str] = []
        self.player_count: int = 0
        self.locations: Dict[str, ParsedLocation] = {}
        self.items: Dict[str, ParsedItem] = {}
        self.npcs: Dict[str, ParsedNPC] = {}
        self.tasks: Dict[str, ParsedTask] = {}
        
        # Load reference data
        self.load_roles_json()
    
    def load_roles_json(self):
        """Load roles.json for minigame validation"""
        roles_file = Path(__file__).parent.parent.parent / "shared_data" / "roles.json"
        with open(roles_file) as f:
            roles_data = json.load(f)
        
        # Build minigame lookup: role -> List[minigame_id]
        self.valid_minigames: Dict[str, Set[str]] = {}
        for role in roles_data["roles"]:
            role_id = role["role_id"]
            minigames = {mg["id"] for mg in role.get("minigames", [])}
            self.valid_minigames[role_id] = minigames
    
    def parse_file(self):
        """Parse the markdown file and extract all data"""
        self._parse_header()
        self._parse_locations()
        self._parse_items()
        self._parse_npcs()
        self._parse_tasks()
        
        # Debug output
        # print(f"DEBUG: Parsed {len(self.tasks)} tasks: {list(self.tasks.keys())}")
        # print(f"DEBUG: Parsed {len(self.locations)} locations: {[loc.name for loc in self.locations.values()]}")
    
    def _parse_header(self):
        """Parse header metadata"""
        # Selected Roles
        roles_match = re.search(r'\*\*Selected Roles\*\*:\s*(.+)', self.content)
        if roles_match:
            # Convert role names to snake_case IDs
            role_names = [r.strip() for r in roles_match.group(1).split(',')]
            self.roles = [r.lower().replace(' ', '_') for r in role_names]
        
        # Player Count
        player_match = re.search(r'\*\*Player Count\*\*:\s*(\d+)', self.content)
        if player_match:
            self.player_count = int(player_match.group(1))
    
    def _parse_locations(self):
        """Parse locations section"""
        # Find ## Locations section
        locations_section = re.search(r'## Locations\n(.*?)(?=\n## |\Z)', self.content, re.DOTALL)
        if not locations_section:
            return
        
        section_text = locations_section.group(1)
        
        # Pattern 1: ### Location Name\n- **ID**: `loc_id`
        location_blocks_1 = re.finditer(r'### (.+?)\n- \*\*ID\*\*: `([^`]+)`', section_text)
        for match in location_blocks_1:
            name = match.group(1).split('(')[0].strip()  # Remove (Starting Location) etc
            loc_id = match.group(2)
            self.locations[loc_id] = ParsedLocation(id=loc_id, name=name)
        
        # Pattern 2: - **ID**: `loc_id` (nested under category headers)
        # Handles format: ### Category\n- **Location Name**\n  - **ID**: `loc_id`
        location_blocks_2 = re.finditer(r'- \*\*ID\*\*: `([^`]+)`\n\s+- \*\*Name\*\*: (.+)', section_text)
        for match in location_blocks_2:
            loc_id = match.group(1)
            name = match.group(2).strip()
            self.locations[loc_id] = ParsedLocation(id=loc_id, name=name)
        
        # Pattern 2: - **ID**: `loc_id`\n- **Name**: Location Name (no heading)
        location_blocks_2 = re.finditer(r'- \*\*ID\*\*: `([^`]+)`\n- \*\*Name\*\*: (.+?)(?:\n|$)', section_text)
        for match in location_blocks_2:
            loc_id = match.group(1)
            name = match.group(2).strip()
            if loc_id not in self.locations:  # Don't overwrite pattern 1 matches
                self.locations[loc_id] = ParsedLocation(id=loc_id, name=name)

        # Pattern 3: - **Location Name** (`loc_id`): description  (markdown_renderer.py format)
        location_blocks_3 = re.finditer(r'- \*\*(.+?)\*\* \(`([^`]+)`\)', section_text)
        for match in location_blocks_3:
            name = match.group(1).strip()
            loc_id = match.group(2)
            if loc_id not in self.locations:
                self.locations[loc_id] = ParsedLocation(id=loc_id, name=name)
    
    def _parse_items(self):
        """Parse items section"""
        # Find ## Items by Location section
        items_section = re.search(r'## Items by Location\n(.*?)(?=\n## |\Z)', self.content, re.DOTALL)
        if not items_section:
            return
        
        section_text = items_section.group(1)
        
        # Find location headers
        current_location = None
        for line in section_text.split('\n'):
            # Location header
            if line.startswith('### '):
                current_location = line[4:].strip()
                continue
            
            # Item ID
            id_match = re.match(r'- \*\*ID\*\*: `([^`]+)`', line)
            if id_match and current_location:
                item_id = id_match.group(1)
                
                # Find the item block
                item_block_match = re.search(
                    rf'- \*\*ID\*\*: `{re.escape(item_id)}`\n(.*?)(?=\n- \*\*ID\*\*:|\n### |\Z)',
                    section_text,
                    re.DOTALL
                )
                
                if item_block_match:
                    item_text = item_block_match.group(1)
                    
                    # Extract name
                    name_match = re.search(r'- \*\*Name\*\*: (.+)', item_text)
                    name = name_match.group(1) if name_match else item_id
                    
                    # Extract Required For
                    req_match = re.search(r'- \*\*Required For\*\*: (.+)', item_text)
                    required_for = req_match.group(1) if req_match else "None"
                    
                    # Extract Hidden field
                    hidden_match = re.search(r'- \*\*Hidden\*\*:\s*(true|false)', item_text, re.IGNORECASE)
                    hidden = hidden_match and hidden_match.group(1).lower() == 'true'
                    
                    # Extract Unlock tasks
                    unlock_tasks = []
                    unlock_section = re.search(r'- \*\*Unlock\*\*:(.*?)(?=\n- \*\*|\Z)', item_text, re.DOTALL)
                    if unlock_section:
                        for task_match in re.finditer(r'Task `([^`]+)`', unlock_section.group(1)):
                            unlock_tasks.append(task_match.group(1))
                    
                    self.items[item_id] = ParsedItem(
                        id=item_id,
                        name=name,
                        location=current_location,
                        required_for=required_for,
                        hidden=hidden,
                        unlock_tasks=unlock_tasks
                    )
    
    def _parse_npcs(self):
        """Parse NPCs section"""
        # Find ## NPCs section
        npcs_section = re.search(r'## NPCs\n(.*?)(?=\n## |\Z)', self.content, re.DOTALL)
        if not npcs_section:
            return
        
        section_text = npcs_section.group(1)
        
        # Find all NPC blocks
        npc_blocks = re.finditer(
            r'### .+? - (.+?)\n- \*\*ID\*\*: `([^`]+)`.*?- \*\*Location\*\*: (.+?)\n(.*?)(?=\n### |\Z)',
            section_text,
            re.DOTALL
        )
        
        for match in npc_blocks:
            name = match.group(1)
            npc_id = match.group(2)
            location = match.group(3)
            npc_text = match.group(4)
            
            # Extract outcomes from Information Known (any confidence level)
            info_known_ids = []
            info_section = re.search(r'- \*\*Information Known\*\*:(.*?)(?=\n- \*\*|\Z)', npc_text, re.DOTALL)
            if info_section:
                for outcome_match in re.finditer(r'- `([^`]+)` (?:VERY HIGH|HIGH|MEDIUM|LOW):', info_section.group(1)):
                    info_known_ids.append(outcome_match.group(1))

            # Extract outcomes from Actions Available (any confidence level)
            action_ids = []
            actions_section = re.search(r'- \*\*Actions Available\*\*:(.*?)(?=\n- \*\*|\Z)', npc_text, re.DOTALL)
            if actions_section:
                for action_match in re.finditer(r'- `([^`]+)` (?:VERY HIGH|HIGH|MEDIUM|LOW):', actions_section.group(1)):
                    action_ids.append(action_match.group(1))

            # Personality — must be non-empty and non-placeholder (>20 chars)
            personality_match = re.search(r'- \*\*Personality\*\*:\s*(.+)', npc_text)
            personality_text = personality_match.group(1).strip() if personality_match else ""
            has_personality = (
                len(personality_text) >= 20
                and not personality_text.lower().startswith("personality of")
                and not personality_text.lower().startswith("placeholder")
            )

            # Relationships — must be non-empty (>10 chars)
            rel_match = re.search(r'- \*\*Relationships?\*\*:\s*(.+)', npc_text)
            rel_text = rel_match.group(1).strip() if rel_match else ""
            has_relationships = len(rel_text) >= 10

            # Cover story count
            cover_section = re.search(r'- \*\*Cover Story Options?\*\*:(.*?)(?=\n- \*\*|\Z)', npc_text, re.DOTALL)
            cover_count = 0
            if cover_section:
                cover_count = len(re.findall(r'- `[^`]+`:', cover_section.group(1)))

            self.npcs[npc_id] = ParsedNPC(
                id=npc_id,
                name=name,
                location=location,
                outcomes=info_known_ids + action_ids,
                info_known_ids=info_known_ids,
                action_ids=action_ids,
                has_personality=has_personality,
                has_relationships=has_relationships,
                cover_count=cover_count,
            )
    
    def _parse_tasks(self):
        """Parse tasks from Roles & Tasks section"""
        # Find ## Roles & Tasks section
        tasks_section = re.search(r'## Roles & Tasks\n(.*?)(?=\n## |\Z)', self.content, re.DOTALL)
        if not tasks_section:
            return
        
        section_text = tasks_section.group(1)
        
        # Find all task blocks
        # Pattern: 1. **MM1. 💬 NPC_LLM** - Task Description
        # Support letter suffixes like CL7a, D4a
        task_blocks = re.finditer(
            r'\d+\.\s+\*\*([A-Z]+\d+[a-z]?)\.\s+([🎮💬🔍🤝🗣️])\s+(\w+)\*\*\s+-\s+(.+?)\n(.*?)(?=\n\d+\.\s+\*\*|\n### |\Z)',
            section_text,
            re.DOTALL
        )
        
        current_role = None
        for line in section_text.split('\n'):
            if line.startswith('### '):
                current_role = line[4:].strip().lower().replace(' ', '_')
        
        # Re-parse with role context
        role_sections = re.finditer(r'### (.+?)\n(.*?)(?=\n### |\Z)', section_text, re.DOTALL)
        for role_match in role_sections:
            role_name = role_match.group(1).strip().lower().replace(' ', '_')
            role_text = role_match.group(2)
            
            task_blocks = re.finditer(
                r'\d+\.\s+\*\*([A-Z]+\d+[a-z]?)\.\s+[🎮💬🔍🤝🗣]️?\s+(\w+)\*\*\s+-\s+(.+?)\n(.*?)(?=\n\d+\.\s+\*\*|\Z)',
                role_text,
                re.DOTALL
            )
            
            for task_match in task_blocks:
                task_id = task_match.group(1)
                task_type_raw = task_match.group(2)
                description = task_match.group(3)
                task_text = task_match.group(4)
                
                # Normalize task type (handle variations like "INFO" -> "info", "NPC_LLM" -> "npc_llm")
                task_type = task_type_raw.lower().replace('_', '_')
                
                # Extract location (strip backticks for ID-only format)
                # Support both indented (4 spaces) and non-indented formats
                location_match = re.search(r'^\s*-\s+\*Location:\*\s+(.+?)$', task_text, re.MULTILINE)
                if location_match:
                    location = location_match.group(1).strip()
                    # Strip backticks if present (ID-only format: `bank_lobby`)
                    if location.startswith('`') and location.endswith('`'):
                        location = location[1:-1]
                else:
                    location = "Unknown"
                
                # Extract prerequisites (support indentation)
                prerequisites = []
                prereq_section = re.search(r'^\s*-\s+\*Prerequisites:\*(.*?)(?=^\s*-\s+\*[A-Z]|\Z)', task_text, re.DOTALL | re.MULTILINE)
                if prereq_section:
                    prereq_text = prereq_section.group(1)
                    
                    # Task prerequisites
                    for task_prereq in re.finditer(r'Task `([^`]+)`', prereq_text):
                        prerequisites.append({'type': 'task', 'id': task_prereq.group(1)})
                    
                    # Outcome prerequisites
                    for outcome_prereq in re.finditer(r'Outcome `([^`]+)`', prereq_text):
                        prerequisites.append({'type': 'outcome', 'id': outcome_prereq.group(1)})
                    
                    # Item prerequisites
                    for item_prereq in re.finditer(r'Item `([^`]+)`', prereq_text):
                        prerequisites.append({'type': 'item', 'id': item_prereq.group(1)})
                    
                    # Info prerequisites (for INFO_SHARE tasks)
                    for info_prereq in re.finditer(r'Info `([^`]+)`', prereq_text):
                        prerequisites.append({'type': 'outcome', 'id': info_prereq.group(1)})
                    
                    # Also check for "None" explicitly
                    if 'None' in prereq_text or 'starting task' in prereq_text.lower():
                        pass  # No prerequisites
                
                # Extract minigame ID for minigame tasks
                minigame_id = None
                if task_type == 'minigame':
                    # Pattern: 🎮 minigame_id
                    minigame_match = re.search(r'🎮\s+(\w+)', task_match.group(0))
                    if minigame_match:
                        minigame_id = minigame_match.group(1)
                
                # Extract NPC ID for npc tasks (support indentation)
                npc_id = None
                target_outcomes = []
                if task_type in ['npc_llm', 'npc']:
                    npc_match = re.search(r'^\s*-\s+\*NPC:\*\s+`([^`]+)`', task_text, re.MULTILINE)
                    if npc_match:
                        npc_id = npc_match.group(1)
                    
                    # Extract target outcomes (support indentation)
                    outcomes_match = re.search(r'^\s*-\s+\*Target Outcomes:\*\s+`([^`]+)`', task_text, re.MULTILINE)
                    if outcomes_match:
                        target_outcomes = [outcomes_match.group(1)]
                
                # Extract handoff item for handoff tasks
                handoff_item = None
                if task_type == 'handoff':
                    handoff_item_match = re.search(r'^\s*-\s+\*Handoff Item:\*\s+`([^`]+)`', task_text, re.MULTILINE)
                    if handoff_item_match:
                        handoff_item = handoff_item_match.group(1)

                self.tasks[task_id] = ParsedTask(
                    id=task_id,
                    role=role_name,
                    type=task_type,
                    description=description,
                    location=location,
                    prerequisites=prerequisites,
                    minigame_id=minigame_id,
                    npc_id=npc_id,
                    target_outcomes=target_outcomes,
                    handoff_item=handoff_item
                )
    
    def validate_all(self) -> ValidationReport:
        """Run all validation checks"""
        self.parse_file()
        
        # Structural validity checks
        self.check_valid_minigame_ids()  # Rule 1
        self.check_task_id_format()  # Rule 2
        self.check_required_sections()  # Rule 3
        self.check_task_count_ranges()  # Rule 4
        self.check_location_count()  # Rule 5
        
        # Data integrity checks
        self.check_npc_references()  # Rule 10
        self.check_item_references()  # Rule 11
        self.check_location_consistency()  # Rule 12
        self.check_outcome_ids()  # Rule 13
        self.check_handoff_tasks_have_items()  # Rule 40
        
        # Task distribution checks
        self.check_balanced_roles()  # Rule 14
        self.check_task_type_balance()  # Rule 16
        
        # Cross-role interaction checks
        self.check_sufficient_interactions()  # Rule 17
        
        # Advisory checks
        self.check_search_task_balance()  # Rule 24
        self.check_hidden_items_unlocks()  # Rule 25
        
        # Dependency graph validation (NEW - Rules 26-30)
        self.check_task_id_parser_compatibility()  # Rule 30
        self.check_dependency_graph()  # Rules 26-29
        
        # Playability simulation (NEW - Rules 31-35)
        # Run if we have parseable tasks (even if count/balance issues exist)
        if len(self.tasks) > 0 and len(self.roles) > 0:
            self.check_playability_simulation()  # Rules 31-35

        # NPC quality checks (Rules 36-39)
        if self.npcs:
            self.check_npc_completeness()       # Rule 36
            self.check_npc_action_coverage()    # Rule 37
            self.check_cover_story_depth()      # Rule 38
            self.check_cross_role_info_chain()  # Rule 39

        return self.report
    
    # Validation check methods
    
    def check_valid_minigame_ids(self):
        """Rule 1: Check all minigames exist in roles.json"""
        invalid = []
        for task_id, task in self.tasks.items():
            if task.type == 'minigame' and task.minigame_id:
                if task.role not in self.valid_minigames:
                    invalid.append(f"{task_id}: unknown role '{task.role}'")
                elif task.minigame_id not in self.valid_minigames[task.role]:
                    invalid.append(f"{task_id}: '{task.minigame_id}' not valid for {task.role}")
        
        if invalid:
            self.report.add_issue(ValidationIssue(
                rule_number=1,
                level=ValidationLevel.CRITICAL,
                title="Invalid Minigame IDs",
                message="Found minigame tasks with invalid or non-existent minigame IDs",
                details=invalid,
                fix_suggestion="Replace with valid minigames from shared_data/roles.json"
            ))
    
    def check_task_id_format(self):
        """Rule 2: Check task ID format (supports letter suffixes like CL7a)"""
        invalid = []
        valid_pattern = re.compile(r'^(MM|H|SC|D|I|G|M|L|F|CB|CL|PP)\d+[a-z]?$')
        
        for task_id in self.tasks.keys():
            if not valid_pattern.match(task_id):
                invalid.append(task_id)
        
        if invalid:
            self.report.add_issue(ValidationIssue(
                rule_number=2,
                level=ValidationLevel.CRITICAL,
                title="Invalid Task ID Format",
                message="Task IDs must follow format: ROLE_CODE + NUMBER + optional letter (e.g., MM1, SC2, CL7a)",
                details=invalid,
                fix_suggestion="Rename tasks to follow proper format"
            ))
    
    def check_required_sections(self):
        """Rule 3: Check required sections are present"""
        required = ["## Objective", "## Locations", "## NPCs", "## Roles & Tasks"]
        missing = [s for s in required if s not in self.content]
        
        if missing:
            self.report.add_issue(ValidationIssue(
                rule_number=3,
                level=ValidationLevel.CRITICAL,
                title="Missing Required Sections",
                message="Experience file must contain all required sections",
                details=missing,
                fix_suggestion="Add missing sections to file"
            ))
    
    def check_task_count_ranges(self):
        """Rule 4: Check task count is appropriate for player count (min 3 tasks/role)"""
        total_tasks = len(self.tasks)
        min_tasks = max(6, self.player_count * 3)
        max_tasks = self.player_count * 12

        if total_tasks < min_tasks:
            self.report.add_issue(ValidationIssue(
                rule_number=4,
                level=ValidationLevel.IMPORTANT,
                title="Task Count Out of Range",
                message=f"For {self.player_count} players, expected {min_tasks}-{max_tasks} tasks, found {total_tasks}",
                fix_suggestion="Add tasks to reach target range"
            ))
        elif total_tasks > max_tasks:
            self.report.add_issue(ValidationIssue(
                rule_number=4,
                level=ValidationLevel.IMPORTANT,
                title="Task Count Out of Range",
                message=f"For {self.player_count} players, expected {min_tasks}-{max_tasks} tasks, found {total_tasks}",
                fix_suggestion="Remove tasks to reach target range"
            ))
    
    def check_location_count(self):
        """Rule 5: Check location count (scales with player count)"""
        location_count = len(self.locations)
        
        # Determine expected range based on player count
        if 2 <= self.player_count <= 3:
            min_locs, max_locs = 4, 6
        elif 4 <= self.player_count <= 5:
            min_locs, max_locs = 6, 9
        elif 6 <= self.player_count <= 8:
            min_locs, max_locs = 8, 12
        elif 9 <= self.player_count <= 12:
            min_locs, max_locs = 10, 15
        else:
            # Default for unusual player counts
            min_locs, max_locs = 4, 15
        
        if not (min_locs <= location_count <= max_locs):
            self.report.add_issue(ValidationIssue(
                rule_number=5,
                level=ValidationLevel.CRITICAL,
                title="Location Count Out of Range",
                message=f"For {self.player_count} players, expected {min_locs}-{max_locs} locations, found {location_count}",
                fix_suggestion=f"Add or remove locations to reach {min_locs}-{max_locs} range"
            ))
    
    def check_npc_references(self):
        """Rule 10: Check all NPC IDs in tasks exist AND check for Player NPCs"""
        invalid = []
        player_npcs = []
        
        # Check for "Player NPCs" (NPCs that reference player roles)
        for npc_id, npc in self.npcs.items():
            # Check if NPC ID contains "_player" or similar patterns
            if "_player" in npc_id.lower() or npc_id.lower().endswith("_player"):
                player_npcs.append(f"NPC '{npc_id}': Uses '_player' suffix (NPCs are AI characters, not player roles!)")
            
            # Check if NPC name matches a player role
            npc_name_lower = npc.name.lower()
            npc_role_lower = npc.role.lower() if hasattr(npc, 'role') else ""
            for role in self.roles:
                role_lower = role.lower().replace("_", " ")
                if role_lower in npc_name_lower and "player" in npc_role_lower:
                    player_npcs.append(f"NPC '{npc_id}' ('{npc.name}'): Appears to be a player role, not an AI character")
        
        # Check task NPC references exist
        for task_id, task in self.tasks.items():
            if task.npc_id and task.npc_id not in self.npcs:
                invalid.append(f"{task_id}: references unknown NPC '{task.npc_id}'")
        
        if player_npcs:
            self.report.add_issue(ValidationIssue(
                rule_number=10,
                level=ValidationLevel.CRITICAL,
                title="Player NPCs Detected (Invalid!)",
                message="Found NPCs that appear to be player roles. NPCs must be AI characters (guards, staff, civilians), not other players! Player-to-player communication uses INFO_SHARE tasks, NOT NPC_LLM tasks.",
                details=player_npcs,
                fix_suggestion="Remove Player NPCs and convert NPC_LLM tasks that reference them to INFO_SHARE tasks"
            ))
        
        if invalid:
            self.report.add_issue(ValidationIssue(
                rule_number=10,
                level=ValidationLevel.CRITICAL,
                title="Invalid NPC References",
                message="Tasks reference NPCs that don't exist",
                details=invalid,
                fix_suggestion="Add missing NPC definitions or correct NPC IDs"
            ))
    
    def check_item_references(self):
        """Rule 11: Check all item IDs are valid"""
        invalid = []
        
        # Check item prerequisites in tasks
        for task_id, task in self.tasks.items():
            for prereq in task.prerequisites:
                if prereq['type'] == 'item' and prereq['id'] not in self.items:
                    invalid.append(f"{task_id}: requires unknown item '{prereq['id']}'")
        
        # Check item "Required For" references
        for item_id, item in self.items.items():
            if item.required_for and item.required_for != "None":
                # Parse task IDs from "Required For" field
                task_ids = re.findall(r'[A-Z]+\d+', item.required_for)
                for task_id in task_ids:
                    if task_id not in self.tasks:
                        invalid.append(f"Item '{item_id}': Required For references unknown task '{task_id}'")
        
        if invalid:
            self.report.add_issue(ValidationIssue(
                rule_number=11,
                level=ValidationLevel.CRITICAL,
                title="Invalid Item References",
                message="Found invalid item references",
                details=invalid,
                fix_suggestion="Add missing item definitions or correct item IDs"
            ))
    
    def check_location_consistency(self):
        """Rule 12: Check location IDs are consistent (ID-only enforcement)"""
        # Build set of location IDs (we now enforce ID-only references)
        location_ids = set(self.locations.keys())
        location_ids.add("Any")  # Special case for radio/info tasks
        
        invalid = []
        
        # Check task locations (should be IDs now, extracted without backticks)
        for task_id, task in self.tasks.items():
            if task.location not in location_ids:
                invalid.append(f"{task_id}: unknown location ID '{task.location}'")
        
        if invalid:
            self.report.add_issue(ValidationIssue(
                rule_number=12,
                level=ValidationLevel.CRITICAL,
                title="Invalid Location References",
                message="Tasks reference location IDs that don't exist. Use IDs (e.g., `bank_lobby`) not names.",
                details=invalid,
                fix_suggestion="Use correct location IDs in backticks: *Location:* `location_id`"
            ))
    
    def check_outcome_ids(self):
        """Rule 13: Check outcome IDs in prerequisites AND target outcomes exist in NPC definitions"""
        invalid_prereqs = []
        invalid_targets = []
        
        # Check prerequisites referencing outcomes
        for task_id, task in self.tasks.items():
            for prereq in task.prerequisites:
                if prereq['type'] == 'outcome':
                    outcome_id = prereq['id']
                    # Find which NPC should have this outcome
                    found = False
                    for npc_id, npc in self.npcs.items():
                        if outcome_id in npc.outcomes:
                            found = True
                            break
                    
                    if not found:
                        invalid_prereqs.append(f"{task_id}: requires outcome '{outcome_id}' which no NPC provides")
            
            # CRITICAL: Check NPC tasks' target outcomes exist in the NPC definition
            if task.type in ['npc_llm', 'npc'] and task.target_outcomes:
                for target_outcome in task.target_outcomes:
                    # Find the NPC this task references
                    if task.npc_id:
                        npc = self.npcs.get(task.npc_id)
                        if npc:
                            if target_outcome not in npc.outcomes:
                                invalid_targets.append(f"{task_id}: target outcome '{target_outcome}' not found in NPC '{task.npc_id}' definition")
                        # else: handled by check_npc_references
                    else:
                        invalid_targets.append(f"{task_id}: NPC task has target outcome '{target_outcome}' but no NPC specified")
        
        if invalid_prereqs:
            self.report.add_issue(ValidationIssue(
                rule_number=13,
                level=ValidationLevel.CRITICAL,
                title="Invalid Outcome IDs in Prerequisites",
                message="Tasks require outcomes that no NPC provides",
                details=invalid_prereqs,
                fix_suggestion="Add outcome to NPC definition or correct outcome ID"
            ))
        
        if invalid_targets:
            self.report.add_issue(ValidationIssue(
                rule_number=13,
                level=ValidationLevel.CRITICAL,
                title="Invalid Target Outcomes in NPC Tasks",
                message="NPC tasks specify target outcomes that don't exist in the NPC's Information Known section",
                details=invalid_targets,
                fix_suggestion="Add target outcome to NPC's Information Known section with matching ID"
            ))
    
    def check_handoff_tasks_have_items(self):
        """Rule 40: Every handoff task must specify a handoff_item"""
        missing = [
            task.id for task in self.tasks.values()
            if task.type == 'handoff' and not task.handoff_item
        ]
        if missing:
            self.report.add_issue(ValidationIssue(
                rule_number=40,
                level=ValidationLevel.CRITICAL,
                title="Handoff Task Missing Item",
                message="Handoff tasks must specify a handoff_item — tasks without one cannot be completed",
                details=[f"Task {tid} is type 'handoff' but has no Handoff Item defined" for tid in missing],
                fix_suggestion="Assign a valid item ID as handoff_item to each handoff task"
            ))

    def check_balanced_roles(self):
        """Rule 14: Check role task distribution"""
        # Count tasks per role
        task_counts = {}
        for task in self.tasks.values():
            task_counts[task.role] = task_counts.get(task.role, 0) + 1
        
        unbalanced = []
        for role, count in task_counts.items():
            if count < 2:
                unbalanced.append(f"{role}: only {count} task(s) (minimum 2)")
            elif count > 8:
                unbalanced.append(f"{role}: {count} tasks (maximum 8)")
        
        if unbalanced:
            self.report.add_issue(ValidationIssue(
                rule_number=14,
                level=ValidationLevel.IMPORTANT,
                title="Unbalanced Role Distribution",
                message="Some roles have too few or too many tasks",
                details=unbalanced,
                fix_suggestion="Redistribute tasks to balance roles (2-8 tasks each)"
            ))
    
    def check_task_type_balance(self):
        """Rule 16: Check task type balance (60-70% social)"""
        social_types = ['npc_llm', 'npc', 'handoff', 'info_share', 'info', 'search']
        
        social_count = sum(1 for t in self.tasks.values() if t.type in social_types)
        total_count = len(self.tasks)
        
        if total_count > 0:
            social_pct = (social_count / total_count) * 100
            
            if social_pct < 60:
                self.report.add_issue(ValidationIssue(
                    rule_number=16,
                    level=ValidationLevel.IMPORTANT,
                    title="Too Few Social Interactions",
                    message=f"Social tasks: {social_pct:.1f}% (target: 60-70%)",
                    details=[f"{social_count}/{total_count} tasks are social interactions"],
                    fix_suggestion="Convert some minigames to NPC interactions or handoffs"
                ))
            elif social_pct > 70:
                self.report.add_issue(ValidationIssue(
                    rule_number=16,
                    level=ValidationLevel.ADVISORY,
                    title="Too Many Social Interactions",
                    message=f"Social tasks: {social_pct:.1f}% (target: 60-70%)",
                    details=[f"{social_count}/{total_count} tasks are social interactions"],
                    fix_suggestion="Add more minigame tasks to balance gameplay"
                ))
    
    def check_sufficient_interactions(self):
        """Rule 17: Check for sufficient cross-role interaction"""
        handoff_count = sum(1 for t in self.tasks.values() if t.type == 'handoff')
        info_count = sum(1 for t in self.tasks.values() if t.type in ['info_share', 'info'])
        
        issues = []
        if handoff_count < 3:
            issues.append(f"Only {handoff_count} handoff task(s) (minimum 3 recommended)")
        if info_count < 2:
            issues.append(f"Only {info_count} info share task(s) (minimum 2 recommended)")
        
        if issues:
            self.report.add_issue(ValidationIssue(
                rule_number=17,
                level=ValidationLevel.IMPORTANT,
                title="Insufficient Cross-Role Interaction",
                message="Not enough collaborative tasks between roles",
                details=issues,
                fix_suggestion="Add more handoff (🤝) and info share (🗣️) tasks"
            ))
    
    def check_search_task_balance(self):
        """Rule 24: Check search task balance"""
        search_count = sum(1 for t in self.tasks.values() if t.type == 'search')
        
        if not (6 <= search_count <= 10):
            self.report.add_issue(ValidationIssue(
                rule_number=24,
                level=ValidationLevel.ADVISORY,
                title="Search Task Count",
                message=f"Found {search_count} search tasks (recommended: 6-10)",
                fix_suggestion="Adjust number of search tasks for better item discovery balance"
            ))
    
    def check_hidden_items_unlocks(self):
        """Rule 25: Check hidden items have proper unlock conditions"""
        invalid_unlocks = []
        impossible_items = []
        
        for item_id, item in self.items.items():
            # Check unlock task IDs are valid
            for unlock_task_id in item.unlock_tasks:
                if unlock_task_id not in self.tasks:
                    invalid_unlocks.append(f"Item '{item_id}': Unlock references unknown task '{unlock_task_id}'")
            
            # CRITICAL CHECK: Hidden items MUST have unlock conditions
            # A hidden item with no unlock is IMPOSSIBLE to find!
            if item.hidden and not item.unlock_tasks:
                impossible_items.append(f"Item '{item_id}' is Hidden: true but has NO unlock conditions - will be IMPOSSIBLE to find!")
        
        if invalid_unlocks:
            self.report.add_issue(ValidationIssue(
                rule_number=25,
                level=ValidationLevel.CRITICAL,
                title="Invalid Item Unlock References",
                message="Items have unlock conditions referencing non-existent tasks",
                details=invalid_unlocks,
                fix_suggestion="Remove invalid unlock task references or add missing task definitions"
            ))
        
        if impossible_items:
            self.report.add_issue(ValidationIssue(
                rule_number=25,
                level=ValidationLevel.CRITICAL,
                title="Hidden Items Without Unlock Conditions",
                message="Hidden items MUST have unlock conditions or they cannot be found",
                details=impossible_items,
                fix_suggestion="Either: (1) Set Hidden: false, OR (2) Add unlock prerequisites using **Unlock**: format"
            ))
    
    def check_dependency_graph(self):
        """Rules 26-29: Validate dependency graph structure"""
        # Convert parsed tasks to graph format
        graph_tasks = {}
        for task_id, task in self.tasks.items():
            graph_tasks[task_id] = GraphTask(
                id=task_id,
                prerequisites=task.prerequisites,
                type=task.type
            )
        
        # Run graph analysis
        analyzer = ScenarioGraphAnalyzer(graph_tasks)
        
        # Rule 26: Check for cycles
        cycles = analyzer.find_cycles()
        if cycles:
            for cycle in cycles:
                cycle_str = ' -> '.join(cycle)
                self.report.add_issue(ValidationIssue(
                    rule_number=26,
                    level=ValidationLevel.CRITICAL,
                    title="Circular Dependency Detected",
                    message=f"Tasks form a circular dependency: {cycle_str}",
                    details=[cycle_str],
                    fix_suggestion=f"Remove prerequisite from {cycle[-1]} to {cycle[0]} to break the cycle"
                ))
        
        # Find start tasks
        start_tasks = analyzer.find_start_tasks()
        
        # Rule 27: Check for orphaned tasks
        orphans = analyzer.find_orphaned_tasks()
        if orphans:
            self.report.add_issue(ValidationIssue(
                rule_number=27,
                level=ValidationLevel.CRITICAL,
                title="Orphaned Tasks (Unreachable)",
                message=f"Found {len(orphans)} tasks that cannot be reached from any starting task",
                details=orphans,
                fix_suggestion="Add prerequisites to connect these tasks to the main flow, or mark them as starting tasks (Prerequisites: None)"
            ))
        
        # Rule 28: Check for dead-end tasks (Important, not Critical)
        dead_ends = analyzer.find_dead_end_tasks()
        # The last task per role is a natural terminal node — the game ends via the
        # Escape mechanism once all roles complete their final task. Never flag these.
        role_last_ids: set = set()
        for role in self.roles:
            role_task_ids = sorted(tid for tid, task in self.tasks.items() if task.role == role)
            if role_task_ids:
                role_last_ids.add(role_task_ids[-1])
        non_final_dead_ends = [
            tid for tid in dead_ends
            if tid not in role_last_ids
        ]
        
        if non_final_dead_ends:
            self.report.add_issue(ValidationIssue(
                rule_number=28,
                level=ValidationLevel.IMPORTANT,
                title="Dead-End Tasks Detected",
                message=f"Found {len(non_final_dead_ends)} tasks that don't unlock anything else (may reduce player engagement)",
                details=non_final_dead_ends,
                fix_suggestion="Add dependent tasks that unlock from these, or ensure they contribute to the main objective"
            ))
        
        # Rule 29: Check each role has starting tasks
        for role in self.roles:
            role_tasks = [tid for tid, task in self.tasks.items() if task.role == role]
            role_start_tasks = [tid for tid in start_tasks if tid in role_tasks]
            
            if not role_start_tasks:
                self.report.add_issue(ValidationIssue(
                    rule_number=29,
                    level=ValidationLevel.CRITICAL,
                    title=f"No Starting Tasks for Role: {role}",
                    message=f"Role '{role}' has no tasks with 'Prerequisites: None (starting task)'. Players with this role cannot begin playing.",
                    details=[f"Role {role} has {len(role_tasks)} tasks but none are starting tasks"],
                    fix_suggestion=f"Change at least one {role} task to have 'Prerequisites: None (starting task)'"
                ))
    
    def check_task_id_parser_compatibility(self):
        """Rule 30: Ensure task IDs will parse correctly in experience_loader.py"""
        # The backend parser uses this regex to extract task IDs
        # We need to ensure all task IDs in the scenario match this pattern
        parser_regex = r'^[A-Z]{1,3}\d+[a-z]?$'
        
        incompatible = []
        for task_id in self.tasks.keys():
            if not re.match(parser_regex, task_id):
                incompatible.append(f"{task_id} (doesn't match {parser_regex})")
        
        if incompatible:
            self.report.add_issue(ValidationIssue(
                rule_number=30,
                level=ValidationLevel.CRITICAL,
                title="Parser-Incompatible Task IDs",
                message="Task IDs use format that backend parser (experience_loader.py) cannot handle",
                details=incompatible,
                fix_suggestion="Use format: ROLE_CODE (1-3 uppercase letters) + NUMBER + optional lowercase letter (e.g., MM1, CL7a, D4a)"
            ))
    
    def check_playability_simulation(self):
        """Rules 31-35: Simulate gameplay to detect deadlocks and balance issues"""
        # Convert parsed tasks to simulation format
        sim_tasks = {}
        for task_id, task in self.tasks.items():
            sim_tasks[task_id] = SimTask(
                id=task_id,
                role=task.role,
                prerequisites=task.prerequisites,
                type=task.type,
                target_outcomes=getattr(task, 'target_outcomes', []),
                search_items=getattr(task, 'search_items', []),
            )
        
        # Run simulation
        simulator = PlayabilitySimulator(sim_tasks, self.roles)
        result = simulator.simulate(max_turns=500, strategy="round_robin")
        
        # Rule 31: Check for deadlocks
        if not result.success:
            for issue in result.issues:
                if "Deadlock" in issue or "No players have available tasks" in issue:
                    self.report.add_issue(ValidationIssue(
                        rule_number=31,
                        level=ValidationLevel.CRITICAL,
                        title="Potential Deadlock Detected",
                        message=issue,
                        details=[],
                        fix_suggestion="Review dependency chain - some tasks may have impossible prerequisites or missing outcomes/items"
                    ))
        
        # Rule 32: Check for long idle periods
        for role, max_idle in result.role_max_idle.items():
            if max_idle > 5:  # More than 5 consecutive idle turns
                self.report.add_issue(ValidationIssue(
                    rule_number=32,
                    level=ValidationLevel.IMPORTANT,
                    title=f"Long Idle Period for {role}",
                    message=f"Role '{role}' had {max_idle} consecutive turns with no available tasks",
                    details=[],
                    fix_suggestion=f"Add parallel tasks or adjust prerequisites to keep {role} engaged throughout the game"
                ))
        
        # Rule 33: Check workload distribution (advisory)
        if result.total_turns > 0:
            for role, task_count in result.role_task_counts.items():
                role_timeline = result.role_timeline.get(role, [])
                if role_timeline:
                    # Check if >50% of tasks happen in final 25% of game
                    final_quarter = result.total_turns * 0.75
                    late_tasks = sum(1 for turn in role_timeline if turn >= final_quarter)
                    
                    if task_count > 0 and late_tasks / task_count > 0.5:
                        self.report.add_issue(ValidationIssue(
                            rule_number=33,
                            level=ValidationLevel.ADVISORY,
                            title=f"Workload Imbalance for {role}",
                            message=f"Role '{role}' has {late_tasks}/{task_count} tasks ({late_tasks/task_count*100:.0f}%) in final 25% of game",
                            details=[],
                            fix_suggestion=f"Redistribute {role}'s tasks more evenly across the game timeline"
                        ))
        
        # Rule 34: Check early engagement (first 3 turns)
        for role in self.roles:
            role_timeline = result.role_timeline.get(role, [])
            early_tasks = sum(1 for turn in role_timeline if turn <= 3)
            
            if early_tasks == 0 and result.role_task_counts.get(role, 0) > 0:
                self.report.add_issue(ValidationIssue(
                    rule_number=34,
                    level=ValidationLevel.IMPORTANT,
                    title=f"No Early Engagement for {role}",
                    message=f"Role '{role}' has no tasks available in the first 3 turns of gameplay",
                    details=[],
                    fix_suggestion=f"Add starting tasks or reduce prerequisites to engage {role} earlier in the game"
                ))
        
        # Rule 35: Check parallelism (advisory)
        # Count how many turns had multiple players with work
        if result.turns:
            parallel_turns = sum(1 for turn_data in result.turns if len(turn_data.active_players) >= max(2, len(self.roles) // 2))
            parallelism_ratio = parallel_turns / len(result.turns) if result.turns else 0
            
            if parallelism_ratio < 0.5 and len(self.roles) > 1:
                self.report.add_issue(ValidationIssue(
                    rule_number=35,
                    level=ValidationLevel.ADVISORY,
                    title="Limited Parallelism",
                    message=f"Only {parallelism_ratio*100:.0f}% of turns had tasks available for multiple players (target: 50%+)",
                    details=[],
                    fix_suggestion="Add more parallel task branches to increase player engagement and reduce turn time"
                ))


    def check_npc_completeness(self):
        """Rule 36: Each NPC must have personality, relationships, ≥1 named outcome ID, and ≥1 cover option."""
        incomplete = []
        for npc_id, npc in self.npcs.items():
            missing = []
            if not npc.has_personality:
                missing.append("personality (missing or placeholder)")
            if not npc.has_relationships:
                missing.append("relationships (missing or too short)")
            # A named outcome can come from either information_known or actions_available
            if not npc.outcomes:
                missing.append("no named outcome IDs (add `snake_case_id` CONFIDENCE: description in Information Known or Actions Available)")
            if npc.cover_count == 0:
                missing.append("cover_options (none found)")
            if missing:
                incomplete.append(f"NPC '{npc_id}' ({npc.name}): missing — {', '.join(missing)}")

        if incomplete:
            self.report.add_issue(ValidationIssue(
                rule_number=36,
                level=ValidationLevel.IMPORTANT,
                title="Incomplete NPC Profiles",
                message="NPCs are missing required fields for rich AI conversations",
                details=incomplete,
                fix_suggestion=(
                    "Fill in personality (2-3 grounded sentences), relationships (cross-reference other NPCs), "
                    "information_known with named IDs (`snake_case` HIGH/MEDIUM/LOW: description), "
                    "and at least one cover story option."
                )
            ))

    def check_npc_action_coverage(self):
        """Rule 37: NPCs targeted by NPC_LLM tasks must have at least 1 named outcome (info or action)."""
        targeted_npcs = {task.npc_id for task in self.tasks.values() if task.npc_id}
        dead_conversations = []
        for npc_id in targeted_npcs:
            npc = self.npcs.get(npc_id)
            if not npc:
                continue
            if len(npc.outcomes) == 0:
                dead_conversations.append(
                    f"NPC '{npc_id}' ({npc.name}): targeted by NPC_LLM task but has "
                    f"no named outcome IDs in Information Known or Actions Available — players have nothing to learn/unlock"
                )
        if dead_conversations:
            self.report.add_issue(ValidationIssue(
                rule_number=37,
                level=ValidationLevel.IMPORTANT,
                title="NPCs With No Learnable Outcomes",
                message="NPC_LLM tasks target NPCs that provide nothing useful to the player",
                details=dead_conversations,
                fix_suggestion=(
                    "Add at least one `actions_available` entry with a named ID "
                    "(e.g., `leave_post` HIGH: Can be convinced to step away) "
                    "OR at least 2 `information_known` entries."
                )
            ))

    def check_cover_story_depth(self):
        """Rule 38 (ADVISORY): Each NPC should have at least 3 cover story options."""
        shallow = []
        for npc_id, npc in self.npcs.items():
            if npc.cover_count < 3:
                shallow.append(f"NPC '{npc_id}' ({npc.name}): {npc.cover_count} cover option(s) (target: 3)")
        if shallow:
            self.report.add_issue(ValidationIssue(
                rule_number=38,
                level=ValidationLevel.ADVISORY,
                title="Cover Story Depth",
                message="NPCs with fewer than 3 cover story options limit player creativity",
                details=shallow,
                fix_suggestion=(
                    "Add cover options until each NPC has 3. Each needs `cover_id`, "
                    "a one-sentence player cover identity, and an npc_reaction note."
                )
            ))

    def check_cross_role_info_chain(self):
        """Rule 39: At least one outcome must flow from one role to another via info_share or cross-prereq."""
        if len(self.roles) < 2:
            return  # Single-player has no cross-role requirement

        # Build: outcome_id -> set of roles that have an NPC_LLM task targeting it
        outcome_learned_by: Dict[str, set] = {}
        for task in self.tasks.values():
            if task.type in ('npc_llm', 'npc') and task.target_outcomes:
                for oid in task.target_outcomes:
                    outcome_learned_by.setdefault(oid, set()).add(task.role)

        # Build: outcome_id -> set of roles that have a task with that outcome as a prerequisite
        outcome_required_by: Dict[str, set] = {}
        for task in self.tasks.values():
            for prereq in task.prerequisites:
                if prereq['type'] == 'outcome':
                    outcome_required_by.setdefault(prereq['id'], set()).add(task.role)

        # A cross-role info chain exists when an outcome is learned by role A
        # and required (as a prerequisite) by role B where A != B
        chains_found = []
        for oid, learning_roles in outcome_learned_by.items():
            requiring_roles = outcome_required_by.get(oid, set())
            for lr in learning_roles:
                for rr in requiring_roles:
                    if lr != rr:
                        chains_found.append(f"outcome `{oid}`: learned by {lr}, needed by {rr}")

        if not chains_found:
            self.report.add_issue(ValidationIssue(
                rule_number=39,
                level=ValidationLevel.IMPORTANT,
                title="No Cross-Role Information Chain",
                message=(
                    "No outcome flows from one role's NPC task to another role's prerequisite. "
                    "Players are working in isolation — they never need each other's intel."
                ),
                details=[
                    "Need at least one chain: Role A learns outcome X from NPC, Role B has a task "
                    "that requires Outcome X as a prerequisite (or Role A has an info_share task that passes X to Role B)"
                ],
                fix_suggestion=(
                    "Add an info_share task for Role A (with the NPC outcome as a prerequisite) "
                    "and add 'Outcome X' as a prerequisite on one of Role B's tasks."
                )
            ))


def main():
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python validate_scenario.py <experience_file.md>")
        sys.exit(1)
    
    experience_file = Path(sys.argv[1])
    if not experience_file.exists():
        print(f"Error: File not found: {experience_file}")
        sys.exit(1)
    
    validator = ScenarioValidator(experience_file)
    report = validator.validate_all()
    report.print_report()
    
    sys.exit(0 if report.passed else 1)


if __name__ == '__main__':
    main()
