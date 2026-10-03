"""UI-independent link budget; heuristic delivery estimates, not a protocol emulator."""

import math
from .models import LinkMetrics, RadioProfile


def reference_loss(freq_mhz: float) -> float:
    """Free-space reference loss at 1 m (MHz); not a range specification."""
    if not math.isfinite(freq_mhz) or freq_mhz <= 0:
        raise ValueError("Frequency must be positive and finite")
    return 20 * math.log10(freq_mhz) - 27.55


def calculate_link(
    tx: RadioProfile,
    rx: RadioProfile,
    distance_m: float,
    obstacle_db: float = 0,
    extra_loss_db: float = 0,
    fading_db: float = 0,
) -> LinkMetrics:
    if not all(math.isfinite(v) for v in (distance_m, obstacle_db, extra_loss_db, fading_db)):
        raise ValueError("Link inputs must be finite")
    if distance_m < 0 or obstacle_db < 0 or extra_loss_db < 0:
        raise ValueError("Distance and losses cannot be negative")
    d = max(0.5, distance_m)
    rssi = (
        tx.tx_dbm
        - tx.pl_d0_db
        - 10 * tx.n * math.log10(d)
        - obstacle_db
        - extra_loss_db
        + fading_db
    )
    margin = rssi - rx.sens_dbm
    success = max(0.0, min(1.0, (margin + 10) / 25)) * 100
    retries = max(0.0, min(6.0, (100 - success) / 18))
    latency = 8 + d * 0.4 + retries * 6
    return LinkMetrics(rssi, margin, success, retries, latency, obstacle_db, d)
