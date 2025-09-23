import sys
from pathlib import Path
from PySide6.QtWidgets import QApplication

from model import MainModel
from view import MainView
from controller import MainController
from style_manager import StyleManager

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(True)
    
    BASE_DIR = Path(__file__).resolve().parent
    UI_FILE = BASE_DIR / "GUI" / "ui" / "main.ui"
    PRESETS_FILE = BASE_DIR / "JSON" / "image_presets.json"
    # --- 修正: settings.json のパスを JSON フォルダ内に変更 ---
    SETTINGS_FILE = BASE_DIR / "JSON" / "settings.json"

    # スタイルを先に適用
    style_manager = StyleManager(app)
    style_manager.set_main_window_gray_theme()

    # MVCのセットアップ
    model = MainModel()
    view = MainView(UI_FILE)
    controller = MainController(model=model, view=view)

    # アプリケーションの初期化処理
    model.set_settings_file_path(SETTINGS_FILE)
    model.load_settings() # 保存された設定を読み込む
    
    model.find_and_set_render_path()
    model.load_presets_from_file(PRESETS_FILE)
    model.set_image_size_from_preset(model._current_preset)

    view.show()
    sys.exit(app.exec())

