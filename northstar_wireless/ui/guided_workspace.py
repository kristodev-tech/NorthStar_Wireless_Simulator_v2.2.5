"""Optional hints and direct stage navigation, using the existing simulator controls."""

from pathlib import Path
from .responsive_controls import WrappingButton as QPushButton, WrappingCheckBox as QCheckBox
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QFormLayout,
    QLayout,
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QSizePolicy,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)
from ..domain.presets import DEMO_NETWORKS, RADIO_PROFILES

STAGES = [
    "1. Network & devices",
    "2. Map & obstacles",
    "3. Coverage & calibration",
    "4. Routes & placement",
    "5. Review, save & export",
]
HINTS = [
    "Load a demo or start a blank project. Choose the radio preset before adding devices. Select a device to edit its label or radio.",
    "Set pixels per meter to match your layout. Draw walls with the selected material, then turn drawing off to move devices. Thickness is a loss multiplier.",
    "Choose a transmitter and show its heatmap. For repeatable readings, turn animated fading off. Select one device to calibrate its radio values.",
    "Choose different route endpoints, then compute an abstract path or suggest a relay position. Every placed node may be used as an intermediate graph point; real hardware must support forwarding.",
    "Review your assumptions and link margins, save the editable JSON project, then export an image or spreadsheet. Estimates still require device and field validation.",
]


class AdaptiveStack(QStackedWidget):
    """Avoid reserving every page's height in the surrounding scroll panel."""

    def sizeHint(self):
        return self.currentWidget().sizeHint() if self.currentWidget() else super().sizeHint()

    def minimumSizeHint(self):
        return (
            self.currentWidget().minimumSizeHint()
            if self.currentWidget()
            else super().minimumSizeHint()
        )


