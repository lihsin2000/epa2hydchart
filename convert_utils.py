import traceback
from typing import TYPE_CHECKING

from PyQt6.QtWidgets import QApplication, QDialog, QMessageBox, QWidget

if TYPE_CHECKING:
    from main import MainWindow

import globals
import message


class _SvgCanvas(QWidget):
    """顯示 SVG，支援滾輪縮放（以滑鼠為中心）和拖曳平移。"""
    def __init__(self, svg_bytes, parent=None):
        super().__init__(parent)
        from PyQt6.QtSvg import QSvgRenderer
        from PyQt6.QtCore import QByteArray, Qt
        self._renderer = QSvgRenderer(QByteArray(svg_bytes))
        self._zoom = 1.0
        self._pan_x = 0.0
        self._pan_y = 0.0
        self._drag_start = None
        self._pan_start = (0.0, 0.0)
        self.setMinimumSize(200, 150)
        self.setCursor(Qt.CursorShape.OpenHandCursor)

    def _content_rect(self):
        """目前縮放下 SVG 的渲染矩形 (cx, cy, tw, th)。"""
        svg_size = self._renderer.defaultSize()
        w, h = float(self.width()), float(self.height())
        if svg_size.width() > 0 and svg_size.height() > 0:
            total = min(w / svg_size.width(), h / svg_size.height()) * self._zoom
            tw, th = svg_size.width() * total, svg_size.height() * total
            return (w - tw) / 2 + self._pan_x, (h - th) / 2 + self._pan_y, tw, th
        return 0.0, 0.0, w, h

    def paintEvent(self, _event):
        from PyQt6.QtGui import QPainter
        from PyQt6.QtCore import QRectF, Qt
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.fillRect(self.rect(), Qt.GlobalColor.white)
        cx, cy, tw, th = self._content_rect()
        self._renderer.render(painter, QRectF(cx, cy, tw, th))

    def wheelEvent(self, event):
        svg_size = self._renderer.defaultSize()
        if svg_size.width() == 0:
            return
        w, h = float(self.width()), float(self.height())
        base = min(w / svg_size.width(), h / svg_size.height())
        old_total = base * self._zoom
        old_tw = svg_size.width() * old_total
        old_th = svg_size.height() * old_total
        old_cx = (w - old_tw) / 2 + self._pan_x
        old_cy = (h - old_th) / 2 + self._pan_y
        # SVG 座標（縮放前滑鼠下方的點）
        mx, my = event.position().x(), event.position().y()
        svg_x = (mx - old_cx) / old_total
        svg_y = (my - old_cy) / old_total
        self._zoom *= 1.15 if event.angleDelta().y() > 0 else 1 / 1.15
        new_total = base * self._zoom
        new_tw = svg_size.width() * new_total
        new_th = svg_size.height() * new_total
        new_cx = (w - new_tw) / 2 + self._pan_x
        new_cy = (h - new_th) / 2 + self._pan_y
        # 讓滑鼠下方的 SVG 點保持不動
        self._pan_x += mx - (svg_x * new_total + new_cx)
        self._pan_y += my - (svg_y * new_total + new_cy)
        self.update()

    def mousePressEvent(self, event):
        from PyQt6.QtCore import Qt
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_start = event.position()
            self._pan_start = (self._pan_x, self._pan_y)
            self.setCursor(Qt.CursorShape.ClosedHandCursor)

    def mouseMoveEvent(self, event):
        from PyQt6.QtCore import Qt
        if event.buttons() & Qt.MouseButton.LeftButton and self._drag_start is not None:
            d = event.position() - self._drag_start
            self._pan_x = self._pan_start[0] + d.x()
            self._pan_y = self._pan_start[1] + d.y()
            self.update()

    def mouseReleaseEvent(self, event):
        from PyQt6.QtCore import Qt
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_start = None
            self.setCursor(Qt.CursorShape.OpenHandCursor)


