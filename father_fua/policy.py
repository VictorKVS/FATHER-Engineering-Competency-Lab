from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PolicyDecision:
    decision: str
    reason: str
    policy_version: str


class PolicyEngine:
    def __init__(self, version: str = "0.1") -> None:
        self.version = version
        self._allows: set[tuple[str, str]] = set()
        self._denies: set[tuple[str, str]] = set()

    def allow(self, subject: str, action: str) -> None:
        self._allows.add((subject, action))

    def deny(self, subject: str, action: str) -> None:
        self._denies.add((subject, action))

    def decide(
        self,
        *,
        subject: str,
        action: str,
        data_classification: str = "INTERNAL",
        target_model_location: str | None = None,
        privileged: bool = False,
        human_approved: bool = False,
    ) -> PolicyDecision:
        key = (subject, action)
        if key in self._denies:
            return PolicyDecision("DENY", "explicit deny", self.version)
        if data_classification in {"RESTRICTED", "SECRET-LIKE", "PII", "CREDENTIAL"} and target_model_location == "REMOTE":
            return PolicyDecision("DENY", "classification blocks remote target", self.version)
        if privileged and not human_approved:
            return PolicyDecision("REQUIRE_APPROVAL", "human approval required", self.version)
        if key in self._allows:
            return PolicyDecision("ALLOW", "explicit allow", self.version)
        return PolicyDecision("DENY", "deny by default", self.version)
