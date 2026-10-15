"""Errors the caller has to fix. The gRPC layer maps them to INVALID_ARGUMENT."""


class InvalidInputError(ValueError):
    pass


class RateSheetError(InvalidInputError):
    """Every problem found in a rate sheet, so the airline can fix them all in one go."""

    def __init__(self, errors: list[str]):
        super().__init__("invalid rate sheet: " + "; ".join(errors))
        self.errors = errors
