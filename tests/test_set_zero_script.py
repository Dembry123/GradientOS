import argparse
import importlib.machinery
import importlib.util
from pathlib import Path

import pytest


def load_set_zero_module():
    script_path = Path(__file__).resolve().parents[1] / "set_zero"
    loader = importlib.machinery.SourceFileLoader("set_zero_script", str(script_path))
    spec = importlib.util.spec_from_loader(loader.name, loader)
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    return module


def controller_args(**overrides):
    values = {
        "host": "127.0.0.1",
        "port": 3000,
        "no_start_controller": False,
        "controller_timeout": 1.0,
        "controller_arg": [],
    }
    values.update(overrides)
    return argparse.Namespace(**values)


def test_ensure_controller_uses_existing_controller(monkeypatch):
    module = load_set_zero_module()
    started = False

    monkeypatch.setattr(module, "_probe_controller", lambda host, port: True)

    def fake_start(_args):
        nonlocal started
        started = True

    monkeypatch.setattr(module, "_start_controller", fake_start)

    module.ensure_controller(controller_args())

    assert started is False


def test_ensure_controller_starts_when_probe_fails(monkeypatch):
    module = load_set_zero_module()
    probes = iter([False, False, True])
    started = False

    class FakeProc:
        def poll(self):
            return None

    def fake_probe(_host, _port):
        return next(probes)

    def fake_start(_args):
        nonlocal started
        started = True
        return FakeProc()

    monkeypatch.setattr(module, "_probe_controller", fake_probe)
    monkeypatch.setattr(module, "_start_controller", fake_start)
    monkeypatch.setattr(module.time, "sleep", lambda _seconds: None)

    module.ensure_controller(controller_args())

    assert started is True


def test_ensure_controller_can_fail_instead_of_starting(monkeypatch):
    module = load_set_zero_module()
    monkeypatch.setattr(module, "_probe_controller", lambda host, port: False)

    with pytest.raises(RuntimeError, match="not responding"):
        module.ensure_controller(controller_args(no_start_controller=True))


def test_auto_start_rejects_non_default_port():
    module = load_set_zero_module()

    with pytest.raises(RuntimeError, match="Auto-start uses"):
        module._start_controller(controller_args(port=3001))
