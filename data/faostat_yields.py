"""
FAOSTAT Crop Yield Data — Historical production & yield for commodity intelligence.
Source: FAO (Food and Agriculture Organization) — https://www.fao.org/faostat/
Data: Public domain, freely accessible.

Provides historical yield trends for NDVI-to-yield correlation and
commercial insight estimation.
"""

# Historical yield data (tonnes/hectare) from FAOSTAT
# Source: https://www.fao.org/faostat/en/#data/QCL
# Updated to latest available year (2023)
YIELD_HISTORY = {
    "Coffee": {
        "unit": "tonnes/ha",
        "top_producer": "Brazil",
        "global_production_mt": 10.78,  # million tonnes (2023)
        "years": [2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023],
        "brazil_yield": [1.55, 1.63, 1.36, 1.72, 1.58, 1.65, 1.49, 1.78, 1.52, 1.68],
        "global_yield": [0.87, 0.88, 0.85, 0.91, 0.89, 0.90, 0.86, 0.93, 0.88, 0.91],
        "price_per_tonne": 4200,  # approximate USD/tonne (2024 avg)
        "global_area_mha": 11.8,  # million hectares
    },
    "Wheat": {
        "unit": "tonnes/ha",
        "top_producer": "China",
        "global_production_mt": 783.4,
        "years": [2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023],
        "global_yield": [3.26, 3.32, 3.41, 3.47, 3.38, 3.49, 3.51, 3.43, 3.37, 3.52],
        "india_yield": [2.87, 2.75, 2.71, 3.03, 3.37, 3.51, 3.43, 3.47, 3.32, 3.51],
        "price_per_tonne": 265,
        "global_area_mha": 222.0,
    },
    "Corn": {
        "unit": "tonnes/ha",
        "top_producer": "United States",
        "global_production_mt": 1222.5,
        "years": [2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023],
        "global_yield": [5.64, 5.56, 5.84, 5.75, 5.91, 5.80, 5.74, 6.09, 5.68, 6.12],
        "us_yield": [10.73, 10.57, 10.96, 11.08, 11.04, 10.49, 10.78, 11.01, 10.93, 11.21],
        "price_per_tonne": 195,
        "global_area_mha": 199.7,
    },
    "Soybeans": {
        "unit": "tonnes/ha",
        "top_producer": "Brazil",
        "global_production_mt": 395.4,
        "years": [2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023],
        "global_yield": [2.56, 2.60, 2.78, 2.85, 2.68, 2.77, 2.74, 2.82, 2.67, 2.88],
        "brazil_yield": [2.87, 3.02, 2.95, 3.39, 3.39, 3.24, 3.35, 3.52, 3.27, 3.55],
        "price_per_tonne": 460,
        "global_area_mha": 137.1,
    },
    "Cotton": {
        "unit": "tonnes/ha (lint)",
        "top_producer": "India",
        "global_production_mt": 25.4,  # lint equivalent
        "years": [2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023],
        "global_yield": [0.77, 0.72, 0.77, 0.81, 0.76, 0.78, 0.73, 0.79, 0.74, 0.80],
        "egypt_yield": [0.95, 0.68, 0.72, 0.83, 0.87, 0.90, 0.85, 0.92, 0.88, 0.91],
        "price_per_tonne": 2100,
        "global_area_mha": 32.0,
    },
}

# Region-to-commodity mapping for yield lookup
REGION_YIELD_KEY = {
    "Coffee": "brazil_yield",
    "Wheat": "india_yield",
    "Corn": "us_yield",
    "Soybeans": "brazil_yield",
    "Cotton": "egypt_yield",
}


