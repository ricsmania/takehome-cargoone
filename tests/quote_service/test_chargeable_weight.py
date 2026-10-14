"""Chargeable weight = max(actual weight, L x W x H cm / 6000)."""

from decimal import Decimal

from quote_service.chargeable_weight import calculate_chargeable_weight
from quote_service.quote import Dimensions


def dimensions(length: str, width: str, height: str) -> Dimensions:
    return Dimensions(length_cm=Decimal(length), width_cm=Decimal(width), height_cm=Decimal(height))


def test_volumetric_weight_wins_for_bulky_shipment():
    # given the README shipment: 80 kg actual, 120 x 80 x 60 cm = 96 kg volumetric
    weight, size = Decimal(80), dimensions("120", "80", "60")

    # when chargeable weight is calculated
    chargeable = calculate_chargeable_weight(weight, size)

    # then the volumetric weight is used
    assert chargeable == Decimal(96)


def test_actual_weight_wins_for_dense_shipment():
    # given 75 kg actual, 10 x 10 x 10 cm = 0.17 kg volumetric
    weight, size = Decimal(75), dimensions("10", "10", "10")

    # when chargeable weight is calculated
    chargeable = calculate_chargeable_weight(weight, size)

    # then the actual weight is used
    assert chargeable == Decimal(75)


def test_dimensions_are_rounded_up_to_whole_cm():
    # given 120.2 x 80 x 60 cm, which rounds up to 121 x 80 x 60 cm = 96.8 kg volumetric
    weight, size = Decimal(80), dimensions("120.2", "80", "60")

    # when chargeable weight is calculated
    chargeable = calculate_chargeable_weight(weight, size)

    # then the rounded-up dimensions are used (unrounded they would give 96.2 kg)
    assert chargeable == Decimal("96.8")


def test_chargeable_weight_is_rounded_up_to_0_1_kg():
    # given 44.91 kg actual, above the 0.17 kg volumetric weight
    weight, size = Decimal("44.91"), dimensions("10", "10", "10")

    # when chargeable weight is calculated
    chargeable = calculate_chargeable_weight(weight, size)

    # then it rounds up to 45.0 kg, which moves the shipment into the 45 break
    assert chargeable == Decimal("45.0")


def test_zero_weight_and_size_stays_zero():
    # given an empty shipment: 0 kg, 0 x 0 x 0 cm
    weight, size = Decimal(0), dimensions("0", "0", "0")

    # when chargeable weight is calculated
    chargeable = calculate_chargeable_weight(weight, size)

    # then rounding up does not turn 0 into 0.1 kg
    assert chargeable == Decimal(0)
