"""Illustrative device presets. Use measured or manufacturer values for real planning."""

from .models import RADIO_PROFILES, RadioProfile
from .link_budget import reference_loss

# Nominal center frequencies describe bands, not channel coordination.
for name, tech, tx, sensitivity, frequency, exponent, sigma in [
    ("Wi-Fi 2.4 GHz (generic)", "WIFI24", 20, -90, 2440, 2.6, 2.5),
    ("Wi-Fi 5 GHz (generic)", "WIFI5", 20, -85, 5200, 2.8, 2.5),
    ("Wi-Fi 6 GHz (generic)", "WIFI6", 18, -85, 6100, 2.9, 2.5),
    ("Bluetooth Classic (generic)", "BT_CLASSIC", 4, -90, 2440, 2.5, 2),
    ("Bluetooth LE 1M (generic)", "BLE", 0, -96, 2440, 2.4, 2),
    ("Bluetooth LE 2M (generic)", "BLE", 0, -92, 2440, 2.4, 2),
    ("Bluetooth LE Coded (generic)", "BLE", 0, -103, 2440, 2.4, 2),
    ("Sub-GHz FSK 868 MHz (generic)", "FSK868", 14, -105, 868, 2.2, 2),
    ("Sub-GHz FSK 915 MHz (generic)", "FSK915", 14, -105, 915, 2.2, 2),
    ("LoRa 915 MHz (illustrative)", "LORA915", 14, -130, 915, 2.2, 2),
]:
    RADIO_PROFILES[name] = RadioProfile(
        name, tech, tx, sensitivity, frequency, reference_loss(frequency), exponent, sigma
    )

DEMO_NETWORKS = {
    "XBee (Zigbee)": "ZIGBEE",
    "RM024 (FHSS)": "RM024",
    "Wi-Fi 2.4 GHz": "WIFI24",
    "Wi-Fi 5 GHz": "WIFI5",
    "Wi-Fi 6 GHz": "WIFI6",
    "Bluetooth Classic": "BT_CLASSIC",
    "Bluetooth Low Energy": "BLE",
    "Sub-GHz FSK 868 MHz": "FSK868",
    "Sub-GHz FSK 915 MHz": "FSK915",
    "LoRa 915 MHz": "LORA915",
}
