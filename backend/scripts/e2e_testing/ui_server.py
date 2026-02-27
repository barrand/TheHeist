#!/usr/bin/env python3
"""
E2E Testing UI Server

Web-based UI for managing scenario generation and E2E testing.
"""

import os
import json
import subprocess
import signal
import asyncio
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List
from dataclasses import dataclass, asdict

from flask import Flask, render_template, jsonify, request, Response, stream_with_context
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Paths
BACKEND_ROOT = Path(__file__).parent.parent.parent
PROJECT_ROOT = BACKEND_ROOT.parent
EXPERIENCES_DIR = BACKEND_ROOT / "experiences"
ROLES_JSON = PROJECT_ROOT / "shared_data" / "roles.json"

# Role codes for task IDs (must match experience_loader.py)
ROLE_CODES = {
    "mastermind": "MM", "hacker": "H", "safe_cracker": "SC", "insider": "I",
    "driver": "D", "grifter": "G", "muscle": "M", "lookout": "L",
    "fence": "F", "cat_burglar": "CB", "cleaner": "CL", "pickpocket": "PP",
}
BACKEND_LOG = Path("/tmp/heist_logs/backend.log")
E2E_LOG = Path("/tmp/heist_logs/e2e_test.log")

# Global state
current_test_process: Optional[subprocess.Popen] = None
backend_process: Optional[subprocess.Popen] = None


@dataclass
class ScenarioInfo:
    id: str
    name: str
    player_count: int
    task_count: int
    roles: List[str]
    has_json: bool
    has_md: bool


def discover_scenarios() -> List[ScenarioInfo]:
    """Find all generated scenarios"""
    scenarios = {}
    
    # Find all JSON scenarios
    for json_file in EXPERIENCES_DIR.glob("*.json"):
        try:
            data = json.load(open(json_file))
            scenario_id = data.get("scenario_id", json_file.stem)
            
            # Count roles
            roles = set()
            for task in data.get("tasks", []):
                roles.add(task.get("assigned_role"))
            
            scenarios[scenario_id] = ScenarioInfo(
                id=scenario_id,
                name=scenario_id.replace("_", " ").title(),
                player_count=len(roles),
                task_count=len(data.get("tasks", [])),
                roles=sorted(list(roles)),
                has_json=True,
                has_md=(EXPERIENCES_DIR / f"generated_{scenario_id}_{len(roles)}players.md").exists()
            )
        except Exception as e:
            print(f"Error loading {json_file}: {e}")
    
    return sorted(scenarios.values(), key=lambda s: s.name)


@app.route("/")
def index():
    """Main UI page"""
    return render_template("index.html")


@app.route("/api/scenarios")
def list_scenarios():
    """Get list of available scenarios"""
    scenarios = discover_scenarios()
    return jsonify([asdict(s) for s in scenarios])


@app.route("/api/scenarios/<scenario_id>", methods=["DELETE"])
def delete_scenario(scenario_id):
    """Delete a single scenario (both .md and .json files)"""
    deleted = []
    try:
        for f in EXPERIENCES_DIR.glob(f"*{scenario_id}*.json"):
            f.unlink()
            deleted.append(f.name)
        for f in EXPERIENCES_DIR.glob(f"*{scenario_id}*.md"):
            if not f.name.startswith("README") and not f.name.endswith("_FORMAT.md"):
                f.unlink()
                deleted.append(f.name)
        return jsonify({"success": True, "deleted": deleted})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


@app.route("/api/scenarios", methods=["DELETE"])
def delete_all_scenarios():
    """Delete all generated scenario files"""
    deleted = []
    protected = {"README.md", "NPC_FORMAT.md", "INVENTORY_FORMAT.md"}
    try:
        for f in EXPERIENCES_DIR.glob("generated_*.md"):
            f.unlink()
            deleted.append(f.name)
        for f in EXPERIENCES_DIR.glob("*.json"):
            f.unlink()
            deleted.append(f.name)
        return jsonify({"success": True, "deleted": deleted, "count": len(deleted)})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


