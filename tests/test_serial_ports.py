from types import SimpleNamespace

from gradient_os.arm_controller import serial_ports


def test_macos_default_serial_port_prefers_cu_candidate(monkeypatch):
    monkeypatch.setattr(serial_ports.platform, "system", lambda: "Darwin") 
    monkeypatch.setattr(
        serial_ports.glob,
        "glob",
        lambda pattern, recursive=True: ["/dev/cu.usbserial-0001"]
        if pattern == "/dev/cu.usbserial*"
        else [],
    )
    monkeypatch.setattr(serial_ports.os.path, "exists", lambda path: True)
    monkeypatch.setattr(serial_ports.os.path, "realpath", lambda path: path)
    monkeypatch.setattr(serial_ports, "list_ports_candidates", lambda include_uart=False: [])

    assert serial_ports.default_serial_port() == "/dev/cu.usbserial-0001"


def test_macos_default_serial_port_is_none_without_adapter(monkeypatch):
    monkeypatch.setattr(serial_ports.platform, "system", lambda: "Darwin")
    monkeypatch.setattr(serial_ports.glob, "glob", lambda pattern, recursive=True: [])
    monkeypatch.setattr(serial_ports, "list_ports_candidates", lambda include_uart=False: [])

    assert serial_ports.default_serial_port() is None


def test_macos_list_ports_filters_bluetooth(monkeypatch):
    from serial.tools import list_ports

    monkeypatch.setattr(serial_ports.platform, "system", lambda: "Darwin")
    monkeypatch.setattr(
        list_ports,
        "comports",
        lambda: [
            SimpleNamespace(device="/dev/cu.Bluetooth-Incoming-Port", vid=None),
            SimpleNamespace(device="/dev/cu.usbserial-0001", vid=0x0403),
        ],
    )
    monkeypatch.setattr(serial_ports.os.path, "exists", lambda path: True)
    monkeypatch.setattr(serial_ports.os.path, "realpath", lambda path: path)

    assert serial_ports.list_ports_candidates() == ["/dev/cu.usbserial-0001"]
