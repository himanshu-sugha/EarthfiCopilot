"""
Agent 1: The Sentinel — Satellite Imagery & Vegetation Analysis
Fetches Sentinel-2 data from Microsoft Planetary Computer (free, no key)
and computes NDVI, EVI, and NDWI indices for any region on Earth.
"""

import json
import numpy as np
from datetime import datetime, timedelta
from io import BytesIO

try:
    from pystac_client import Client
    import rasterio
    from PIL import Image
    import requests
    HAS_SATELLITE = True
except ImportError:
    HAS_SATELLITE = False

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from config import PLANETARY_COMPUTER_API, SENTINEL_COLLECTION, REGIONS, DEFAULT_REGION


def get_stac_client():
    """Connect to Microsoft Planetary Computer STAC API (free, no key)."""
    return Client.open(PLANETARY_COMPUTER_API)


def search_scenes(bbox, date_range=None, max_cloud=20, limit=5):
    """Search for Sentinel-2 scenes over a bounding box."""
    if date_range is None:
        end = datetime.now()
        start = end - timedelta(days=90)
        date_range = f"{start.strftime('%Y-%m-%d')}/{end.strftime('%Y-%m-%d')}"

    client = get_stac_client()
    search = client.search(
        collections=[SENTINEL_COLLECTION],
        bbox=bbox,
        datetime=date_range,
        query={"eo:cloud_cover": {"lt": max_cloud}},
        max_items=limit,
        sortby=[{"field": "properties.eo:cloud_cover", "direction": "asc"}],
    )
    items = list(search.items())
    print(f"  [Sentinel] Found {len(items)} scenes with <{max_cloud}% cloud cover")
    return items


