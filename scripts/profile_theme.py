"""Shared light palette. Run directly to rebuild light variants of all SVGs."""

import re
from pathlib import Path


LIGHT_PALETTE = {
    "#07121f": "#edf6fa", "#0d1827": "#f1f6fa", "#0d202e": "#ffffff",
    "#101d30": "#f8fbff", "#112c3b": "#e2f1f2", "#122d36": "#dcefeb",
    "#132f3d": "#e1f2ee", "#142337": "#ffffff", "#174c50": "#bce8dc",
    "#192b3b": "#dfe8ef", "#1c394c": "#ccdde7", "#237c73": "#77cdb5",
    "#24374b": "#d6e2ec", "#26364a": "#cfdee8", "#28535b": "#b6d7d0",
    "#2c5368": "#afcbd8", "#2dd4bf": "#0d9488", "#37b5a0": "#2b9c80",
    "#44758b": "#709bab", "#547089": "#8ca8bb", "#5eead4": "#087f72",
    "#648699": "#526d80", "#69d7bf": "#087f72", "#6ae6c9": "#08735f",
    "#76b8ff": "#2263a9", "#81e9d8": "#087f72", "#82b7f8": "#2263a9",
    "#8ae8d5": "#086a5e", "#8da9bc": "#526579", "#b2a0f9": "#7050ad",
    "#b5a0fc": "#7050ad", "#cbd8e5": "#334c65", "#ccd8e6": "#364c63",
    "#e4bf78": "#8a6016", "#edf4fc": "#172e46", "#f0f6fc": "#172e46",
    "#f1ce71": "#8a6016", "#f39580": "#ad4d35",
}


def to_light(svg):
    # Substitute in one pass so a replacement cannot be recolored a second time.
    return re.sub(r"#[0-9a-fA-F]{6}\b", lambda match: LIGHT_PALETTE[match[0].lower()], svg)


if __name__ == "__main__":
    assets = Path(__file__).resolve().parents[1] / "assets"
    for source in sorted(assets.glob("*.svg")):
        if not source.stem.endswith("-light"):
            target = source.with_stem(source.stem + "-light")
            target.write_text(to_light(source.read_text(encoding="utf-8")), encoding="utf-8")
            print(target.name)
