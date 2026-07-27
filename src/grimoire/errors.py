"""Stable public errors for Grimoire input contracts."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, order=True)
class ManifestIssue:
    code: str
    path: str
    expected: str
    actual: str

    def to_dict(self) -> dict[str, str]:
        return {
            "code": self.code,
            "path": self.path,
            "expected": self.expected,
            "actual": self.actual,
        }


class ManifestValidationError(ValueError):
    error_code = "GRIM_MANIFEST_INVALID"

    def __init__(self, issues: list[ManifestIssue] | tuple[ManifestIssue, ...]):
        ordered = tuple(sorted(issues, key=lambda issue: (issue.path, issue.code)))
        if not ordered:
            raise ValueError("manifest validation requires at least one issue")
        self.issues = ordered
        super().__init__(f"manifest validation failed with {len(ordered)} issue(s)")

    def to_dict(self) -> dict[str, object]:
        return {
            "status": "INVALID",
            "error_code": self.error_code,
            "issues": [issue.to_dict() for issue in self.issues],
        }
