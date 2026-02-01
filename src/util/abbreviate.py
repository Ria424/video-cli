__all__ = (
    "DATA_UNITS",
    "abbreviate_byte",
)

import math

DATA_UNITS = (
    "B",
    "Ki",
    "Mi",
    "Gi",
    "Ti",
    "Pi",
    "Ei",
    "Zi",
    "Yi",
)


def abbreviate_byte(byte: int) -> str:
    maximum_exponent = len(DATA_UNITS) - 1

    decimal_part, exponent = math.modf(math.log(byte, 1024))
    exponent: int = min(int(exponent), maximum_exponent)
    decimal_part = byte / (1024 ** min(exponent, maximum_exponent))

    return f"{decimal_part:.3f}{DATA_UNITS[min(exponent, maximum_exponent)]}"
