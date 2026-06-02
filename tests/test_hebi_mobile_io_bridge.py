import numpy as np
import pytest
from scipy.spatial.transform import Rotation as R

from gradient_os.teleop.hebi_mobile_io_bridge import (
    BridgeConfig,
    HebiMobileIOBridge,
    PhonePose,
    RobotToolPose,
    SpatialPhoneMapper,
    _gripper_button_axis,
)


def test_phone_pose_mapping_defaults_to_handheld_hebi_frame():
    config = BridgeConfig(
        translation_scale=0.5,
        rotation_scale=1.0,
        max_target_offset_m=10.0,
        max_target_rotation_deg=180.0,
    )
    mapper = SpatialPhoneMapper(config)
    reference = PhonePose(
        position_m=np.array([0.0, 0.0, 0.0]),
        orientation=R.identity(),
    )
    current = PhonePose(
        position_m=np.array([0.10, 0.20, 0.30]),
        orientation=R.from_euler("y", 10.0, degrees=True),
    )

    mapper.reset(reference)
    target = mapper.target_delta(current)

    assert target.linear_m == pytest.approx(np.array([0.10, -0.05, 0.15]))
    assert target.angular_deg == pytest.approx(np.array([10.0, 0.0, 0.0]))


def test_phone_pose_mapping_supports_axis_inversion_flags():
    config = BridgeConfig(
        translation_scale=1.0,
        rotation_scale=1.0,
        phone_axis_map="x,y,z",
        max_target_offset_m=10.0,
        max_target_rotation_deg=180.0,
        invert_x=True,
        invert_z=True,
        invert_yaw=True,
    )
    mapper = SpatialPhoneMapper(config)
    reference = PhonePose(
        position_m=np.array([0.0, 0.0, 0.0]),
        orientation=R.identity(),
    )
    current = PhonePose(
        position_m=np.array([0.10, 0.20, 0.30]),
        orientation=R.from_euler("z", 10.0, degrees=True),
    )

    mapper.reset(reference)
    target = mapper.target_delta(current)

    assert target.linear_m == pytest.approx(np.array([-0.10, 0.20, -0.30]))
    assert target.angular_deg == pytest.approx(np.array([0.0, 0.0, -10.0]))


def test_spatial_mapper_does_not_limit_target_delta_by_default():
    mapper = SpatialPhoneMapper(
        BridgeConfig(
            rotation_scale=1.0,
            phone_axis_map="x,y,z",
        )
    )
    reference = PhonePose(
        position_m=np.array([0.0, 0.0, 0.0]),
        orientation=R.identity(),
    )
    current = PhonePose(
        position_m=np.array([0.20, 0.0, 0.0]),
        orientation=R.from_euler("z", 90.0, degrees=True),
    )

    mapper.reset(reference)
    target = mapper.target_delta(current)

    assert target.linear_m == pytest.approx(np.array([0.20, 0.0, 0.0]))
    assert target.angular_deg == pytest.approx(np.array([0.0, 0.0, 90.0]))


def test_spatial_mapper_default_translation_scale_is_one_to_one():
    mapper = SpatialPhoneMapper(
        BridgeConfig(
            phone_axis_map="x,y,z",
            max_target_offset_m=10.0,
        )
    )
    reference = PhonePose(
        position_m=np.array([0.0, 0.0, 0.0]),
        orientation=R.identity(),
    )
    current = PhonePose(
        position_m=np.array([0.1524, 0.0, 0.0]),
        orientation=R.identity(),
    )

    mapper.reset(reference)
    target = mapper.target_delta(current)

    assert target.linear_m == pytest.approx(np.array([0.1524, 0.0, 0.0]))


def test_spatial_mapper_deadbands_small_hold_jitter():
    config = BridgeConfig(
        translation_scale=1.0,
        phone_axis_map="x,y,z",
        linear_deadband_m=0.01,
        angular_deadband_deg=1.0,
        linear_kp=10.0,
        angular_kp=10.0,
        filter_alpha=1.0,
    )
    mapper = SpatialPhoneMapper(config)
    reference = PhonePose(
        position_m=np.array([0.0, 0.0, 0.0]),
        orientation=R.identity(),
    )
    current = PhonePose(
        position_m=np.array([0.005, 0.0, 0.0]),
        orientation=R.from_euler("z", 0.5, degrees=True),
    )

    mapper.reset(reference)
    command = mapper.command_for_pose(current, dt_s=0.04, gripper_axis_value=0.0)

    assert command.linear_m_s == pytest.approx(np.zeros(3))
    assert command.angular_deg_s == pytest.approx(np.zeros(3))


