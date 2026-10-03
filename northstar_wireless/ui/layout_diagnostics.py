"""Describe width constraints when a GUI regression fails."""

from PySide6.QtWidgets import QWidget


def layout_snapshot(window):
    panel = window.right_scroll
    rows = []
    for child in window.workflow.findChildren(QWidget):
        if child.isVisible():
            text = child.text() if callable(getattr(child, "text", None)) else ""
            rows.append(
                {
                    "type": type(child).__name__,
                    "text": text,
                    "width": child.width(),
                    "height": child.height(),
                    "minimum_width": child.minimumWidth(),
                    "minimum_hint_width": child.minimumSizeHint().width(),
                    "size_hint_width": child.sizeHint().width(),
                    "font": child.font().toString(),
                }
            )
    return {
        "stage": window.workflow.step.currentText(),
        "viewport_width": panel.viewport().width(),
        "horizontal_overflow": panel.horizontalScrollBar().maximum(),
        "widgets": rows,
    }
