"""Compatibility for possible count_objects.detect() return shapes.

Only the call name and human/nonhuman use are supported by project history;
the original detector code and actual return type are not available.
"""
from numbers import Integral


def people_count(result: object) -> int:
    """Accept a non-negative count or (count, other_metadata).

    Some older project code uses count_objects.detect() and some references
    describe a two-part result. Do not silently accept arbitrary object lists
    or floats; a wrong count should stop the robot, not signal free passage.
    """
    if isinstance(result, tuple) and len(result) == 2:
        result = result[0]
    if isinstance(result, bool) or not isinstance(result, Integral):
        raise ValueError(f'unsupported detector result {type(result).__name__}')
    if result < 0:
        raise ValueError('people count cannot be negative')
    return int(result)