class _FakeMobileIOButtons:
    def __init__(self, states: dict[int, bool]):
        self.states = states

    def get_button_state(self, button_index: int) -> bool:
        return self.states.get(button_index, False)


@pytest.mark.parametrize(
    ("states", "expected"),
    [
        ({2: True}, 1.0),
        ({4: True}, -1.0),
        ({2: True, 4: True}, 0.0),
        ({}, 0.0),
    ],
)
def test_gripper_buttons_map_b2_open_b4_close(states, expected):
    mobile_io = _FakeMobileIOButtons(states)

    assert _gripper_button_axis(mobile_io, BridgeConfig()) == pytest.approx(expected)


class _FakeReleaseClient:
    def __init__(self):
        self.calls: list[str] = []

    def set_deadman(self, enabled: bool) -> None:
        self.calls.append(f"deadman:{enabled}")

    def zero(self) -> None:
        self.calls.append("zero")

    def stop(self) -> None:
        self.calls.append("stop")


def test_bridge_release_drops_deadman_before_zero_and_stop():
    bridge = HebiMobileIOBridge(BridgeConfig())
    fake_client = _FakeReleaseClient()
    bridge.client = fake_client  # type: ignore[assignment]
    bridge.enabled = True
    bridge.last_pose = PhonePose(np.zeros(3), R.identity())

    bridge._release()

    assert fake_client.calls == ["deadman:False", "zero", "stop"]
    assert bridge.enabled is False
    assert bridge.last_pose is None


def test_spatial_mapper_clamps_velocity_and_integrates_estimate():
    config = BridgeConfig(
        translation_scale=1.0,
        phone_axis_map="x,y,z",
        max_target_offset_m=1.0,
        linear_kp=100.0,
        linear_deadband_m=0.0,
        angular_deadband_deg=0.0,
        max_linear_m_s=0.05,
        filter_alpha=1.0,
    )
    mapper = SpatialPhoneMapper(config)
    reference = PhonePose(
        position_m=np.array([0.0, 0.0, 0.0]),
        orientation=R.identity(),
    )
    current = PhonePose(
        position_m=np.array([0.2, 0.0, 0.0]),
        orientation=R.identity(),
    )

    mapper.reset(reference)
    command = mapper.command_for_pose(current, dt_s=0.04, gripper_axis_value=0.0)

    assert np.linalg.norm(command.linear_m_s) == pytest.approx(0.05)
    assert mapper.estimated_linear_m[0] == pytest.approx(0.002)


def test_spatial_mapper_uses_live_robot_pose_feedback_when_available():
    config = BridgeConfig(
        translation_scale=1.0,
        phone_axis_map="x,y,z",
        max_target_offset_m=1.0,
        linear_kp=2.0,
        linear_deadband_m=0.0,
        angular_deadband_deg=0.0,
        max_linear_m_s=1.0,
        filter_alpha=1.0,
    )
    mapper = SpatialPhoneMapper(config)
    phone_reference = PhonePose(
        position_m=np.array([0.0, 0.0, 0.0]),
        orientation=R.identity(),
    )
    robot_reference = RobotToolPose(
        position_m=np.array([1.0, 2.0, 3.0]),
        orientation=R.identity(),
    )
    current_phone = PhonePose(
        position_m=np.array([0.20, 0.0, 0.0]),
        orientation=R.identity(),
    )
    current_robot = RobotToolPose(
        position_m=np.array([1.15, 2.0, 3.0]),
        orientation=R.identity(),
    )

    mapper.reset(phone_reference, reference_robot_pose=robot_reference)
    command = mapper.command_for_pose(
        current_phone,
        dt_s=0.1,
        gripper_axis_value=0.0,
        robot_pose=current_robot,
    )

    assert command.linear_m_s == pytest.approx(np.array([0.10, 0.0, 0.0]))
    assert mapper.estimated_linear_m[0] == pytest.approx(0.16)


