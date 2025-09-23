# Filename: view.py
from pathlib import Path
from PySide6.QtCore import QIODevice, QFile, Qt
from PySide6.QtGui import QCloseEvent, QIntValidator
from PySide6.QtWidgets import (
    QApplication, QCheckBox, QComboBox, QDialog, QFileDialog, QLineEdit,
    QListWidget, QPushButton, QTextEdit, QVBoxLayout, QWidget, QSpinBox
)
from PySide6.QtUiTools import QUiLoader


class MainView(QWidget):
    """
    メインUIのコンテンツを管理するクラス。QWidgetを継承する。
    """
    def __init__(self, ui_file: Path, parent=None):
        super().__init__(parent)
        
        loader = QUiLoader()
        file = QFile(ui_file)
        if not file.open(QIODevice.OpenModeFlag.ReadOnly):
            raise IOError(f"Cannot open ui file: {ui_file}")
        
        ui_widget = loader.load(file, None)
        file.close()

        if ui_widget is None:
             raise RuntimeError(f"Failed to load UI from file: {ui_file}. Check the file content.")
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(ui_widget)
        
        self.ui = ui_widget

        self._setup_ui_elements()
        self.aov_dialog = AovDialog(parent=self)

    def _setup_ui_elements(self):
        """UIファイル内のウィジェットへの参照を初期化する"""
        self.render_path_edit: QLineEdit = self.ui.findChild(QLineEdit, "Render_path_lineEdit")
        self.project_path_edit: QLineEdit = self.ui.findChild(QLineEdit, "project_lineEdit")
        self.project_path_button: QPushButton = self.ui.findChild(QPushButton, "project_pushButton")
        
        self.reload_button: QPushButton = self.ui.findChild(QPushButton, "reload_pushButton")
        self.file_list_widget: QListWidget = self.ui.findChild(QListWidget, "listWidget")
        self.json_list_widget: QListWidget = self.ui.findChild(QListWidget, "listWidget_2")
        
        self.log_text_edit: QTextEdit = self.ui.findChild(QTextEdit, "log_textEdit")
        self.error_text_edit: QTextEdit = self.ui.findChild(QTextEdit, "error_textEdit")

        self.preset_combo: QComboBox = self.ui.findChild(QComboBox, "imagepreset_comboBox_2")
        self.width_edit: QLineEdit = self.ui.findChild(QLineEdit, "width_lineEdit")
        self.height_edit: QLineEdit = self.ui.findChild(QLineEdit, "height_lineEdit")
        self.format_combo: QComboBox = self.ui.findChild(QComboBox, "imageformat_comboBox_2")

        self.engine_combo: QComboBox = self.ui.findChild(QComboBox, "renderring_engin_comboBox")
        self.aov_button: QPushButton = self.ui.findChild(QPushButton, "AOV_pushButton")

        self.file_name_edit: QLineEdit = self.ui.findChild(QLineEdit, "file_name_lineEdit_2")
        self.start_frame_spin: QSpinBox = self.ui.findChild(QSpinBox, "imagestart_spinBox_2")
        self.end_frame_spin: QSpinBox = self.ui.findChild(QSpinBox, "imagelast_spinBox_2")
        
        self.cam_aa_spin: QSpinBox = self.ui.findChild(QSpinBox, "cam_AA_spinBox")
        self.diffuse_spin: QSpinBox = self.ui.findChild(QSpinBox, "diffuse_spinBox")
        self.specular_spin: QSpinBox = self.ui.findChild(QSpinBox, "specular_spinBox")
        self.transmission_spin: QSpinBox = self.ui.findChild(QSpinBox, "transmission_spinBox")
        self.sss_spin: QSpinBox = self.ui.findChild(QSpinBox, "SSS_spinBox")
        self.volume_indirect_spin: QSpinBox = self.ui.findChild(QSpinBox, "volume_indirect_spinBox")
        
        self.motion_blur_check: QCheckBox = self.ui.findChild(QCheckBox, "motionblur_checkBox")
        self.ray_tracing_check: QCheckBox = self.ui.findChild(QCheckBox, "ray_checkBox")
        self.reflection_spin: QSpinBox = self.ui.findChild(QSpinBox, "refection_spinBox")
        self.refraction_spin: QSpinBox = self.ui.findChild(QSpinBox, "refraction_spinBox")
        
        self.render_start_button: QPushButton = self.ui.findChild(QPushButton, "render_strat_pushButton")
        
        self.camera_edit: QLineEdit = self.ui.findChild(QLineEdit, "camera_lineEdit")
        self.aov_check: QCheckBox = self.ui.findChild(QCheckBox, "aov_checkBox")
        
        if self.width_edit: self.width_edit.setValidator(QIntValidator(0, 16384))
        if self.height_edit: self.height_edit.setValidator(QIntValidator(0, 16384))
    
    # ▼▼▼ デフォルトサンプリング値をUIに設定するメソッドを追加 ▼▼▼
    def update_sampling_spinboxes(self, defaults: dict):
        """デフォルトのサンプリング値をスピンボックスに設定する"""
        if self.cam_aa_spin:
            self.cam_aa_spin.setValue(defaults.get("cam_aa", 0))
        if self.diffuse_spin:
            self.diffuse_spin.setValue(defaults.get("diffuse", 0))
        if self.specular_spin:
            self.specular_spin.setValue(defaults.get("specular", 0))
        if self.transmission_spin:
            self.transmission_spin.setValue(defaults.get("transmission", 0))
        if self.sss_spin:
            self.sss_spin.setValue(defaults.get("sss", 0))
        if self.volume_indirect_spin:
            self.volume_indirect_spin.setValue(defaults.get("volume_indirect", 0))

    def get_current_render_settings(self) -> dict:
        """UIから現在のレンダリング設定を収集して辞書で返す"""
        settings = {
            "file_name": self.file_name_edit.text() if self.file_name_edit else "",
            "format": self.format_combo.currentText() if self.format_combo else "exr",
            "width": int(self.width_edit.text()) if self.width_edit and self.width_edit.text().isdigit() else 1280,
            "height": int(self.height_edit.text()) if self.height_edit and self.height_edit.text().isdigit() else 720,
            "start_frame": self.start_frame_spin.value() if self.start_frame_spin else 1,
            "end_frame": self.end_frame_spin.value() if self.end_frame_spin else 1,
            "engine": self.engine_combo.currentText().lower() if self.engine_combo else "cpu",
            "cam_aa": self.cam_aa_spin.value() if self.cam_aa_spin else 3,
            "diffuse": self.diffuse_spin.value() if self.diffuse_spin else 2,
            "specular": self.specular_spin.value() if self.specular_spin else 2,
            "transmission": self.transmission_spin.value() if self.transmission_spin else 2,
            "sss": self.sss_spin.value() if self.sss_spin else 2,
            "volume_indirect": self.volume_indirect_spin.value() if self.volume_indirect_spin else 2,
            "motion_blur": self.motion_blur_check.isChecked() if self.motion_blur_check else False,
            "ray_tracing": self.ray_tracing_check.isChecked() if self.ray_tracing_check else False,
            "reflection": self.reflection_spin.value() if self.reflection_spin else 8,
            "refraction": self.refraction_spin.value() if self.refraction_spin else 8,
            "camera": self.camera_edit.text() if self.camera_edit else "perspShape",
            "aov_enabled": self.aov_check.isChecked() if self.aov_check else False,
        }
        return settings

    def get_selected_scene(self) -> str | None:
        if self.file_list_widget and self.file_list_widget.currentItem():
            return self.file_list_widget.currentItem().text()
        return None

    def update_aov_json_list(self, files: list[str]):
        if self.json_list_widget:
            self.json_list_widget.clear()
            self.json_list_widget.addItems(files)

    def set_render_path(self, path: str):
        if self.render_path_edit: self.render_path_edit.setText(path)

    def set_project_path(self, path: str):
        if self.project_path_edit: self.project_path_edit.setText(path)

    def update_render_file_list(self, files: list[str]):
        if self.file_list_widget:
            self.file_list_widget.clear()
            self.file_list_widget.addItems(files)
            if files: self.file_list_widget.setCurrentRow(0)

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
        if self.preset_combo:
            self.preset_combo.blockSignals(True)
            if preset_name == "Custom" and self.preset_combo.findText(preset_name) == -1:
                self.preset_combo.addItem(preset_name)
            index = self.preset_combo.findText(preset_name, Qt.MatchFlag.MatchFixedString)
            if index != -1: self.preset_combo.setCurrentIndex(index)
            self.preset_combo.blockSignals(False)

    def update_format_selection(self, format_name: str):
        if self.format_combo:
            self.format_combo.blockSignals(True)
            index = self.format_combo.findText(format_name, Qt.MatchFlag.MatchFixedString)
            if index != -1: self.format_combo.setCurrentIndex(index)
            self.format_combo.blockSignals(False)
            
    def update_engine_selection(self, engine_name: str):
        if self.engine_combo:
            self.engine_combo.blockSignals(True)
            index = self.engine_combo.findText(engine_name.upper(), Qt.MatchFlag.MatchFixedString)
            if index != -1: self.engine_combo.setCurrentIndex(index)
            self.engine_combo.blockSignals(False)

    def update_image_size(self, width: int, height: int):
        if self.width_edit and self.width_edit.text() != str(width):
            self.width_edit.setText(str(width))
        if self.height_edit and self.height_edit.text() != str(height):
            self.height_edit.setText(str(height))

    def append_log(self, message: str):
        if self.log_text_edit: self.log_text_edit.append(message)

    def append_error(self, message: str):
        if self.error_text_edit: self.error_text_edit.append(message)


class AovDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        script_dir = Path(__file__).resolve().parent
        ui_path = script_dir / "GUI" / "ui" / "Aov.ui"
        
        loader = QUiLoader()
        file = QFile(ui_path)
        
        if file.open(QIODevice.OpenModeFlag.ReadOnly):
            self.ui = loader.load(file, None)
            file.close()
            
            if self.ui:
                layout = QVBoxLayout(self)
                layout.addWidget(self.ui)
                self.setWindowTitle("AOV設定")
                self._setup_ui_elements()
            else:
                raise RuntimeError(f"Failed to load UI from {ui_path}")
        else:
            raise IOError(f"Cannot open ui file: {ui_path}")
    
    def _setup_ui_elements(self):
        self.aov_checkboxes: list[QCheckBox] = self.ui.findChildren(QCheckBox)
        self.export_button: QPushButton = self.ui.findChild(QPushButton, "json_export_pushButton")

    def update_aov_checkboxes(self, active_aovs: list[str]):
        for checkbox in self.aov_checkboxes:
            aov_name = checkbox.objectName().replace("_checkBox", "")
            is_checked = aov_name in active_aovs
            checkbox.setChecked(is_checked)
            
    def get_selected_aovs(self) -> list[str]:
        selected_aovs = []
        for checkbox in self.aov_checkboxes:
            if checkbox.isChecked():
                aov_name = checkbox.objectName().replace("_checkBox", "")
                selected_aovs.append(aov_name)
        return selected_aovs