class GuidedWorkspace(QFrame):
    def __init__(self, window):
        super().__init__()
        self.window = window
        self.setObjectName("GuideCard")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        title = QLabel("Planning workspace")
        title.setWordWrap(True)
        title.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Preferred)
        title.setStyleSheet("font-weight: bold; font-size: 15px; color: #87d9ed;")
        layout.addWidget(title)
        self.step = QComboBox()
        self.step.addItems(STAGES)
        self.step.setSizeAdjustPolicy(QComboBox.AdjustToMinimumContentsLengthWithIcon)
        self.step.setMinimumContentsLength(8)
        self.step.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.step.currentTextChanged.connect(self.step.setToolTip)
        self.step.setToolTip(self.step.currentText())
        self.step.setAccessibleName("Planning stage")
        layout.addWidget(self.step)
        self.show_hints = QCheckBox("Show step-by-step hints")
        self.show_hints.setChecked(window.settings.value("show_workflow_hints", True, type=bool))
        layout.addWidget(self.show_hints)
        self.hint = QLabel()
        self.hint.setWordWrap(True)
        self.hint.setObjectName("StepHint")
        layout.addWidget(self.hint)
        self.state = QLabel()
        self.state.setWordWrap(True)
        layout.addWidget(self.state)
        nav = QHBoxLayout()
        self.back = QPushButton("Back")
        self.next = QPushButton("Next")
        nav.addWidget(self.back)
        nav.addWidget(self.next)
        layout.addLayout(nav)
        self.pages = AdaptiveStack()
        self.pages.layout().setSizeConstraint(QLayout.SetNoConstraint)
        self.pages.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        layout.addWidget(self.pages)
        page_layouts = []
        for _ in STAGES:
            page = QWidget()
            page_layout = QVBoxLayout(page)
            page_layout.setContentsMargins(0, 0, 0, 0)
            page_layouts.append(page_layout)
            self.pages.addWidget(page)
        groups = {g.title(): g for g in window.controls_card.findChildren(QGroupBox)}
        self.new_button = QPushButton("Start Blank Project…")
        self.new_button.clicked.connect(window._new_project_wizard)
        page_layouts[0].addWidget(self.new_button)
        page_layouts[0].addWidget(groups["Network / Demo"])
        page_layouts[0].addWidget(groups["Add Device Node"])
        page_layouts[1].addWidget(groups["Scale / Grid"])
        page_layouts[1].addWidget(groups["Obstacles"])
        fit = QPushButton("Fit Layout in Map")
        fit.clicked.connect(
            lambda: window.view.fitInView(
                window.scene.itemsBoundingRect().adjusted(-20, -20, 20, 20), Qt.KeepAspectRatio
            )
        )
        page_layouts[1].addWidget(fit)
        page_layouts[2].addWidget(groups["Heatmap Overlay"])
        page_layouts[2].addWidget(window.calibration_group)
        page_layouts[2].addWidget(window.metrics_card)
        page_layouts[3].addWidget(groups["Routing / Mesh"])
        page_layouts[3].addWidget(window.btn_suggest_router)
        row = QHBoxLayout()
        row.addWidget(window.btn_accept_router)
        row.addWidget(window.btn_reject_router)
        page_layouts[3].addLayout(row)
        page_layouts[3].addWidget(groups["Links"])
        self.review_text = QLabel(
            "Press Review Link Margins for a deterministic summary of the displayed link pairs, in both directions."
        )
        self.review_text.setWordWrap(True)
        review = QPushButton("Review Link Margins")
        review.clicked.connect(self.review_links)
        page_layouts[4].addWidget(review)
        page_layouts[4].addWidget(self.review_text)
        self.save_button = QPushButton("Save Project (JSON)")
        self.save_button.clicked.connect(window._save_current_project)
        page_layouts[4].addWidget(self.save_button)
        save_as = QPushButton("Save Project As…")
        save_as.clicked.connect(window._save_project_dialog)
        page_layouts[4].addWidget(save_as)
        page_layouts[4].addWidget(window.btn_export_png)
        page_layouts[4].addWidget(window.btn_export_xlsx)
        guide = QPushButton("Open Full User Guide")
        guide.clicked.connect(window._open_user_guide)
        page_layouts[4].addWidget(guide)
        for page in [self.pages.widget(i) for i in range(5)]:
            for child in page.findChildren(QWidget):
                # The moved cards were hidden before adoption; restore the cards,
                # leaving conditional accept/reject buttons controlled by the simulator.
                if isinstance(child, QGroupBox):
                    child.show()
        window.metrics_card.show()
        self.back.clicked.connect(
            lambda: self.step.setCurrentIndex(max(0, self.step.currentIndex() - 1))
        )
        self.next.clicked.connect(
            lambda: self.step.setCurrentIndex(min(4, self.step.currentIndex() + 1))
        )
        self.step.currentIndexChanged.connect(self.activate_step)
        self.show_hints.toggled.connect(self.toggle_hints)
        self._review_signature = None
        self.activate_step(0)
        self.toggle_hints(self.show_hints.isChecked())

    def toggle_hints(self, visible):
        self.hint.setVisible(visible)
        self.window.settings.setValue("show_workflow_hints", visible)
        self.updateGeometry()

    def activate_step(self, index):
        if index != 1 and self.window.btn_draw_obs.isChecked():
            self.window.btn_draw_obs.setChecked(False)
        self.pages.setCurrentIndex(index)
        self.hint.setText(HINTS[index])
        self.back.setEnabled(index > 0)
        self.next.setEnabled(index < 4)
        self.pages.setFixedHeight(self.pages.currentWidget().sizeHint().height())
        self.pages.updateGeometry()
        self.updateGeometry()
        if self.window.right_scroll:
            self.window.right_scroll.verticalScrollBar().setValue(0)
        self.refresh()

    def signature(self):
        w = self.window
        return (w._routing_signature(), tuple((id(link.a), id(link.b)) for link in w.links))

    def refresh(self):
        w = self.window
        devices, walls = len(w.nodes), len(w._get_obstacles())
        status = (
            "Unsaved changes"
            if w._dirty
            else ("Saved" if w.current_project_path else "Not saved to a file")
        )
        name = Path(w.current_project_path).name if w.current_project_path else "Untitled"
        self.state.setText(
            f"{name} • {devices} device{'s' if devices != 1 else ''} • {walls} obstacle{'s' if walls != 1 else ''}\n{status}"
        )
        selected = [node for node in w.nodes if node.isSelected()]
        w.btn_edit_radio.setEnabled(len(selected) == 1)
        w.btn_rename_node.setEnabled(len(selected) == 1)
        w.btn_heat_use_selected.setEnabled(len(selected) == 1)
        w.btn_route_use_selected.setEnabled(len(selected) == 2)
        different = w.cb_route_src.currentText() != w.cb_route_dst.currentText()
        w.btn_route_compute.setEnabled(devices >= 2 and different)
        w.btn_suggest_router.setEnabled(devices >= 2)
        w.btn_export_png.setEnabled(devices > 0 or walls > 0)
        w.btn_export_xlsx.setEnabled(devices > 0 or walls > 0)
        w.btn_add_node.setEnabled(devices < 100)
        if self._review_signature is not None and self.signature() != self._review_signature:
            self.review_text.setText(
                "The layout or assumptions changed. Press Review Link Margins to update this summary."
            )
            self._review_signature = None
        self.resize_active_page()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, "pages") and event.size().width() != event.oldSize().width():
            self.resize_active_page()

    def resize_active_page(self):
        page = self.pages.currentWidget()
        if page:
            margins = self.layout().contentsMargins()
            width = max(
                1,
                min(
                    self.pages.width(),
                    self.contentsRect().width() - margins.left() - margins.right(),
                ),
            )
            # Windows font metrics can make paired labels and fields wider than
            # the sidebar. Stack fields before computing the active page height.
            policy = QFormLayout.WrapAllRows if width < 400 else QFormLayout.WrapLongRows
            for form in page.findChildren(QFormLayout):
                if form.rowWrapPolicy() != policy:
                    form.setRowWrapPolicy(policy)
            if self.step.currentIndex() == 4:
                self.review_text.setMinimumHeight(self.review_text.heightForWidth(width))
            page.layout().invalidate()
            height = max(page.sizeHint().height(), page.layout().heightForWidth(width))
            if self.pages.height() != height:
                self.pages.setFixedHeight(height)
                self.updateGeometry()

    def review_links(self):
        w = self.window
        w._update_sim()
        obstacles = w._get_obstacles()
        metrics = []
        for link in w.links:
            metrics.append(w.engine.compute_link_det(link.a, link.b, obstacles, w._m_per_px()))
            metrics.append(w.engine.compute_link_det(link.b, link.a, obstacles, w._m_per_px()))
        if not metrics:
            self.review_text.setText("Add at least two devices to review link margins.")
            return
        below = sum(metric.margin_db < 0 for metric in metrics)
        caution = sum(0 <= metric.margin_db < 6 for metric in metrics)
        minimum = min(metric.margin_db for metric in metrics)
        fading = "on (review uses stable values)" if w.engine.live_fading else "off"
        self.review_text.setText(
            f"Displayed pairs: {len(w.links)} ({len(metrics)} directed estimates)\nBelow sensitivity: {below}\nMargins from 0 to 6 dB: {caution}\nWeakest margin: {minimum:.1f} dB\nScale: {w.px_per_meter:g} px/m\nAdditional loss: {w.engine.extra_loss_db:g} dB\nAnimated fading: {fading}\n\nThis summary is a planning estimate, not a site certification. Review your radio settings and wall assumptions before exporting."
        )
        self._review_signature = self.signature()
        self.resize_active_page()
        self.updateGeometry()


