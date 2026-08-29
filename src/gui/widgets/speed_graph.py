"""
NightByte AI - Modern Minimalist Live Speed Graph
Smooth vector waveform curve with soft gradient fill that blends seamlessly into card surfaces.
"""

from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import (
    QPainter, QPen, QBrush, QColor, QLinearGradient, 
    QPainterPath, QFont
)


class LiveSpeedGraph(QWidget):
    """Custom high-performance vector speed graph widget."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(110)
        self.history = [0.0] * 60
        self.current_speed = 0.0
        self.peak_speed = 0.0
        
        # Color palette (Modern Blue Glow)
        self.line_color = QColor("#38bdf8")        # Sky 400
        self.fill_color_top = QColor(56, 189, 248, 60)
        self.fill_color_bot = QColor(56, 189, 248, 2)
        self.grid_color = QColor(255, 255, 255, 12)
        self.text_color = QColor(100, 116, 139)    # Slate 500

    def update_history(self, history: list[float], current: float, peak: float):
        self.history = history[-60:] if len(history) >= 60 else ([0.0] * (60 - len(history))) + history
        self.current_speed = current
        self.peak_speed = max(peak, max(self.history, default=0.0))
        self.update()

    def _format_speed(self, kb_s: float) -> str:
        if kb_s >= 1024.0:
            return f"{kb_s / 1024.0:.1f} MB/s"
        return f"{kb_s:.0f} KB/s"

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setRenderHint(QPainter.TextAntialiasing, True)

        w = self.width()
        h = self.height()
        padding_top = 18
        padding_bottom = 16
        padding_left = 8
        padding_right = 58

        plot_w = w - padding_left - padding_right
        plot_h = h - padding_top - padding_bottom

        # Transparent canvas background (blends into parent card)
        painter.fillRect(0, 0, w, h, QColor(0, 0, 0, 0))

        max_val = max(100.0, self.peak_speed * 1.15)

        # Draw clean grid lines
        grid_pen = QPen(self.grid_color, 1, Qt.DashLine)
        painter.setPen(grid_pen)
        painter.setFont(QFont("Segoe UI", 8))

        for ratio in [0.0, 0.5, 1.0]:
            y = padding_top + plot_h * (1.0 - ratio)
            painter.drawLine(int(padding_left), int(y), int(padding_left + plot_w), int(y))
            val_at_line = max_val * ratio
            painter.setPen(self.text_color)
            painter.drawText(int(padding_left + plot_w + 6), int(y + 4), self._format_speed(val_at_line))
            painter.setPen(grid_pen)

        if not self.history or plot_w <= 0 or plot_h <= 0:
            return

        points = []
        n_samples = len(self.history)
        dx = plot_w / max(1, n_samples - 1)

        for i, val in enumerate(self.history):
            x = padding_left + i * dx
            norm = min(1.0, max(0.0, val / max_val))
            y = padding_top + plot_h * (1.0 - norm)
            points.append(QPointF(x, y))

        # Bezier path
        path = QPainterPath()
        path.moveTo(points[0])
        for i in range(1, len(points)):
            p0 = points[i - 1]
            p1 = points[i]
            cx = (p0.x() + p1.x()) / 2.0
            path.cubicTo(cx, p0.y(), cx, p1.y(), p1.x(), p1.y())

        # Gradient fill
        fill_path = QPainterPath(path)
        fill_path.lineTo(padding_left + plot_w, padding_top + plot_h)
        fill_path.lineTo(padding_left, padding_top + plot_h)
        fill_path.closeSubpath()

        grad = QLinearGradient(0, padding_top, 0, padding_top + plot_h)
        grad.setColorAt(0.0, self.fill_color_top)
        grad.setColorAt(1.0, self.fill_color_bot)
        painter.fillPath(fill_path, QBrush(grad))

        # Top stroke
        curve_pen = QPen(self.line_color, 2.0, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
        painter.setPen(curve_pen)
        painter.drawPath(path)

        # Pulse dot on last point
        last_pt = points[-1]
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(56, 189, 248, 80))
        painter.drawEllipse(last_pt, 5, 5)
        painter.setBrush(QColor("#38bdf8"))
        painter.drawEllipse(last_pt, 2.5, 2.5)
