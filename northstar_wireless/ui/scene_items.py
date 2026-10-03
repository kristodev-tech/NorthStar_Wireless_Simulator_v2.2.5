import math


from typing import Optional


from PySide6.QtCore import Qt, QPointF, QRectF, QTimer

from PySide6.QtGui import (
    QBrush,
    QColor,
    QFont,
    QPainter,
    QPen,
    QImage,
    QPixmap,
    QLinearGradient,
    QPainterPathStroker,
    QPainterPath,
)

from PySide6.QtWidgets import (
    QFrame,
    QSizePolicy,
    QGraphicsItem,
    QGraphicsLineItem,
    QGraphicsRectItem,
    QGraphicsScene,
    QGraphicsTextItem,
    QGraphicsView,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
    QGraphicsPixmapItem,
    QScrollArea,
    QGraphicsEllipseItem,
)

from ..domain.models import RadioProfile, ObstacleMaterial, MATERIALS
from .commands import _CmdMoveItem, _CmdAddObstacle


def clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, v))


def dist(a: QPointF, b: QPointF) -> float:
    dx = a.x() - b.x()
    dy = a.y() - b.y()
    return math.hypot(dx, dy)


class NodeItem(QGraphicsEllipseItem):
    """
    Draggable device node with a label.
    """

    def __init__(
        self,
        name: str,
        profile: RadioProfile,
        base_label: str,
        type_number: int,
        profile_key: str,
        pos: QPointF,
    ):
        r = 16
        super().__init__(-r, -r, 2 * r, 2 * r)

        # ── Interaction flags ────────────────────────────────────────────────
        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges, True)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)

        # Keep nodes above obstacles/links
        self.setZValue(20)

        # ── Identity / UI sync fields ────────────────────────────────────────
        self.name = name
        self.profile = profile

        self.custom_name = name != f"{base_label}{type_number}"
        self.base_label = base_label  # "Scale", "Gateway", etc.
        self.type_number = type_number  # 1, 2, 3... (reused when deleted)
        self.profile_key = profile_key  # key in RADIO_PROFILES dict

        self.setPos(pos)

        # ── Visuals ─────────────────────────────────────────────────────────
        self._label = QGraphicsTextItem(self)
        self._label.setPlainText(self.name)
        self._label.setDefaultTextColor(QColor("#e8e8e8"))
        self._label.setFont(QFont("Segoe UI", 9))
        self._label.setPos(-28, 18)
        self._label.setZValue(50)

        self._apply_style()

    def _refresh_label(self):
        """Call after renaming."""
        self._label.setPlainText(self.name)

    def mousePressEvent(self, event):
        self._drag_start_pos = QPointF(self.pos())
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)
        try:
            mw = getattr(self.scene(), "_mw", None)
            if not mw or getattr(mw, "_loading_project", False):
                return
            old = getattr(self, "_drag_start_pos", None)
            new = QPointF(self.pos())
            if old is not None and (old != new):
                mw.undo_stack.push(_CmdMoveItem(self, old, new, mw, text="Move Node"))
        except Exception:
            pass

    def _apply_style(self):
        # Fill changes when selected
        if self.isSelected():
            self.setBrush(QBrush(QColor("#2d7dff")))
            self.setPen(QPen(QColor("#9fc0ff"), 2))
        else:
            self.setBrush(QBrush(QColor("#1f2a3f")))
            self.setPen(QPen(QColor("#45d7ff"), 2))

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemPositionChange:
            sc = self.scene()
            mw = getattr(sc, "_mw", None) if sc else None
            if mw and getattr(mw, "snap_to_grid", False):
                return mw._snap_point(QPointF(value))

        if change in (QGraphicsItem.ItemSelectedChange, QGraphicsItem.ItemSelectedHasChanged):
            QTimer.singleShot(0, self._apply_style)

        return super().itemChange(change, value)

    def scene_center(self) -> QPointF:
        return self.mapToScene(QPointF(0, 0))


