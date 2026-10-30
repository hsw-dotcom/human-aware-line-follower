"""UART/USB serial reference protocol, reconstructed from historical notes."""
from dataclasses import dataclass


@dataclass(frozen=True)
class SensorPacket:
    r: int
    g: int
    b: int
    button: int

    @property
    def color_condition(self) -> bool:
        # Historical final rule, including its permissive OR conditions.
        return self.r >= 4 or self.r >= 2 * self.g or self.r >= 2 * self.b


def parse_packet(raw: bytes | str) -> SensorPacket:
    """Accept only 'r:g:b:button'. Reject stale/garbled serial messages."""
    try:
        line = raw.decode('ascii') if isinstance(raw, bytes) else raw
    except UnicodeDecodeError as exc:
        raise ValueError('non-ASCII packet') from exc
    parts = line.strip().split(':')
    if len(parts) != 4:
        raise ValueError('expected r:g:b:button')
    try:
        numbers = [int(s) for s in parts]
    except ValueError as exc:
        raise ValueError('all packet fields must be integers') from exc
    r, g, b, button = numbers
    if not all(0 <= value <= 65535 for value in (r, g, b)):
        raise ValueError('RGB fields out of range')
    if button not in (0, 1):
        raise ValueError('button must be 0 or 1')
    return SensorPacket(r, g, b, button)


def encode_result(result: int) -> bytes:
    if result not in (0, 1):
        raise ValueError('result must be 0 or 1')
    return f'{result}\n'.encode('ascii')
