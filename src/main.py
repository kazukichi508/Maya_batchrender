import sys
from pathlib import Path
from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtCore import QCoreApplication, Qt # Qtをインポート

from model import MainModel
from view import MainView
from controller import MainController
from style_manager import StyleManager

if __name__ == "__main__":
    # 高DPIスケーリングを有効にする
    QCoreApplication.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling)

    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(True)
    
    main_window = QMainWindow()
    main_window.setWindowTitle("Maya Batch Render")

    # ▼▼▼ ファイルパスの指定方法を修正 ▼▼▼
    # src ディレクトリ自体を基準ディレクトリとして定義
    BASE_DIR = Path(__file__).resolve().parent
    
    UI_FILE = BASE_DIR / "GUI" / "ui" / "main.ui"
    PRESETS_FILE = BASE_DIR / "JSON" / "image_presets.json"
    SETTINGS_FILE = BASE_DIR / "JSON" / "settings.json"
    # ▲▲▲ ここまで修正 ▲▲▲

    # スタイルマネージャーの適用
    style_manager = StyleManager(app)
    style_manager.set_main_window_gray_theme()

    # MVCコンポーネントのインスタンス化
    model = MainModel()
    view = MainView(UI_FILE, parent=main_window)
    controller = MainController(model=model, view=view)

    # モデルの初期化
    model.set_settings_file_path(SETTINGS_FILE)
    model.find_and_set_render_path()
    model.load_presets_from_file(PRESETS_FILE)
    model.apply_default_settings()
    

    # メインウィンドウにビューをセット
    main_window.setCentralWidget(view)
    main_window.resize(view.ui.size())

    # 画面中央にウィンドウを移動
    screen = app.primaryScreen()
    screen_geometry = screen.availableGeometry()
    window_geometry = main_window.frameGeometry()
    center_point = screen_geometry.center()
    window_geometry.moveCenter(center_point)
    main_window.move(window_geometry.topLeft())

    main_window.show()

    sys.exit(app.exec())

