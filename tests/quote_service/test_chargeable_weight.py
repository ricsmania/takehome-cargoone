"""Chargeable weight = max(actual weight, L x W x H cm / 6000)."""

import pytest

from quote_service.quote import Dimensions
from quote_service.service import QuoteService


def test_volumetric_weight_wins_for_bulky_shipment():
    # given the README shipment: 80 kg actual, 120 x 80 x 60 cm = 96 kg volumetric
    dimensions = Dimensions(weight=80, length=120, width=80, height=60)

    # when chargeable weight is calculated
    chargeable = QuoteService().CalculateChargeableWeight(dimensions)

    # then the volumetric weight is used
    assert chargeable == pytest.approx(96)


def test_actual_weight_wins_for_dense_shipment():
    # given 75 kg actual, 10 x 10 x 10 cm = 0.17 kg volumetric
    dimensions = Dimensions(weight=75, length=10, width=10, height=10)

    # when chargeable weight is calculated
    chargeable = QuoteService().CalculateChargeableWeight(dimensions)

    # then the actual weight is used
    assert chargeable == pytest.approx(75)


def test_volumetric_weight_is_rounded_to_one_decimal():
    # given 30 kg actual, 100 x 50 x 50 cm = 41.666... kg volumetric
    dimensions = Dimensions(weight=30, length=100, width=50, height=50)

    # when chargeable weight is calculated
    chargeable = QuoteService().CalculateChargeableWeight(dimensions)

    # then it is rounded to 1 decimal
    assert chargeable == 41.7


def test_rounding_is_half_up():
    # given 10 kg actual, 277.6 x 30 x 30 cm = 41.64 kg and 100 x 50 x 49.98 cm = 41.65 kg exactly
    below_half = Dimensions(weight=10, length=277.6, width=30, height=30)
    at_half = Dimensions(weight=10, length=100, width=50, height=49.98)

    # when chargeable weight is calculated
    service = QuoteService()

    # then .x4 rounds down and .x5 rounds up
    assert service.CalculateChargeableWeight(below_half) == 41.6
    assert service.CalculateChargeableWeight(at_half) == 41.7


def test_actual_weight_is_rounded_too():
    # given 44.96 kg actual, which is above the 0.17 kg volumetric weight
    dimensions = Dimensions(weight=44.96, length=10, width=10, height=10)

    # when chargeable weight is calculated
    chargeable = QuoteService().CalculateChargeableWeight(dimensions)

    # then it rounds to 45.0, which puts it in the 45 break
    assert chargeable == 45.0
