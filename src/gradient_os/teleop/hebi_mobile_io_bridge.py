"""Compatibility facade for HEBI Mobile I/O teleop.

Implementation lives in focused modules:

* ``hebi_models`` for pose/config DTOs
* ``phone_mapping`` for phone-to-robot math
* ``gradient_jog_client`` for GradientOS HTTP calls
* ``hebi_mobile_io_device`` for HEBI device discovery/input helpers
* ``hebi_mobile_io_runtime`` for bridge orchestration
* ``hebi_mobile_io_calibration`` and ``hebi_mobile_io_cli`` for CLI workflows
"""

from __future__ import annotations

from .gradient_jog_client import GradientJogApiClient
from .hebi_mobile_io_calibration import (
    CALIBRATION_PROMPTS,
    CalibrationPrompt,
    run_phone_frame_calibration,
)
from .hebi_mobile_io_cli import build_arg_parser, config_from_args, main
from .hebi_mobile_io_device import (
    _create_mobile_io,
    _gripper_button_axis,
    _import_hebi,
    _read_button_state,
    _read_phone_pose,
)
from .hebi_mobile_io_runtime import HebiMobileIOBridge
from .hebi_models import (
    BridgeConfig,
    JogCommand,
    MappingConfig,
    PhonePose,
    QuaternionOrder,
    RobotToolPose,
    TargetDelta,
    _rotation_from_quaternion,
    _vector3,
    _xyz_payload,
)
from .phone_mapping import SpatialPhoneMapper

__all__ = [
    "BridgeConfig",
    "CALIBRATION_PROMPTS",
    "CalibrationPrompt",
    "GradientJogApiClient",
    "HebiMobileIOBridge",
    "JogCommand",
    "MappingConfig",
    "PhonePose",
    "QuaternionOrder",
    "RobotToolPose",
    "SpatialPhoneMapper",
    "TargetDelta",
    "_create_mobile_io",
    "_gripper_button_axis",
    "_import_hebi",
    "_read_button_state",
    "_read_phone_pose",
    "_rotation_from_quaternion",
    "_vector3",
    "_xyz_payload",
    "build_arg_parser",
    "config_from_args",
    "main",
    "run_phone_frame_calibration",
]


if __name__ == "__main__":
    raise SystemExit(main())