@app.route("/api/generate", methods=["POST"])
def generate_scenario():
    """Generate a new scenario — streams NDJSON progress lines"""
    data = request.json
    scenario_id = data.get("scenario_id", "custom_heist")
    roles = data.get("roles", ["mastermind", "hacker"])
    seed = data.get("seed")

    def _line(payload: dict) -> str:
        return json.dumps(payload) + "\n"

    def _progress(msg: str) -> str:
        return _line({"type": "progress", "message": msg})

    def generate():
        import sys
        sys.path.insert(0, str(BACKEND_ROOT / "scripts"))

        try:
            yield _progress(f"Starting generation: {scenario_id} with {len(roles)} roles")

            yield _progress("Loading generators...")
            from generators.procedural_generator import generate_scenario_graph, GeneratorConfig
            from generators.graph_validator_fixer import validate_and_fix_graph
            from generators.json_exporter import export_to_json
            from generators.markdown_renderer import export_to_markdown

            yield _progress("Generating scenario graph...")
            config = GeneratorConfig(seed=seed if seed else None)
            graph = generate_scenario_graph(scenario_id, roles, config)
            yield _progress(f"Graph: {len(graph.tasks)} tasks, {len(graph.locations)} locations")

            yield _progress("Validating and fixing graph...")
            fixed_graph, validation_result = validate_and_fix_graph(graph, max_iterations=10)
            if not validation_result.is_valid:
                yield _line({
                    "type": "result", "success": False,
                    "error": "Graph validation failed",
                    "errors": validation_result.errors
                })
                return
            fixed_count = len(validation_result.fixes_applied)
            yield _progress(f"Graph valid" + (f" ({fixed_count} issues auto-fixed)" if fixed_count else ""))

            yield _progress("Exporting to JSON and markdown...")
            export_to_json(fixed_graph)
            export_to_markdown(fixed_graph)
            player_count = len(roles)
            exported_filename = f"generated_{scenario_id}_{player_count}players.md"
            yield _progress(f"Exported: {exported_filename}")

            yield _progress("Validating scenario markdown...")
            from validate_scenario import ScenarioValidator, ValidationLevel
            md_path = EXPERIENCES_DIR / exported_filename
            validator = ScenarioValidator(md_path)
            report = validator.validate_all()
            critical_issues = [i for i in report.issues if i.level == ValidationLevel.CRITICAL]
            important_count = sum(1 for i in report.issues if i.level == ValidationLevel.IMPORTANT)
            yield _progress(
                f"Markdown validation: {len(critical_issues)} critical, {important_count} important"
            )

            if critical_issues:
                yield _progress(f"Running editor to fix {len(critical_issues)} critical issue(s)...")
                from scenario_editor_agent import ScenarioEditorAgent
                agent = ScenarioEditorAgent()
                for idx, issue in enumerate(critical_issues, 1):
                    yield _progress(f"  Fixing [{idx}/{len(critical_issues)}]: {issue.title}")
                results = agent.fix_issues(md_path, critical_issues)
                fixed_count = sum(1 for r in results if r.success)
                yield _progress(f"Editor done: {fixed_count}/{len(critical_issues)} fixed")
            else:
                yield _progress("✅ Markdown validation passed, no edits needed")

            yield _line({
                "type": "result",
                "success": True,
                "scenario_id": scenario_id,
                "player_count": player_count,
                "tasks": len(fixed_graph.tasks),
                "locations": len(fixed_graph.locations),
                "items": len(fixed_graph.items),
            })

        except Exception as e:
            import traceback
            yield _line({
                "type": "result",
                "success": False,
                "error": str(e),
                "traceback": traceback.format_exc()
            })

    return Response(
        stream_with_context(generate()),
        mimetype="application/x-ndjson",
        headers={"X-Accel-Buffering": "no", "Cache-Control": "no-cache"},
    )


@app.route("/api/test/start", methods=["POST"])
def start_test():
    """Start E2E test on a scenario"""
    global current_test_process
    
    data = request.json
    scenario_file = data.get("scenario_file")
    difficulty = data.get("difficulty", "easy")
    skip_npc = data.get("skip_npc", True)
    
    if current_test_process and current_test_process.poll() is None:
        return jsonify({"success": False, "error": "Test already running"})
    
    try:
        cmd = [
            "python3",
            "scripts/test_gameplay_e2e.py",
            "--scenario", scenario_file,
            "--difficulty", difficulty,
        ]
        
        if skip_npc:
            cmd.append("--skip-npc")
        
        # Clear E2E log
        if E2E_LOG.exists():
            E2E_LOG.unlink()
        E2E_LOG.parent.mkdir(parents=True, exist_ok=True)
        E2E_LOG.touch()
        
        # Start process with log redirection
        log_file = open(E2E_LOG, "w")
        current_test_process = subprocess.Popen(
            cmd,
            cwd=str(BACKEND_ROOT),
            stdout=log_file,
            stderr=subprocess.STDOUT,
            preexec_fn=os.setsid if os.name != 'nt' else None
        )
        
        return jsonify({
            "success": True,
            "pid": current_test_process.pid,
            "scenario": scenario_file
        })
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


