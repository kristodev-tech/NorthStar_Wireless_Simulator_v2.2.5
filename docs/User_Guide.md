# NorthStar Wireless Simulator
## User Guide • Version 2.2.5

NorthStar Software Works

This guide describes the current application. The included legacy 1.2 Word document is retained for reference and does not describe the new radio options or fixes.

## Guided workspace — start here

Use the stage selector at the top of the right panel to choose **Network & devices**, **Map & obstacles**, **Coverage & calibration**, **Routes & placement**, or **Review, save & export**. Back/Next move between stages; you can jump directly to any stage. The map stays available. Hide **Show step-by-step hints** when you prefer direct editing.

The workspace shows device/wall counts and whether the project has a saved file or unsaved changes. It does not mark calibration or radio accuracy as complete automatically. Controls needing a selection are disabled until you select the appropriate device(s). Moving away from Map & obstacles turns obstacle drawing off to avoid accidental walls.

**Start Blank Project** opens a small setup dialog for the radio family, starting profile and map scale. Cancel leaves your project unchanged; creating another project first handles any unsaved work. The new project starts with no devices, the selected radio preset and fresh map/simulation settings.

Checkboxes use an explicit empty box when off and a filled cyan box with a white tick when on. Disabled checked states use a muted tick. Obstacle drawing buttons also show a filled pressed state while active.

In the final stage, **Review Link Margins** summarizes displayed link pairs in both directions using stable values, identifies margins below sensitivity or below 6 dB, and shows scale/loss assumptions. A changed layout invalidates the review so old results cannot appear current. This review concerns the displayed pairs; it does not certify a real installation.

## 1. What the simulator does

Place wireless devices on a map, draw walls, then explore estimated signal strength and receiver margin. A heatmap shows coverage from a selected transmitter. Routing highlights abstract paths through the placed devices, and router suggestions search for a position with a stronger weakest link.

These are estimates based on a simplified model. The application does not discover nearby Wi-Fi, pair Bluetooth devices, use your computer's radio, or communicate with real scales. It runs offline once installed.

## 2. Launching

For the source package, first run `01_Setup_Environment.bat`, then `02_Run_App.bat`. The setup installs all dependencies into the project's private `.venv`. You need Python 3.11, 3.12 or 3.13 on Windows. Setup requires internet access; simulation does not.

For a built installer, run the setup EXE, review and accept the terms, and choose whether to create a desktop shortcut. The installed app does not require a separate Python installation. You will also see application terms on its first launch.

The main window contains a map on the left and five selectable planning stages in a scrollable controls area on the right. Drag the divider to change their relative widths. If controls extend below the window, scroll the right panel. Resizing the window preserves access to the controls. Use View → Fit Layout (Ctrl+0) to see the entire layout, or Actual Scale (Ctrl+1) to reset the view. Press F1 for the original quick-start help; read this guide for v2 features.

## 3. Start with a demo or a blank project

Choose a family under Network / Demo and press **Load Demo**. The simulator replaces the current scene with three devices and a drywall obstacle. It prompts you to save unsaved work before replacing it.

For a blank layout, use **File → New Project** or **Start Blank Project** in stage 1. Choose the family, starting radio profile and scale, then create the project. Choose a device label and press **Add Node**. **New / Clear** on the map also clears a layout after handling unsaved work. The first node locks the project to that radio family. This prevents incompatible technologies from appearing connected. Start a new project to use a different family.

Example layouts are also included in `examples/`. Open one using **File → Load Project**. Wi-Fi 2.4, 5 and 6 GHz are separate planning families; BLE 1M, 2M and Coded profiles share a family under the assumption that the endpoints support the PHY used.

## 4. Place and label devices

Drag a device to reposition it. Ctrl+click lets you select multiple devices. Select one device before changing its label or radio preset. Node additions, moves, deletion, radio calibration and label changes support Undo/Redo from the Edit menu or Ctrl+Z/Ctrl+Y.

Device labels include Scale, Router, Gateway, Sensor, Repeater, Access Point, Laptop, Phone, Bluetooth Peripheral, BLE Beacon, Headset and IoT Device. These names help identify equipment. They do not implement the device's protocol behavior or decide whether it is physically capable of forwarding packets.

**Delete Selected** removes selected devices or obstacles. Clear removes the complete layout after handling unsaved work.

## 5. Map scale and walls

**Pixels per meter** determines how screen distance converts to physical distance. At 10 pixels/meter, 100 pixels represents 10 meters. Use **Grid spacing (m)** to set the visible grid. Show grid and Snap to grid control display and movement snapping.

Choose an obstacle material and enable **Draw Obstacles**. Click and drag a rectangle on the map. Disable drawing when finished. Select an obstacle to change its material and **Thickness (x)** multiplier. Thickness is a multiplier of the preset material loss, not a measured thickness in centimeters. Moving, deleting or changing obstacles affects link estimates.

The model weights a corner graze less than a full crossing. Default attenuation values are approximate and are not frequency-dependent construction measurements. Calibrate against your actual wall and device measurements.

