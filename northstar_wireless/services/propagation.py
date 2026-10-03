from PySide6.QtCore import QPointF, QRectF
from ..domain.link_budget import calculate_link
import math
import random


def dist(a, b):
    return math.hypot(a.x() - b.x(), a.y() - b.y())


def clamp(value, low, high):
    return min(high, max(low, value))


class PropagationEngine:
    def __init__(self):
        self.extra_loss_db = 0.0
        self.live_fading = True
        self.rng = random.Random(2026)

    def _calculate(self, a, b, receiver, obstacles, m_per_px, live):
        distance = max(0.5, dist(a.scene_center(), b) * m_per_px)
        loss = self._obstacle_loss(a.scene_center(), b, obstacles)
        noise = self.rng.gauss(0, a.profile.noise_sigma_db) if live and self.live_fading else 0.0
        return calculate_link(a.profile, receiver, distance, loss, self.extra_loss_db, noise)

    def compute_link(self, a, b, obstacles, m_per_px=0.1):
        return self._calculate(a, b.scene_center(), b.profile, obstacles, m_per_px, True)

    def compute_link_det(self, a, b, obstacles, m_per_px=0.1):
        return self._calculate(a, b.scene_center(), b.profile, obstacles, m_per_px, False)

    def compute_to_point(self, tx_node, p_scene, obstacles, m_per_px=0.1):
        return self._calculate(tx_node, p_scene, tx_node.profile, obstacles, m_per_px, False)

    def _obstacle_loss(self, a: QPointF, b: QPointF, obstacles: list) -> float:
        """
        Improved obstacle loss:
        loss += base_atten * thickness * partial_weight

        partial_weight is based on how much of the segment passes through the rect:
        - corner graze -> small inside length -> small weight
        - full pass through -> larger inside length -> weight approaches 1
        """
        loss = 0.0

        for obs in obstacles:
            rect = obs.mapRectToScene(obs.rect())

            inside_len = self._segment_rect_inside_length(a, b, rect)
            if inside_len <= 0.0:
                continue

            # Normalize by a characteristic obstacle size so weights feel intuitive.
            # Using the smaller dimension makes "thin walls" behave like walls.
            char = max(1e-6, min(rect.width(), rect.height()))

            # Weight: 0..1 (corner clip small, full crossing near 1)
            w = clamp(inside_len / char, 0.0, 1.0)

            base = float(obs.material.attenuation_db)
            thick = float(getattr(obs, "thickness", 1.0))

            loss += base * thick * w

        return loss

    def _segment_rect_inside_length(self, p1: QPointF, p2: QPointF, r: QRectF) -> float:
        """
        Returns the length of the segment p1->p2 that lies inside rect r.
        If it doesn't intersect, returns 0.
        """
        x1, y1 = p1.x(), p1.y()
        x2, y2 = p2.x(), p2.y()
        dx = x2 - x1
        dy = y2 - y1

        t0, t1 = 0.0, 1.0

        def clip(p, q, t0, t1):
            if abs(p) < 1e-12:
                if q < 0:
                    return None
                return (t0, t1)
            t = q / p
            if p < 0:
                if t > t1:
                    return None
                if t > t0:
                    t0 = t
            else:
                if t < t0:
                    return None
                if t < t1:
                    t1 = t
            return (t0, t1)

        left, right, top, bottom = r.left(), r.right(), r.top(), r.bottom()

        res = clip(-dx, x1 - left, t0, t1)
        if res is None:
            return 0.0
        t0, t1 = res

        res = clip(dx, right - x1, t0, t1)
        if res is None:
            return 0.0
        t0, t1 = res

        res = clip(-dy, y1 - top, t0, t1)
        if res is None:
            return 0.0
        t0, t1 = res

        res = clip(dy, bottom - y1, t0, t1)
        if res is None:
            return 0.0
        t0, t1 = res

        if t1 <= t0:
            return 0.0

        # Length inside is (t1 - t0) * total length
        seg_len = math.hypot(dx, dy)
        return (t1 - t0) * seg_len

    def _segment_intersects_rect(self, p1: QPointF, p2: QPointF, r: QRectF) -> bool:
        # If either endpoint inside, count as intersect
        if r.contains(p1) or r.contains(p2):
            return True

        # Check intersection against each rect edge
        edges = [
            (QPointF(r.left(), r.top()), QPointF(r.right(), r.top())),
            (QPointF(r.right(), r.top()), QPointF(r.right(), r.bottom())),
            (QPointF(r.right(), r.bottom()), QPointF(r.left(), r.bottom())),
            (QPointF(r.left(), r.bottom()), QPointF(r.left(), r.top())),
        ]
        for e1, e2 in edges:
            if self._segments_intersect(p1, p2, e1, e2):
                return True
        return False

    def _segments_intersect(self, a1: QPointF, a2: QPointF, b1: QPointF, b2: QPointF) -> bool:
        def ccw(pA, pB, pC):
            return (pC.y() - pA.y()) * (pB.x() - pA.x()) > (pB.y() - pA.y()) * (pC.x() - pA.x())

        return (ccw(a1, b1, b2) != ccw(a2, b1, b2)) and (ccw(a1, a2, b1) != ccw(a1, a2, b2))
