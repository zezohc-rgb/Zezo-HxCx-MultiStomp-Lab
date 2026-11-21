"""Explicit, auditable extraction of candidate code from a ZDL binary.

Offsets are provided by a researcher, NOT inferred from file contents.
No automatic format recognition, DSP loading, or execution is performed.
"""
from dataclasses import dataclass
import hashlib

MAX_ZDL = 64 * 1024 * 1024

class ExtractionError(ValueError):
    pass

@dataclass(frozen=True)
class CandidateRegion:
    source_sha256: str
    offset: int
    length: int
    region_sha256: str
    data: bytes

def extract_candidate_region(blob: bytes, offset: int, length: int,
                             expected_sha256: str | None = None) -> CandidateRegion:
    if not isinstance(blob, bytes):
        raise ExtractionError('Source must be bytes')
    if len(blob) > MAX_ZDL:
        raise ExtractionError('Source exceeds 64 MiB')
    digest = hashlib.sha256(blob).hexdigest()
    if expected_sha256 is not None and digest.lower() != expected_sha256.lower():
        raise ExtractionError('Source SHA-256 mismatch')
    if type(offset) is not int or type(length) is not int:
        raise ExtractionError('Offset and length must be integers')
    if offset < 0 or length <= 0 or offset > len(blob) or length > len(blob) - offset:
        raise ExtractionError('Candidate region outside source')
    if offset % 32 or length % 32:
        raise ExtractionError('C674x candidate region must be 32-byte aligned')
    region = blob[offset:offset + length]
    return CandidateRegion(digest, offset, length, hashlib.sha256(region).hexdigest(), region)
