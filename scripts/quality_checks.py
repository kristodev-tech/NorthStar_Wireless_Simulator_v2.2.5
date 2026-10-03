"""Run the release checks with a persistent, readable diagnostic log."""

import argparse
from pathlib import Path
import os
import platform
import subprocess
import sys


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--layout-stress", action="store_true", help="Run optional extreme layout checks"
    )
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    output = root / "build"
    output.mkdir(exist_ok=True)
    env = os.environ.copy()
    env["QT_QPA_PLATFORM"] = "offscreen"
    targets = ["main.py", "northstar_wireless", "tests", "scripts/quality_checks.py"]
    selection = "layout_stress" if args.layout_stress else "not layout_stress"
    report_name = "pytest-stress-results.xml" if args.layout_stress else "pytest-results.xml"
    checks = [
        ("Ruff lint", ["ruff", "check", *targets]),
        ("Ruff format", ["ruff", "format", "--check", *targets]),
        ("Domain and storage type checks", ["mypy"]),
        (
            "Optional layout stress tests"
            if args.layout_stress
            else "Functional and normal-size UI tests",
            ["pytest", "-q", "-m", selection, f"--junitxml=build/{report_name}"],
        ),
    ]
    log_path = output / (
        "quality_checks_stress.log" if args.layout_stress else "quality_checks.log"
    )
    with log_path.open("w", encoding="utf-8") as log:

        def write(text):
            print(text, end="", flush=True)
            log.write(text)
            log.flush()

        write(f"Python: {sys.version}\nSystem: {platform.platform()}\n")
        write(f"QT_SCALE_FACTOR: {env.get('QT_SCALE_FACTOR', 'default')}\nLog: {log_path}\n")
        for index, (title, command) in enumerate(checks, 1):
            write(f"[{index}/4] {title}\n")
            process = subprocess.Popen(
                [sys.executable, "-m", *command],
                cwd=root,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding="utf-8",
                errors="replace",
            )
            for line in process.stdout:
                write(line)
            result = process.wait()
            if result:
                write(f"Check failed with code {result}. See {log_path}\n")
                return result
        write("All checks passed.\n")
        if not args.layout_stress:
            write(
                "Extreme layout checks are optional: run 07_Layout_Stress_Tests.bat separately.\n"
            )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