class ObstacleItem(QGraphicsRectItem):
    """
    Obstacle rectangle with attenuation label centered above it.

    IMPORTANT:
    - We store the rectangle in LOCAL coordinates (0,0,w,h)
    - We place the item in the scene using setPos(scene_rect.topLeft())
    This prevents label positioning from drifting "far away" due to scene-based rect origins.
    """

    def __init__(self, rect: QRectF, material: ObstacleMaterial, thickness: float = 1.0):
        # Force local rect (0,0,w,h)
        local_rect = QRectF(0, 0, rect.width(), rect.height())
        super().__init__(local_rect)

        # Place obstacle at the intended scene position
        self.setPos(rect.topLeft())

        # ── Interaction flags ────────────────────────────────────────────────
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.ItemIsMovable, True)

        # ✅ Keep obstacles below nodes but above link lines
        self.setZValue(10)

        self.material = material
        self.thickness = float(max(0.1, thickness))  # ✅ keep sane

        self.setToolTip(
            f"<b>{self.material.name}</b><br>Attenuation: <b>-{self.material.attenuation_db:.0f} dB</b>"
        )
        # ── Label (centered above) ───────────────────────────────────────────
        self._label = QGraphicsTextItem(self)
        self._label.setDefaultTextColor(QColor("#b9c2d3"))
        self._label.setFont(QFont("Segoe UI", 8))

        # Keep text readable when zooming
        self._label.setFlag(QGraphicsItem.ItemIgnoresTransformations, True)

        # Ensure it renders above the obstacle
        self._label.setZValue(999)

        self._set_label_text()
        self._apply_style()

    def mousePressEvent(self, event):
        self._drag_start_pos = QPointF(self.pos())
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)
        try:
            mw = getattr(self.scene(), "_mw", None)
            if not mw or getattr(mw, "_loading_project", False):
                return
            old = getattr(self, "_drag_start_pos", None)
            new = QPointF(self.pos())
            if old is not None and (old != new):
                mw.undo_stack.push(_CmdMoveItem(self, old, new, mw, text="Move Obstacle"))
        except Exception:
            pass

    def _update_tooltip(self):
        eff = self.material.attenuation_db * self.thickness
        self.setToolTip(
            f"<b>{self.material.name}</b><br>"
            f"Base: <b>-{self.material.attenuation_db:.1f} dB</b><br>"
            f"Thickness: <b>x{self.thickness:.2f}</b><br>"
            f"Max loss (full pass): <b>-{eff:.1f} dB</b>"
        )

    def _set_label_text(self):
        eff = self.material.attenuation_db * self.thickness
        self._label.setPlainText(f"{self.material.name} (-{eff:.0f} dB)")
        self._update_label_pos()
        self._update_tooltip()

    def _apply_style(self):
        # Material color hint
        name = self.material.name.lower()
        if "metal" in name:
            fill = QColor(120, 120, 120, 80)
            edge = QColor("#c6c6c6")
        elif "concrete" in name:
            fill = QColor(150, 130, 110, 80)
            edge = QColor("#d9c7b7")
        elif "glass" in name:
            fill = QColor(80, 160, 200, 60)
            edge = QColor("#8bd7ff")
        else:
            fill = QColor(160, 160, 160, 50)
            edge = QColor("#b9c2d3")

        self.setBrush(QBrush(fill))
        self.setPen(QPen(edge, 2))

    def _update_label_pos(self):
        """
        Center the label above the obstacle (using LOCAL rect).
        """
        br = self._label.boundingRect()
        r = self.rect()  # local rect (0,0,w,h)

        x = (r.width() - br.width()) / 2.0
        y = -br.height() - 2.0
        self._label.setPos(x, y)

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemPositionChange:
            sc = self.scene()
            mw = getattr(sc, "_mw", None) if sc else None
            if mw and getattr(mw, "snap_to_grid", False):
                return mw._snap_point(QPointF(value))

        if change in (QGraphicsItem.ItemPositionHasChanged, QGraphicsItem.ItemTransformHasChanged):
            self._update_label_pos()

        return super().itemChange(change, value)


class LinkItem(QGraphicsLineItem):
    """
    Line between two nodes. Color by quality.
    """

    def __init__(self, a: NodeItem, b: NodeItem):
        super().__init__()
        self.a = a
        self.b = b
        self.setZValue(2)
        self.setPen(QPen(QColor("#2fdc71"), 2))  # default green
        self.setFlag(QGraphicsItem.ItemIsSelectable, False)

    def shape(self):
        stroker = QPainterPathStroker()
        stroker.setWidth(12)  # hover hit width
        p = QPainterPath()
        p.moveTo(self.line().p1())
        p.lineTo(self.line().p2())
        return stroker.createStroke(p)


