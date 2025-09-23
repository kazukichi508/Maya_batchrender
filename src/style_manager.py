# src/style_manager.py

from PySide6.QtWidgets import QApplication

class StyleManager:
    """
    アプリケーションのスタイルシートを管理するクラス。
    """
    def __init__(self, app: QApplication):
        self._app = app
        self._current_theme = "default" # 現在のテーマを保持

    def set_main_window_gray_theme(self):
        """
        メインウィンドウとダイアログの背景色をグレーにするスタイルシートを適用する。
        """
        # ▼▼▼ QDialog をセレクタに追加 ▼▼▼
        stylesheet = """
        QMainWindow, QDialog {
            background-color: #3C3C3C; /* 濃いグレー */
            color: #F0F0F0;            /* 文字色を明るく */
        }
        QWidget {
            background-color: #4D4D4D; /* QMainWindow内のウィジェットの背景色 */
            color: #F0F0F0;
        }
        QLabel {
            background-color: transparent; /* ラベルの背景は透明に */
        }
        QLineEdit, QTextEdit, QListView, QSpinBox, QComboBox {
            background-color: #333333; /* 入力欄などの背景色 */
            color: #F0F0F0;
            border: 1px solid #5A5A5A;
        }
        QPushButton {
            background-color: #555555;
            color: #F0F0F0;
            border: 1px solid #666666;
            padding: 5px;
            border-radius: 3px;
        }
        QPushButton:hover {
            background-color: #6A6A6A;
        }
        QPushButton:pressed {
            background-color: #2E2E2E;
        }
        QListView::item:selected {
            background-color: #0078D7; /* 選択項目の背景色 */
            color: #FFFFFF;
        }
        QCheckBox {
            color: #F0F0F0;
        }
        """
        # ▲▲▲ スタイルシートの定義 ▲▲▲
        self._app.setStyleSheet(stylesheet)
        self._current_theme = "gray"
        print("グレーテーマを適用しました。")

    def reset_default_theme(self):
        """
        スタイルシートをリセットし、デフォルトのテーマに戻す。
        """
        self._app.setStyleSheet("") # 空文字列でスタイルシートをクリア
        self._current_theme = "default"
        print("デフォルトテーマに戻しました。")

    def get_current_theme(self):
        """現在のテーマ名を返す"""
        return self._current_theme