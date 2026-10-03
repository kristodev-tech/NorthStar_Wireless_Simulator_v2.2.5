"""Versioned validation before UI mutation, and atomic project writes."""

import copy
import json
import math
import os
import tempfile
from pathlib import Path
from ..domain.presets import RADIO_PROFILES
from ..domain.models import MATERIALS

RADIO_RANGES = {
    "tx_dbm": (-40, 40),
    "sens_dbm": (-150, -20),
    "freq_mhz": (100, 10000),
    "pl_d0_db": (0, 120),
    "n": (1, 6),
    "noise_sigma_db": (0, 20),
}


def number(value: object, low: float, high: float, name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (float, int)):
        raise ValueError(f"{name} must be numeric")
    result = float(value)
    if not math.isfinite(result) or not low <= result <= high:
        raise ValueError(f"{name} must be between {low} and {high}")
    return result


def validate_project(value: object) -> dict:
    if not isinstance(value, dict):
        raise ValueError("Project must be a JSON object")
    data = copy.deepcopy(value)
    if type(data.get("version", 1)) is not int or data.get("version", 1) not in (1, 2):
        raise ValueError("Unsupported project version; use a compatible application")
    nodes = data.get("nodes", [])
    obstacles = data.get("obstacles", [])
    if not isinstance(nodes, list) or len(nodes) > 100:
        raise ValueError("Project must contain at most 100 nodes")
    if not isinstance(obstacles, list) or len(obstacles) > 100:
        raise ValueError("Project must contain at most 100 obstacles")
    names: set[str] = set()
    numbers: set[tuple[str, int]] = set()
    technologies: set[str] = set()
    for node in nodes:
        if not isinstance(node, dict):
            raise ValueError("Invalid node record")
        key = node.get("profile_key")
        if key not in RADIO_PROFILES:
            raise ValueError(f"Unknown radio preset: {key}")
        for axis in ("x", "y"):
            number(node.get(axis, 100), -100000, 100000, axis)
        name = node.get("name")
        if not isinstance(name, str) or not name.strip() or len(name) > 120 or name in names:
            raise ValueError("Node names must be unique nonempty strings up to 120 characters")
        if any(ord(c) < 32 or ord(c) == 127 for c in name):
            raise ValueError("Node names cannot contain control characters")
        if "custom_name" in node and not isinstance(node["custom_name"], bool):
            raise ValueError("Custom name flag must be boolean")
        names.add(name)
        base = node.get("base_label", "Node")
        if not isinstance(base, str) or not base or len(base) > 80:
            raise ValueError("Invalid device label")
        num = node.get("type_number", 0)
        number(num, 0, 100000, "Device number")
        if int(num) != num:
            raise ValueError("Device number must be an integer")
        if num:
            identity = (base, int(num))
            if identity in numbers:
                raise ValueError("Duplicate device label and number")
            numbers.add(identity)
        radio = node.get("radio")
        if radio is not None:
            if not isinstance(radio, dict) or set(radio) != {"name", "tech", *RADIO_RANGES}:
                raise ValueError("Incomplete radio parameters")
            if radio["tech"] != RADIO_PROFILES[key].tech:
                raise ValueError("Radio family does not match the selected preset")
            if not isinstance(radio["name"], str) or len(radio["name"]) > 160:
                raise ValueError("Invalid radio name")
            for field, (low, high) in RADIO_RANGES.items():
                number(radio[field], low, high, field)
        technologies.add(RADIO_PROFILES[key].tech)
    if len(technologies) > 1:
        raise ValueError("One radio family is supported per project")
    tech = next(iter(technologies), None)
    lock = data.get("network_tech")
    if tech and lock and lock != tech:
        raise ValueError("Project network family does not match the devices")
    if lock and lock not in {p.tech for p in RADIO_PROFILES.values()}:
        raise ValueError("Unknown network family")
    data["network_tech"] = tech if tech else lock
    for obs in obstacles:
        if not isinstance(obs, dict) or obs.get("material") not in MATERIALS:
            raise ValueError("Unknown obstacle material")
        for axis in ("x", "y"):
            number(obs.get(axis, 200), -100000, 100000, axis)
        for dimension in ("w", "h"):
            number(obs.get(dimension, 120), 1, 100000, dimension)
        number(obs.get("thickness", 1), 0.1, 10, "Thickness")
    for section in ("scale", "simulation", "heatmap", "links", "routing", "_meta"):
        if not isinstance(data.get(section, {}), dict):
            raise ValueError(f"Invalid {section} settings")
    scale = data.get("scale", {})
    number(scale.get("px_per_meter", 10), 1, 200, "Pixels per meter")
    number(scale.get("grid_spacing_m", 5), 0.5, 100, "Grid spacing")
    simulation = data.get("simulation", {})
    number(simulation.get("extra_loss_db", 0), 0, 100, "Additional loss")
    if not isinstance(simulation.get("live_fading", True), bool):
        raise ValueError("Live fading must be true or false")
    links = data.get("links", {})
    if links.get("mode", "All-to-All") not in ("All-to-All", "Nearest Neighbor"):
        raise ValueError("Unknown link display mode")
    number(links.get("nn_k", 2), 1, 20, "Neighbor count")
    if int(links.get("nn_k", 2)) != links.get("nn_k", 2):
        raise ValueError("Neighbor count must be an integer")
    for field in ("show_grid", "snap_to_grid"):
        if not isinstance(scale.get(field, True if field == "show_grid" else False), bool):
            raise ValueError(f"{field} must be true or false")
    heat = data.get("heatmap", {})
    if not isinstance(heat.get("show", False), bool):
        raise ValueError("Heatmap visibility must be true or false")
    if heat.get("mode", "RSSI (dBm)") not in ("RSSI (dBm)", "Margin (dB)", "Success (%)"):
        raise ValueError("Unknown heatmap mode")
    if not isinstance(heat.get("tx", ""), str):
        raise ValueError("Invalid heatmap transmitter")
    route = data.get("routing", {})
    if not isinstance(route.get("enabled", False), bool):
        raise ValueError("Routing enable must be true or false")
    if route.get("mode", "Best Path (Max-Min Margin)") not in (
        "Best Path (Max-Min Margin)",
        "Best Path (Min Total Loss)",
    ):
        raise ValueError("Unknown routing mode")
    for field in ("source", "destination"):
        if not isinstance(route.get(field, ""), str):
            raise ValueError(f"Invalid route {field}")
    data["nodes"] = nodes
    data["obstacles"] = obstacles
    return data


def save_project(path: str | Path, data: dict) -> None:
    validated = validate_project(data)
    destination = Path(path)
    descriptor, temporary = tempfile.mkstemp(
        prefix=destination.name + ".", suffix=".tmp", dir=destination.parent
    )
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            json.dump(validated, handle, indent=2, allow_nan=False)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, destination)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)
