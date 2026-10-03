"""Radio calibration edits are isolated from presets and participate in undo/redo."""

from dataclasses import replace
from PySide6.QtGui import QUndoCommand
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QFormLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)
from ..domain.link_budget import reference_loss
from ..services.project_store import RADIO_RANGES


class ChangeRadioCommand(QUndoCommand):
    def __init__(self, window, node, profile, key):
        super().__init__("Change radio parameters")
        self.window, self.node = window, node
        self.old, self.old_key = node.profile, node.profile_key
        self.new, self.new_key = replace(profile), key

    def _apply(self, profile, key):
        self.node.profile, self.node.profile_key = profile, key
        self.node._refresh_label()
        self.window._mark_heatmap_dirty()
        self.window._mark_route_dirty()
        self.window._on_selection_changed()

    def redo(self):
        self._apply(self.new, self.new_key)

    def undo(self):
        self._apply(self.old, self.old_key)


def edit_radio(window, node):
    dialog = QDialog(window)
    dialog.setWindowTitle(f"Radio calibration — {node.name}")
    dialog.resize(460, 540)
    layout = QVBoxLayout(dialog)
    note = QLabel(
        "These values apply only to this device. Preset defaults are illustrative; calibrate with device specifications and measurements."
    )
    note.setWordWrap(True)
    layout.addWidget(note)
    content = QWidget()
    form = QFormLayout(content)
    form.setRowWrapPolicy(QFormLayout.WrapLongRows)
    fields = {}
    labels = {
        "tx_dbm": "TX power (dBm)",
        "sens_dbm": "Sensitivity (dBm)",
        "freq_mhz": "Frequency (MHz)",
        "pl_d0_db": "Reference loss at 1 m (dB)",
        "n": "Path loss exponent",
        "noise_sigma_db": "Fading standard deviation (dB)",
    }
    for key, limits in RADIO_RANGES.items():
        widget = QDoubleSpinBox()
        widget.setRange(*limits)
        widget.setDecimals(2)
        widget.setValue(getattr(node.profile, key))
        form.addRow(labels[key], widget)
        fields[key] = widget
    reference = QPushButton("Use Free-Space Reference Loss for Frequency")
    reference.clicked.connect(
        lambda: fields["pl_d0_db"].setValue(reference_loss(fields["freq_mhz"].value()))
    )
    form.addRow(reference)
    scroll = QScrollArea()
    scroll.setWidgetResizable(True)
    scroll.setWidget(content)
    layout.addWidget(scroll)
    buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
    buttons.accepted.connect(dialog.accept)
    buttons.rejected.connect(dialog.reject)
    layout.addWidget(buttons)
    if dialog.exec() == QDialog.Accepted:
        profile = replace(node.profile, **{key: widget.value() for key, widget in fields.items()})
        window.undo_stack.push(ChangeRadioCommand(window, node, profile, node.profile_key))
