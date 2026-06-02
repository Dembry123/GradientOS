import numpy as np
import pytest

from gradient_os.arm_controller import command_api


def test_jog_joint_target_uses_nearest_limited_wraparound_angle(monkeypatch):
    monkeypatch.setattr(
        command_api.utils,
        "LOGICAL_JOINT_LIMITS_RAD",
        [(-np.pi, np.pi)] * 6,
    )
    q_current = np.zeros(6)
    q_target = np.zeros(6)
    q_current[5] = np.deg2rad(179.0)
    q_target[5] = np.deg2rad(-179.0)

    q_limited, wrapped, limited = command_api._nearest_limited_joint_target(
        q_current,
        q_target,
    )

    assert wrapped[5]
    assert limited[5]
    assert q_limited[5] == pytest.approx(np.pi)
    assert abs(q_limited[5] - q_current[5]) < np.deg2rad(2.0)
