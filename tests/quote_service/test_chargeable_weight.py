"""Chargeable weight = max(actual weight, L x W x H cm / 6000)."""

import pytest

from quote_service.chargeable_weight import calculate_chargeable_weight
from quote_service.quote import Dimensions


def test_volumetric_weight_wins_for_bulky_shipment():
    # given the README shipment: 80 kg actual, 120 x 80 x 60 cm = 96 kg volumetric
    dimensions = Dimensions(weight=80, length=120, width=80, height=60)

    # when chargeable weight is calculated
    chargeable = calculate_chargeable_weight(dimensions)

    # then the volumetric weight is used
    assert chargeable == pytest.approx(96)


def test_actual_weight_wins_for_dense_shipment():
    # given 75 kg actual, 10 x 10 x 10 cm = 0.17 kg volumetric
    dimensions = Dimensions(weight=75, length=10, width=10, height=10)

    # when chargeable weight is calculated
    chargeable = calculate_chargeable_weight(dimensions)

    # then the actual weight is used
    assert chargeable == pytest.approx(75)


def test_dimensions_are_rounded_up_to_whole_cm():
    # given 120.2 x 80 x 60 cm, which rounds up to 121 x 80 x 60 cm = 96.8 kg volumetric
    dimensions = Dimensions(weight=80, length=120.2, width=80, height=60)

    # when chargeable weight is calculated
    chargeable = calculate_chargeable_weight(dimensions)

    # then the rounded-up dimensions are used (unrounded they would give 96.2 kg)
    assert chargeable == 96.8


def test_chargeable_weight_is_rounded_up_to_0_1_kg():
    # given 44.91 kg actual, above the 0.17 kg volumetric weight
    dimensions = Dimensions(weight=44.91, length=10, width=10, height=10)

    # when chargeable weight is calculated
    chargeable = calculate_chargeable_weight(dimensions)

    # then it rounds up to 45.0 kg, which moves the shipment into the 45 break
    assert chargeable == 45.0