def get_yield_history(commodity: str) -> dict:
    """
    Get historical yield data for a commodity.
    Returns dict with years, yields, and production statistics.
    """
    # Normalize commodity name
    commodity_key = commodity.strip().title()
    if commodity_key not in YIELD_HISTORY:
        # Try partial match
        for k in YIELD_HISTORY:
            if k.lower() in commodity.lower() or commodity.lower() in k.lower():
                commodity_key = k
                break
        else:
            return {"error": f"No yield data for: {commodity}"}

    data = YIELD_HISTORY[commodity_key]
    regional_key = REGION_YIELD_KEY.get(commodity_key, "global_yield")
    regional_yields = data.get(regional_key, data["global_yield"])

    # Calculate trend
    if len(regional_yields) >= 2:
        recent_avg = sum(regional_yields[-3:]) / 3
        historical_avg = sum(regional_yields[:3]) / 3
        trend_pct = round((recent_avg - historical_avg) / historical_avg * 100, 1)
    else:
        trend_pct = 0

    return {
        "commodity": commodity_key,
        "source": "FAO/FAOSTAT",
        "unit": data["unit"],
        "top_producer": data["top_producer"],
        "global_production_mt": data["global_production_mt"],
        "global_area_mha": data["global_area_mha"],
        "price_per_tonne_usd": data["price_per_tonne"],
        "years": data["years"],
        "global_yield": data["global_yield"],
        "regional_yield": regional_yields,
        "regional_key": regional_key.replace("_yield", "").replace("_", " ").title(),
        "ten_year_trend_pct": trend_pct,
        "latest_yield": regional_yields[-1] if regional_yields else None,
        "avg_yield_5yr": round(sum(regional_yields[-5:]) / 5, 2) if len(regional_yields) >= 5 else None,
    }


def estimate_yield_from_ndvi(commodity: str, ndvi_mean: float, ndvi_change_pct: float) -> dict:
    """
    Estimate yield impact using NDVI data cross-referenced with historical yields.
    Uses established NDVI-yield correlation from agricultural remote sensing research.

    References:
    - Mkhabela et al. (2011): NDVI-yield correlation R²=0.7-0.85
    - Bolton & Friedl (2013): Satellite-derived crop yield estimation
    """
    history = get_yield_history(commodity)
    if "error" in history:
        return history

    latest_yield = history["latest_yield"]
    avg_yield = history["avg_yield_5yr"]
    price = history["price_per_tonne_usd"]

    # NDVI-to-yield impact model
    # Based on: Healthy NDVI ≥ 0.6 → normal yield
    # Each 0.1 drop in NDVI → ~8-15% yield reduction (crop-dependent)
    ndvi_health = min(max(ndvi_mean, 0), 1)

    if ndvi_health >= 0.6:
        # Healthy or above — yield at or above historical average
        yield_factor = 1.0 + ((ndvi_health - 0.6) * 0.5)  # up to ~20% bonus
    elif ndvi_health >= 0.4:
        # Moderate stress
        yield_factor = 1.0 - ((0.6 - ndvi_health) * 1.5)  # 0-30% loss
    else:
        # Severe stress
        yield_factor = max(0.3, 1.0 - ((0.6 - ndvi_health) * 2.0))  # 30-70% loss

    estimated_yield = round(avg_yield * yield_factor, 2)
    yield_change_pct = round((estimated_yield - avg_yield) / avg_yield * 100, 1)

    # Revenue projection (per 10,000 hectares)
    area_ha = 10000
    estimated_production_t = estimated_yield * area_ha
    normal_production_t = avg_yield * area_ha
    production_diff_t = estimated_production_t - normal_production_t
    revenue_impact_usd = round(production_diff_t * price)

    return {
        "commodity": history["commodity"],
        "source": "FAO/FAOSTAT + Sentinel-2 NDVI",
        "historical_avg_yield": avg_yield,
        "latest_reported_yield": latest_yield,
        "estimated_current_yield": estimated_yield,
        "yield_change_pct": yield_change_pct,
        "yield_factor": round(yield_factor, 3),
        "ndvi_input": ndvi_mean,
        "production_outlook": "Above Normal" if yield_factor > 1.05 else "Normal" if yield_factor > 0.95 else "Below Normal",
        "revenue_impact_per_10k_ha": revenue_impact_usd,
        "unit": history["unit"],
        "ten_year_trend": history["ten_year_trend_pct"],
        "methodology": "NDVI-yield correlation model (Mkhabela et al. 2011, Bolton & Friedl 2013)",
    }

