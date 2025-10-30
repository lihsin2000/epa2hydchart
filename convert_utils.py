import globals
import message
import traceback
from PyQt6.QtWidgets import QApplication, QMessageBox
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from main import MainWindow


def save_png(png_path, svg_path):
    """Convert SVG to PNG synchronously."""

    try:
        import cairosvg
        cairosvg.svg2png(
            url=svg_path,
            write_to=png_path,
            output_width=10000,
            dpi=600
        )
        return True
    except Exception as e:
        # print(f"PNG conversion error: {str(e)}")
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


def save_svg(msp, cad, path):
    """Convert DXF to SVG format."""
    try:
        svg_path = path

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

        with open(svg_path, "wt", encoding="utf8") as fp:
            fp.write(svg_string)
        return True
    except Exception as e:
        traceback.print_exc()
        globals.logger.exception(e)
        return False
