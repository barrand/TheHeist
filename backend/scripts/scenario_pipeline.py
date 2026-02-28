"""
Scenario Pipeline — Single Source of Truth

This is the ONE place that runs the full scenario generation pipeline:
  procedural_generator → graph_validator_fixer → json_exporter
  → markdown_renderer → validate_scenario → scenario_editor_agent

Both the E2E portal (ui_server.py) and the live game service
(app/services/scenario_generator_service.py) call this module.
Neither contains its own copy of the pipeline logic.

Usage:
    from scenario_pipeline import run_pipeline, PipelineResult

    result = run_pipeline(
        scenario_id="museum_heist",
        roles=["mastermind", "hacker"],
        progress_fn=lambda msg: print(msg),   # optional
    )
    if result.success:
        # result.md_path is ready to load
        ...
"""

import logging
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, List, Optional

logger = logging.getLogger(__name__)

# Canonical paths — scripts/ and experiences/ live relative to this file
_SCRIPTS_DIR = Path(__file__).parent
_EXPERIENCES_DIR = Path(__file__).parent.parent / "experiences"


def _cache_filename(scenario_id: str, roles: List[str]) -> str:
    """
    Derive the base filename (no extension) for a cached scenario.
    Cache key = scenario_id + sorted role list.
    Example: "generated_museum_heist_hacker_mastermind"
    """
    roles_part = "_".join(sorted(roles))
    return f"generated_{scenario_id}_{roles_part}"


@dataclass
class PipelineResult:
    success: bool
    md_path: Optional[Path] = None
    tasks: int = 0
    locations: int = 0
    items: int = 0
    npcs: int = 0
    # Issues remaining after the full pipeline (including editor pass)
    remaining_critical: int = 0
    remaining_important: int = 0
    remaining_advisory: int = 0
    error: Optional[str] = None
    traceback: Optional[str] = None


