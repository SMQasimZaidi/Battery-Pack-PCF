"""Plain-text report generated from the Python results."""


def write_markdown(path, site, summary, corp, scen, issues, warnings):
    L = []
    L.append(f"# Battery pack PCF report, {site['reporting_period']}")
    L.append(f"\n{site['company']}. Illustrative portfolio model, not real company data.\n")
    L.append("## Product carbon footprint (cradle to gate)\n")
    L.append("| Variant | Capacity (kWh) | kg CO2e per pack | kg CO2e per kWh | Battery cell share |")
    L.append("|---|---|---|---|---|")
    for v, r in summary.iterrows():
        L.append(f"| {v} | {r.capacity_kwh:.1f} | {r.pcf_kgco2e_per_pack:.1f} | "
                 f"{r.pcf_kgco2e_per_kwh:.1f} | {r.battery_cell_share:.0%} |")
    L.append("\n## Annual GHG inventory (t CO2e)\n")
    L.append("| Scope | t CO2e | Share |")
    L.append("|---|---|---|")
    for s, val in corp["by_scope_t"].items():
        L.append(f"| {s} | {val:.1f} | {val / corp['total_t']:.0%} |")
    L.append(f"| **Total** | **{corp['total_t']:.1f}** | 100% |")
    L.append(f"\nCapacity produced: {corp['capacity_produced_mwh']:.1f} MWh. "
             f"Intensity: {corp['intensity_kg_per_kwh']:.1f} kg CO2e per kWh.\n")
    L.append("## Reduction scenarios\n")
    L.append("| Scenario | Variant | Reduction |")
    L.append("|---|---|---|")
    for _, r in scen.iterrows():
        L.append(f"| {r.scenario} | {r.variant} | {r.reduction_pct:.1f}% |")
    L.append("\n## Data quality\n")
    L.append("No blocking issues." if not issues else "\n".join(f"* {i}" for i in issues))
    for w in warnings:
        L.append(f"* Warning: {w}")
    L.append("\n![Hotspots](figures/pcf_hotspots.png)\n\n![Scenarios](figures/reduction_scenarios.png)")
    path.write_text("\n".join(L))