@app.route("/api/test/stop", methods=["POST"])
def stop_test():
    """Stop running E2E test"""
    global current_test_process
    
    if current_test_process and current_test_process.poll() is None:
        try:
            # Kill process group to stop all children
            os.killpg(os.getpgid(current_test_process.pid), signal.SIGTERM)
            current_test_process.wait(timeout=5)
            return jsonify({"success": True})
        except Exception as e:
            return jsonify({"success": False, "error": str(e)})
    
    return jsonify({"success": False, "error": "No test running"})


@app.route("/api/test/status")
def test_status():
    """Get current test status"""
    global current_test_process
    
    if current_test_process:
        is_running = current_test_process.poll() is None
        return jsonify({
            "running": is_running,
            "pid": current_test_process.pid if is_running else None,
            "exit_code": current_test_process.returncode if not is_running else None
        })
    
    return jsonify({"running": False, "pid": None, "exit_code": None})


@app.route("/api/logs/backend/stream")
def stream_backend_log():
    """Stream backend log in real-time"""
    def generate():
        # Send existing log content first
        if BACKEND_LOG.exists():
            with open(BACKEND_LOG) as f:
                lines = f.readlines()
                # Send last 100 lines
                for line in lines[-100:]:
                    yield f"data: {json.dumps({'line': line.rstrip()})}\n\n"
        
        # Then tail -f for new content
        try:
            process = subprocess.Popen(
                ["tail", "-f", str(BACKEND_LOG)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            for line in iter(process.stdout.readline, ""):
                if line:
                    yield f"data: {json.dumps({'line': line.rstrip()})}\n\n"
                    
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
    
    return Response(generate(), mimetype="text/event-stream")


@app.route("/api/logs/e2e/stream")
def stream_e2e_log():
    """Stream E2E test log in real-time"""
    def generate():
        # Wait for log file to exist
        max_wait = 30
        waited = 0
        while not E2E_LOG.exists() and waited < max_wait:
            import time
            time.sleep(0.5)
            waited += 0.5
        
        if not E2E_LOG.exists():
            yield f"data: {json.dumps({'line': 'Waiting for E2E test to start...'})}\n\n"
            return
        
        # Tail the log
        try:
            process = subprocess.Popen(
                ["tail", "-f", str(E2E_LOG)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            for line in iter(process.stdout.readline, ""):
                if line:
                    yield f"data: {json.dumps({'line': line.rstrip()})}\n\n"
                    
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
    
    return Response(generate(), mimetype="text/event-stream")


@app.route("/api/config/roles")
def get_available_roles():
    """Get list of available player roles from shared_data/roles.json"""
    try:
        data = json.load(open(ROLES_JSON))
        roles = []
        for r in data.get("roles", []):
            role_id = r.get("role_id", "")
            name = r.get("name", role_id.replace("_", " ").title())
            code = ROLE_CODES.get(role_id, role_id[:2].upper() if len(role_id) >= 2 else "X")
            roles.append({"id": role_id, "name": name, "code": code})
        return jsonify(roles)
    except Exception as e:
        print(f"Error loading roles from {ROLES_JSON}: {e}")
        # Fallback to minimal set
        return jsonify([
            {"id": "mastermind", "name": "Mastermind", "code": "MM"},
            {"id": "hacker", "name": "Hacker", "code": "H"},
            {"id": "safe_cracker", "name": "Safe Cracker", "code": "SC"},
        ])


@app.route("/api/config/scenario_types")
def get_scenario_types():
    """Get list of scenario type templates"""
    return jsonify([
        {"id": "museum_heist", "name": "Museum Heist"},
        {"id": "bank_vault", "name": "Bank Vault"},
        {"id": "office_infiltration", "name": "Office Infiltration"},
        {"id": "casino_heist", "name": "Casino Heist"},
        {"id": "art_gallery", "name": "Art Gallery"},
        {"id": "mansion_safe", "name": "Mansion Safe"},
        {"id": "custom_heist", "name": "Custom Heist"},
    ])


if __name__ == "__main__":
    import os
    port = int(os.environ.get("E2E_PORT", "5555"))
    
    print("\n" + "="*60)
    print("🎮 E2E Testing UI Server")
    print("="*60)
    print(f"Backend root: {BACKEND_ROOT}")
    print(f"Scenarios: {EXPERIENCES_DIR}")
    print(f"Opening at: http://localhost:{port}")
    print("="*60 + "\n")
    
    # Open browser automatically
    import webbrowser
    import threading
    def open_browser():
        import time
        time.sleep(1)
        webbrowser.open(f"http://localhost:{port}")
    
    threading.Thread(target=open_browser, daemon=True).start()
    
    app.run(host="localhost", port=port, debug=False, threaded=True)
