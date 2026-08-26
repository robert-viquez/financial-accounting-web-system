from decimal import Decimal, ROUND_HALF_UP


QUANTITY_QUANTUM = Decimal("0.001")


def normalize_quantity(value):
    """Return an inventory quantity at the precision persisted by the models."""
    return Decimal(value).quantize(QUANTITY_QUANTUM, rounding=ROUND_HALF_UP)
