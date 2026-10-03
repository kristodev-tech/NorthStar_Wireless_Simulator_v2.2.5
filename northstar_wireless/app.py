"""Application startup, first-run terms, logging, and Qt lifecycle."""

import logging
from logging.handlers import RotatingFileHandler
import sys
from pathlib import Path
from PySide6.QtCore import QSettings, QStandardPaths
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication, QDialog, QDialogButtonBox, QTextBrowser, QVBoxLayout
from .services.paths import resource_path
from .ui.theme import app_stylesheet


def accept_terms():
    settings = QSettings("NorthStar Software Works", "Wireless Simulator")
    if settings.value("terms_version", "") == "2.2.5":
        return True
    dialog = QDialog()
    dialog.setWindowTitle("NorthStar Wireless Simulator — Terms")
    dialog.resize(620, 500)
    layout = QVBoxLayout(dialog)
    text = QTextBrowser()
    text.setPlainText(Path(resource_path("docs/EULA.txt")).read_text(encoding="utf-8"))
    layout.addWidget(text)
    buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
    buttons.button(QDialogButtonBox.Ok).setText("I Accept")
    buttons.button(QDialogButtonBox.Cancel).setText("Decline")
    buttons.accepted.connect(dialog.accept)
    buttons.rejected.connect(dialog.reject)
    layout.addWidget(buttons)
    accepted = dialog.exec() == QDialog.Accepted
    if accepted:
        settings.setValue("terms_version", "2.2.5")
    return accepted


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setOrganizationName("NorthStar Software Works")
    app.setApplicationName("NorthStar Wireless Simulator")
    app.setApplicationVersion("2.2.5")
    app.setStyleSheet(app_stylesheet())
    app.setWindowIcon(QIcon(resource_path("assets/branding/northstar.ico")))
    log_dir = Path(QStandardPaths.writableLocation(QStandardPaths.AppDataLocation)) / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    handler = RotatingFileHandler(
        log_dir / "application.log", maxBytes=1000000, backupCount=3, encoding="utf-8"
    )
    logging.basicConfig(
        level=logging.INFO, handlers=[handler], format="%(asctime)s %(levelname)s %(message)s"
    )
    logger = logging.getLogger(__name__)
    logger.info("Starting NorthStar Wireless Simulator 2.2.5")

    def exception_hook(kind, value, trace):
        logger.error("Unhandled application error", exc_info=(kind, value, trace))
        from PySide6.QtWidgets import QMessageBox

        QMessageBox.warning(
            None, "Application error", f"An operation failed: {value}\nDiagnostics: {log_dir}"
        )

    sys.excepthook = exception_hook
    if "--self-test" in sys.argv:
        from .services.self_test import run_self_test

        report = None
        if "--self-test-report" in sys.argv:
            index = sys.argv.index("--self-test-report")
            report = sys.argv[index + 1]
        return run_self_test(app, report)
    if not accept_terms():
        return 0
    from .ui.main_window import MainWindow

    window = MainWindow()
    window.show()
    result = app.exec()
    logger.info("Application closed")
    return result
