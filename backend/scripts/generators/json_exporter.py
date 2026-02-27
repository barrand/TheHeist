"""
JSON Exporter
Serializes scenario graphs to JSON format for backend consumption
"""

import json
from pathlib import Path
from typing import Optional
from dataclasses import asdict


def export_to_json(graph, output_path: Optional[str] = None) -> str:
    """
    Export scenario graph to JSON file.
    
    Args:
        graph: ScenarioGraph instance
        output_path: Optional path to write JSON. If None, auto-generates path.
    
    Returns:
        Path to written JSON file
    """
    
    # Convert dataclasses to dict
    graph_dict = asdict(graph)
    
    # Clean up None values and empty lists for readability
    graph_dict = _clean_dict(graph_dict)
    
    # Determine output path
    if output_path is None:
        output_dir = Path(__file__).parent.parent.parent / "experiences"
        output_dir.mkdir(exist_ok=True)
        output_path = output_dir / f"{graph.scenario_id}.json"
    else:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Write JSON with pretty formatting
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(graph_dict, f, indent=2, ensure_ascii=False)
    
    return str(output_path)


def _clean_dict(d):
    """Recursively clean dict by removing None values and empty collections"""
    if isinstance(d, dict):
        cleaned = {}
        for k, v in d.items():
            cleaned_v = _clean_dict(v)
            # Keep the value if it's not None, not empty list/dict, or if it's a boolean/number
            if cleaned_v is not None and (
                cleaned_v != [] and cleaned_v != {} or 
                isinstance(cleaned_v, (bool, int, float)) or
                isinstance(cleaned_v, str)
            ):
                cleaned[k] = cleaned_v
        return cleaned
    elif isinstance(d, list):
        return [_clean_dict(item) for item in d]
    else:
        return d


def load_from_json(json_path: str):
    """
    Load scenario graph from JSON file.
    
    Args:
        json_path: Path to JSON file
    
    Returns:
        Dict representing the scenario graph
    """
    with open(json_path, 'r', encoding='utf-8') as f:
        return json.load(f)
