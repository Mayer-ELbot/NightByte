"""
SteamDown Ultra AI - Live Vector Speed Graph
Real-time animated speed graph with antialiased bezier curve and glowing gradient fill.
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
        self.setMinimumHeight(130)
        self.history = [0.0] * 60
        self.current_speed = 0.0
        self.peak_speed = 0.0
        self.line_color = QColor("#06b6d4")     # Neon Cyan
        self.fill_color_top = QColor(6, 182, 212, 80)
        self.fill_color_bot = QColor(6, 182, 212, 5)
        self.grid_color = QColor(255, 255, 255, 18)
        self.text_color = QColor(148, 163, 184) # Slate 400

    def update_history(self, history: list[float], current: float, peak: float):
        """Update speed dataset and trigger repaint."""
        self.history = history[-60:] if len(history) >= 60 else ([0.0] * (60 - len(history))) + history
        self.current_speed = current
        self.peak_speed = max(peak, max(self.history, default=0.0))
        self.update()

    def _format_speed(self, kb_s: float) -> str:
        """Format speed in KB/s or MB/s."""
        if kb_s >= 1024.0:
            return f"{kb_s / 1024.0:.1f} MB/s"
        return f"{kb_s:.0f} KB/s"

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setRenderHint(QPainter.TextAntialiasing, True)

        w = self.width()
        h = self.height()
        padding_top = 22
        padding_bottom = 20
        padding_left = 12
        padding_right = 65
        
        plot_w = w - padding_left - padding_right
        plot_h = h - padding_top - padding_bottom

        # Background canvas
        bg_brush = QBrush(QColor("#111827")) # Deep dark
        painter.fillRect(0, 0, w, h, bg_brush)

        # Scale ceiling
        max_val = max(100.0, self.peak_speed * 1.15)

        # Draw Grid lines (3 horizontal lines: 0%, 50%, 100%)
        grid_pen = QPen(self.grid_color, 1, Qt.DashLine)
        painter.setPen(grid_pen)
        
        font = QFont("Segoe UI", 8)
        painter.setFont(font)

        for ratio in [0.0, 0.5, 1.0]:
            y = padding_top + plot_h * (1.0 - ratio)
            painter.drawLine(int(padding_left), int(y), int(padding_left + plot_w), int(y))
            
            # Label
            val_at_line = max_val * ratio
            painter.setPen(self.text_color)
            painter.drawText(int(padding_left + plot_w + 6), int(y + 4), self._format_speed(val_at_line))
            painter.setPen(grid_pen)

        if not self.history or plot_w <= 0 or plot_h <= 0:
            return

        # Build Curve Path
        points = []
        n_samples = len(self.history)
        dx = plot_w / max(1, n_samples - 1)

        for i, val in enumerate(self.history):
            x = padding_left + i * dx
            norm = min(1.0, max(0.0, val / max_val))
            y = padding_top + plot_h * (1.0 - norm)
            points.append(QPointF(x, y))

        # Create smooth spline / polyline path
        path = QPainterPath()
        path.moveTo(points[0])
        for pt in points[1:]:
            path.lineTo(pt)

        # Create fill polygon
        fill_path = QPainterPath(path)
        fill_path.lineTo(padding_left + plot_w, padding_top + plot_h)
        fill_path.lineTo(padding_left, padding_top + plot_h)
        fill_path.closeSubpath()

        # Fill with gradient
        grad = QLinearGradient(0, padding_top, 0, padding_top + plot_h)
        grad.setColorAt(0.0, self.fill_color_top)
        grad.setColorAt(1.0, self.fill_color_bot)
        painter.fillPath(fill_path, QBrush(grad))

        # Stroke the top curve line
        curve_pen = QPen(self.line_color, 2.2, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
        painter.setPen(curve_pen)
        painter.drawPath(path)

        # Draw glowing dot on current last point
        last_pt = points[-1]
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(6, 182, 212, 100))
        painter.drawEllipse(last_pt, 6, 6)
        painter.setBrush(QColor("#38bdf8"))
        painter.drawEllipse(last_pt, 3, 3)