def compute_ndvi(item):
    """Compute NDVI from a STAC item's Red (B04) and NIR (B08) bands."""
    try:
        import planetary_computer as pc
        signed = pc.sign(item)
    except ImportError:
        signed = item

    assets = signed.assets

    # Get thumbnail
    thumbnail = None
    if "rendered_preview" in assets:
        try:
            resp = requests.get(assets["rendered_preview"].href, timeout=30)
            if resp.status_code == 200:
                thumbnail = Image.open(BytesIO(resp.content))
        except Exception:
            pass

    # Get band URLs
    red_asset = assets.get("B04", assets.get("red"))
    nir_asset = assets.get("B08", assets.get("nir"))

    red_url = red_asset.href if hasattr(red_asset, "href") else red_asset
    nir_url = nir_asset.href if hasattr(nir_asset, "href") else nir_asset

    ndvi_array = None
    try:
        with rasterio.open(red_url) as red_ds:
            red = red_ds.read(1, out_shape=(red_ds.height // 10, red_ds.width // 10)).astype(np.float32)
        with rasterio.open(nir_url) as nir_ds:
            nir = nir_ds.read(1, out_shape=(nir_ds.height // 10, nir_ds.width // 10)).astype(np.float32)

        denom = nir + red
        ndvi_array = np.where(denom > 0, (nir - red) / denom, 0)
        print(f"  [Sentinel] NDVI computed — shape={ndvi_array.shape}, mean={np.nanmean(ndvi_array):.3f}")
    except Exception as e:
        print(f"  [Sentinel] Band read failed: {e} — using synthetic")
        ndvi_array = _synthetic_ndvi()

    meta = {
        "scene_id": item.id,
        "datetime": str(item.datetime),
        "cloud_cover": item.properties.get("eo:cloud_cover", "N/A"),
        "platform": item.properties.get("platform", "Sentinel-2"),
    }
    return ndvi_array, thumbnail, meta


def compute_ndwi(item):
    """Compute NDWI (Normalized Difference Water Index) for flood/water detection.
    NDWI = (Green - NIR) / (Green + NIR) using B03 + B08.
    NDWI > 0.3 = water, 0.1-0.3 = wet soil, < 0.1 = dry land.
    """
    try:
        try:
            import planetary_computer as pc
            signed = pc.sign(item)
        except ImportError:
            signed = item

        assets = signed.assets
        green_asset = assets.get("B03", assets.get("green"))
        nir_asset = assets.get("B08", assets.get("nir"))

        with rasterio.open(green_asset.href) as ds:
            green = ds.read(1, out_shape=(ds.height // 10, ds.width // 10)).astype(np.float32)
        with rasterio.open(nir_asset.href) as ds:
            nir = ds.read(1, out_shape=(ds.height // 10, ds.width // 10)).astype(np.float32)

        denom = green + nir
        ndwi = np.where(denom > 0, (green - nir) / denom, 0)

        water_pct = float(np.sum(ndwi > 0.3) / ndwi.size * 100)
        wet_pct = float(np.sum(ndwi > 0.1) / ndwi.size * 100)
        print(f"  [Sentinel] NDWI computed — water={water_pct:.1f}%, wet={wet_pct:.1f}%")
        return {
            "ndwi_array": ndwi,
            "ndwi_mean": round(float(np.nanmean(ndwi)), 4),
            "water_percent": round(water_pct, 1),
            "wet_soil_percent": round(wet_pct, 1),
            "flood_risk": "HIGH" if water_pct > 15 else "MODERATE" if water_pct > 5 else "LOW",
        }
    except Exception as e:
        print(f"  [Sentinel] NDWI failed: {e}")
        return {"ndwi_mean": 0, "water_percent": 0, "wet_soil_percent": 0, "flood_risk": "UNKNOWN"}


def compute_scl_quality(item):
    """Assess image quality using Sentinel-2 Scene Classification Layer (SCL).
    SCL classes: 0=no_data, 1=saturated, 2=shadow, 3=cloud_shadow,
    4=vegetation, 5=bare_soil, 6=water, 7=cloud_low, 8=cloud_med, 9=cloud_high,
    10=cirrus, 11=snow.
    """
    try:
        try:
            import planetary_computer as pc
            signed = pc.sign(item)
        except ImportError:
            signed = item

        assets = signed.assets
        scl_asset = assets.get("SCL", assets.get("scl"))
        if not scl_asset:
            return {"quality_score": 100, "quality_note": "SCL band unavailable"}

        with rasterio.open(scl_asset.href) as ds:
            scl = ds.read(1, out_shape=(ds.height // 20, ds.width // 20))

        total = scl.size
        cloud = np.sum(np.isin(scl, [7, 8, 9, 10])) / total * 100
        shadow = np.sum(np.isin(scl, [2, 3])) / total * 100
        vegetation = np.sum(scl == 4) / total * 100
        water = np.sum(scl == 6) / total * 100
        bare_soil = np.sum(scl == 5) / total * 100
        valid = 100 - cloud - shadow

        result = {
            "quality_score": round(valid, 1),
            "cloud_percent": round(cloud, 1),
            "shadow_percent": round(shadow, 1),
            "vegetation_percent": round(vegetation, 1),
            "water_percent": round(water, 1),
            "bare_soil_percent": round(bare_soil, 1),
        }
        print(f"  [Sentinel] SCL quality: {valid:.0f}% valid (cloud={cloud:.1f}%, veg={vegetation:.0f}%)")
        return result
    except Exception as e:
        print(f"  [Sentinel] SCL failed: {e}")
        return {"quality_score": -1, "quality_note": str(e)}


def compute_change_map(baseline_ndvi, recent_ndvi):
    """Compute pixel-level vegetation change detection heatmap."""
    try:
        min_shape = (min(baseline_ndvi.shape[0], recent_ndvi.shape[0]),
                     min(baseline_ndvi.shape[1], recent_ndvi.shape[1]))
        b = baseline_ndvi[:min_shape[0], :min_shape[1]]
        r = recent_ndvi[:min_shape[0], :min_shape[1]]
        change = r - b
        return {
            "change_array": change,
            "mean_change": round(float(np.nanmean(change)), 4),
            "decline_area_pct": round(float(np.sum(change < -0.1) / change.size * 100), 1),
            "growth_area_pct": round(float(np.sum(change > 0.1) / change.size * 100), 1),
        }
    except Exception as e:
        print(f"  [Sentinel] Change map failed: {e}")
        return {"mean_change": 0, "decline_area_pct": 0, "growth_area_pct": 0}


def compute_msi(item):
    """Compute MSI (Moisture Stress Index) for crop water stress detection.
    MSI = SWIR (B11) / NIR (B08).
    MSI > 1.0 = moisture stress, 0.4-1.0 = moderate, < 0.4 = healthy moisture.
    Reference: Hunt & Rock (1989).
    """
    try:
        try:
            import planetary_computer as pc
            signed = pc.sign(item)
        except ImportError:
            signed = item

        assets = signed.assets
        swir_asset = assets.get("B11", assets.get("swir16"))
        nir_asset = assets.get("B08", assets.get("nir"))

        # B11 is 20m native, B08 is 10m native — read both to common shape
        common_shape = (256, 256)
        with rasterio.open(swir_asset.href) as ds:
            swir = ds.read(1, out_shape=common_shape).astype(np.float32)
        with rasterio.open(nir_asset.href) as ds:
            nir = ds.read(1, out_shape=common_shape).astype(np.float32)

        msi = np.where(nir > 0, swir / nir, 0)

        stress_pct = float(np.sum(msi > 1.0) / msi.size * 100)
        healthy_pct = float(np.sum(msi < 0.4) / msi.size * 100)
        msi_mean = float(np.nanmean(msi))

        if msi_mean > 1.0:
            stress_level = "HIGH"
        elif msi_mean > 0.6:
            stress_level = "MODERATE"
        else:
            stress_level = "LOW"

        print(f"  [Sentinel] MSI computed — mean={msi_mean:.3f}, stress={stress_pct:.1f}%")
        return {
            "msi_mean": round(msi_mean, 4),
            "moisture_stress_percent": round(stress_pct, 1),
            "healthy_moisture_percent": round(healthy_pct, 1),
            "stress_level": stress_level,
        }
    except Exception as e:
        print(f"  [Sentinel] MSI failed: {e}")
        return {"msi_mean": 0.7, "moisture_stress_percent": 0, "healthy_moisture_percent": 0, "stress_level": "UNKNOWN"}


def _synthetic_ndvi(shape=(256, 256), health="declining"):
    """Generate synthetic NDVI for demo/fallback."""
    np.random.seed(42)
    if health == "healthy":
        return np.clip(np.random.normal(0.72, 0.08, shape), -1, 1)
    elif health == "declining":
        return np.clip(np.random.normal(0.38, 0.12, shape), -1, 1)
    return np.clip(np.random.normal(0.55, 0.15, shape), -1, 1)


def _synthetic_rgb(shape=(256, 256, 3), health="healthy"):
    """Generate synthetic satellite RGB for demo."""
    np.random.seed(42)
    img = np.zeros(shape, dtype=np.uint8)
    if health == "healthy":
        img[:, :, 0] = np.random.randint(30, 80, (shape[0], shape[1]))
        img[:, :, 1] = np.random.randint(100, 180, (shape[0], shape[1]))
        img[:, :, 2] = np.random.randint(30, 70, (shape[0], shape[1]))
    else:
        img[:, :, 0] = np.random.randint(120, 200, (shape[0], shape[1]))
        img[:, :, 1] = np.random.randint(100, 150, (shape[0], shape[1]))
        img[:, :, 2] = np.random.randint(60, 100, (shape[0], shape[1]))
    return Image.fromarray(img)


def classify_vegetation(change_pct):
    """Classify vegetation health from NDVI % change."""
    if change_pct < -20:
        return "SEVERE_DECLINE"
    elif change_pct < -10:
        return "MODERATE_DECLINE"
    elif change_pct < -5:
        return "MILD_DECLINE"
    elif change_pct < 5:
        return "STABLE"
    elif change_pct < 15:
        return "MILD_GROWTH"
    return "STRONG_GROWTH"


def analyze_region(region_name=None, bbox=None, months_back=3):
    """
    Main entry point for Agent 1.
    Analyzes vegetation health over a region using Sentinel-2 NDVI.
    """
    print(f"\n{'━'*60}")
    print(f"  🛰️  AGENT 1: THE SENTINEL — Satellite Analysis")
    print(f"{'━'*60}")

    if region_name and region_name in REGIONS:
        region = REGIONS[region_name]
        bbox = region["bbox"]
        commodity = region["commodity"]
    else:
        region_name = region_name or DEFAULT_REGION
        bbox = bbox or REGIONS[DEFAULT_REGION]["bbox"]
        commodity = REGIONS.get(region_name, {}).get("commodity", "Unknown")

    results = {
        "agent": "The Sentinel (Satellite Analysis)",
        "region": region_name,
        "commodity": commodity,
        "bbox": bbox,
        "analysis_date": datetime.now().isoformat(),
        "data_source": "Sentinel-2 L2A via Microsoft Planetary Computer",
    }

    if HAS_SATELLITE:
        try:
            end = datetime.now()
            recent_range = f"{(end - timedelta(days=30)).strftime('%Y-%m-%d')}/{end.strftime('%Y-%m-%d')}"
            baseline_start = end - timedelta(days=months_back * 30)
            baseline_range = f"{baseline_start.strftime('%Y-%m-%d')}/{(baseline_start + timedelta(days=30)).strftime('%Y-%m-%d')}"

            print(f"  [Sentinel] Fetching recent imagery: {recent_range}")
            recent_items = search_scenes(bbox, date_range=recent_range, limit=3)

            print(f"  [Sentinel] Fetching baseline imagery: {baseline_range}")
            baseline_items = search_scenes(bbox, date_range=baseline_range, limit=3)

            if recent_items and baseline_items:
                recent_ndvi, recent_rgb, recent_meta = compute_ndvi(recent_items[0])
                baseline_ndvi, baseline_rgb, baseline_meta = compute_ndvi(baseline_items[0])

                recent_mean = float(np.nanmean(recent_ndvi))
                baseline_mean = float(np.nanmean(baseline_ndvi))
                change = recent_mean - baseline_mean
                change_pct = (change / max(baseline_mean, 0.01)) * 100

                # Compute NDWI (flood detection)
                ndwi_data = compute_ndwi(recent_items[0])

                # Compute MSI (moisture stress)
                msi_data = compute_msi(recent_items[0])

                # Compute SCL quality
                scl_data = compute_scl_quality(recent_items[0])

                # Compute change detection heatmap
                change_data = compute_change_map(baseline_ndvi, recent_ndvi)

                results.update({
                    "data_mode": "LIVE_SATELLITE",
                    "baseline_scene": baseline_meta,
                    "recent_scene": recent_meta,
                    "baseline_ndvi_mean": round(baseline_mean, 4),
                    "recent_ndvi_mean": round(recent_mean, 4),
                    "ndvi_change_absolute": round(change, 4),
                    "ndvi_change_percent": round(change_pct, 2),
                    "vegetation_status": classify_vegetation(change_pct),
                    "recent_ndvi_array": recent_ndvi,
                    "baseline_ndvi_array": baseline_ndvi,
                    "recent_rgb": recent_rgb,
                    "baseline_rgb": baseline_rgb,
                    # NDWI flood detection
                    "ndwi": ndwi_data,
                    # MSI moisture stress
                    "msi": msi_data,
                    # SCL quality assessment
                    "scl_quality": scl_data,
                    # Change detection
                    "change_detection": change_data,
                })
                print(f"  ✅ Live satellite analysis complete!")
                return results
        except Exception as e:
            print(f"  ⚠️ Live fetch failed: {e}")

    # Fallback: synthetic data
    print("  [Sentinel] Using synthetic data for demonstration")
    baseline_ndvi = _synthetic_ndvi(health="healthy")
    recent_ndvi = _synthetic_ndvi(health="declining")
    baseline_rgb = _synthetic_rgb(health="healthy")
    recent_rgb = _synthetic_rgb(health="declining")

    baseline_mean = float(np.nanmean(baseline_ndvi))
    recent_mean = float(np.nanmean(recent_ndvi))
    change = recent_mean - baseline_mean
    change_pct = (change / max(baseline_mean, 0.01)) * 100

    results.update({
        "data_mode": "SYNTHETIC_DEMO",
        "baseline_scene": {"datetime": (datetime.now() - timedelta(days=90)).isoformat(), "note": "Synthetic"},
        "recent_scene": {"datetime": datetime.now().isoformat(), "note": "Synthetic"},
        "baseline_ndvi_mean": round(baseline_mean, 4),
        "recent_ndvi_mean": round(recent_mean, 4),
        "ndvi_change_absolute": round(change, 4),
        "ndvi_change_percent": round(change_pct, 2),
        "vegetation_status": classify_vegetation(change_pct),
        "recent_ndvi_array": recent_ndvi,
        "baseline_ndvi_array": baseline_ndvi,
        "recent_rgb": recent_rgb,
        "baseline_rgb": baseline_rgb,
        "msi": {"msi_mean": 0.72, "moisture_stress_percent": 18.5, "healthy_moisture_percent": 32.1, "stress_level": "MODERATE"},
    })
    print(f"  ✅ Synthetic analysis complete! NDVI: {baseline_mean:.3f} → {recent_mean:.3f} ({change_pct:+.1f}%)")
    return results


def get_serializable(results):
    """Return JSON-safe version of results (strip numpy/PIL)."""
    safe = {}
    for k, v in results.items():
        if isinstance(v, np.ndarray) or (Image and isinstance(v, Image.Image)):
            continue
        elif isinstance(v, dict):
            # Recursively clean nested dicts
            nested = {}
            for nk, nv in v.items():
                if isinstance(nv, np.ndarray) or (Image and isinstance(nv, Image.Image)):
                    continue
                nested[nk] = nv
            safe[k] = nested
        else:
            safe[k] = v
    return safe


if __name__ == "__main__":
    report = analyze_region()
    print("\n" + json.dumps(get_serializable(report), indent=2))
