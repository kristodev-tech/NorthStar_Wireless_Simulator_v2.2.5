from PySide6.QtCore import QPointF

from PySide6.QtGui import QUndoCommand

from PySide6.QtWidgets import (
    QGraphicsItem,
)

from ..domain.models import ObstacleMaterial


class _CmdMoveItem(QUndoCommand):
    def __init__(self, item: QGraphicsItem, old_pos: QPointF, new_pos: QPointF, mw, text="Move"):
        super().__init__(text)
        self.item = item
        self.old = QPointF(old_pos)
        self.new = QPointF(new_pos)
        self.mw = mw

    def undo(self):
        self.item.setPos(self.old)
        self.mw._mark_heatmap_dirty()

    def redo(self):
        self.item.setPos(self.new)
        self.mw._mark_heatmap_dirty()


class _CmdAddNode(QUndoCommand):
    def __init__(self, mw, node):
        super().__init__("Add Node")
        self.mw = mw
        self.node = node
        self.added = False

    def redo(self):
        if hasattr(self, "node"):
            self.mw._used_numbers.setdefault(self.node.base_label, set()).add(self.node.type_number)
            self.mw.network_tech = self.node.profile.tech
            self.mw._refresh_profile_dropdown()
            self.mw._update_network_status_label()
        if not self.added:
            self.mw.scene.addItem(self.node)
            self.mw.nodes.append(self.node)
            self.added = True
        else:
            self.mw.scene.addItem(self.node)
            if self.node not in self.mw.nodes:
                self.mw.nodes.append(self.node)
        self.mw._rebuild_links()
        self.mw._refresh_heat_tx_list()
        if hasattr(self.mw, "_refresh_route_lists"):
            self.mw._refresh_route_lists()
        self.mw._mark_heatmap_dirty()

    def undo(self):
        if self.node in self.mw.nodes:
            self.mw.nodes.remove(self.node)
        self.mw.scene.removeItem(self.node)
        if not self.mw.nodes:
            self.mw.network_tech = None
            self.mw._refresh_profile_dropdown()
            self.mw._update_network_status_label()
        # free numbering
        try:
            self.mw._release_type_number(self.node.base_label, self.node.type_number)
        except Exception:
            pass
        self.mw._rebuild_links()
        self.mw._refresh_heat_tx_list()
        if hasattr(self.mw, "_refresh_route_lists"):
            self.mw._refresh_route_lists()
        self.mw._mark_heatmap_dirty()


class _CmdDeleteNode(QUndoCommand):
    def __init__(self, mw, node):
        super().__init__("Delete Node")
        self.mw = mw
        self.node = node
        self.was_in_scene = True

    def redo(self):
        if self.node in self.mw.nodes:
            self.mw.nodes.remove(self.node)
        try:
            self.mw._release_type_number(self.node.base_label, self.node.type_number)
        except Exception:
            pass
        self.mw.scene.removeItem(self.node)
        self.mw._rebuild_links()
        self.mw._refresh_heat_tx_list()
        if hasattr(self.mw, "_refresh_route_lists"):
            self.mw._refresh_route_lists()
        self.mw._mark_heatmap_dirty()

        # auto-unlock network if last node removed (keeps your existing behavior)
        if len(self.mw.nodes) == 0:
            self.mw.network_tech = None
            self.mw._refresh_profile_dropdown()
            self.mw._update_network_status_label()

    def undo(self):
        # re-allocate numbering
        used = self.mw._used_numbers.setdefault(self.node.base_label, set())
        used.add(int(self.node.type_number))

        self.mw.scene.addItem(self.node)
        if self.node not in self.mw.nodes:
            self.mw.nodes.append(self.node)

        # relock network tech if needed
        if self.mw.network_tech is None:
            self.mw.network_tech = self.node.profile.tech
            self.mw._refresh_profile_dropdown()
            self.mw._update_network_status_label()

        self.mw._rebuild_links()
        self.mw._refresh_heat_tx_list()
        if hasattr(self.mw, "_refresh_route_lists"):
            self.mw._refresh_route_lists()
        self.mw._mark_heatmap_dirty()


