# 2.2.5 — Normal builds and optional stress review

- Normal quality/build checks retain lint, formatting, type checks and 55 functional/normal-layout tests.
- Three forced narrow-panel/oversized-font cases are marked layout_stress and run separately.
- Add 07_Layout_Stress_Tests.bat; optional failures remain visible with separate reports.
- Windows CI reviews stress results separately without blocking normal EXE/installer builds.

# 2.2.4 — Coverage legend and validation workflow

- Allow legend text to shrink horizontally and grow vertically beside the gradient.
- Add large-font, wide-text legend regression checks.
- Persist quality-check logs and failed GUI screenshots/widget-width reports.
- Check guided layouts in the packaged startup self-check.
- Supply Windows CI for Python versions, scaling, EXE and installer compilation.

# 2.2.3 — Responsive controls across font metrics

- Give the guided-stage dropdown an explicit compact minimum size.
- Reduce dropdown minimum content lengths so long choices do not widen the sidebar.
- Wrap button and checkbox captions with height-for-width layout support.
- Preserve checkbox state rendering and clicking anywhere on the wrapped caption.
- Add 160% font-width stress coverage and checks against clipped button captions.

# 2.2.2 — Narrow-window layout fix

- Use stacked form rows in narrow guided-workspace panels.
- Shorten long action labels so controls fit with larger font metrics.
- Keep horizontal-overflow checks and add a 300-pixel sidebar/larger-text regression.

# 2.2.1 — Windows build quality-check fix

- Keep Ruff default exclusions so .venv and third-party site-packages are skipped.
- Restrict build lint/format checks to main.py, northstar_wireless and tests.
- Apply exclusions even when excluded files are passed explicitly.

# 2.2.0

- Module and experiment device types with optional custom project names.
- Rename selected devices with Undo/Redo; preserve names across type changes and saves.
- Eleven additional obstacle presets for buildings, equipment and outdoor layouts.
- Prevent duplicate names, including collisions with generated numbered names.

# 2.1.0 — Guided workspace and usability fixes

Adds explicit checkbox indicators for checked/unchecked/disabled states, consistent Fusion rendering, filled toggle controls and focus contrast. Reorganizes existing controls into five navigable planning stages with optional hints, Back/Next, project state, selection-aware buttons, blank-project setup and user-guide access. Stage navigation preserves project data and turns obstacle drawing off when leaving the map stage.

Adds a deterministic review of displayed pairs in both directions, with invalidation after relevant changes. Corrects normal Save versus Save As, export physical scale and deterministic snapshot consistency. Excel reports now record model assumptions, scale, loss allowance, radio calibration, wall thickness and heatmap/routing state; formula-like imported names remain text. Fixes the accidental blank second Excel row and recovery cleanup handling.

All v2.0.0 features, branding and Windows build/installer scripts are retained. JSON schema remains 2; v1/v2 projects are compatible under existing validation rules. This is a candidate source kit; Windows packaging, installed behavior and display scaling still need Windows QA.

# 2.0.0 — NorthStar architecture and wireless edition

Preserves original RF layout editing, obstacles, routing, heatmaps, router suggestions, Undo/Redo and exports. Adds Wi-Fi/Bluetooth/FSK/LoRa planning presets, device labels, per-device radio calibration, stable fading control, additional loss, NorthStar icons, optional wallpaper and reproducible Windows build scripts.

Fixes equal-cost route crashes, routes through below-sensitivity hops, repeated heatmap recomputation, radio/scale/thickness cache invalidation, disconnected recovery saving, missing close-time save method, invalid project substitution, unsaved replacement, stale scene references and add-node redo numbering. Adds local logs, first-run terms, validation before scene clearing, atomic explicit saves, sample layouts and regression/workflow tests.

Known limits: abstract routes permit any placed node as an intermediate point; protocol forwarding roles are not enforced. All success/retry/latency curves are generic. One family per project; no cross-radio interference or channel coordination. Larger heatmap/router searches remain synchronous. Source tested on Python 3.12/Linux; Windows build/installer and other interpreter/platform combinations require user-side verification.
