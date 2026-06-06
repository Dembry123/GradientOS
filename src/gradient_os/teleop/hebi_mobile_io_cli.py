"""CLI entrypoint for HEBI Mobile I/O teleop."""

from __future__ import annotations

import argparse
import os
import sys

from .hebi_mobile_io_calibration import run_phone_frame_calibration
from .hebi_mobile_io_runtime import HebiMobileIOBridge
from .hebi_models import BridgeConfig


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Bridge HEBI Mobile I/O iPhone ARKit pose into GradientOS realtime jog.",
    )
    parser.add_argument("--api-host", default="http://127.0.0.1:4000")
    parser.add_argument("--family", default="HEBI")
    parser.add_argument("--name", default="mobileIO")
    parser.add_argument("--rate-hz", type=float, default=25.0)
    parser.add_argument(
        "--teleop-mode",
        choices=("velocity_jog", "absolute_pose"),
        default=os.getenv("GRADIENT_TELEOP_MODE", "velocity_jog"),
    )
    parser.add_argument("--lookup-wait-s", type=float, default=1.0)
    parser.add_argument("--stale-timeout-s", type=float, default=0.35)
    parser.add_argument("--request-timeout-s", type=float, default=0.45)
    parser.add_argument("--enable-button", type=int, default=1)
    parser.add_argument("--quit-button", type=int, default=8)
    parser.add_argument("--gripper-open-button", type=int, default=2)
    parser.add_argument("--gripper-close-button", type=int, default=4)
    parser.add_argument("--gripper-axis", type=int, default=3)
    parser.add_argument("--axis-deadzone", type=float, default=0.08)
    parser.add_argument("--translation-scale", type=float, default=1.0)
    parser.add_argument("--rotation-scale", type=float, default=1.0)
    parser.add_argument(
        "--phone-axis-map",
        default="y,-x,z",
        help=(
            "Map phone-local axes into robot axes as robot_x,robot_y,robot_z. "
            "Default y,-x,z means phone forward -> robot +X and phone right -> robot -Y."
        ),
    )
    parser.add_argument("--invert-x", action="store_true", help="Invert mapped robot X translation.")
    parser.add_argument("--invert-y", action="store_true", help="Invert mapped robot Y translation.")
    parser.add_argument("--invert-z", action="store_true", help="Invert mapped robot Z translation.")
    parser.add_argument("--invert-roll", action="store_true", help="Invert mapped robot roll.")
    parser.add_argument("--invert-pitch", action="store_true", help="Invert mapped robot pitch.")
    parser.add_argument("--invert-yaw", action="store_true", help="Invert mapped robot yaw.")
    parser.add_argument("--linear-kp", type=float, default=3.0)
    parser.add_argument("--angular-kp", type=float, default=4.0)
    parser.add_argument("--linear-deadband-m", type=float, default=0.004)
    parser.add_argument("--angular-deadband-deg", type=float, default=0.75)
    parser.add_argument(
        "--max-target-offset-m",
        type=float,
        default=float("inf"),
        help="Optional robot target offset limit in meters; <=0 or inf means unlimited.",
    )
    parser.add_argument(
        "--max-target-rotation-deg",
        type=float,
        default=float("inf"),
        help="Optional robot target rotation limit in degrees; <=0 or inf means unlimited.",
    )
    parser.add_argument("--max-linear-m-s", type=float, default=0.08)
    parser.add_argument("--max-angular-deg-s", type=float, default=45.0)
    parser.add_argument("--max-gripper-deg-s", type=float, default=45.0)
    parser.add_argument("--filter-alpha", type=float, default=0.35)
    parser.add_argument("--quaternion-order", choices=("wxyz", "xyzw"), default="wxyz")
    parser.add_argument("--list-devices", action="store_true")
    parser.add_argument("--setup-mobile-ui", action="store_true")
    parser.add_argument("--no-stop-on-release", action="store_true")
    parser.add_argument("--robot-pose-poll-interval-s", type=float, default=0.08)
    parser.add_argument("--no-publish-phone-pose", action="store_true")
    parser.add_argument("--phone-pose-publish-interval-s", type=float, default=0.05)
    parser.add_argument("--no-auto-reconnect", action="store_true")
    parser.add_argument("--reconnect-interval-s", type=float, default=1.0)
    parser.add_argument("--reconnect-after-stale-s", type=float, default=1.5)
    parser.add_argument(
        "--calibrate-phone-frame",
        action="store_true",
        help="Run an interactive no-motion phone-frame calibration wizard.",
    )
    parser.add_argument("--live", action="store_true", help="Send commands to the GradientOS API.")
    parser.add_argument("--log-interval-s", type=float, default=1.0)
    parser.add_argument(
        "--diagnostic-log",
        action="store_true",
        help="Write low-rate phone/target/command JSONL diagnostics under diagnostics/jog_motion.",
    )
    parser.add_argument("--diagnostic-log-interval-s", type=float, default=0.1)
    parser.add_argument("--diagnostic-log-path", default=None)
    return parser


