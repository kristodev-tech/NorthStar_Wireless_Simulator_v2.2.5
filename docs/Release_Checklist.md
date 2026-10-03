# Windows release checklist

This is a source/build kit. Windows binaries, Inno compilation, signing and clean-machine install checks remain to be performed on Windows.

1. Extract to a fresh writable folder. Run setup using the intended 64-bit Python 3.11, 3.12 or 3.13. Record interpreter and dependency versions; Python 3.12 is the source-tested interpreter.
2. Run quality checks; stop if any gate fails. Build the EXE; inspect the frozen self-check JSON in `build/self_test.json`.
3. Launch the actual visible EXE from `dist/NorthStarWirelessSimulator`. Review terms acceptance/decline, icons, menus, About/version, original features and each radio family. Check 1024×700, 1366×768 and high-DPI display scaling.
4. Open a real legacy v1 JSON project. Save under a new name, reopen, and compare nodes/walls/settings. Test radio overrides, Undo/Redo, delete/restore nodes and a failed/invalid load. Preserve the original v1 file.
5. Test drawing and moving walls, thickness, map scale, two route algorithms, no-path behavior, router suggestion accept/reject, heatmap changes and cursor values. Verify Save/Cancel/Discard before replacing layouts and during close.
6. Wait over 30 seconds after a modification, terminate the process without closing normally, relaunch and recover. Save the recovered file. Check failed saves in an inaccessible folder and failed exports.
7. Export PNG and XLSX; open and inspect both. Use stable mode for repeatable comparisons. Compare a small measured layout to calibrate presets before using results operationally.
8. Review EULA/purchase/source redistribution terms for your distribution model. Confirm Qt/PySide6 LGPL obligations and all actual bundled licenses/notices. See THIRD_PARTY_NOTICES.md. Confirm any branding use and AI disclosure needed on the product page.
9. Sign the EXE if configured, then build the installer from the final signed binaries; sign and verify the installer. Never modify signed artifacts afterward. Record hashes. An unsigned build is for testing; a self-signed certificate is trusted only where installed/trusted appropriately.
10. Install on a representative clean Windows 11 Home and Pro PC. Check terms page, default per-user location, shortcut icons, launch from Start Menu/Desktop, examples, documentation, uninstall and reinstall. Also test upgrade over a previous v2 build; confirm project data/settings are preserved. Windows 10 behavior is unverified.
11. Freeze the exact source, requirements, version metadata, build logs, test results, final installer and release hash with your release tag. Keep rollback source and user project backups.

The wallpaper is supplied as optional artwork; the installer must not set it automatically. Personal project files are never included in the product installer.


## Additional 2.2.5 acceptance checks

- Verify grid, snap, heatmap, route, fading and hint checkboxes show explicit checked and unchecked states, including disabled controls. Check keyboard focus and 100%, 125%, 150% and 200% Windows scaling.
- Navigate every stage, hide/show hints, scroll to every control and confirm the map remains usable. Verify Back/Next never replace or save a project automatically.
- Create a blank project for Wi-Fi/Bluetooth and test Save/Discard/Cancel while replacing existing work. Cancel must leave the layout unchanged. Opening a 2.0.0 project must preserve its saved assumptions.
- Test ordinary Save updating its existing JSON file, and Save As creating a separate copy. Review link margins, change scale or a wall, then verify the review says it needs updating.
- Export at a nondefault physical scale and verify distances in Excel against the current layout. Verify the workbook's Summary, calibration and thickness columns, and opening the HTML guide from the app and installer shortcut.
