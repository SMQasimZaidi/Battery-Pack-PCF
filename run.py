"""One command reporting pipeline: load data, check it, calculate, and write every report."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from pcf import model, plots
from pcf.checks import run_checks
from pcf.excel_report import build_workbook
from pcf.md_report import write_markdown

OUT = Path(__file__).parent / "outputs"


def main():
    (OUT / "figures").mkdir(parents=True, exist_ok=True)
    bom, variants, site, scenarios = model.load_inputs()

    inv, alloc = model.full_inventory(bom, variants, site)
    issues, warnings = run_checks(inv, variants, site)
    if issues:
        print("Stopped. Fix these data issues first:")
        for i in issues:
            print(" -", i)
        sys.exit(1)

    pcf = model.calculate_pcf(inv, variants)
    summary = model.summarise(pcf, variants)
    corp = model.corporate_ghg(pcf, variants, site)
    scen = model.run_scenarios(inv, variants, scenarios)

    period = site["reporting_period"]
    build_workbook(bom, variants, site, OUT / f"PCF_report_{period}.xlsx")
    plots.hotspots(pcf, variants, OUT / "figures" / "pcf_hotspots.png")
    plots.scenarios(scen, OUT / "figures" / "reduction_scenarios.png")
    write_markdown(OUT / f"PCF_report_{period}.md", site, summary, corp, scen, issues, warnings)

    print(summary.round(2), "\n")
    for s, v in corp["by_scope_t"].items():
        print(f"{s:15s} {v:8.1f} t CO2e")
    print(f"{'Total':15s} {corp['total_t']:8.1f} t CO2e")
    for w in warnings:
        print("Warning:", w)
    print(f"\nReports written to {OUT}")


if __name__ == "__main__":
    main()