def config_from_args(args: argparse.Namespace) -> BridgeConfig:
    return BridgeConfig(
        api_host=args.api_host,
        family=args.family,
        name=args.name,
        rate_hz=args.rate_hz,
        teleop_mode=args.teleop_mode,
        lookup_wait_s=args.lookup_wait_s,
        stale_timeout_s=args.stale_timeout_s,
        request_timeout_s=args.request_timeout_s,
        enable_button=args.enable_button,
        quit_button=args.quit_button,
        gripper_open_button=args.gripper_open_button,
        gripper_close_button=args.gripper_close_button,
        gripper_axis=args.gripper_axis,
        axis_deadzone=args.axis_deadzone,
        translation_scale=args.translation_scale,
        rotation_scale=args.rotation_scale,
        phone_axis_map=args.phone_axis_map,
        invert_x=args.invert_x,
        invert_y=args.invert_y,
        invert_z=args.invert_z,
        invert_roll=args.invert_roll,
        invert_pitch=args.invert_pitch,
        invert_yaw=args.invert_yaw,
        linear_kp=args.linear_kp,
        angular_kp=args.angular_kp,
        linear_deadband_m=args.linear_deadband_m,
        angular_deadband_deg=args.angular_deadband_deg,
        max_target_offset_m=args.max_target_offset_m,
        max_target_rotation_deg=args.max_target_rotation_deg,
        max_linear_m_s=args.max_linear_m_s,
        max_angular_deg_s=args.max_angular_deg_s,
        max_gripper_deg_s=args.max_gripper_deg_s,
        filter_alpha=args.filter_alpha,
        quaternion_order=args.quaternion_order,
        dry_run=not args.live,
        stop_on_release=not args.no_stop_on_release,
        robot_pose_poll_interval_s=args.robot_pose_poll_interval_s,
        publish_phone_pose=not args.no_publish_phone_pose,
        phone_pose_publish_interval_s=args.phone_pose_publish_interval_s,
        auto_reconnect=not args.no_auto_reconnect,
        reconnect_interval_s=args.reconnect_interval_s,
        reconnect_after_stale_s=args.reconnect_after_stale_s,
        calibrate_phone_frame=args.calibrate_phone_frame,
        setup_mobile_ui=args.setup_mobile_ui,
        list_devices=args.list_devices,
        log_interval_s=args.log_interval_s,
        diagnostic_log=args.diagnostic_log,
        diagnostic_log_interval_s=args.diagnostic_log_interval_s,
        diagnostic_log_path=args.diagnostic_log_path,
    )


def main(argv: list[str] | None = None) -> int:
    parser = build_arg_parser()
    args = parser.parse_args(argv)
    config = config_from_args(args)
    try:
        if config.calibrate_phone_frame:
            return run_phone_frame_calibration(config)
        return HebiMobileIOBridge(config).run()
    except Exception as exc:
        print(f"[teleop] ERROR: {exc}", file=sys.stderr)
        return 1