def run_pipeline(
    scenario_id: str,
    roles: List[str],
    seed: Optional[int] = None,
    progress_fn: Optional[Callable[[str], None]] = None,
) -> PipelineResult:
    """
    Run the full scenario generation pipeline synchronously.

    This function is blocking (LLM calls, file I/O) and should be called
    from a thread pool by any async caller (asyncio.run_in_executor, etc.).

    Args:
        scenario_id: e.g. "museum_heist"
        roles: list of role_id strings selected by players
        seed: optional RNG seed for reproducible generation
        progress_fn: optional callback called with a human-readable progress
                     string at each pipeline step.

    Returns:
        PipelineResult with success=True and md_path set on success.
    """
    def _emit(msg: str):
        logger.info(f"[pipeline] {msg}")
        if progress_fn:
            progress_fn(msg)

    # Ensure scripts/ is on sys.path for all generator/validator imports
    scripts_str = str(_SCRIPTS_DIR)
    if scripts_str not in sys.path:
        sys.path.insert(0, scripts_str)

    try:
        # ── 1. Import generators ───────────────────────────────────────────
        _emit("Loading generators...")
        from generators.procedural_generator import generate_scenario_graph, GeneratorConfig
        from generators.graph_validator_fixer import validate_and_fix_graph
        from generators.json_exporter import export_to_json
        from generators.markdown_renderer import export_to_markdown
        from validate_scenario import ScenarioValidator, ValidationLevel

        # ── 2. Generate graph ──────────────────────────────────────────────
        _emit("Generating scenario graph...")
        config = GeneratorConfig(seed=seed)
        graph = generate_scenario_graph(
            scenario_id, roles, config,
            progress_fn=lambda msg: _emit(f"  {msg}"),
        )
        _emit(
            f"Graph complete: {len(graph.tasks)} tasks, "
            f"{len(graph.locations)} locations, {len(graph.npcs)} NPCs"
        )

        # ── 3. Validate and auto-fix graph ─────────────────────────────────
        _emit("Validating and fixing graph...")
        fixed_graph, validation_result = validate_and_fix_graph(graph, max_iterations=10)
        if not validation_result.is_valid:
            raise RuntimeError(
                f"Graph validation failed: {'; '.join(validation_result.errors)}"
            )
        fix_count = len(validation_result.fixes_applied)
        _emit("Graph valid" + (f" ({fix_count} issues auto-fixed)" if fix_count else ""))

        # ── 4. Export to JSON + markdown ───────────────────────────────────
        _emit("Exporting to JSON and markdown...")
        export_to_json(fixed_graph, roles=roles)
        export_to_markdown(fixed_graph, roles=roles)
        base_name = _cache_filename(scenario_id, roles)
        md_path = _EXPERIENCES_DIR / f"{base_name}.md"
        _emit(f"Exported: {md_path.name}")

        # ── 5. Markdown validation ─────────────────────────────────────────
        _emit("Validating scenario markdown...")
        validator = ScenarioValidator(md_path)
        report = validator.validate_all()
        critical = [i for i in report.issues if i.level == ValidationLevel.CRITICAL]
        important = [i for i in report.issues if i.level == ValidationLevel.IMPORTANT]
        advisory = [i for i in report.issues if i.level == ValidationLevel.ADVISORY]
        _emit(
            f"Markdown validation: {len(critical)} critical, "
            f"{len(important)} important, {len(advisory)} advisory"
        )
        for issue in critical:
            detail = "; ".join(issue.details) if issue.details else ""
            _emit(f"  🔴 {issue.title}" + (f": {detail}" if detail else ""))
        for issue in important:
            detail = "; ".join(issue.details) if issue.details else ""
            _emit(f"  ⚠️  {issue.title}" + (f": {detail}" if detail else ""))
        for issue in advisory:
            detail = "; ".join(issue.details) if issue.details else ""
            _emit(f"  ℹ️  {issue.title}" + (f": {detail}" if detail else ""))

        # ── 6. Editor pass — fix critical AND important ────────────────────
        issues_to_fix = critical + important
        if issues_to_fix:
            _emit(
                f"Running editor to fix {len(issues_to_fix)} issue(s) "
                f"({len(critical)} critical, {len(important)} important)..."
            )
            from scenario_editor_agent import ScenarioEditorAgent
            agent = ScenarioEditorAgent()
            results = []
            for idx, issue in enumerate(issues_to_fix, 1):
                tag = "🔴" if issue.level == ValidationLevel.CRITICAL else "🟡"
                _emit(f"  {tag} [{idx}/{len(issues_to_fix)}]: {issue.title} — calling LLM...")
                result = agent.fix_issues(md_path, [issue], max_issues=1)[0]
                results.append(result)
                _emit(f"    {'✓ fixed' if result.success else '✗ could not fix'}")
            fixed_count = sum(1 for r in results if r.success)
            _emit(f"Editor done: {fixed_count}/{len(issues_to_fix)} issue(s) addressed")

            # ── 7. Post-edit re-validation ─────────────────────────────────
            report2 = ScenarioValidator(md_path).validate_all()
            c2 = [i for i in report2.issues if i.level == ValidationLevel.CRITICAL]
            im2 = [i for i in report2.issues if i.level == ValidationLevel.IMPORTANT]
            ad2 = [i for i in report2.issues if i.level == ValidationLevel.ADVISORY]
            _emit(
                f"Post-edit validation: {len(c2)} critical, "
                f"{len(im2)} important, {len(ad2)} advisory"
            )
            if not c2 and not im2:
                _emit("✅ All critical and important issues resolved")
            else:
                for i in c2 + im2:
                    _emit(f"  ⚠️  Still open: {i.title}")
            critical, important, advisory = c2, im2, ad2
        else:
            _emit("✅ No critical or important issues — scenario looks good")

        _emit(
            f"Done! {len(fixed_graph.tasks)} tasks, "
            f"{len(fixed_graph.locations)} locations, "
            f"{len(fixed_graph.items)} items"
        )

        return PipelineResult(
            success=True,
            md_path=md_path,
            tasks=len(fixed_graph.tasks),
            locations=len(fixed_graph.locations),
            items=len(fixed_graph.items),
            npcs=len(fixed_graph.npcs),
            remaining_critical=len(critical),
            remaining_important=len(important),
            remaining_advisory=len(advisory),
        )

    except Exception as exc:
        import traceback as _tb
        tb = _tb.format_exc()
        _emit(f"❌ Failed: {exc}")
        logger.error(f"[pipeline] Generation failed: {exc}\n{tb}")
        return PipelineResult(success=False, error=str(exc), traceback=tb)
