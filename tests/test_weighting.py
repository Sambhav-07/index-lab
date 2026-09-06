import pandas as pd
import pytest

from src.weighting import equal_weights, market_cap_weights, custom_weights, WeightingError


def test_equal_weights():
    weights = equal_weights(["A", "B", "C"])
    assert weights.sum() == pytest.approx(1.0)
    assert weights.tolist() == pytest.approx([1 / 3, 1 / 3, 1 / 3])


def test_market_cap_weights():
    universe = pd.DataFrame(
        {"ticker": ["A", "B"], "float_market_cap": [100, 300]}
    )
    weights = market_cap_weights(["A", "B"], universe)
    assert weights["A"] == pytest.approx(0.25)
    assert weights["B"] == pytest.approx(0.75)


def test_custom_percentage_weights():
    weights = custom_weights(["A", "B"], [40, 60])
    assert weights["A"] == pytest.approx(0.40)
    assert weights["B"] == pytest.approx(0.60)


def test_invalid_custom_weights_raise_error():
    with pytest.raises(WeightingError):
        custom_weights(["A", "B"], [0.4, 0.5])
