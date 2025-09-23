from pathlib import Path
from PySide6.QtCore import QIODevice, QFile, Qt
from PySide6.QtGui import QCloseEvent, QIntValidator
from PySide6.QtWidgets import (
    QApplication, QCheckBox, QComboBox, QDialog, QFileDialog, QLineEdit,
    QListWidget, QMainWindow, QPushButton, QTextEdit
)
from PySide6.QtUiTools import QUiLoader


class MainView(QMainWindow):
    """
    メインウィンドウのUIとロジックを管理するクラス。
    """
    def __init__(self, ui_file: Path):
        super().__init__()
        
        loader = QUiLoader()
        file = QFile(ui_file)
        if not file.open(QIODevice.OpenModeFlag.ReadOnly):
            raise IOError(f"Cannot open ui file: {ui_file}")
        
        self.window = loader.load(file, self)
        file.close()

        self.setWindowTitle("Maya Batch Render")
        
        self._setup_ui_elements()
        
        # AOVダイアログをインスタンス化
        self.aov_dialog = AovDialog(self.window)

    def _setup_ui_elements(self):
        """UIファイル内のウィジェットへの参照を初期化する"""
        self.render_path_edit: QLineEdit = self.window.findChild(QLineEdit, "Render_path_lineEdit")
        self.project_path_edit: QLineEdit = self.window.findChild(QLineEdit, "project_lineEdit")
        self.project_path_button: QPushButton = self.window.findChild(QPushButton, "project_pushButton")
        
        self.reload_button: QPushButton = self.window.findChild(QPushButton, "reload_pushButton")
        self.file_list_widget: QListWidget = self.window.findChild(QListWidget, "listWidget")
        
        self.log_text_edit: QTextEdit = self.window.findChild(QTextEdit, "log_textEdit")
        self.error_text_edit: QTextEdit = self.window.findChild(QTextEdit, "error_textEdit")

        # --- 画像設定関連 ---
        self.preset_combo: QComboBox = self.window.findChild(QComboBox, "imagepreset_comboBox_2")
        self.width_edit: QLineEdit = self.window.findChild(QLineEdit, "width_lineEdit")
        self.height_edit: QLineEdit = self.window.findChild(QLineEdit, "height_lineEdit")
        self.format_combo: QComboBox = self.window.findChild(QComboBox, "imageformat_comboBox_2")

        # --- レンダリング設定関連 ---
        self.engine_combo: QComboBox = self.window.findChild(QComboBox, "renderring_engin_comboBox")
        
        # --- AOV関連 ---
        self.aov_button: QPushButton = self.window.findChild(QPushButton, "AOV_pushButton")

        # 数値入力バリデーターの設定
        if self.width_edit:
            self.width_edit.setValidator(QIntValidator(0, 16384))
        if self.height_edit:
            self.height_edit.setValidator(QIntValidator(0, 16384))

    def closeEvent(self, event: QCloseEvent):
        """ウィンドウが閉じられたときにアプリケーションを確実に終了させる"""
        QApplication.instance().quit()
        event.accept()

    # --- Controllerから呼び出されるスロット群 ---
    def set_render_path(self, path: str):
        if self.render_path_edit:
            self.render_path_edit.setText(path)

    def set_project_path(self, path: str):
        if self.project_path_edit:
            self.project_path_edit.setText(path)

    def update_render_file_list(self, files: list[str]):
        if self.file_list_widget:
            self.file_list_widget.clear()
            self.file_list_widget.addItems(files)

    def populate_presets(self, preset_names: list[str]):
        if self.preset_combo:
            self.preset_combo.blockSignals(True)
            self.preset_combo.clear()
            self.preset_combo.addItems(preset_names)
            self.preset_combo.blockSignals(False)

    def populate_formats(self, format_names: list[str]):
        if self.format_combo:
            self.format_combo.blockSignals(True)
            self.format_combo.clear()
            self.format_combo.addItems(format_names)
            self.format_combo.blockSignals(False)

    def populate_engines(self, engine_names: list[str]):
        if self.engine_combo:
            self.engine_combo.blockSignals(True)
            self.engine_combo.clear()
            self.engine_combo.addItems([e.upper() for e in engine_names])
            self.engine_combo.blockSignals(False)

    def update_preset_selection(self, preset_name: str):
        """指定されたプリセット名にコンボボックスの選択を更新する"""
        if self.preset_combo:
            self.preset_combo.blockSignals(True)
            # "Custom"がリストにない場合は一時的に追加
            if preset_name == "Custom" and self.preset_combo.findText(preset_name) == -1:
                self.preset_combo.addItem(preset_name)
            
            index = self.preset_combo.findText(preset_name)
            if index != -1 and self.preset_combo.currentIndex() != index:
                self.preset_combo.setCurrentIndex(index)
            self.preset_combo.blockSignals(False)

    def update_format_selection(self, format_name: str):
        """指定されたフォーマット名にコンボボックスの選択を更新する"""
        if self.format_combo:
            self.format_combo.blockSignals(True)
            index = self.format_combo.findText(format_name, Qt.MatchFlag.MatchFixedString | Qt.MatchFlag.MatchCaseInsensitive)
            if index != -1 and self.format_combo.currentIndex() != index:
                self.format_combo.setCurrentIndex(index)
            self.format_combo.blockSignals(False)
            
    def update_engine_selection(self, engine_name: str):
        """指定されたエンジン名にコンボボックスの選択を更新する"""
        if self.engine_combo:
            self.engine_combo.blockSignals(True)
            # 大文字小文字を区別しない検索
            index = self.engine_combo.findText(engine_name, Qt.MatchFlag.MatchFixedString | Qt.MatchFlag.MatchCaseInsensitive)
            if index != -1 and self.engine_combo.currentIndex() != index:
                self.engine_combo.setCurrentIndex(index)
            self.engine_combo.blockSignals(False)

    def update_image_size(self, width: int, height: int):
        if self.width_edit and self.width_edit.text() != str(width):
            self.width_edit.setText(str(width))
        if self.height_edit and self.height_edit.text() != str(height):
            self.height_edit.setText(str(height))

    def append_log(self, message: str):
        if self.log_text_edit:
            self.log_text_edit.append(message)

    def append_error(self, message: str):
        if self.error_text_edit:
            self.error_text_edit.append(message)

    def show(self):
        self.window.show()


class AovDialog(QDialog):
    """
    AOV設定ダイアログ(Aov.ui)のUIを管理するクラス。
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        
        script_dir = Path(__file__).resolve().parent
        ui_path = script_dir / "GUI" / "ui" / "Aov.ui"
        
        loader = QUiLoader()
        file = QFile(ui_path)
        
        self.export_button = None

        if not file.open(QIODevice.OpenModeFlag.ReadOnly):
            print(f"Warning: Cannot open ui file: {ui_path}")
            self.ui = QDialog(self)
        else:
            self.ui = loader.load(file, self)
            file.close()
        
        self.setWindowTitle("AOV設定")
        if self.ui and self.ui.layout():
            self.setLayout(self.ui.layout())
        
        # UI内のボタンへの参照を取得
        if self.ui:
            self.export_button = self.ui.findChild(QPushButton, "json_export_pushButton")

