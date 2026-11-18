"""Hough circle parameters and validation."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class HoughParams:
    """Parameters for cv2.HoughCircles plus the fixed preprocessing step."""

    dp: float = 1.0
    min_dist: int = 200
    param1: int = 100
    param2: int = 40
    min_radius: int = 150
    max_radius: int = 300
    blur_ksize: int = 5
    blur_sigma: float = 2.0

    def validate(self) -> None:
        if self.dp <= 0:
            raise ValueError("dp 必须大于 0")
        if self.min_dist < 1:
            raise ValueError("minDist 必须大于等于 1")
        if self.param1 < 1:
            raise ValueError("param1 必须大于等于 1")
        if self.param2 < 1:
            raise ValueError("param2 必须大于等于 1")
        if self.min_radius < 0 or self.max_radius < 0:
            raise ValueError("半径不能为负数")
        if self.min_radius > self.max_radius:
            raise ValueError("minRadius 不能大于 maxRadius")
        if self.blur_ksize < 1 or self.blur_ksize % 2 == 0:
            raise ValueError("模糊核必须为正奇数")
