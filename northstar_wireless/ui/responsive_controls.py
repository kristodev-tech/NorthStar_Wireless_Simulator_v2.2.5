"""Text controls whose minimum width does not depend on their entire caption."""

from PySide6.QtCore import QRect, QSize, Qt
from PySide6.QtGui import QPalette
from PySide6.QtWidgets import (
    QCheckBox,
    QPushButton,
    QSizePolicy,
    QStyle,
    QStyleOptionButton,
    QStylePainter,
)

FLAGS = Qt.AlignCenter | Qt.TextWordWrap


class WrappingButton(QPushButton):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        policy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        policy.setHeightForWidth(True)
        self.setSizePolicy(policy)

    def hasHeightForWidth(self):
        return True

    def _padding(self):
        hint = super().sizeHint()
        metrics = self.fontMetrics()
        return max(24, hint.width() - metrics.horizontalAdvance(self.text())), max(
            16, hint.height() - metrics.height()
        )

    def heightForWidth(self, width):
        horizontal, vertical = self._padding()
        rect = QRect(0, 0, max(1, width - horizontal), 10000)
        return self.fontMetrics().boundingRect(rect, FLAGS, self.text()).height() + vertical

    def minimumSizeHint(self):
        return QSize(80, self.fontMetrics().height() + self._padding()[1])

    def sizeHint(self):
        width = min(220, super().sizeHint().width())
        return QSize(width, self.heightForWidth(width))

    def paintEvent(self, event):
        option = QStyleOptionButton()
        self.initStyleOption(option)
        option.text = ""
        painter = QStylePainter(self)
        painter.drawControl(QStyle.CE_PushButton, option)
        rect = self.style().subElementRect(QStyle.SE_PushButtonContents, option, self)
        painter.setPen(option.palette.color(QPalette.ButtonText))
        painter.drawText(rect, FLAGS, self.text())


class WrappingCheckBox(QCheckBox):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        policy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        policy.setHeightForWidth(True)
        self.setSizePolicy(policy)

    def hasHeightForWidth(self):
        return True

    def _indicator_space(self):
        return self.style().pixelMetric(QStyle.PM_IndicatorWidth, None, self) + 10

    def heightForWidth(self, width):
        rect = QRect(0, 0, max(1, width - self._indicator_space()), 10000)
        text_height = (
            self.fontMetrics()
            .boundingRect(rect, Qt.AlignVCenter | Qt.TextWordWrap, self.text())
            .height()
        )
        return max(text_height, super().sizeHint().height()) + 4

    def minimumSizeHint(self):
        return QSize(80, super().sizeHint().height() + 4)

    def sizeHint(self):
        width = min(220, super().sizeHint().width())
        return QSize(width, self.heightForWidth(width))

    def hitButton(self, pos):
        return self.rect().contains(pos)

    def paintEvent(self, event):
        option = QStyleOptionButton()
        self.initStyleOption(option)
        option.text = ""
        painter = QStylePainter(self)
        painter.drawControl(QStyle.CE_CheckBox, option)
        rect = self.rect().adjusted(self._indicator_space(), 0, -2, 0)
        painter.setPen(option.palette.color(QPalette.WindowText))
        painter.drawText(rect, Qt.AlignVCenter | Qt.TextWordWrap, self.text())
