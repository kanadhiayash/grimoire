"""Truthful multidimensional status contracts."""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum
from types import MappingProxyType
from typing import Iterable, Mapping


class CompletionStatus(str, Enum):
    PASS = "PASS"
    PARTIAL = "PARTIAL"
    BLOCKED = "BLOCKED"
    NOT_VERIFIED = "NOT_VERIFIED"


class StatusDimension(str, Enum):
    PACK_GENERATION_STATUS = "PACK_GENERATION_STATUS"
    MANIFEST_VALIDATION_STATUS = "MANIFEST_VALIDATION_STATUS"
    APPLICABILITY_STATUS = "APPLICABILITY_STATUS"
    CONTROL_VERIFICATION_STATUS = "CONTROL_VERIFICATION_STATUS"
    PROJECT_READINESS_STATUS = "PROJECT_READINESS_STATUS"
    RELEASE_ASSURANCE_STATUS = "RELEASE_ASSURANCE_STATUS"
    LEGAL_REVIEW_STATUS = "LEGAL_REVIEW_STATUS"
    ZEREF_EXECUTION_STATUS = "ZEREF_EXECUTION_STATUS"


_STATUS_PRECEDENCE = {
    CompletionStatus.PASS: 0,
    CompletionStatus.PARTIAL: 1,
    CompletionStatus.NOT_VERIFIED: 2,
    CompletionStatus.BLOCKED: 3,
}
_REASON_CODE = re.compile(r"^[a-z][a-z0-9_]*$")


def _completion_status(value: CompletionStatus | str) -> CompletionStatus:
    if isinstance(value, CompletionStatus):
        return value
    return CompletionStatus(value)


def _status_dimension(value: StatusDimension | str) -> StatusDimension:
    if isinstance(value, StatusDimension):
        return value
    return StatusDimension(value)


def aggregate_status(
    statuses: Iterable[CompletionStatus | str],
) -> CompletionStatus:
    """Return the most conservative status in a non-empty collection."""

    normalized = tuple(_completion_status(status) for status in statuses)
    if not normalized:
        raise ValueError("at least one status is required")
    return max(normalized, key=_STATUS_PRECEDENCE.__getitem__)


def conservative_legacy_status(value: CompletionStatus | str) -> CompletionStatus:
    """Map a dimensionless 0.5.x status without inferring missing evidence."""

    status = _completion_status(value)
    if status is CompletionStatus.BLOCKED:
        return CompletionStatus.BLOCKED
    return CompletionStatus.NOT_VERIFIED


@dataclass(frozen=True)
class StatusResult:
    dimension: StatusDimension | str
    status: CompletionStatus | str
    reason_codes: tuple[str, ...]

    def __post_init__(self) -> None:
        dimension = _status_dimension(self.dimension)
        status = _completion_status(self.status)
        reason_codes = tuple(self.reason_codes)
        if not reason_codes:
            raise ValueError("at least one reason code is required")
        for code in reason_codes:
            if not isinstance(code, str) or not _REASON_CODE.fullmatch(code):
                raise ValueError(f"invalid reason code: {code!r}")
        object.__setattr__(self, "dimension", dimension)
        object.__setattr__(self, "status", status)
        object.__setattr__(self, "reason_codes", reason_codes)

    def to_dict(self) -> dict[str, object]:
        return {
            "status": self.status.value,
            "reason_codes": list(self.reason_codes),
        }


@dataclass(frozen=True)
class StatusReport:
    results: Mapping[StatusDimension | str, StatusResult]

    def __post_init__(self) -> None:
        normalized: dict[StatusDimension, StatusResult] = {}
        for raw_dimension, result in self.results.items():
            dimension = _status_dimension(raw_dimension)
            if result.dimension is not dimension:
                raise ValueError(
                    f"status result dimension mismatch: {dimension.value}"
                )
            if dimension in normalized:
                raise ValueError(f"duplicate status dimension: {dimension.value}")
            normalized[dimension] = result

        required = set(StatusDimension)
        missing = sorted(
            (dimension.value for dimension in required - set(normalized))
        )
        if missing:
            raise ValueError("missing status dimensions: " + ", ".join(missing))
        object.__setattr__(self, "results", MappingProxyType(normalized))

    @property
    def aggregate(self) -> CompletionStatus:
        return aggregate_status(result.status for result in self.results.values())

    def to_dict(self) -> dict[str, object]:
        return {
            "status_model_version": 1,
            "status": self.aggregate.value,
            "dimensions": {
                dimension.value: self.results[dimension].to_dict()
                for dimension in StatusDimension
            },
        }
