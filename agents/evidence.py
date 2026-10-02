from pathlib import Path

MAX_UPLOAD_BYTES = 50 * 1024 * 1024

def run(evidence_type=None, path=None, latitude=None, longitude=None, address=None):
    valid = True
    if path:
        p = Path(path)
        valid = p.is_file() and p.stat().st_size <= MAX_UPLOAD_BYTES
    return {
        'evidence_type': evidence_type or 'None',
        'evidence_valid': valid,
        'latitude': latitude,
        'longitude': longitude,
        'address': address or '',
    }
