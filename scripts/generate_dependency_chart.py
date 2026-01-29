#!/usr/bin/env python3
import argparse
import json
import os
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse


DATA_DIR_DEFAULT = os.path.join(os.path.dirname(__file__), "..", "data")
PHASES = ["Infiltrate", "Access", "Acquire", "Escape"]

ROLE_PHASES = {
    "mastermind": ["Infiltrate", "Access", "Acquire", "Escape"],
    "hacker": ["Access", "Acquire"],
    "safe_cracker": ["Acquire"],
    "driver": ["Escape"],
    "insider": ["Infiltrate", "Access"],
    "grifter": ["Infiltrate"],
    "muscle": ["Access", "Escape"],
    "lookout": ["Infiltrate", "Escape"],
    "fence": ["Acquire", "Escape"],
    "cat_burglar": ["Infiltrate", "Acquire"],
    "cleaner": ["Escape"],
    "pickpocket": ["Infiltrate", "Acquire"],
}


def load_json(path):
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def get_scenario(scenarios, scenario_id):
    for scenario in scenarios:
        if scenario.get("scenario_id") == scenario_id:
            return scenario
    return None


def get_role_map(roles):
    return {role["role_id"]: role for role in roles}


def sanitize_node_id(value):
    return "".join(ch for ch in value if ch.isalnum() or ch in ("_", "-"))


def build_mermaid(scenario, selected_roles, role_map):
    lines = ["flowchart TD"]
    scenario_node_id = sanitize_node_id(scenario["scenario_id"])
    scenario_label = scenario["name"]

    lines.append(f'  {scenario_node_id}["{scenario_label}"]')

    for phase in PHASES:
        phase_id = sanitize_node_id(phase)
        lines.append(f"  {phase_id}[{phase}]")

    lines.append(f"  {scenario_node_id} --> {sanitize_node_id(PHASES[0])}")
    for idx in range(len(PHASES) - 1):
        current_phase = sanitize_node_id(PHASES[idx])
        next_phase = sanitize_node_id(PHASES[idx + 1])
        lines.append(f"  {current_phase} --> {next_phase}")

    for role_id in selected_roles:
        role = role_map.get(role_id)
        if not role:
            continue
        role_node_id = f"role_{sanitize_node_id(role_id)}"
        role_label = role["name"]
        lines.append(f'  {role_node_id}["{role_label}"]')

        phase_targets = ROLE_PHASES.get(role_id, PHASES)
        for phase in phase_targets:
            lines.append(f"  {role_node_id} --> {sanitize_node_id(phase)}")

    return "\n".join(lines)


def generate_chart(scenario_id, roles, data_dir):
    scenarios_path = os.path.join(data_dir, "scenarios.json")
    roles_path = os.path.join(data_dir, "roles.json")

    scenarios_data = load_json(scenarios_path)
    roles_data = load_json(roles_path)

    scenario = get_scenario(scenarios_data.get("scenarios", []), scenario_id)
    if not scenario:
        raise ValueError(f"Unknown scenario_id: {scenario_id}")

    role_map = get_role_map(roles_data.get("roles", []))
    missing_roles = [role_id for role_id in roles if role_id not in role_map]
    if missing_roles:
        raise ValueError(f"Unknown role ids: {', '.join(missing_roles)}")

    return build_mermaid(scenario, roles, role_map)


class DependencyChartHandler(BaseHTTPRequestHandler):
    data_dir = DATA_DIR_DEFAULT

    def _set_headers(self, status_code=200, content_type="text/plain"):
        self.send_response(status_code)
        self.send_header("Content-Type", content_type)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_OPTIONS(self):
        self._set_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path in ("/", "/health"):
            self._set_headers(200)
            self.wfile.write(b"Dependency chart server running.")
            return
        self._set_headers(404)
        self.wfile.write(b"Not found")

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path != "/generate":
            self._set_headers(404)
            self.wfile.write(b"Not found")
            return

        content_length = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(content_length)

        try:
            payload = json.loads(body.decode("utf-8"))
            scenario_id = payload.get("scenario_id")
            roles = payload.get("roles", [])

            if not scenario_id:
                raise ValueError("scenario_id is required")
            if not isinstance(roles, list) or len(roles) == 0:
                raise ValueError("roles must be a non-empty list")

            mermaid = generate_chart(scenario_id, roles, self.data_dir)
            self._set_headers(200)
            self.wfile.write(mermaid.encode("utf-8"))
        except Exception as exc:
            self._set_headers(400)
            self.wfile.write(str(exc).encode("utf-8"))


def run_server(host, port, data_dir):
    DependencyChartHandler.data_dir = data_dir
    server = HTTPServer((host, port), DependencyChartHandler)
    print(f"Dependency chart server running on http://{host}:{port}")
    server.serve_forever()


def main():
    parser = argparse.ArgumentParser(description="Generate a Mermaid dependency chart.")
    parser.add_argument("--scenario-id", help="Scenario id from scenarios.json")
    parser.add_argument(
        "--roles",
        help="Comma-separated role ids from roles.json",
    )
    parser.add_argument(
        "--data-dir",
        default=DATA_DIR_DEFAULT,
        help="Path to data directory containing scenarios.json and roles.json",
    )
    parser.add_argument(
        "--serve",
        action="store_true",
        help="Run a local HTTP server for the UI",
    )
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()

    if args.serve:
        run_server(args.host, args.port, args.data_dir)
        return

    if not args.scenario_id or not args.roles:
        parser.error("--scenario-id and --roles are required unless --serve is used")

    roles = [role_id.strip() for role_id in args.roles.split(",") if role_id.strip()]
    chart = generate_chart(args.scenario_id, roles, args.data_dir)
    print(chart)


if __name__ == "__main__":
    main()
