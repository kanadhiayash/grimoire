"""Resolve validated project facts into deterministic standards decisions."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping, Sequence

from grimoire.models.manifest import ValidatedManifest
from grimoire.predicates import PredicateValidationError, evaluate_predicate
from grimoire.registry.standards import StandardRecord


class DecisionState(str, Enum):
    SELECTED = "SELECTED"
    EXCLUDED = "EXCLUDED"
    UNCERTAIN = "UNCERTAIN"
    CONFLICTED = "CONFLICTED"


class ProfileResolutionError(ValueError):
    """Raised when profile inheritance cannot be resolved deterministically."""

    def __init__(self, reason_codes: set[str]):
        self.reason_codes = tuple(sorted(reason_codes))
        super().__init__(", ".join(self.reason_codes))


@dataclass(frozen=True)
class ApplicabilityDecision:
    standard_id: str
    version: str
    state: DecisionState
    reason_codes: tuple[str, ...]
    predicate_trace: Mapping[str, Any]
    provenance: Mapping[str, str]
    missing_facts: tuple[str, ...] = ()
    review_required: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "standard_id": self.standard_id,
            "version": self.version,
            "state": self.state.value,
            "reason_codes": list(self.reason_codes),
            "predicate_trace": dict(self.predicate_trace),
            "provenance": dict(self.provenance),
            "missing_facts": list(self.missing_facts),
            "review_required": self.review_required,
        }


@dataclass(frozen=True)
class ApplicabilityResult:
    decisions: tuple[ApplicabilityDecision, ...]
    conflicts: tuple[Mapping[str, str], ...]
    active_profiles: tuple[str, ...]

    def by_id(self, standard_id: str) -> ApplicabilityDecision:
        for decision in self.decisions:
            if decision.standard_id == standard_id:
                return decision
        raise KeyError(standard_id)

    def to_dict(self) -> dict[str, Any]:
        groups = {
            "selected": DecisionState.SELECTED,
            "excluded": DecisionState.EXCLUDED,
            "uncertain": DecisionState.UNCERTAIN,
            "conflicted": DecisionState.CONFLICTED,
        }
        return {
            **{
                name: [
                    decision.standard_id
                    for decision in self.decisions
                    if decision.state is state
                ]
                for name, state in groups.items()
            },
            "decisions": [decision.to_dict() for decision in self.decisions],
            "conflicts": [dict(conflict) for conflict in self.conflicts],
            "active_profiles": list(self.active_profiles),
        }


def _as_mapping(value: Any, *, reason: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise ProfileResolutionError({reason})
    return value


def _copy_value(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {str(key): _copy_value(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_copy_value(item) for item in value]
    return value


def _flatten(value: Mapping[str, Any], prefix: str = "") -> dict[str, Any]:
    flattened: dict[str, Any] = {}
    for key in sorted(value):
        if not isinstance(key, str) or not key:
            raise ProfileResolutionError({"invalid_fact_path"})
        path = f"{prefix}.{key}" if prefix else key
        item = value[key]
        if isinstance(item, Mapping):
            flattened.update(_flatten(item, path))
        else:
            flattened[path] = _copy_value(item)
    return flattened


def _set_path(target: dict[str, Any], path: str, value: Any) -> None:
    cursor = target
    parts = path.split(".")
    for part in parts[:-1]:
        child = cursor.get(part)
        if child is None:
            child = {}
            cursor[part] = child
        if not isinstance(child, dict):
            return
        cursor = child
    cursor[parts[-1]] = _copy_value(value)


def _lookup(context: Mapping[str, Any], path: str) -> tuple[bool, Any]:
    current: Any = context
    for part in path.split("."):
        if not isinstance(current, Mapping) or part not in current:
            return False, None
        current = current[part]
    return True, current


def _fields(predicate: Mapping[str, Any]) -> tuple[str, ...]:
    if "all" in predicate or "any" in predicate:
        key = "all" if "all" in predicate else "any"
        values = predicate[key]
        return tuple(
            sorted(
                {
                    field
                    for child in values
                    for field in _fields(_as_mapping(child, reason="invalid_predicate"))
                }
            )
        )
    if "not" in predicate:
        return _fields(_as_mapping(predicate["not"], reason="invalid_predicate"))
    field = predicate.get("field")
    return (field,) if isinstance(field, str) else ()


def _profile_facts(
    profiles: Mapping[str, Any],
    active_profiles: Sequence[str],
) -> tuple[tuple[str, ...], tuple[tuple[str, Mapping[str, Any]], ...]]:
    ordered: list[str] = []
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(name: str) -> None:
        if name in visiting:
            raise ProfileResolutionError({"profile_cycle"})
        if name in visited:
            return
        profile = _as_mapping(profiles.get(name), reason="unknown_profile")
        parents = profile.get("parents", [])
        if not isinstance(parents, list) or not all(isinstance(parent, str) for parent in parents):
            raise ProfileResolutionError({"invalid_profile_parents"})
        visiting.add(name)
        for parent in parents:
            visit(parent)
        visiting.remove(name)
        visited.add(name)
        ordered.append(name)

    for profile_name in active_profiles:
        if not isinstance(profile_name, str):
            raise ProfileResolutionError({"invalid_profile_name"})
        visit(profile_name)

    return tuple(ordered), tuple(
        (
            name,
            _as_mapping(profiles[name], reason="unknown_profile").get("facts", {}),
        )
        for name in ordered
    )


def _resolve_context(
    manifest: Mapping[str, Any],
    profiles: Mapping[str, Any],
    active_profiles: Sequence[str],
    overlays: Sequence[Mapping[str, Any]],
) -> tuple[dict[str, Any], tuple[Mapping[str, str], ...], tuple[str, ...]]:
    context = _copy_value(manifest)
    assigned = _flatten(context)
    sources = {path: "manifest" for path in assigned}
    active, profile_sources = _profile_facts(profiles, active_profiles)
    additions: list[tuple[str, Mapping[str, Any]]] = list(profile_sources)
    for index, overlay in enumerate(overlays):
        if not isinstance(overlay, Mapping):
            raise ProfileResolutionError({"invalid_overlay"})
        name = overlay.get("id", f"overlay-{index + 1}")
        facts = overlay.get("facts", {})
        if not isinstance(name, str) or not name:
            raise ProfileResolutionError({"invalid_overlay"})
        additions.append((name, _as_mapping(facts, reason="invalid_overlay")))

    conflicts: list[Mapping[str, str]] = []
    for source, facts in additions:
        for path, value in _flatten(_as_mapping(facts, reason="invalid_facts")).items():
            if path not in assigned:
                assigned[path] = value
                sources[path] = source
                _set_path(context, path, value)
            elif assigned[path] != value or type(assigned[path]) is not type(value):
                conflicts.append(
                    MappingProxyType(
                        {
                            "path": path,
                            "first_source": sources[path],
                            "second_source": source,
                        }
                    )
                )
    return context, tuple(sorted(conflicts, key=lambda item: (item["path"], item["second_source"]))), active


def _valid_exceptions(
    exceptions: Sequence[Mapping[str, Any]],
    records: Mapping[str, StandardRecord],
) -> tuple[dict[str, Mapping[str, Any]], dict[str, tuple[str, ...]]]:
    accepted: dict[str, Mapping[str, Any]] = {}
    invalid: dict[str, tuple[str, ...]] = {}
    for exception in exceptions:
        if not isinstance(exception, Mapping):
            continue
        standard_id = exception.get("standard_id")
        if not isinstance(standard_id, str) or standard_id not in records:
            continue
        reasons: set[str] = set()
        if not isinstance(exception.get("approved_by"), str) or not exception["approved_by"]:
            reasons.add("invalid_exception")
        if not isinstance(exception.get("reason"), str) or not exception["reason"]:
            reasons.add("invalid_exception")
        if exception.get("review_required") is not True:
            reasons.add("review_required")
        if standard_id in accepted:
            reasons.add("duplicate_exception")
        if reasons:
            invalid[standard_id] = tuple(sorted(reasons))
        else:
            accepted[standard_id] = exception
    return accepted, invalid


def resolve_applicability(
    manifest: ValidatedManifest | Mapping[str, Any],
    registry: Mapping[str, StandardRecord],
    *,
    profiles: Mapping[str, Any] | None = None,
    active_profiles: Sequence[str] = (),
    overlays: Sequence[Mapping[str, Any]] = (),
    exceptions: Sequence[Mapping[str, Any]] = (),
) -> ApplicabilityResult:
    """Resolve each valid registry record without silently inferring missing facts."""

    manifest_value = manifest.to_dict() if isinstance(manifest, ValidatedManifest) else manifest
    context, conflicts, active = _resolve_context(
        _as_mapping(manifest_value, reason="invalid_manifest"),
        profiles or {},
        active_profiles,
        overlays,
    )
    accepted_exceptions, invalid_exceptions = _valid_exceptions(exceptions, registry)
    conflicting_paths = {conflict["path"] for conflict in conflicts}
    decisions: list[ApplicabilityDecision] = []

    for standard_id in sorted(registry):
        record = registry[standard_id]
        predicate_value = dict(record.applicability)
        try:
            fields = _fields(predicate_value)
            missing = tuple(field for field in fields if not _lookup(context, field)[0])
            predicate = evaluate_predicate(predicate_value, context)
        except (PredicateValidationError, ProfileResolutionError):
            decisions.append(
                ApplicabilityDecision(
                    standard_id=record.id,
                    version=record.version,
                    state=DecisionState.CONFLICTED,
                    reason_codes=("invalid_predicate",),
                    predicate_trace=MappingProxyType({"status": "INVALID"}),
                    provenance=MappingProxyType(dict(record.provenance)),
                    review_required=True,
                )
            )
            continue
        conflict = any(field in conflicting_paths for field in fields)
        if standard_id in invalid_exceptions:
            state = DecisionState.CONFLICTED
            reasons = invalid_exceptions[standard_id]
            review_required = True
        elif conflict:
            state = DecisionState.CONFLICTED
            reasons = ("fact_conflict",)
            review_required = True
        elif standard_id in accepted_exceptions:
            state = DecisionState.EXCLUDED
            reasons = ("approved_exception", "review_required")
            review_required = True
        elif missing:
            state = DecisionState.UNCERTAIN
            reasons = ("missing_fact",)
            review_required = False
        elif predicate.result:
            state = DecisionState.SELECTED
            reasons = ("predicate_matched",)
            review_required = False
        else:
            state = DecisionState.EXCLUDED
            reasons = ("predicate_not_matched",)
            review_required = False
        decisions.append(
            ApplicabilityDecision(
                standard_id=record.id,
                version=record.version,
                state=state,
                reason_codes=reasons,
                predicate_trace=MappingProxyType(dict(predicate.trace)),
                provenance=MappingProxyType(dict(record.provenance)),
                missing_facts=missing,
                review_required=review_required,
            )
        )

    return ApplicabilityResult(tuple(decisions), conflicts, active)