class MapView(QGraphicsView):
    """
    Adds an "obstacle draw" mode:
      - click+drag to create a rectangle obstacle
    """

    def __init__(self, scene: QGraphicsScene, parent=None):
        super().__init__(scene, parent)
        self.setRenderHints(QPainter.Antialiasing | QPainter.SmoothPixmapTransform)
        self.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)
        self.setDragMode(QGraphicsView.RubberBandDrag)

        self.setMouseTracking(True)
        self.viewport().setMouseTracking(True)

        self.draw_obstacles = False
        self.draw_material = MATERIALS["Concrete"]

        self._drag_start: Optional[QPointF] = None
        self._preview_rect: Optional[QGraphicsRectItem] = None

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.window():
            self.window()._on_view_resized(self.viewport().size())

    def set_draw_mode(self, enabled: bool):
        self.draw_obstacles = enabled
        self.setDragMode(QGraphicsView.NoDrag if enabled else QGraphicsView.RubberBandDrag)

    def drawBackground(self, painter: QPainter, rect: QRectF):
        super().drawBackground(painter, rect)

        mw = getattr(self.scene(), "_mw", None)
        if not mw or not getattr(mw, "show_grid", False):
            return

        px_per_m = float(getattr(mw, "px_per_meter", 10.0))
        grid_m = float(getattr(mw, "grid_spacing_m", 5.0))

        step_px = max(8.0, grid_m * px_per_m)  # avoid insane density
        left = math.floor(rect.left() / step_px) * step_px
        top = math.floor(rect.top() / step_px) * step_px

        # subtle grid color for dark theme
        minor_pen = QPen(QColor(60, 75, 110, 55), 1)
        major_pen = QPen(QColor(90, 110, 160, 85), 1)

        # Major every 5 lines
        major_every = 5

        x = left
        i = 0
        while x < rect.right():
            painter.setPen(major_pen if (i % major_every == 0) else minor_pen)
            painter.drawLine(QPointF(x, rect.top()), QPointF(x, rect.bottom()))
            x += step_px
            i += 1

        y = top
        j = 0
        while y < rect.bottom():
            painter.setPen(major_pen if (j % major_every == 0) else minor_pen)
            painter.drawLine(QPointF(rect.left(), y), QPointF(rect.right(), y))
            y += step_px
            j += 1

    def mousePressEvent(self, e):
        if self.draw_obstacles and e.button() == Qt.LeftButton:
            self._drag_start = self.mapToScene(e.pos())
            self._preview_rect = QGraphicsRectItem()
            self._preview_rect.setZValue(100)
            self._preview_rect.setBrush(QBrush(QColor(200, 200, 200, 25)))
            self._preview_rect.setPen(QPen(QColor("#8bd7ff"), 2, Qt.DashLine))
            self.scene().addItem(self._preview_rect)
            e.accept()
            return
        super().mousePressEvent(e)

    def mouseMoveEvent(self, e):
        # ── Obstacle draw preview ───────────────────────────────────────────────
        if self.draw_obstacles and self._drag_start and self._preview_rect:
            p = self.mapToScene(e.pos())
            r = QRectF(self._drag_start, self.mapToScene(e.pos())).normalized()
            self._preview_rect.setRect(r)
            e.accept()

            # ✅ Also update live cursor readout (heatmap legend)
            w = self.window()
            if w and hasattr(w, "_on_map_mouse_moved"):
                w._on_map_mouse_moved(p)
            return

        # ── Normal hover / cursor readout ───────────────────────────────────────
        p = self.mapToScene(e.pos())
        w = self.window()
        if w and hasattr(w, "_on_map_mouse_moved"):
            w._on_map_mouse_moved(p)

        super().mouseMoveEvent(e)

    def mouseReleaseEvent(self, e):
        if (
            self.draw_obstacles
            and e.button() == Qt.LeftButton
            and self._drag_start
            and self._preview_rect
        ):
            r = self._preview_rect.rect()
            self.scene().removeItem(self._preview_rect)
            self._preview_rect = None

            self._drag_start = None

            if r.width() < 10 or r.height() < 10:
                e.accept()
                return

            w = self.window()
            th = 1.0
            if w and hasattr(w, "sp_obs_thickness"):
                th = float(w.sp_obs_thickness.value())

            obs = ObstacleItem(r, self.draw_material, thickness=th)
            mw = self.window()
            if mw and hasattr(mw, "undo_stack") and not getattr(mw, "_loading_project", False):
                mw.undo_stack.push(_CmdAddObstacle(mw, obs))
            else:
                self.scene().addItem(obs)
            e.accept()
            return
        super().mouseReleaseEvent(e)


class HeatmapItem(QGraphicsPixmapItem):
    """
    Displays a low-res heatmap scaled to the scene size.
    """

    def __init__(self, scene_rect: QRectF):
        super().__init__()
        self.setZValue(1)  # behind links (2), obstacles (10), nodes (20)
        self.setOpacity(1.0)
        self.setVisible(False)

        self._scene_rect = scene_rect
        self._px_scale = 12  # heatmap resolution: bigger = faster, blockier

    def set_resolution(self, px_scale: int):
        self._px_scale = max(4, int(px_scale))

    def update_heatmap(self, img: QImage):
        """
        img is low-res (heatmap cells). We scale the pixmap itself to the scene size,
        so the overlay always covers the full scene rect with no letterboxing.
        """
        w = max(1, int(self._scene_rect.width()))
        h = max(1, int(self._scene_rect.height()))

        pm = QPixmap.fromImage(img).scaled(w, h, Qt.IgnoreAspectRatio, Qt.FastTransformation)

        self.setPixmap(pm)
        self.setPos(self._scene_rect.topLeft())
        self.setScale(1.0)  # ensure we aren't carrying any old item scale


