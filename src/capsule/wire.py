"""
Capsule wire format: serialisation, parsing and byte-offset mapping.

A capsule on the wire is its canonical JSON encoding (sorted keys, no
insignificant whitespace) - the exact same byte sequence the SHA3-512 integrity
lock is computed over. That property is what makes the hex inspector honest:
the bytes shown to the user are the bytes that were hashed, signed and
transmitted, not a pretty-printed approximation.
"""

import json
from typing import Any, Dict, List

from src.capsule.models import QuantumSecurityCapsule


def to_wire_bytes(capsule: QuantumSecurityCapsule) -> bytes:
    """Serialises a capsule to its canonical on-the-wire byte sequence."""
    return json.dumps(
        capsule.to_dict(), sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


def from_wire_bytes(data: bytes) -> QuantumSecurityCapsule:
    """Parses wire bytes back into a capsule object."""
    return QuantumSecurityCapsule(**json.loads(data.decode("utf-8")))


def from_dict(payload: Dict[str, Any]) -> QuantumSecurityCapsule:
    """Builds a capsule from a decoded JSON object."""
    return QuantumSecurityCapsule(**payload)


def _value_end(data: bytes, start: int) -> int:
    """
    Returns the exclusive end offset of the JSON value beginning at `start`.

    Handles strings (respecting backslash escapes), objects, arrays and bare
    literals (numbers, true/false/null).
    """
    first = data[start:start + 1]

    if first == b'"':
        i = start + 1
        while i < len(data):
            byte = data[i]
            if byte == 0x5C:  # backslash - skip the escaped character
                i += 2
                continue
            if byte == 0x22:  # closing quote
                return i + 1
            i += 1
        return len(data)

    if first in (b"{", b"["):
        opener = data[start]
        closer = 0x7D if opener == 0x7B else 0x5D
        depth = 0
        in_string = False
        i = start
        while i < len(data):
            byte = data[i]
            if in_string:
                if byte == 0x5C:
                    i += 2
                    continue
                if byte == 0x22:
                    in_string = False
            elif byte == 0x22:
                in_string = True
            elif byte == opener:
                depth += 1
            elif byte == closer:
                depth -= 1
                if depth == 0:
                    return i + 1
            i += 1
        return len(data)

    # Bare literal: runs until the next structural delimiter.
    i = start
    while i < len(data) and data[i] not in (0x2C, 0x7D, 0x5D):  # , } ]
        i += 1
    return i


def field_offsets(capsule: QuantumSecurityCapsule) -> Dict[str, Dict[str, int]]:
    """
    Maps each top-level capsule field to its exact byte range in the wire format.

    This drives click-to-highlight in the packet inspector: selecting
    `replay_token` in the structured view highlights precisely the bytes that
    field occupies on the wire.

    Returns:
        {field_name: {"key_start", "value_start", "value_end", "length"}}
    """
    data = to_wire_bytes(capsule)
    offsets: Dict[str, Dict[str, int]] = {}
    cursor = 0

    for key in sorted(capsule.to_dict().keys()):
        token = b'"' + key.encode("utf-8") + b'":'
        key_start = data.find(token, cursor)
        if key_start == -1:
            continue
        value_start = key_start + len(token)
        value_end = _value_end(data, value_start)
        offsets[key] = {
            "key_start": key_start,
            "value_start": value_start,
            "value_end": value_end,
            "length": value_end - value_start,
        }
        cursor = value_end

    return offsets


def hex_dump(data: bytes, width: int = 16, limit: int = None) -> List[Dict[str, Any]]:
    """
    Renders bytes as Wireshark-style rows.

    Returns:
        A list of {"offset", "hex", "ascii"} rows, where `hex` is a list of
        two-character byte strings and `ascii` substitutes '.' for
        non-printable bytes.
    """
    view = data if limit is None else data[:limit]
    rows: List[Dict[str, Any]] = []
    for offset in range(0, len(view), width):
        chunk = view[offset:offset + width]
        rows.append(
            {
                "offset": offset,
                "hex": [f"{b:02x}" for b in chunk],
                "ascii": "".join(chr(b) if 32 <= b < 127 else "." for b in chunk),
            }
        )
    return rows


def flip_bit(data: bytes, byte_offset: int, bit: int = 0) -> bytes:
    """
    Flips a single bit at the given byte offset - the tamper primitive used by
    the attack lab to prove the integrity lock actually catches modification.
    """
    if not 0 <= byte_offset < len(data):
        raise IndexError(
            f"Byte offset {byte_offset} outside capsule ({len(data)} bytes)"
        )
    if not 0 <= bit <= 7:
        raise ValueError(f"Bit index must be 0-7, got {bit}")
    mutable = bytearray(data)
    mutable[byte_offset] ^= (1 << bit)
    return bytes(mutable)
