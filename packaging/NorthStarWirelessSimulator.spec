from pathlib import Path
root = Path(SPECPATH).parent
analysis = Analysis([str(root / "main.py")], pathex=[str(root)],
    binaries=[], datas=[(str(root / "assets"), "assets"), (str(root / "docs"), "docs"),
                       (str(root / "examples"), "examples")], hiddenimports=[],
    hookspath=[], hooksconfig={}, runtime_hooks=[], excludes=[], noarchive=False)
pyz = PYZ(analysis.pure)
exe = EXE(pyz, analysis.scripts, [], exclude_binaries=True, name="NorthStarWirelessSimulator",
    debug=False, bootloader_ignore_signals=False, strip=False, upx=False, console=False,
    icon=str(root / "assets/branding/northstar.ico"),
    version=str(root / "packaging/version_info.txt"))
collection = COLLECT(exe, analysis.binaries, analysis.datas, strip=False, upx=False,
                     name="NorthStarWirelessSimulator")