def forecast_yield(commodity: str, ndvi_mean: float = 0.5, forecast_years: int = 4) -> dict:
    """
    ML-based yield and price forecasting using sklearn.
    Uses polynomial regression (degree 2) on 10-year FAOSTAT data + NDVI adjustment.
    
    Returns forecast for next N years with confidence bands.
    """
    try:
        from sklearn.linear_model import LinearRegression
        from sklearn.preprocessing import PolynomialFeatures
        import numpy as np
    except ImportError:
        return {"error": "sklearn not installed"}

    history = get_yield_history(commodity)
    if "error" in history:
        return history

    years = np.array(history["years"]).reshape(-1, 1)
    regional_yields = np.array(history["regional_yield"])
    global_yields = np.array(history["global_yield"])
    price_per_tonne = history["price_per_tonne_usd"]

    # Polynomial features (degree=2 for curve fitting)
    poly = PolynomialFeatures(degree=2, include_bias=False)
    years_poly = poly.fit_transform(years)

    # Fit regional yield model
    model_regional = LinearRegression()
    model_regional.fit(years_poly, regional_yields)
    r2_regional = round(model_regional.score(years_poly, regional_yields), 3)

    # Fit global yield model
    model_global = LinearRegression()
    model_global.fit(years_poly, global_yields)
    r2_global = round(model_global.score(years_poly, global_yields), 3)

    # Generate forecast years
    last_year = history["years"][-1]
    future_years = [last_year + i for i in range(1, forecast_years + 1)]
    future_arr = np.array(future_years).reshape(-1, 1)
    future_poly = poly.transform(future_arr)

    # Predict
    regional_forecast = model_regional.predict(future_poly)
    global_forecast = model_global.predict(future_poly)

    # NDVI adjustment factor (current satellite observation modifies the forecast)
    if ndvi_mean >= 0.6:
        ndvi_adjust = 1.0 + (ndvi_mean - 0.6) * 0.3  # up to +12% boost
    elif ndvi_mean >= 0.4:
        ndvi_adjust = 1.0 - (0.6 - ndvi_mean) * 0.8  # up to -16% stress
    else:
        ndvi_adjust = max(0.5, 1.0 - (0.6 - ndvi_mean) * 1.5)

    # Apply NDVI adjustment to first forecast year
    adjusted_forecast = regional_forecast.copy()
    adjusted_forecast[0] = adjusted_forecast[0] * ndvi_adjust

    # Confidence bands (based on historical standard deviation)
    hist_std = float(np.std(regional_yields))
    upper_band = [round(float(y + hist_std), 3) for y in adjusted_forecast]
    lower_band = [round(float(max(0, y - hist_std)), 3) for y in adjusted_forecast]

    # Price forecast from yield forecast
    avg_hist_yield = float(np.mean(regional_yields[-3:]))
    price_forecasts = []
    for fy in adjusted_forecast:
        # Price inversely correlated with yield (supply/demand)
        yield_ratio = float(fy) / avg_hist_yield if avg_hist_yield > 0 else 1.0
        # 1% yield increase → ~0.5-1% price decrease (commodity elasticity)
        price_adjust = 1.0 / (yield_ratio ** 0.6)
        price_forecasts.append(round(price_per_tonne * price_adjust))

    # Fitted historical values (for chart overlay)
    fitted_regional = model_regional.predict(years_poly)

    return {
        "commodity": history["commodity"],
        "model": "Polynomial Regression (degree=2)",
        "r2_regional": r2_regional,
        "r2_global": r2_global,
        "ndvi_adjustment": round(ndvi_adjust, 3),
        "historical_years": history["years"],
        "historical_regional": [round(float(y), 3) for y in regional_yields],
        "historical_global": [round(float(y), 3) for y in global_yields],
        "fitted_regional": [round(float(y), 3) for y in fitted_regional],
        "forecast_years": future_years,
        "forecast_regional": [round(float(y), 3) for y in adjusted_forecast],
        "forecast_global": [round(float(y), 3) for y in global_forecast],
        "upper_confidence": upper_band,
        "lower_confidence": lower_band,
        "price_forecast": price_forecasts,
        "current_price": price_per_tonne,
        "unit": history["unit"],
        "regional_key": history["regional_key"],
        "methodology": "sklearn PolynomialRegression(deg=2) + NDVI satellite adjustment",
    }


if __name__ == "__main__":
    # Quick test
    for crop in ["Coffee", "Wheat", "Corn", "Soybeans", "Cotton"]:
        h = get_yield_history(crop)
        print(f"\n{crop}: {h['latest_yield']} {h['unit']} | trend: {h['ten_year_trend_pct']}% | 5yr avg: {h['avg_yield_5yr']}")

        est = estimate_yield_from_ndvi(crop, ndvi_mean=0.45, ndvi_change_pct=-10)
        print(f"  NDVI 0.45 → est yield: {est['estimated_current_yield']} ({est['yield_change_pct']:+.1f}%) | revenue impact: ${est['revenue_impact_per_10k_ha']:,}/10kha")

        fc = forecast_yield(crop, ndvi_mean=0.45)
        if "error" not in fc:
            print(f"  Forecast {fc['forecast_years']}: {fc['forecast_regional']}")
            print(f"  Price forecast: {fc['price_forecast']} | R²={fc['r2_regional']}")
