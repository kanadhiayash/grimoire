"""Immutable normalized project manifest models."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ProjectConfig:
    name: str
    lifecycle_stage: str
    product_types: tuple[str, ...]


@dataclass(frozen=True)
class StackConfig:
    languages: tuple[str, ...] = ()
    frameworks: tuple[str, ...] = ()
    services: tuple[str, ...] = ()


@dataclass(frozen=True)
class DataConfig:
    personal_data: bool = False
    sensitive: tuple[str, ...] = ()


@dataclass(frozen=True)
class AIConfig:
    user_facing: bool = False
    automated_decisions: bool = False
    external_models: bool = False


@dataclass(frozen=True)
class RiskConfig:
    level: str = ""


@dataclass(frozen=True)
class StandardsConfig:
    version: str = ""


@dataclass(frozen=True)
class ZerefConfig:
    mode: str = ""
    cost_ceiling: str = "bounded"


@dataclass(frozen=True)
class ValidatedManifest:
    schema_uri: str | None
    schema_version: int
    project: ProjectConfig
    users: tuple[str, ...]
    markets: tuple[str, ...]
    platforms: tuple[str, ...]
    stack: StackConfig
    data: DataConfig
    ai: AIConfig
    risk: RiskConfig
    standards: StandardsConfig
    zeref: ZerefConfig
    unknowns: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        value: dict[str, Any] = {
            "schema_version": self.schema_version,
            "project": {
                "name": self.project.name,
                "lifecycle_stage": self.project.lifecycle_stage,
                "product_types": list(self.project.product_types),
            },
            "users": list(self.users),
            "markets": list(self.markets),
            "platforms": list(self.platforms),
            "stack": {
                "languages": list(self.stack.languages),
                "frameworks": list(self.stack.frameworks),
                "services": list(self.stack.services),
            },
            "data": {
                "personal_data": self.data.personal_data,
                "sensitive": list(self.data.sensitive),
            },
            "ai": {
                "user_facing": self.ai.user_facing,
                "automated_decisions": self.ai.automated_decisions,
                "external_models": self.ai.external_models,
            },
            "risk": {"level": self.risk.level},
            "standards": {"version": self.standards.version},
            "zeref": {
                "mode": self.zeref.mode,
                "cost_ceiling": self.zeref.cost_ceiling,
            },
            "unknowns": list(self.unknowns),
        }
        if self.schema_uri is not None:
            value["$schema"] = self.schema_uri
        return value
