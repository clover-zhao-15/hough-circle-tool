"""Circle detection and annotation with OpenCV."""

from __future__ import annotations

from dataclasses import dataclass

import cv2
import numpy as np

from .params import HoughParams


@dataclass(frozen=True)
class Circle:
    x: int
    y: int
    radius: int


def detect_circles(image: np.ndarray, params: HoughParams) -> list[Circle]:
    """Detect circles in a BGR or grayscale image."""
    params.validate()
    if image is None or image.size == 0:
        raise ValueError("图片为空")

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if image.ndim == 3 else image
    gray = cv2.GaussianBlur(
        gray, (params.blur_ksize, params.blur_ksize), params.blur_sigma
    )
    found = cv2.HoughCircles(
        gray,
        cv2.HOUGH_GRADIENT,
        dp=params.dp,
        minDist=params.min_dist,
        param1=params.param1,
        param2=params.param2,
        minRadius=params.min_radius,
        maxRadius=params.max_radius,
    )
    if found is None:
        return []
    return [
        Circle(int(round(x)), int(round(y)), int(round(radius)))
        for x, y, radius in found[0]
    ]


def annotate(image: np.ndarray, circles: list[Circle]) -> np.ndarray:
    """Return a copy of image with circle outlines, centers and radius labels."""
    result = image.copy()
    for circle in circles:
        cv2.circle(
            result, (circle.x, circle.y), circle.radius, (0, 0, 255), 2, cv2.LINE_AA
        )
        cv2.circle(result, (circle.x, circle.y), 3, (0, 0, 255), -1, cv2.LINE_AA)
        label = f"r={circle.radius}"
        (_, text_height), baseline = cv2.getTextSize(
            label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2
        )
        text_x = max(circle.x - 30, 4)
        text_y = max(circle.y - circle.radius - 8, text_height + baseline + 4)
        cv2.putText(
            result,
            label,
            (text_x, text_y),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (0, 0, 255),
            2,
            cv2.LINE_AA,
        )
    return result
