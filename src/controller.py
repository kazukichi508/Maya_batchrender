from pathlib import Path
from PySide6.QtWidgets import QFileDialog

from model import MainModel
from view import MainView
from aov_manager import AovManager


class MainController:
    """
    ModelとViewを連携させ、アプリケーションの動作を制御するコントローラー。
    """
    def __init__(self, model: MainModel, view: MainView):
        self._model = model
        self._view = view
        
        # AOV Managerを初期化
        self._aov_manager = AovManager(self._view.aov_dialog)
        
        self._connect_signals()
        
    def _connect_signals(self):
        """
        ModelのシグナルをViewのスロットに、Viewのシグナルをこのクラスのスロットに接続する。
        """
        # --- Model -> View ---
        self._model.render_path_changed.connect(self._view.set_render_path)
        self._model.project_path_changed.connect(self._view.set_project_path)
        self._model.render_files_changed.connect(self._view.update_render_file_list)
        
        self._model.log_message_generated.connect(self._view.append_log)
        self._model.error_message_generated.connect(self._view.append_error)

        self._model.image_presets_loaded.connect(self._view.populate_presets)
        self._model.image_formats_loaded.connect(self._view.populate_formats)
        self._model.render_engines_loaded.connect(self._view.populate_engines)

        self._model.image_size_changed.connect(self._view.update_image_size)
        self._model.current_preset_changed.connect(self._view.update_preset_selection)
        self._model.image_format_changed.connect(self._view.update_format_selection)
        self._model.render_engine_changed.connect(self._view.update_engine_selection)

        # --- View -> Controller ---
        if self._view.project_path_button:
            self._view.project_path_button.clicked.connect(self._on_select_project_path)
        if self._view.reload_button:
            self._view.reload_button.clicked.connect(self._model.refresh_render_files)

        if self._view.preset_combo:
            self._view.preset_combo.currentTextChanged.connect(self._model.set_image_size_from_preset)
        if self._view.width_edit:
            self._view.width_edit.textChanged.connect(self._model.set_image_width)
        if self._view.height_edit:
            self._view.height_edit.textChanged.connect(self._model.set_image_height)

        if self._view.format_combo:
            self._view.format_combo.currentTextChanged.connect(self._model.set_image_format)
        if self._view.engine_combo:
            self._view.engine_combo.currentTextChanged.connect(self._model.set_render_engine)
        
        # --- AOV関連 ---
        if self._view.aov_button:
            self._view.aov_button.clicked.connect(self._view.aov_dialog.show)
        
        # --- 修正: AovDialog内のボタンに直接接続する ---
        if self._view.aov_dialog and self._view.aov_dialog.export_button:
            self._view.aov_dialog.export_button.clicked.connect(self._on_export_aov_settings)


    def _on_select_project_path(self):
        """プロジェクトパス選択ダイアログを開き、選択されたパスをModelに設定する"""
        current_path = self._model.get_project_path() or ""
        dir_name = QFileDialog.getExistingDirectory(self._view.window, "プロジェクトフォルダを選択", current_path)
        if dir_name:
            self._model.set_project_path(dir_name)
    
    def _on_export_aov_settings(self):
        """AOV設定をJSONに書き出すスロット"""
        output_path = self._model.get_aov_json_path()
        if not output_path:
            self._model.add_error("プロジェクトパスが設定されていないため、AOV設定を保存できません。")
            return

        # AOV Manager に書き出しを指示
        message = self._aov_manager.export_aov_settings(output_path)
        
        # 結果をログに表示
        if "失敗" in message:
            self._model.add_error(message)
        else:
            self._model.add_log(message)
        
        # 書き出し後にダイアログを閉じる
        self._view.aov_dialog.accept()

