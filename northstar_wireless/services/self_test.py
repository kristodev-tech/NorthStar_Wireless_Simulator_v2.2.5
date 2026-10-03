"""Packaged startup self-check. Not a substitute for installed Windows QA."""

import json
import logging
import tempfile
from pathlib import Path
from PySide6.QtCore import QTimer
from PySide6.QtGui import QIcon
from ..domain.presets import DEMO_NETWORKS
from .paths import resource_path
from .project_store import save_project


def run_self_test(app, report_path=None):
    result = {"version": "2.2.5", "passed": False, "checks": []}
    window = None
    try:
        from ..ui.main_window import MainWindow

        for resource in [
            "assets/branding/northstar.ico",
            "assets/icons/ico_new.png",
            "assets/ui/check_checked.png",
            "docs/EULA.txt",
            "docs/User_Guide.html",
        ]:
            if not Path(resource_path(resource)).is_file():
                raise FileNotFoundError(resource)
        if QIcon(resource_path("assets/branding/northstar.ico")).isNull():
            raise ValueError("App icon failed to load")
        result["checks"].append("bundled assets")
        window = MainWindow(enable_recovery=False)
        window.tick.stop()
        window._cursor_timer.stop()
        window.autosave_timer.stop()
        with tempfile.TemporaryDirectory(prefix="northstar-selftest-") as directory:
            for label, tech in DEMO_NETWORKS.items():
                window._add_demo(tech)
                window._update_sim()
                path = Path(directory) / "project.json"
                save_project(path, window._project_to_dict())
                window._apply_project_dict(json.loads(path.read_text()))
                if len(window.nodes) != 3:
                    raise ValueError("Demo reload failed")
                result["checks"].append(label)
        # Verify the guided UI in the frozen build, not just resource loading.
        for width, height in [(1024, 700), (1366, 768)]:
            window.resize(width, height)
            window.show()
            for stage in range(5):
                window.workflow.step.setCurrentIndex(stage)
                app.processEvents()
                if window.right_scroll.horizontalScrollBar().maximum():
                    from ..ui.layout_diagnostics import layout_snapshot

                    raise ValueError(json.dumps(layout_snapshot(window)))
        result["checks"].append("guided layouts at 1024 and 1366 pixels")
        result["passed"] = True
    except Exception as error:
        logging.getLogger(__name__).exception("Self-check failed")
        result["error"] = str(error)
    finally:
        if window:
            for timer in window.findChildren(QTimer):
                timer.stop()
            window.hide()
        if report_path:
            Path(report_path).write_text(json.dumps(result, indent=2), encoding="utf-8")
    return 0 if result["passed"] else 1
