import globals, log, traceback
from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtWidgets import QApplication, QMessageBox
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from main import MainWindow

class PngConverterThread(QThread):
    """Worker thread for PNG conversion to prevent UI freezing"""
    finished = pyqtSignal(bool, str)  # success, error_message
    
    def __init__(self, svg_path, png_path):
        super().__init__()
        self.svg_path = svg_path
        self.png_path = png_path
    
    def run(self):
        try:
            import cairosvg
            cairosvg.svg2png(
                url=self.svg_path,
                write_to=self.png_path,
                output_width=10000,
                dpi=600
            )
            self.finished.emit(True, "")
        except Exception as e:
            self.finished.emit(False, str(e))

def save_png(*args, **kwargs):
    """
    Convert SVG to PNG using a separate thread to prevent UI freezing
    """
    png_path = kwargs.get('pngPath')
    svg_path = kwargs.get('svgPath')
    callback = kwargs.get('callback')  # Optional callback for when conversion completes
    
    # Create and start the converter thread
    png_thread = PngConverterThread(svg_path, png_path)
    
    def on_conversion_finished(success, error_msg):
        if success:
            if callback:
                callback(True)
        else:
            traceback.print_exc()
            print(f"PNG conversion error: {error_msg}")
            if callback:
                callback(False)
    
    png_thread.finished.connect(on_conversion_finished)
    png_thread.start()
    
    # Store reference to prevent garbage collection
    if not hasattr(globals, '_png_threads'):
        globals._png_threads = []
    globals._png_threads.append(png_thread)
    
    # Note: This now returns immediately, actual result is async
    return True

def save_dxf(*args, **kwargs):
    """
    Save DXF file with retry mechanism for file access errors
    """
    dxf_path = kwargs.get('dxfPath')
    main_window_instance = kwargs.get('main_window_instance')
    
    while True:
        try:
            globals.cad.saveas(dxf_path)
            return True
        except:
            traceback.print_exc()
            
            msg_box = QMessageBox(QApplication.activeWindow())
            msg_box.setIcon(QMessageBox.Icon.Critical)
            msg_box.setWindowTitle("錯誤")
            msg_box.setText(f'無法儲存 {dxf_path}，請關閉相關檔案後重試')
            retry_button = msg_box.addButton("重試", msg_box.ButtonRole.ActionRole)
            cancel_button = msg_box.addButton("取消", msg_box.ButtonRole.ActionRole)
            msg_box.exec()
            
            if msg_box.clickedButton() == retry_button:
                continue
            elif msg_box.clickedButton() == cancel_button:
                msg = f'[Error]無法儲存 {dxf_path}，中止匯出'
                log.renew_log(msg, True)
                return False

def save_svg(*args, **kwargs):
    """
    Convert DXF to SVG format
    """
    try:
        msp = kwargs.get('msp')
        cad = kwargs.get('cad')
        svg_path = kwargs.get('path')
        
        from ezdxf.addons.drawing import Frontend, RenderContext, svg, layout, config
        msp = cad.modelspace()
        context = RenderContext(cad)
        backend = svg.SVGBackend()
        cfg = config.Configuration(
            background_policy=config.BackgroundPolicy.WHITE,
        )
        frontend = Frontend(context, backend, config=cfg)
        frontend.draw_layout(msp)
        page = layout.Page(0, 0, layout.Units.mm, margins=layout.Margins.all(10))
        svg_string = backend.get_string(
            page, settings=layout.Settings(scale=1, fit_page=False)
        )

        with open(svg_path, "wt", encoding="utf8") as fp:
            fp.write(svg_string)
        return True
    except Exception as e:
        traceback.print_exc()
        return False
