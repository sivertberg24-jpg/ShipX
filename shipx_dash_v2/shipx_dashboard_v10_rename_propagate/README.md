
# ShipX Dashboard - Multi-study RAO viewer (v10 — rename propagation)

**This build guarantees that when you apply names in *Study Names*, those names replace the originals everywhere.**

Robust rename propagation:
- Studies dictionary rekeyed (old→new).
- All plots' selected studies remapped to new names.
- All selection widgets are re-keyed (via `rename_rev`) and stale state is cleared.
- Defaults are sanitized against current options (prevents 'default not in options' errors).
- Page re-runs immediately on rename for a clean rebuild.

Also included:
- Form-based selection per plot (no per-click reruns).
- Flexible ParameterStudy detection; natural numeric order.
- Stacked plots with independent period windows; optional peak markers.
- Heavy work only on Load folder; demo fallback if parser missing.

Run:
```
pip install -r requirements.txt
streamlit run app.py
```
Place your real `veres_re1_to_excel.py` next to `app.py` to parse `.re1` files.
