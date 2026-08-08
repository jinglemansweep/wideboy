import pytest

np = pytest.importorskip("numpy")

from wideboy.display.remap import remap_logical_to_physical  # noqa: E402


def test_remap_default_order():
    frame = np.zeros((64, 768, 3), dtype=np.uint8)
    frame[:, 0:256, 0] = 255
    frame[:, 256:512, 1] = 255
    frame[:, 512:768, 2] = 255

    physical = remap_logical_to_physical(frame, [0, 1, 2])
    assert physical.shape == (192, 256, 3)

    assert physical[0, 0, 0] == 255
    assert physical[64, 0, 1] == 255
    assert physical[128, 0, 2] == 255


def test_remap_reversed_order():
    frame = np.zeros((64, 768, 3), dtype=np.uint8)
    frame[:, 0:256, 0] = 255
    frame[:, 256:512, 1] = 255
    frame[:, 512:768, 2] = 255

    physical = remap_logical_to_physical(frame, [2, 1, 0])
    assert physical.shape == (192, 256, 3)

    assert physical[0, 0, 2] == 255
    assert physical[64, 0, 1] == 255
    assert physical[128, 0, 0] == 255


def test_remap_custom_order():
    frame = np.zeros((64, 768, 3), dtype=np.uint8)
    for i in range(3):
        frame[:, i * 256 : (i + 1) * 256, i] = 128

    physical = remap_logical_to_physical(frame, [1, 0, 2])
    assert physical.shape == (192, 256, 3)

    assert physical[0, 0, 1] == 128
    assert physical[64, 0, 0] == 128
    assert physical[128, 0, 2] == 128
