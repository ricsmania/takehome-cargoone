"""Chargeable weight: the larger of actual and volumetric weight. Pure, no I/O."""

from decimal import ROUND_CEILING, Decimal

from quote_service.quote import Dimensions


def calculate_chargeable_weight(dimensions: Dimensions) -> float:
  # Both round up, so we never charge for less than the shipment weighs or measures.
  # Decimal from str avoids float artefacts (96.8 stored as 96.80000001) adding an extra 0.1 kg.
  length, width, height = (
    Decimal(str(side)).quantize(Decimal(1), rounding=ROUND_CEILING)
    for side in (dimensions.length, dimensions.width, dimensions.height)
  )
  volumetric = length * width * height / 6000
  chargeable = max(Decimal(str(dimensions.weight)), volumetric)
  return float(chargeable.quantize(Decimal("0.1"), rounding=ROUND_CEILING))