## 6. Calibrate an individual radio

Select one device and press **Edit Selected Radio Parameters** in Simulation / Calibration.

| Setting | Meaning |
| --- | --- |
| TX power, dBm | Transmitter output used by the model; antenna gains are not separate settings |
| Sensitivity, dBm | Receiver threshold at the chosen operating mode; more negative means a weaker signal can be received |
| Frequency, MHz | Nominal band information; changing this alone does not coordinate channels or change the reference loss |
| Reference loss at 1 m, dB | Model path loss at the reference distance |
| Path loss exponent | How quickly loss increases with distance; larger values decay faster |
| Fading standard deviation, dB | Amount of random variation in animated link estimates |

The button **Use Free-Space Reference Loss for Frequency** recalculates the reference loss from the chosen frequency. This is explicit so an experimentally calibrated reference loss is not accidentally replaced. Save applies to that device only; shared preset defaults are not modified. Cancel discards the dialog edits. Radio edits can be undone and are stored in project JSON.

Use device data sheets and measurements at the intended PHY/data rate. A sensitivity value at one rate does not imply the same sensitivity at every rate. The Bluetooth coded preset is illustrative, not a guaranteed range improvement. The LoRa preset does not model spreading factors, coding rates, airtime or regional rules.

## 7. Stable mode and additional loss

Uncheck **Animate random fading** for repeatable live link readings. Heatmaps and routing always use deterministic values. With fading enabled, link readings fluctuate around the model's average; those fluctuations are not recordings of physical interference.

**Additional loss** adds a common loss allowance to links, heatmaps and router scoring. It can represent a conservative planning allowance for unknown conditions. It does not compute channel interference, noise floor, SINR or competing traffic.

## 8. Read link metrics

Ctrl+click two devices to focus their link. The metrics panel represents a directed A → B estimate in the simulator's current link ordering. TX comes from A and receiver sensitivity comes from B. Reverse direction may have a different margin. Hover a link to see its direction, RSSI, margin, estimated success, distance and wall loss.

- **RSSI:** estimated received power in dBm.
- **Margin:** RSSI minus the receiver sensitivity; positive values are above the threshold.
- **Success estimate:** a heuristic curve mapping margin to a percentage, not a measured packet delivery rate.
- **Retries/latency estimates:** generic formulas for comparison, not protocol timing guarantees.

Link colors communicate estimated quality. A visible link is not proof of a real association or a viable route.

Under Links, choose All-to-All or Nearest Neighbor and set K. This changes which links are drawn. Routing considers all viable directed pairs independently of the drawn-link mode. For nearest-neighbor display, repositioning nodes is followed on the next simulation refresh.

## 9. Use the heatmap

Enable **Show Heatmap**, choose its transmitter, and choose RSSI, Margin or Success. **Use Selected Node as TX** selects the currently selected device. The heatmap assumes a receiver with the transmitter profile's sensitivity at each map point.

The heatmap refreshes after a meaningful change, including device movement, wall thickness, radio calibration, map scale or additional loss. Repeated unchanged updates reuse the existing image. Moving the pointer over the map updates the cursor readout.

Green/red heatmap colors represent the configured metric, not an exact measured boundary. The RSSI color legend uses a fixed -110 to -40 dBm range; values outside it saturate. Use margin when comparing radios with very different sensitivity, such as the illustrative LoRa preset.

## 10. Explore routes and router placement

Enable multi-hop routing, choose different Source and Destination devices, and press **Compute Route**. You can also select two devices and use **Use Selected (2 nodes)**.

- **Max-Min Margin:** maximize the weakest hop's receiver margin.
- **Min Total Loss:** minimize the total modeled path loss across the chosen hops.

Hops below receiver sensitivity are excluded. The report shows the path, number of hops, bottleneck margin, and heuristic end-to-end success/latency. If no route is found, move devices closer, reduce measured loss assumptions if justified, or add a genuinely relay-capable device.

These paths are abstract graph results. Bluetooth Classic and ordinary BLE nodes do not automatically form mesh networks; Wi-Fi stations do not automatically relay between each other. The graph currently allows any placed node to act as an intermediate point. Interpret a suggested path only where real hardware and network configuration support each hop.

**Suggest Router Placement** searches a coarse map grid for a position improving the weakest link while avoiding obstacles. Accept adds a router node; Reject dismisses the marker. It is a planning suggestion, not an optimal-layout proof or a protocol-aware deployment plan.

## 11. Save, open and recover

Use **File → Save Project** (Ctrl+S) to update the current file. The first save opens a file chooser. **Save Project As** always opens the chooser so you can save a separate copy. The Save button in stage 5 follows the same rules. JSON contains the devices, actual edited radio values, obstacles, map settings, link display, heatmap, simulation allowance and routing choices. Explicit saves use an atomic replacement so a failed write preserves the previous file.