class SvgPreviewDialog(QDialog):
    def __init__(self, svg_bytes, parent=None):
        super().__init__(parent)
        from preview_ui import Ui_Dialog_Preview
        from PyQt6.QtWidgets import QVBoxLayout

        self.ui = Ui_Dialog_Preview()
        self.ui.setupUi(self)
        self.setModal(True)

        canvas = _SvgCanvas(svg_bytes)
        inner = QVBoxLayout(self.ui.svgCanvas)
        inner.setContentsMargins(0, 0, 0, 0)
        inner.addWidget(canvas)

        self.ui.btn_back.clicked.connect(self.reject)
        self.ui.btn_continue.clicked.connect(self.accept)


def save_png(png_path, svg_path=None, bytestring=None):
    try:
        from PyQt6.QtSvg import QSvgRenderer
        from PyQt6.QtGui import QImage, QPainter, QColor
        from PyQt6.QtCore import Qt, QByteArray

        if bytestring is not None:
            svg_bytes = bytestring.encode('utf-8') if isinstance(bytestring, str) else bytestring
            renderer = QSvgRenderer(QByteArray(svg_bytes))
        elif svg_path is not None:
            svg_bytes = open(svg_path, 'rb').read()
            renderer = QSvgRenderer(svg_path)
        else:
            raise ValueError("必須提供 svg_path 或 bytestring")

        if not renderer.isValid():
            raise RuntimeError("無效的 SVG 資料")

        size = renderer.defaultSize()
        output_width = 10000
        output_height = round(output_width * size.height() / size.width()) if size.width() > 0 else output_width

        image = QImage(output_width, output_height, QImage.Format.Format_ARGB32)
        image.fill(QColor(Qt.GlobalColor.white))

        painter = QPainter(image)
        renderer.render(painter)
        painter.end()

        if not image.save(png_path):
            raise RuntimeError(f"QImage.save() 失敗：{png_path}")

        return True
    except Exception as e:
        traceback.print_exc()
        globals.logger.exception(e)
        return False


def save_dxf(dxf_path, main_window_instance):
    """Save DXF file with retry mechanism for file access errors."""

    while True:
        try:
            globals.cad.saveas(dxf_path)
            return True
        except:
            traceback.print_exc()
            globals.logger.exception(e)

            msg_box = QMessageBox(QApplication.activeWindow())
            msg_box.setIcon(QMessageBox.Icon.Critical)
            msg_box.setWindowTitle("錯誤")
            msg_box.setText(f'無法儲存 {dxf_path}，請關閉相關檔案後重試')
            retry_button = msg_box.addButton(
                "重試", msg_box.ButtonRole.ActionRole)
            cancel_button = msg_box.addButton(
                "取消", msg_box.ButtonRole.ActionRole)
            msg_box.exec()

            if msg_box.clickedButton() == retry_button:
                continue
            elif msg_box.clickedButton() == cancel_button:
                msg = f'[Error]無法儲存 {dxf_path}，中止匯出'
                message.renew_message(msg, True)
                return False


def save_svg(msp, cad, path=None):
    """Convert DXF to SVG. If path is None, generates in memory only."""
    try:
        from ezdxf.addons.drawing import Frontend, RenderContext, svg, layout, config
        msp = cad.modelspace()
        context = RenderContext(cad)
        backend = svg.SVGBackend()
        cfg = config.Configuration(
            background_policy=config.BackgroundPolicy.WHITE,
        )
        frontend = Frontend(context, backend, config=cfg)
        frontend.draw_layout(msp)
        page = layout.Page(0, 0, layout.Units.mm,
                           margins=layout.Margins.all(10))
        svg_string = backend.get_string(
            page, settings=layout.Settings(scale=1, fit_page=False)
        )

        if path is not None:
            with open(path, "wt", encoding="utf8") as fp:
                fp.write(svg_string)
        return True, svg_string
    except Exception as e:
        traceback.print_exc()
        globals.logger.exception(e)
        return False, None
