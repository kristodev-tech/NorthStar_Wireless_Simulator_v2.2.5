from dataclasses import dataclass
from typing import Dict


@dataclass
class RadioProfile:
    name: str
    tech: str  # ✅ "ZIGBEE" or "RM024"
    tx_dbm: float  # TX power in dBm
    sens_dbm: float  # Receiver sensitivity threshold (more negative = better)
    freq_mhz: float  # frequency for reference only
    pl_d0_db: float  # path loss at d0 (1m) in dB
    n: float  # path loss exponent
    noise_sigma_db: float  # random fading/noise (std dev)


RADIO_PROFILES: Dict[str, RadioProfile] = {
    "XBee (Zigbee-ish)": RadioProfile(
        name="XBee (Zigbee-ish)",
        tech="ZIGBEE",
        tx_dbm=5.0,
        sens_dbm=-100.0,
        freq_mhz=2400.0,
        pl_d0_db=40.0,
        n=2.3,
        noise_sigma_db=2.5,
    ),
    "RM024 (FHSS-ish)": RadioProfile(
        name="RM024 (FHSS-ish)",
        tech="RM024",
        tx_dbm=20.0,
        sens_dbm=-105.0,
        freq_mhz=915.0,
        pl_d0_db=32.0,
        n=2.0,
        noise_sigma_db=2.0,
    ),
    "Custom (Strong Link)": RadioProfile(
        name="Custom (Strong Link)",
        tech="ZIGBEE",  # or "RM024" depending on what you intend
        tx_dbm=15.0,
        sens_dbm=-110.0,
        freq_mhz=915.0,
        pl_d0_db=32.0,
        n=1.9,
        noise_sigma_db=1.5,
    ),
}


@dataclass
class ObstacleMaterial:
    name: str
    attenuation_db: float


MATERIALS: Dict[str, ObstacleMaterial] = {
    "Drywall": ObstacleMaterial("Drywall", 3.0),
    "Concrete": ObstacleMaterial("Concrete", 12.0),
    "Metal": ObstacleMaterial("Metal", 25.0),
    "Glass": ObstacleMaterial("Glass", 2.0),
    # Illustrative losses per crossing at thickness 1; calibrate to your experiment.
    "Wood / Plywood": ObstacleMaterial("Wood / Plywood", 4.0),
    "Brick Wall": ObstacleMaterial("Brick Wall", 8.0),
    "Reinforced Concrete": ObstacleMaterial("Reinforced Concrete", 20.0),
    "Metal Door": ObstacleMaterial("Metal Door", 22.0),
    "Office Partition": ObstacleMaterial("Office Partition", 3.0),
    "Furniture / Cabinets": ObstacleMaterial("Furniture / Cabinets", 5.0),
    "Storage Rack": ObstacleMaterial("Storage Rack", 14.0),
    "Machinery / Equipment": ObstacleMaterial("Machinery / Equipment", 18.0),
    "Human / Crowd": ObstacleMaterial("Human / Crowd", 6.0),
    "Foliage / Vegetation": ObstacleMaterial("Foliage / Vegetation", 7.0),
    "Water Tank": ObstacleMaterial("Water Tank", 20.0),
}


@dataclass
class LinkMetrics:
    rssi_dbm: float
    margin_db: float
    success_pct: float
    retries_est: float
    latency_ms: float
    obstacle_db: float
    distance_m: float
