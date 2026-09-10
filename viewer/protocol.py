"""Strict parser for the sonar-v1 serial stream. Invalid lines return None."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Reading:
    sequence: int
    angle: int
    distance_mm: int
    status: str


def parse_line(line: str) -> Reading | None:
    if len(line) > 128:
        return None
    fields = line.strip().split(",")
    if len(fields) != 5 or fields[0] != "v1":
        return None
    try:
        sequence, angle, distance = map(int, fields[1:4])
    except ValueError:
        return None
    status = fields[4]
    if not (0 <= sequence <= 0xFFFFFFFF and 0 <= angle <= 180):
        return None
    if not (
        (status == "ok" and 20 <= distance <= 4000)
        or (status == "no_return" and distance == 0)
    ):
        return None
    return Reading(sequence, angle, distance, status)
