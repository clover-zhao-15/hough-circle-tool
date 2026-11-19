import pytest

from hough_circle_tool.params import HoughParams


def test_defaults_match_acceptance_parameters() -> None:
    params = HoughParams()
    assert (params.dp, params.min_dist, params.param1, params.param2) == (
        1.0,
        200,
        100,
        40,
    )
    assert (params.min_radius, params.max_radius) == (150, 300)
    assert (params.blur_ksize, params.blur_sigma) == (5, 2.0)


def test_radius_order_is_rejected() -> None:
    with pytest.raises(ValueError, match="minRadius"):
        HoughParams(min_radius=300, max_radius=100).validate()


@pytest.mark.parametrize(
    "overrides",
    [
        {"dp": 0},
        {"min_dist": 0},
        {"param1": 0},
        {"param2": 0},
        {"blur_ksize": 4},
    ],
)
def test_invalid_values_are_rejected(overrides: dict[str, float]) -> None:
    with pytest.raises(ValueError):
        HoughParams(**overrides).validate()
