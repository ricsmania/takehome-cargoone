"""Chargeable weight: the larger of actual and volumetric weight. Pure, no I/O."""

from decimal import ROUND_CEILING, Decimal

from quote_service.quote import Dimensions

VOLUMETRIC_DIVISOR = Decimal(6000)  # cm3 per kg


def calculate_chargeable_weight(weight_kg: Decimal, dimensions: Dimensions) -> Decimal:
    # Both round up, so we never charge for less than the shipment weighs or measures.
    length, width, height = (
        side.quantize(Decimal(1), rounding=ROUND_CEILING)
        for side in (dimensions.length_cm, dimensions.width_cm, dimensions.height_cm)
    )
    volumetric = length * width * height / VOLUMETRIC_DIVISOR
    return max(weight_kg, volumetric).quantize(Decimal("0.1"), rounding=ROUND_CEILING)
