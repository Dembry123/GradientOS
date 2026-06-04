"""HTTP client for GradientOS realtime jog endpoints."""

from __future__ import annotations

from typing import Any

import requests

from .hebi_models import JogCommand, RobotToolPose


class GradientJogApiClient:
    """Thin HTTP client for GradientOS jog endpoints."""

    def __init__(self, api_host: str, *, timeout_s: float, dry_run: bool) -> None:
        self.api_host = api_host.rstrip("/")
        self.timeout_s = timeout_s
        self.dry_run = dry_run
        self.session = requests.Session()

    def close(self) -> None:
        self.session.close()

    def _post(self, path: str, payload: dict[str, Any] | None = None) -> None:
        if self.dry_run:
            suffix = f" {payload}" if payload else ""
            print(f"[dry-run] POST {path}{suffix}")
            return
        response = self.session.post(
            f"{self.api_host}{path}",
            json=payload,
            timeout=self.timeout_s,
        )
        response.raise_for_status()

    def _get(self, path: str) -> dict[str, Any] | None:
        if self.dry_run:
            return None
        response = self.session.get(
            f"{self.api_host}{path}",
            timeout=self.timeout_s,
        )
        response.raise_for_status()
        payload = response.json()
        if not isinstance(payload, dict):
            raise ValueError(f"GET {path} returned non-object JSON: {payload!r}")
        return payload

    def post_diagnostic(self, path: str, payload: dict[str, Any]) -> None:
        response = self.session.post(
            f"{self.api_host}{path}",
            json=payload,
            timeout=min(self.timeout_s, 0.2),
        )
        response.raise_for_status()

    def start(self) -> None:
        self._post("/control/jog/start")

    def stop(self) -> None:
        self._post("/control/jog/stop")

    def set_deadman(self, enabled: bool) -> None:
        self._post("/control/jog/deadman", {"enabled": enabled})

    def send_velocity(self, command: JogCommand) -> None:
        self._post("/control/jog/velocity", command.as_payload())

    def send_gripper_velocity(self, command: JogCommand) -> None:
        self._post(
            "/control/jog/gripper-velocity",
            {"rate_deg_s": command.gripper_deg_s},
        )

    def zero(self) -> None:
        self.send_velocity(JogCommand())
        self._post("/control/jog/gripper-velocity", {"rate_deg_s": 0.0})

    def get_tool_pose(self) -> RobotToolPose | None:
        payload = self._get("/info/pose")
        if payload is None:
            return None
        return RobotToolPose.from_api_payload(payload)
