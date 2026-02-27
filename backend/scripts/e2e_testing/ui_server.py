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

from flask import Flask, render_template, jsonify, request, Response
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Paths
BACKEND_ROOT = Path(__file__).parent.parent.parent
EXPERIENCES_DIR = BACKEND_ROOT / "experiences"
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


@app.route("/api/generate", methods=["POST"])
def generate_scenario():
    """Generate a new scenario"""
    data = request.json
    scenario_id = data.get("scenario_id", "custom_heist")
    roles = data.get("roles", ["mastermind", "hacker"])
    seed = data.get("seed")
    
    try:
        # Import generator
        import sys
        sys.path.insert(0, str(BACKEND_ROOT / "scripts"))
        
        from generators.procedural_generator import generate_scenario_graph, GeneratorConfig
        from generators.graph_validator import validate_graph
        from generators.json_exporter import export_to_json
        from generators.markdown_renderer import export_to_markdown
        
        # Generate
        config = GeneratorConfig(seed=seed if seed else None)
        graph = generate_scenario_graph(scenario_id, roles, config)
        
        # Validate
        result = validate_graph(graph)
        
        if not result.valid:
            return jsonify({
                "success": False,
                "error": "Validation failed",
                "errors": [f"{e.severity}: {e.message}" for e in result.errors]
            })
        
        # Export
        export_to_json(graph)
        export_to_markdown(graph)
        
        return jsonify({
            "success": True,
            "scenario_id": scenario_id,
            "tasks": len(graph.tasks),
            "locations": len(graph.locations),
            "items": len(graph.items)
        })
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


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
    """Get list of available player roles"""
    return jsonify([
        {"id": "mastermind", "name": "Mastermind", "code": "MM"},
        {"id": "hacker", "name": "Hacker", "code": "H"},
        {"id": "safe_cracker", "name": "Safe Cracker", "code": "SC"},
        {"id": "insider", "name": "Insider", "code": "I"},
        {"id": "driver", "name": "Driver", "code": "D"},
        {"id": "grifter", "name": "Grifter", "code": "G"},
        {"id": "muscle", "name": "Muscle", "code": "M"},
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
    print("\n" + "="*60)
    print("🎮 E2E Testing UI Server")
    print("="*60)
    print(f"Backend root: {BACKEND_ROOT}")
    print(f"Scenarios: {EXPERIENCES_DIR}")
    print(f"Opening at: http://localhost:5555")
    print("="*60 + "\n")
    
    # Open browser automatically
    import webbrowser
    import threading
    def open_browser():
        import time
        time.sleep(1)
        webbrowser.open("http://localhost:5555")
    
    threading.Thread(target=open_browser, daemon=True).start()
    
    app.run(host="localhost", port=5555, debug=False, threaded=True)