def test_spatial_mapper_visual_pose_uses_unclamped_phone_delta():
    config = BridgeConfig(
        translation_scale=1.0,
        phone_axis_map="x,y,z",
        max_target_offset_m=0.03,
    )
    mapper = SpatialPhoneMapper(config)
    phone_reference = PhonePose(
        position_m=np.array([0.0, 0.0, 0.0]),
        orientation=R.identity(),
    )
    robot_reference = RobotToolPose(
        position_m=np.array([0.30, 0.0, 0.20]),
        orientation=R.identity(),
    )
    current_phone = PhonePose(
        position_m=np.array([0.20, 0.0, 0.0]),
        orientation=R.identity(),
    )

    mapper.reset(phone_reference, reference_robot_pose=robot_reference)
    target = mapper.target_delta(current_phone)
    visual_pose = mapper.visual_tool_pose_from_phone(current_phone)

    assert np.linalg.norm(target.linear_m) == pytest.approx(0.03)
    assert visual_pose is not None
    assert visual_pose.position_m == pytest.approx(np.array([0.50, 0.0, 0.20]))


def test_spatial_mapper_uses_b1_phone_orientation_as_translation_frame():
    config = BridgeConfig(
        translation_scale=1.0,
        phone_axis_map="x,y,z",
        max_target_offset_m=10.0,
    )
    mapper = SpatialPhoneMapper(config)
    reference_orientation = R.from_euler("z", 90.0, degrees=True)
    reference = PhonePose(
        position_m=np.array([1.0, 2.0, 0.0]),
        orientation=reference_orientation,
    )
    local_phone_delta = np.array([0.20, -0.10, 0.05])
    current = PhonePose(
        position_m=reference.position_m + reference_orientation.apply(local_phone_delta),
        orientation=reference_orientation,
    )

    mapper.reset(reference)
    target = mapper.target_delta(current)

    assert target.linear_m == pytest.approx(local_phone_delta)


def test_spatial_mapper_keeps_absolute_phone_orientation_across_b1_reengage():
    config = BridgeConfig(
        translation_scale=1.0,
        rotation_scale=1.0,
        phone_axis_map="x,y,z",
        max_target_offset_m=1.0,
        max_target_rotation_deg=180.0,
    )
    mapper = SpatialPhoneMapper(config)
    phone_neutral = PhonePose(
        position_m=np.array([0.0, 0.0, 0.0]),
        orientation=R.identity(),
    )
    robot_neutral = RobotToolPose(
        position_m=np.array([0.30, 0.0, 0.20]),
        orientation=R.identity(),
    )

    mapper.reset(phone_neutral, reference_robot_pose=robot_neutral)
    rolled_phone = PhonePose(
        position_m=np.array([0.0, 0.0, 0.0]),
        orientation=R.from_euler("z", 10.0, degrees=True),
    )

    first_target = mapper.target_delta(rolled_phone)
    assert first_target.angular_deg == pytest.approx(np.array([0.0, 0.0, 10.0]))

    rolled_robot = RobotToolPose(
        position_m=np.array([0.30, 0.0, 0.20]),
        orientation=R.from_euler("z", 10.0, degrees=True),
    )
    mapper.reset(phone_neutral, reference_robot_pose=rolled_robot)

    reengage_target = mapper.target_delta(phone_neutral)
    reengage_pose = mapper.target_tool_pose_from_delta(reengage_target)

    assert reengage_target.angular_deg == pytest.approx(np.array([0.0, 0.0, -10.0]))
    assert reengage_pose is not None
    assert reengage_pose.orientation.as_euler("xyz", degrees=True) == pytest.approx(
        np.array([0.0, 0.0, 0.0]),
        abs=1e-6,
    )


def test_phone_pose_parses_hebi_wxyz_quaternion():
    pose = PhonePose.from_hebi(
        [1.0, 2.0, 3.0],
        [1.0, 0.0, 0.0, 0.0],
        quaternion_order="wxyz",
    )

    assert pose.position_m == pytest.approx(np.array([1.0, 2.0, 3.0]))
    assert pose.orientation.as_quat() == pytest.approx(np.array([0.0, 0.0, 0.0, 1.0]))


def test_robot_tool_pose_parses_info_pose_payload():
    pose = RobotToolPose.from_api_payload(
        {
            "position_m": {"x": 1.0, "y": 2.0, "z": 3.0},
            "orientation_euler_deg": {"roll": 10.0, "pitch": 20.0, "yaw": 30.0},
            "joints_deg": [0.0] * 6,
        }
    )

    assert pose.position_m == pytest.approx(np.array([1.0, 2.0, 3.0]))
    assert pose.orientation.as_euler("xyz", degrees=True) == pytest.approx(
        np.array([10.0, 20.0, 30.0])
    )