class HeatLegendWidget(QWidget):
    """
    Vertical legend with a red->green gradient + range labels + live cursor value.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(140)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

        self._mode = "RSSI (dBm)"
        self._min_text = "-110"
        self._max_text = "-40"
        self._cursor_text = "—"

        outer = QHBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(8)

        # Gradient bar
        self.bar = QFrame()
        self.bar.setFixedWidth(16)
        self.bar.setFixedHeight(120)
        self.bar.setObjectName("HeatLegendBar")
        outer.addWidget(self.bar, 0)

        # Labels
        right = QVBoxLayout()
        right.setContentsMargins(0, 0, 0, 0)
        right.setSpacing(2)

        self.lbl_mode = QLabel("Mode: RSSI (dBm)")
        self.lbl_mode.setObjectName("Dim")

        self.lbl_max = QLabel("Max: -40")
        self.lbl_min = QLabel("Min: -110")

        self.lbl_cursor = QLabel("Cursor: —")
        self.lbl_cursor.setObjectName("Dim")

        # Let text wrap in the space remaining beside the gradient bar.
        for label in (self.lbl_mode, self.lbl_min, self.lbl_max, self.lbl_cursor):
            label.setWordWrap(True)
            label.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Preferred)
        right.addWidget(self.lbl_mode)
        right.addSpacing(4)
        right.addWidget(self.lbl_max)
        right.addWidget(self.lbl_min)
        right.addSpacing(8)
        right.addWidget(self.lbl_cursor)
        right.addStretch(1)

        outer.addLayout(right, 1)

        # paint gradient on the bar
        self.bar.paintEvent = self._paint_bar  # simple hook

    def _paint_bar(self, event):
        p = QPainter(self.bar)
        p.setRenderHint(QPainter.Antialiasing, False)

        r = self.bar.rect()
        grad = QLinearGradient(r.left(), r.top(), r.left(), r.bottom())

        # top = good (green), bottom = bad (red)
        grad.setColorAt(0.0, QColor(0, 200, 0))
        grad.setColorAt(1.0, QColor(220, 0, 0))

        p.fillRect(r, grad)
        p.setPen(QPen(QColor("#2a3550"), 1))
        p.drawRect(r.adjusted(0, 0, -1, -1))

    def set_mode_and_range(self, mode: str, vmin: float, vmax: float, unit: str):
        self._mode = mode
        self._min_text = f"{vmin:g}{unit}"
        self._max_text = f"{vmax:g}{unit}"

        self.lbl_mode.setText(f"Mode: {mode}")
        self.lbl_min.setText(f"Min: {self._min_text}")
        self.lbl_max.setText(f"Max: {self._max_text}")

    def set_cursor_value(self, value_text: str):
        self._cursor_text = value_text
        self.lbl_cursor.setText(f"Cursor: {value_text}")

    def clear_cursor(self):
        self.set_cursor_value("—")


class SuggestMarkerItem(QGraphicsEllipseItem):
    def __init__(self, p: QPointF):
        r = 10
        super().__init__(-r, -r, 2 * r, 2 * r)
        self.setPos(p)
        self.setZValue(15)  # above obstacles, below nodes
        self.setPen(QPen(QColor("#ffd34d"), 2))
        self.setBrush(QBrush(QColor(255, 211, 77, 60)))
        self.setToolTip("Suggested Router Location")


class HelpDialog(QMainWindow):
    def __init__(self, parent=None, title="Quick Start", html=""):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.resize(720, 620)

        root = QWidget()
        lay = QVBoxLayout(root)
        lay.setContentsMargins(12, 12, 12, 12)
        lay.setSpacing(10)

        label = QLabel()
        label.setTextFormat(Qt.RichText)
        label.setText(html)
        label.setWordWrap(True)
        label.setTextInteractionFlags(Qt.TextSelectableByMouse | Qt.LinksAccessibleByMouse)
        label.setOpenExternalLinks(True)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)

        inner = QWidget()
        inner_lay = QVBoxLayout(inner)
        inner_lay.setContentsMargins(6, 6, 6, 6)
        inner_lay.addWidget(label, 1)
        inner_lay.addStretch(1)

        scroll.setWidget(inner)

        btn = QPushButton("Close")
        btn.clicked.connect(self.close)

        lay.addWidget(scroll, 1)
        lay.addWidget(btn, 0, alignment=Qt.AlignRight)

        self.setCentralWidget(root)
