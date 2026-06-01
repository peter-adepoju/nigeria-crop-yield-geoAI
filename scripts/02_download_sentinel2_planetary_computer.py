from __future__ import annotations

import argparse
from pathlib import Path

# Allow scripts to run directly from the repository root without requiring pip install -e . first.
import sys
PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

import pandas as pd

from nigeria_crop_yield.settings import load_config, resolve_path


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Query Microsoft Planetary Computer for Sentinel-2 L2A scenes. "
            "By default this runs as a dry-run because full imagery extraction can be large."
        )
    )
    parser.add_argument("--config", default="configs/config.yaml")
    parser.add_argument("--dry-run", action="store_true", help="Only write STAC query metadata, not rasters.")
    parser.add_argument("--state", default="Kano", help="State to query first for a small proof of concept.")
    args = parser.parse_args()

    cfg = load_config(args.config)
    state_meta = pd.read_csv(resolve_path(cfg["paths"]["state_metadata"]))
    state = state_meta[state_meta["state"].str.lower() == args.state.lower()]
    if state.empty:
        raise ValueError(f"Unknown state: {args.state}")
    row = state.iloc[0]

    # Small point-centered bounding box. Replace with real state/crop polygons for research-grade work.
    lat, lon = float(row.latitude), float(row.longitude)
    delta = 0.08
    bbox = [lon - delta, lat - delta, lon + delta, lat + delta]
    query_info = {
        "collection": cfg["sentinel2"]["collection"],
        "bbox": bbox,
        "datetime": f"{cfg['sentinel2']['start_date']}/{cfg['sentinel2']['end_date']}",
        "query": {"eo:cloud_cover": {"lt": cfg["sentinel2"]["max_cloud_cover"]}},
    }

    out_dir = resolve_path("data/raw/sentinel2")
    out_dir.mkdir(parents=True, exist_ok=True)
    pd.Series(query_info, dtype="object").to_json(out_dir / "example_stac_query.json", indent=2)

    if args.dry_run:
        print("Dry run complete. Wrote data/raw/sentinel2/example_stac_query.json")
        print("Install requirements-geo.txt and remove --dry-run to build a full extractor.")
        return

    try:
        from pystac_client import Client
        import planetary_computer
    except ImportError as exc:
        raise ImportError("Install geospatial dependencies with: pip install -r requirements-geo.txt") from exc

    catalog = Client.open("https://planetarycomputer.microsoft.com/api/stac/v1", modifier=planetary_computer.sign_inplace)
    search = catalog.search(**query_info)
    items = list(search.items())
    index = pd.DataFrame(
        [
            {
                "id": item.id,
                "datetime": item.datetime,
                "cloud_cover": item.properties.get("eo:cloud_cover"),
                "assets": list(item.assets.keys()),
            }
            for item in items
        ]
    )
    index.to_csv(out_dir / f"sentinel2_{args.state.lower()}_stac_items.csv", index=False)
    print(f"Found {len(items)} scenes. Saved STAC item index to {out_dir}")
    print("Next step: use stackstac/rasterio to compute cloud-masked NDVI/EVI/NDWI/SAVI composites over crop polygons.")


if __name__ == "__main__":
    main()
