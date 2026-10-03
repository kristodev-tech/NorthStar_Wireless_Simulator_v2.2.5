# Architecture and extension notes

The project follows the user's NorthStar Software Works architecture reference and developer template workflow: domain rules without Qt widgets, separate storage and asset paths, a private environment, numbered Windows build scripts, explicit terms, NorthStar branding, meaningful tests, per-user data and a documented release gate.

The original 4,000-line script has been separated into startup, models/presets, pure link budget, project storage, Qt geometry adapter, scene items, undo commands, radio editor, theme, guided workspace and main window controller. The controller retains the existing route algorithms, exports and heatmap orchestration to preserve established behavior. It can be split further as those features change. A plugin registry would add overhead without helping the present application.

## Ownership and changes

| Change | Owner |
| --- | --- |
| Add a radio preset/family and demo choice | `domain/presets.py`; add representative project/example and tests |
| Change RSSI/success/latency formulas | `domain/link_budget.py`; verify calculation tests and documentation |
| Add an obstacle material | `domain/models.py`; validate measured loss and clarify its assumptions |
| Change wall intersection or weighting | `services/propagation.py`; test crossing, grazing and missed walls |
| Add stored fields | `services/project_store.py` and main-window serializer/loader; validate before mutation |
| New node editing operations | `ui/commands.py` or `ui/radio_editor.py`; integrate undo/redo |
| New export/route/coverage workflows | Currently in `ui/main_window.py`; extract a dedicated service when the next change warrants it |
| Version release | Package version, app metadata, spec/version_info, installer, EULA revision, README/docs and test report |

Editable radio objects are copied before applying per-node overrides. Global presets remain defaults. JSON schema 1 loads supported legacy projects; schema 2 includes complete per-node radio parameters and simulation/routing settings. Unknown presets are errors rather than silently substituting another radio. Current family locking prevents cross-technology graph connections; this is not a physical interference model.

Resource paths resolve against the project root in source mode and `sys._MEIPASS` in the frozen distribution. User-writable files are outside the installation folder. Atomic project saves validate values, write a unique adjacent temporary file, flush and replace the destination.

The current heatmap and router search are synchronous, bounded exploratory calculations. Large scenes can pause the interface; 100 nodes/100 walls is an input guardrail, not a responsiveness guarantee. For the next scalability release, snapshot positions/rectangles/profiles into immutable data, run calculations in a cancellable worker, and discard stale results using scene revision IDs. Do not read live QGraphicsItems from a worker.

AI features, cloud data, device scanning, databases and activation services are N/A for this application. No networking permission is needed to simulate a layout. Logs are local diagnostic files and may include local paths if an error occurs; do not share them without reviewing their contents.

## Development verification

`03_Quality_Checks.bat` runs lint, formatting, type checks for the UI-independent domain/storage modules, then real domain and offscreen Qt workflow tests. Type checks do not cover all legacy UI controller code. The frozen self-check verifies bundled assets and demo project round trips. Installed Windows behavior is a separate manual gate. Packaging and signing should occur on Windows with a supported 64-bit interpreter.


## 2.2.5 usability layer

`ui/guided_workspace.py` reparents the existing controls into five stage pages. It does not replace the propagation engine or project model. Navigation and hint preferences are UI state, stored outside project JSON; navigation does not certify progress or mutate simulation settings. Leaving the obstacle stage disables drawing mode. Reviews compute stable directed margins for displayed pairs and track a layout/assumption signature; stale summaries are explicitly invalidated.

`ui/theme.py` resolves bundled checkbox PNGs through the same source/frozen asset path service as application icons. The application requests Fusion styling for consistent widget rendering. Actual Windows display scaling remains a release check. The Excel export computes stable link metrics once using the current scale and shares them across Links and Warnings.
