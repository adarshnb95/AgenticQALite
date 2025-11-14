# src/agenticqa/config_loader.py
from dataclasses import dataclass
from typing import Any, Dict, List, Optional
import yaml


@dataclass
class EndpointConfig:
    name: str
    method: str
    path: str
    body: Optional[Dict[str, Any]] = None
    params: Optional[Dict[str, Any]] = None
    headers: Optional[Dict[str, str]] = None
    expected_status: int = 200
    mode: str = "manual"   # "manual" or "agentic"


@dataclass
class ProjectConfig:
    project_name: str
    base_url: str
    endpoints: List[EndpointConfig]


def load_config(path: str = "agenticqa.yaml") -> ProjectConfig:
    with open(path, "r") as f:
        raw = yaml.safe_load(f)

    endpoints = [
        EndpointConfig(**ep)
        for ep in raw.get("endpoints", [])
    ]

    return ProjectConfig(
        project_name=raw.get("project_name", "Unnamed Project"),
        base_url=raw["base_url"],
        endpoints=endpoints,
    )
