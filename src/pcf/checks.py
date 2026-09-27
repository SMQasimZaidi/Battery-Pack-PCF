"""Automated data quality checks that run before every report."""


def run_checks(inv, variants, site):
    issues = []
    vcols = list(variants.index)
    if inv["emission_factor"].isna().any():
        issues.append("Missing emission factor: " + ", ".join(inv.loc[inv["emission_factor"].isna(), "component"]))
    if (inv[vcols] < 0).any().any():
        issues.append("Negative amounts found in the inventory.")
    if (variants["annual_volume"] <= 0).any():
        issues.append("Annual volume must be positive for every variant.")
    for key in ["site_electricity_kwh", "site_natural_gas_kwh", "grid_factor_kgco2e_per_kwh"]:
        if site.get(key) is None:
            issues.append(f"Site data missing: {key}")
    secondary = (inv["data_type"] == "Secondary").mean()
    warnings = []
    if secondary > 0.5:
        warnings.append(f"{secondary:.0%} of inventory rows use secondary data. Prioritise primary data for hotspots.")
    return issues, warnings
