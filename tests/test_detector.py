from pathlib import Path

import cv2
import numpy as np
import pytest

from hough_circle_tool.detector import Circle, annotate, detect_circles
from hough_circle_tool.params import HoughParams

EXAMPLES = Path(__file__).resolve().parents[1] / "examples"


def _sorted_circles(circles: list[Circle]) -> list[Circle]:
    return sorted(circles, key=lambda circle: circle.x)


def test_synthetic_circle_is_detected() -> None:
    image = np.zeros((240, 240, 3), np.uint8)
    cv2.circle(image, (120, 120), 60, (255, 255, 255), -1)

    circles = detect_circles(
        image,
        HoughParams(
            dp=1.0,
            min_dist=100,
            param1=100,
            param2=20,
            min_radius=40,
            max_radius=80,
        ),
    )

    assert len(circles) == 1
    assert abs(circles[0].x - 120) <= 2
    assert abs(circles[0].y - 120) <= 2
    assert abs(circles[0].radius - 60) <= 3


def test_coins_image_has_two_outer_rims() -> None:
    image = cv2.imread(str(EXAMPLES / "coins.jpg"))
    assert image is not None

    circles = _sorted_circles(detect_circles(image, HoughParams()))
    expected = [(192, 190, 178), (568, 192, 180)]

    assert len(circles) == 2
    for circle, (x, y, radius) in zip(circles, expected, strict=True):
        assert abs(circle.x - x) <= 10
        assert abs(circle.y - y) <= 10
        assert abs(circle.radius - radius) <= 10


def test_cookie_plate_image_has_one_rim() -> None:
    image = cv2.imread(str(EXAMPLES / "cookie-plate.png"))
    assert image is not None

    circles = detect_circles(image, HoughParams())

    assert len(circles) == 1
    assert abs(circles[0].x - 264) <= 10
    assert abs(circles[0].y - 258) <= 10
    assert abs(circles[0].radius - 244) <= 10


def test_annotate_draws_without_mutating_source() -> None:
    image = cv2.imread(str(EXAMPLES / "cookie-plate.png"))
    assert image is not None
    original = image.copy()
    circles = detect_circles(image, HoughParams())

    result = annotate(image, circles)

    assert result.shape == image.shape
    assert np.array_equal(image, original)
    assert not np.array_equal(result, original)
