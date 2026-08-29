# Local interactive dashboard

This folder contains an offline interactive dashboard built from the project's
cleaned dashboard CSVs. It has no external dependencies.

Rebuild its data after refreshing the SQLite database or dashboard CSVs:

```bash
python3 scripts/export_dashboard_data.py
python3 scripts/build_dashboard_site.py
```

Then open `dashboard_site/index.html` in a browser. The dashboard includes
national trend lines, payment-mix lines, a state scale-versus-growth scatter
plot, a business-signal filter, and a sortable state table.

The visual system is documented in `../docs/26_dashboard_design_decisions.md`.
