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

    MAX_GENERATION_ATTEMPTS = 3
    # Structural rules: fixed by graph_validator_fixer. NPC rules: sent to editor.
    NPC_QUALITY_RULES = {36, 37, 38, 39}

    try:
        # ── 1. Import generators ───────────────────────────────────────────
        _emit("Loading generators...")
        from generators.procedural_generator import generate_scenario_graph, GeneratorConfig
        from generators.graph_validator_fixer import validate_and_fix_graph
        from generators.json_exporter import export_to_json
        from generators.markdown_renderer import export_to_markdown
        from validate_scenario import ScenarioValidator, ValidationLevel

        def _issue_line(issue):
            tag = "🔴" if issue.level == ValidationLevel.CRITICAL else "⚠️ "
            detail = "; ".join(issue.details[:2]) if issue.details else ""
            return f"  {tag} {issue.title}" + (f": {detail}" if detail else "")

        for attempt in range(1, MAX_GENERATION_ATTEMPTS + 1):
            if attempt > 1:
                _emit(f"♻️  Attempt {attempt}/{MAX_GENERATION_ATTEMPTS} — regenerating (previous attempt had unresolved critical structural issues)...")

            # ── 2. Generate graph ──────────────────────────────────────────
            _emit("Generating scenario graph...")
            config = GeneratorConfig(seed=seed)
            try:
                graph = generate_scenario_graph(
                    scenario_id, roles, config,
                    progress_fn=lambda msg: _emit(f"  {msg}"),
                )
            except ValueError as raw_err:
                # Raw graph had unresolvable cycles before enrichment — retry
                _emit(f"  🔴 Raw graph cycle detected before enrichment: {raw_err}")
                if attempt < MAX_GENERATION_ATTEMPTS:
                    _emit(f"  Retrying (attempt {attempt + 1}/{MAX_GENERATION_ATTEMPTS})...")
                    seed = None  # Use fresh random seed on retry
                    continue
                raise RuntimeError(
                    f"Raw graph cycle could not be resolved after {MAX_GENERATION_ATTEMPTS} attempts"
                ) from raw_err
            _emit(
                f"Graph complete: {len(graph.tasks)} tasks, "
                f"{len(graph.locations)} locations, {len(graph.npcs)} NPCs"
            )

            # ── 3. Graph topology fixer ────────────────────────────────────
            # Mutates the in-memory graph: breaks cycles, connects orphans,
            # wires mid-sequence dead-ends. Does NOT simulate gameplay.
            _emit("── [1/3] Graph topology fix...")
            fixed_graph, validation_result = validate_and_fix_graph(graph, max_iterations=10)
            if not validation_result.is_valid:
                raise RuntimeError(
                    f"Graph validation failed: {'; '.join(validation_result.errors)}"
                )
            fix_count = len(validation_result.fixes_applied)
            for fix_msg in validation_result.fixes_applied:
                _emit(f"  {fix_msg}")
            if fix_count:
                _emit(f"  Topology fixed ({fix_count} auto-fix(es) applied)")
            else:
                _emit(f"  Topology clean — no fixes needed")

            # ── 4. Export to JSON + markdown ───────────────────────────────
            _emit("Exporting to JSON and markdown...")
            export_to_json(fixed_graph, roles=roles)
            export_to_markdown(fixed_graph, roles=roles)
            base_name = _cache_filename(scenario_id, roles)
            md_path = _EXPERIENCES_DIR / f"{base_name}.md"
            _emit(f"  Exported: {md_path.name}")

            # ── 5. Playability simulation + NPC quality check ──────────────
            # Playability (Rule 31): simulates 500 turns — catches deadlocks
            #   that pure topology checks can't see (e.g. outcomes never produced).
            # NPC quality (Rules 36-39): story/interaction quality → sent to editor.
            _emit("── [2/3] Playability simulation...")
            validator = ScenarioValidator(md_path)
            report = validator.validate_all()
            critical  = [i for i in report.issues if i.level == ValidationLevel.CRITICAL]
            important = [i for i in report.issues if i.level == ValidationLevel.IMPORTANT]
            advisory  = [i for i in report.issues if i.level == ValidationLevel.ADVISORY]

            # Deadlock = Rule 31 (playability sim). Other structural = topology bugs that
            # slipped past the fixer. NPC quality = sent to editor.
            DEADLOCK_RULE = 31
            deadlock_issues    = [i for i in critical if i.rule_number == DEADLOCK_RULE]
            other_structural   = [i for i in (critical + important)
                                  if i.rule_number not in NPC_QUALITY_RULES and i.rule_number != DEADLOCK_RULE]
            npc_issues         = [i for i in (critical + important) if i.rule_number in NPC_QUALITY_RULES]
            critical_structural = deadlock_issues + [i for i in other_structural if i.level == ValidationLevel.CRITICAL]

            if deadlock_issues:
                _emit(f"  🔴 Deadlock detected — gameplay simulator could not complete all tasks")
                for issue in deadlock_issues:
                    _emit(f"     {issue.message}")
            else:
                _emit(f"  ✅ Playability OK — no deadlocks found")

            if other_structural:
                _emit(f"  Structural issues ({len(other_structural)}):")
                for issue in other_structural:
                    _emit(f"    {_issue_line(issue)}")

            if advisory:
                _emit(f"  Advisory: " + ", ".join(i.title for i in advisory))

            # ── 5b. Retry if critical structural issues remain ─────────────
            if critical_structural and attempt < MAX_GENERATION_ATTEMPTS:
                reasons = ", ".join(i.title for i in critical_structural)
                _emit(
                    f"  ♻️  Critical issue(s) [{reasons}] — regenerating "
                    f"(attempt {attempt + 1}/{MAX_GENERATION_ATTEMPTS})..."
                )
                seed = None
                continue

            if critical_structural:
                _emit(
                    f"  🔴 {len(critical_structural)} critical issue(s) unresolved after "
                    f"{MAX_GENERATION_ATTEMPTS} attempts — scenario may not be playable"
                )

            # ── 6. NPC quality editor (rules 36–39) ───────────────────────
            # Only NPC quality rules go to the LLM editor. Structural bugs must
            # be fixed by the generator/fixer, not patched with text rewrites.
            _emit("── [3/3] NPC quality check...")
            if npc_issues:
                _emit(f"  {len(npc_issues)} NPC quality issue(s) found — sending to editor...")
                from scenario_editor_agent import ScenarioEditorAgent
                agent = ScenarioEditorAgent()
                results = []
                for idx, issue in enumerate(npc_issues, 1):
                    tag = "🔴" if issue.level == ValidationLevel.CRITICAL else "🟡"
                    _emit(f"  {tag} [{idx}/{len(npc_issues)}]: {issue.title}")
                    result = agent.fix_issues(md_path, [issue], max_issues=1)[0]
                    results.append(result)
                    _emit(f"    {'✓ fixed' if result.success else '✗ could not fix'}")
                fixed_count = sum(1 for r in results if r.success)
                _emit(f"  Editor: {fixed_count}/{len(npc_issues)} fixed")

                # Post-edit re-validation
                report2 = ScenarioValidator(md_path).validate_all()
                c2  = [i for i in report2.issues if i.level == ValidationLevel.CRITICAL]
                im2 = [i for i in report2.issues if i.level == ValidationLevel.IMPORTANT]
                ad2 = [i for i in report2.issues if i.level == ValidationLevel.ADVISORY]
                npc2    = [i for i in (c2 + im2) if i.rule_number in NPC_QUALITY_RULES]
                struct2 = [i for i in (c2 + im2) if i.rule_number not in NPC_QUALITY_RULES]
                if not c2 and not im2:
                    _emit("  ✅ All NPC quality issues resolved")
                else:
                    for issue in npc2:
                        _emit(f"  ✗ Still open (NPC): {issue.title}")
                    for issue in struct2:
                        _emit(f"  ✗ Still open (structural): {issue.title}")
                critical, important, advisory = c2, im2, ad2
            else:
                _emit("  ✅ No NPC quality issues")

            # ── 8. Final pipeline summary ──────────────────────────────────
            total_unresolved = len(critical) + len(important)
            if total_unresolved == 0:
                _emit(
                    f"✅ Done — {len(fixed_graph.tasks)} tasks, "
                    f"{len(fixed_graph.locations)} locations, "
                    f"{len(fixed_graph.items)} items, "
                    f"0 unresolved issues"
                )
            else:
                _emit(
                    f"⚠️  Done with {total_unresolved} unresolved issue(s) — "
                    f"{len(fixed_graph.tasks)} tasks, "
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

        # All attempts exhausted with unresolved critical structural issues
        raise RuntimeError(
            f"Scenario has unresolvable critical structural issues after "
            f"{MAX_GENERATION_ATTEMPTS} generation attempts"
        )

    except Exception as exc:
        import traceback as _tb
        tb = _tb.format_exc()
        _emit(f"❌ Failed: {exc}")
        logger.error(f"[pipeline] Generation failed: {exc}\n{tb}")
        return PipelineResult(success=False, error=str(exc), traceback=tb)
