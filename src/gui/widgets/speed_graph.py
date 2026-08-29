"""
NightByte AI — Speed Graph Widget
Clean white line on dark background.  Zero colour noise.
"""

from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import QPainter, QPen, QColor, QPainterPath, QLinearGradient, QFont


class SpeedGraph(QWidget):
    """Minimal waveform: white bezier curve with very subtle dark-grey fill."""

    MAX_POINTS = 80
    LINE_COLOR = QColor("#ffffff")
    FILL_TOP   = QColor(40, 40, 40, 180)
    FILL_BOT   = QColor(20, 20, 20, 0)
    AXIS_COLOR = QColor("#444444")
    LABEL_COLOR= QColor("#444444")

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(110)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self._points: list[float] = []
        self._max_val: float = 1.0

    # ── public API ───────────────────────────────────────────────
    def add_point(self, value: float):
        self._points.append(max(0.0, value))
        if len(self._points) > self.MAX_POINTS:
            self._points.pop(0)
        self._max_val = max(max(self._points) * 1.15, 1.0)
        self.update()

    def clear(self):
        self._points.clear()
        self._max_val = 1.0
        self.update()

    # ── painting ─────────────────────────────────────────────────
    def paintEvent(self, _):
        if len(self._points) < 2:
            return

        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)

        W, H = self.width(), self.height()
        PAD_R, PAD_B = 58, 8
        PAD_T, PAD_L = 8, 0
        gw = W - PAD_L - PAD_R
        gh = H - PAD_T - PAD_B

        def pt(i: int) -> QPointF:
            n = len(self._points)
            x = PAD_L + i * gw / (n - 1)
            y = PAD_T + gh - (self._points[i] / self._max_val) * gh
            return QPointF(x, y)

        # build smooth bezier path
        path = QPainterPath()
        path.moveTo(pt(0))
        for i in range(1, len(self._points)):
            c1 = QPointF((pt(i - 1).x() + pt(i).x()) / 2, pt(i - 1).y())
            c2 = QPointF((pt(i - 1).x() + pt(i).x()) / 2, pt(i).y())
            path.cubicTo(c1, c2, pt(i))

        # fill under curve
        fill = QPainterPath(path)
        fill.lineTo(pt(len(self._points) - 1).x(), PAD_T + gh)
        fill.lineTo(PAD_L, PAD_T + gh)
        fill.closeSubpath()

        grad = QLinearGradient(0, PAD_T, 0, PAD_T + gh)
        grad.setColorAt(0, self.FILL_TOP)
        grad.setColorAt(1, self.FILL_BOT)
        p.fillPath(fill, grad)

        # line
        pen = QPen(self.LINE_COLOR, 1.5, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
        p.setPen(pen)
        p.drawPath(path)

        # glow dot at last point
        last = pt(len(self._points) - 1)
        p.setPen(Qt.NoPen)
        p.setBrush(QColor("#ffffff"))
        p.drawEllipse(last, 3.5, 3.5)

        # axis labels (right side)
        font = QFont("Segoe UI", 9)
        font.setWeight(QFont.DemiBold)
        p.setFont(font)
        p.setPen(self.LABEL_COLOR)

        def fmt(v: float) -> str:
            if v >= 1024:
                return f"{v/1024:.1f} MB/s"
            return f"{v:.0f} KB/s"

        for frac, val in [(0.0, self._max_val), (0.5, self._max_val * 0.5), (1.0, 0.0)]:
            y = PAD_T + frac * gh
            p.drawText(int(W - PAD_R + 4), int(y + 4), fmt(val if frac < 1 else 0))

        p.end()