def new_project_dialog(window):
    dialog = QDialog(window)
    dialog.setWindowTitle("Start a blank wireless project")
    dialog.resize(460, 320)
    layout = QVBoxLayout(dialog)
    note = QLabel(
        "Choose the starting radio family and map scale. Your current project is protected by a save/discard/cancel prompt."
    )
    note.setWordWrap(True)
    layout.addWidget(note)
    form = QFormLayout()
    form.setRowWrapPolicy(QFormLayout.WrapLongRows)
    family = QComboBox()
    family.addItems(list(DEMO_NETWORKS))
    profile = QComboBox()

    def choose_family():
        profile.clear()
        profile.addItems(
            [
                key
                for key, p in RADIO_PROFILES.items()
                if p.tech == DEMO_NETWORKS[family.currentText()]
            ]
        )

    family.currentTextChanged.connect(choose_family)
    choose_family()
    scale = QDoubleSpinBox()
    scale.setRange(1, 200)
    scale.setValue(10)
    form.addRow("Radio family:", family)
    form.addRow("Starting profile:", profile)
    form.addRow("Pixels per meter:", scale)
    layout.addLayout(form)
    buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
    buttons.button(QDialogButtonBox.Ok).setText("Create Blank Project")
    buttons.accepted.connect(dialog.accept)
    buttons.rejected.connect(dialog.reject)
    layout.addWidget(buttons)
    if dialog.exec() == QDialog.Accepted:
        start_blank_project(window, profile.currentText(), scale.value())


def start_blank_project(window, profile_key, scale):
    if not window._confirm_replace():
        return False
    window._loading_project = True
    try:
        window._clear_all()
        window.cb_profile.setCurrentText(profile_key)
        window.cb_demo_network.setCurrentText(
            next(
                label
                for label, tech in DEMO_NETWORKS.items()
                if tech == RADIO_PROFILES[profile_key].tech
            )
        )
        window.sp_px_per_m.setValue(scale)
        window.sp_grid_m.setValue(5)
        window.chk_grid.setChecked(True)
        window.chk_snap.setChecked(False)
        window.sp_link_mode.setCurrentText("All-to-All")
        window.sp_nn_k.setValue(2)
        window.cb_node_name.setCurrentText("Sensor")
        window.cb_heat_mode.setCurrentText("RSSI (dBm)")
        window.cb_route_mode.setCurrentText("Best Path (Max-Min Margin)")
        window.chk_heatmap.setChecked(False)
        window.chk_route.setChecked(False)
        window.sp_extra_loss.setValue(0)
        window.chk_live_fading.setChecked(True)
        window.btn_draw_obs.setChecked(False)
        window.view.resetTransform()
    finally:
        window._loading_project = False
    window._persistent_edits = True
    window._set_dirty(True)
    window.workflow.step.setCurrentIndex(0)
    window._refresh_guidance()
    return True