class _CmdAddObstacle(QUndoCommand):
    def __init__(self, mw, obs):
        super().__init__("Add Obstacle")
        self.mw = mw
        self.obs = obs
        self.added = False

    def redo(self):
        if not self.added:
            self.mw.scene.addItem(self.obs)
            self.added = True
        else:
            self.mw.scene.addItem(self.obs)
        self.mw._mark_heatmap_dirty()

    def undo(self):
        self.mw.scene.removeItem(self.obs)
        self.mw._mark_heatmap_dirty()


class _CmdDeleteObstacle(QUndoCommand):
    def __init__(self, mw, obs):
        super().__init__("Delete Obstacle")
        self.mw = mw
        self.obs = obs

    def redo(self):
        self.mw.scene.removeItem(self.obs)
        self.mw._mark_heatmap_dirty()

    def undo(self):
        self.mw.scene.addItem(self.obs)
        self.mw._mark_heatmap_dirty()


class _CmdChangeObstacleMaterial(QUndoCommand):
    def __init__(self, mw, obs, old_mat: ObstacleMaterial, new_mat: ObstacleMaterial):
        super().__init__("Change Obstacle Material")
        self.mw = mw
        self.obs = obs
        self.old = old_mat
        self.new = new_mat

    def _apply(self, mat: ObstacleMaterial):
        self.obs.material = mat
        self.obs._set_label_text()
        self.obs._apply_style()
        self.mw._mark_heatmap_dirty()

    def redo(self):
        self._apply(self.new)

    def undo(self):
        self._apply(self.old)


class _CmdChangeObstacleThickness(QUndoCommand):
    def __init__(self, mw, obs, old_th: float, new_th: float):
        super().__init__("Change Obstacle Thickness")
        self.mw = mw
        self.obs = obs
        self.old = float(old_th)
        self.new = float(new_th)

    def _apply(self, th: float):
        self.obs.thickness = float(max(0.1, th))
        self.obs._set_label_text()
        self.mw._mark_heatmap_dirty()

    def redo(self):
        self._apply(self.new)

    def undo(self):
        self._apply(self.old)


class ChangeLabelCommand(QUndoCommand):
    def __init__(self, window, node, base):
        super().__init__("Change device label")
        self.mw, self.node = window, node
        self.old = (node.base_label, node.type_number, node.name)
        used = window._used_numbers.get(base, set())
        number = node.type_number
        names = {n.name for n in window.nodes if n is not node}
        if number in used or f"{base}{number}" in names:
            number = 1
            while number in used or f"{base}{number}" in names:
                number += 1
        self.new = (base, number, node.name if node.custom_name else f"{base}{number}")

    def _apply(self, state):
        self.mw._release_type_number(self.node.base_label, self.node.type_number)
        self.node.base_label, self.node.type_number, self.node.name = state
        self.mw._used_numbers.setdefault(self.node.base_label, set()).add(self.node.type_number)
        self.node._refresh_label()
        self.mw._refresh_heat_tx_list()
        self.mw._refresh_route_lists()
        self.mw._mark_heatmap_dirty()
        self.mw._mark_route_dirty()
        self.mw._on_selection_changed()

    def redo(self):
        self._apply(self.new)

    def undo(self):
        self._apply(self.old)


class RenameNodeCommand(QUndoCommand):
    def __init__(self, window, node, name):
        super().__init__("Rename device")
        self.mw, self.node = window, node
        self.old = (node.name, node.custom_name)
        self.new = (name, True)

    def _apply(self, state):
        old_name = self.node.name
        selected = [
            cb
            for cb in (self.mw.cb_heat_tx, self.mw.cb_route_src, self.mw.cb_route_dst)
            if cb.currentText() == old_name
        ]
        self.node.name, self.node.custom_name = state
        self.node._refresh_label()
        self.mw._refresh_heat_tx_list()
        self.mw._refresh_route_lists()
        for cb in selected:
            cb.setCurrentText(self.node.name)
        self.mw._mark_heatmap_dirty()
        self.mw._mark_route_dirty()
        self.mw._on_selection_changed()

    def redo(self):
        self._apply(self.new)

    def undo(self):
        self._apply(self.old)