The title displays an asterisk for unsaved work. Changes to saved simulation/view settings also mark the project dirty. Project replacement prompts you to save, discard or cancel. Closing a modified project offers saving; canceling or a failed save keeps the app open.

Every 30 seconds, modified nonempty projects are saved to a per-user recovery file. If it exists at startup, the app offers recovery. Save a recovered layout to a normal JSON file. A successful explicit save removes the stale recovery file. Recovery is a convenience, not a substitute for your own backups.

Malformed projects, unsupported schema versions, unknown presets, nonfinite numbers and mixed radio families are rejected before replacing the current layout. Up to 100 devices and 100 obstacles are accepted as a guardrail; practical performance depends on layout size and hardware. Keep exploratory layouts small and use nearest-neighbor display for larger examples.

## 12. Export and share results

**Export Snapshot PNG** saves the map image. **Export XLSX (All Data)** saves the simulator's original engineering workbook with node profiles, obstacles, links, routing and heatmap data where enabled. Open it in Excel or another spreadsheet viewer.

Excel exports use one deterministic snapshot, independent of animated fading, and use the selected physical map scale. The Summary sheet records scale, extra loss, heatmap and routing choices. The Nodes sheet includes reference loss, exponent and fading settings; Obstacles includes the thickness multiplier. Links and Warnings use the same computed values. The map may show an animated moment while the workbook shows stable values; turn fading off to compare them directly. Keep the JSON project alongside exported images and workbooks so the assumptions can be reviewed.

## 13. Formula and assumptions

The link budget is:

`RSSI = TX − PL₀ − 10 × n × log10(distance_m) − wall_loss − additional_loss + fading`

Reference distance is 1 m. Modeled distance is at least 0.5 m. The free-space reference estimate is `PL₀ = 20 × log10(frequency_MHz) − 27.55`.

The generic success curve is `100 × clamp((margin + 10) / 25, 0, 1)`. Retries are `clamp((100 − success) / 18, 0, 6)`. Latency is `8 + 0.4 × distance_m + 6 × retries`, in milliseconds. These heuristic curves are the same across technologies. They are useful for demonstrations but do not imply physical packet statistics. Routes add a generic 4 ms per-hop allowance.

Multipath, antenna patterns, terrain elevation, 3D geometry, channel contention, throughput, Wi-Fi association, Bluetooth pairing, Bluetooth hopping, BLE advertising timing, LoRa airtime and spectral interference are outside this version's model. Material losses do not change with frequency. Use measured calibration and field tests before making equipment or installation decisions.

## 14. Local data, branding and support

Projects are stored wherever you choose. Logs and recovery files are in the Qt per-user AppData location under NorthStar Software Works / NorthStar Wireless Simulator, with log files under `logs`. Windows settings use the NorthStar Software Works / Wireless Simulator registry namespace. Uninstalling the app does not intentionally delete your project files or per-user recovery/settings.

The package supplies an optional wallpaper and 800×800 product image. The installer does not change your Windows wallpaper automatically. Branding assets were created with AI assistance.

If the source app does not launch, rerun setup, then launch with `02_Run_App.bat` to keep error messages visible. If tests say pytest or Ruff is missing, use `03_Quality_Checks.bat` rather than the global Python interpreter. For a compiled build, keep the complete PyInstaller distribution together; the EXE depends on its neighboring `_internal` folder. Review application logs for errors.

Support: https://northstarsoftwareworks.com


## Module experiments and project names (2.2.5)

Choose Wi-Fi Module, Bluetooth Module, BLE Module, Zigbee Module, LoRa Module,
RF Module, Development Board, Transceiver, Test Node or Custom Device in Device type.
Then choose the radio profile for your experiment. Device type is a label; it
never selects the protocol or radio parameters. Existing single-family and relay
model assumptions still apply.

Enter an optional New device name before Add Node (for example `Roof prototype A`).
Leave it empty for automatic numbered names. Select one device and use Rename
Selected Device to change its name. Names must be unique, contain 1–120 characters,
and have no line breaks. Renaming supports Undo/Redo and preserves selected heatmap
transmitters and route endpoints. Changing device type keeps an explicit custom
name. Names are included in project saves, recovery, map labels and exports.

Obstacle type now includes wood, brick, reinforced concrete, metal doors, office
partitions, furniture, racks, machinery, people, foliage and water tanks. Draw a
rectangle representing the object; use Thickness to scale its modeled loss. These
are illustrative, frequency-independent presets, not measured material data or
physical body/object models. Calibrate against measurements for your setup.

In narrow panels, labels appear above their fields so larger text fits without horizontal scrolling. Longer stages remain vertically scrollable. Select one device and choose Edit Selected Radio… to adjust its parameters.

Button and checkbox captions wrap when needed, and their height grows to keep the text visible. Click anywhere on a checkbox caption to toggle it. Dropdowns use compact widths; open the list or hover to read longer options.

The coverage legend can grow vertically when its labels wrap, so larger fonts do not widen the planning panel. Build-test diagnostics are described in Windows_Validation.md.
