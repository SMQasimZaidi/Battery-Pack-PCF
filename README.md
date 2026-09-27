# Battery Pack PCF and Automated Reporting

A cradle-to-gate product carbon footprint (PCF) model for three lithium-ion battery pack variants, with a one-command reporting pipeline that turns raw inventory data into an Excel report, a Markdown summary, charts and a Scope 1, 2 and 3 roll-up.

> **Note:** This is a self-directed portfolio project. The company and all values are illustrative, based on typical literature ranges. Replace them with supplier, metered or Ecoinvent data for real use.

## What it does

1. Reads the bill of materials, variant data and site energy data from `data/`
2. Runs automated data checks (missing factors, negative amounts, secondary data share)
3. Allocates site electricity and gas to each variant by assembly time
4. Calculates the PCF per pack, per kWh and by hotspot category
5. Rolls product footprints up into an annual company inventory by GHG Protocol scope
6. Tests three reduction scenarios
7. Writes a live Excel workbook (all results are formulas), a Markdown report and charts

## Key results (illustrative)

| Pack | Capacity | kg CO2e per pack | kg CO2e per kWh | Battery cell share |
|---|---|---|---|---|
| S | 0.5 kWh | 60.9 | 121.7 | 62% |
| M | 1.0 kWh | 108.4 | 108.4 | 69% |
| L | 2.0 kWh | 201.1 | 100.5 | 75% |

* Battery cells are the dominant hotspot, at 62% to 75% of the footprint.
* Larger packs have a lower footprint per kWh, because fixed parts like the BMS and housing are spread over more capacity.
* Scope 3 Category 1 (purchased goods) is about 97% of the annual inventory. Site energy (Scopes 1 and 2) is under 2%.
* Sourcing cells from a renewable-powered factory is the strongest lever (19% to 23% reduction), followed by LFP chemistry and recycled aluminium.

![Hotspots](outputs/figures/pcf_hotspots.png)
![Scenarios](outputs/figures/reduction_scenarios.png)

## Method

* **Standard:** aligned with ISO 14067 and the GHG Protocol Product Standard
* **Declared unit:** one battery pack of each variant (cradle-to-gate, so no functional unit)
* **System boundary:** raw materials, component production, inbound transport and pack assembly. Use phase and end of life excluded.
* **Impact:** climate change, GWP100 (kg CO2e)
* **Allocation:** site electricity and natural gas split by total assembly time (annual volume × minutes per unit)
* **Scope mapping (for a pack assembler):** purchased parts = Scope 3 Cat 1, inbound freight = Scope 3 Cat 4, site electricity = Scope 2, site gas = Scope 1

## The Excel report

`outputs/PCF_report_2025.xlsx` contains these sheets: Read me, Inputs, Allocation, PCF, Summary, Corporate GHG and Frameworks. Inputs are in blue and every result is a formula, so changing any input updates the whole report. The Corporate GHG sheet includes a reconciliation check proving that allocated Scope 1 and 2 add back to the site totals.

The Frameworks sheet maps each result to GHG Protocol, CSRD (ESRS E1), TCFD and the EU Taxonomy, with the related transition risks, such as the EU Battery Regulation carbon footprint requirements and CBAM on aluminium.

## Limitations

* Illustrative emission factors, not licensed Ecoinvent datasets
* Climate change only
* Location-based Scope 2 only (CSRD also requires market-based)
* A simple average for inbound transport distance

## Run it

```bash
pip install -r requirements.txt
python run.py
```

Edit anything in `data/` and rerun to regenerate every report.

## Structure

```
data/            bom.csv, variants.csv, site.json, scenarios.json
src/pcf/         model.py, checks.py, excel_report.py, md_report.py, plots.py
outputs/         Excel report, Markdown report, figures
run.py           One-command pipeline
```
