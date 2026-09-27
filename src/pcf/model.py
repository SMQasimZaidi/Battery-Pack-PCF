"""PCF calculation.

Declared unit: one battery pack of each variant.
System boundary: cradle to gate (materials, inbound transport, pack assembly).
"""
import json
from pathlib import Path

import pandas as pd

DATA = Path(__file__).resolve().parents[2] / "data"


def load_inputs(data_dir=DATA):
    d = Path(data_dir)
    bom = pd.read_csv(d / "bom.csv")
    variants = pd.read_csv(d / "variants.csv").set_index("variant")
    site = json.loads((d / "site.json").read_text())
    scenarios = json.loads((d / "scenarios.json").read_text())
    return bom, variants, site, scenarios


def allocate_site_energy(variants, site):
    """Split site electricity and gas between variants by total assembly time (volume x minutes)."""
    v = variants.copy()
    v["assembly_time_total"] = v["annual_volume"] * v["assembly_minutes"]
    v["time_share"] = v["assembly_time_total"] / v["assembly_time_total"].sum()
    v["electricity_kwh_per_unit"] = site["site_electricity_kwh"] * v["time_share"] / v["annual_volume"]
    v["gas_kwh_per_unit"] = site["site_natural_gas_kwh"] * v["time_share"] / v["annual_volume"]
    return v


def full_inventory(bom, variants, site):
    """Add the allocated assembly energy rows to the purchased-materials BOM."""
    alloc = allocate_site_energy(variants, site)
    extra = pd.DataFrame([
        {"component": "Assembly electricity (allocated)", "category": "Assembly energy", "unit": "kWh",
         "emission_factor": site["grid_factor_kgco2e_per_kwh"], "factor_source": "Location-based grid factor",
         "data_type": "Primary", "ghg_scope": "Scope 2",
         **{v: alloc.loc[v, "electricity_kwh_per_unit"] for v in variants.index}},
        {"component": "Assembly heating, natural gas (allocated)", "category": "Assembly energy", "unit": "kWh",
         "emission_factor": site["gas_factor_kgco2e_per_kwh"], "factor_source": "Natural gas combustion factor",
         "data_type": "Primary", "ghg_scope": "Scope 1",
         **{v: alloc.loc[v, "gas_kwh_per_unit"] for v in variants.index}},
    ])
    return pd.concat([bom, extra], ignore_index=True), alloc


def calculate_pcf(inv, variants):
    """Return per-component kg CO2e for each variant."""
    out = inv[["component", "category", "ghg_scope", "data_type"]].copy()
    for v in variants.index:
        out[v] = inv["emission_factor"] * inv[v]
    return out


def summarise(pcf, variants):
    totals = pcf[list(variants.index)].sum()
    cells = pcf.loc[pcf["category"] == "Battery cells", list(variants.index)].sum()
    return pd.DataFrame({
        "capacity_kwh": variants["capacity_kwh"],
        "pcf_kgco2e_per_pack": totals,
        "pcf_kgco2e_per_kwh": totals / variants["capacity_kwh"],
        "battery_cell_share": cells / totals,
    })


def corporate_ghg(pcf, variants, site):
    """Roll product footprints up to a simple annual company inventory by GHG Protocol scope."""
    vols = variants["annual_volume"]
    rows = {}
    for scope in ["Scope 1", "Scope 2", "Scope 3 Cat 1", "Scope 3 Cat 4"]:
        per_unit = pcf.loc[pcf["ghg_scope"] == scope, list(variants.index)].sum()
        rows[scope] = (per_unit * vols).sum() / 1000
    total = sum(rows.values())
    capacity_mwh = (variants["capacity_kwh"] * vols).sum() / 1000
    return {
        "by_scope_t": rows,
        "total_t": total,
        "capacity_produced_mwh": capacity_mwh,
        "intensity_kg_per_kwh": total * 1000 / (capacity_mwh * 1000),
        "scope1_check_t": site["site_natural_gas_kwh"] * site["gas_factor_kgco2e_per_kwh"] / 1000,
        "scope2_check_t": site["site_electricity_kwh"] * site["grid_factor_kgco2e_per_kwh"] / 1000,
    }


def run_scenarios(inv, variants, scenarios):
    rows = []
    base = calculate_pcf(inv, variants)[list(variants.index)].sum()
    for name, change in scenarios.items():
        s = inv.copy()
        s.loc[s["component"] == change["component"], "emission_factor"] = change["emission_factor"]
        new = calculate_pcf(s, variants)[list(variants.index)].sum()
        for v in variants.index:
            rows.append({"scenario": name, "variant": v, "base": base[v], "scenario_value": new[v],
                         "reduction_pct": 100 * (1 - new[v] / base[v])})
    return pd.DataFrame(rows)
