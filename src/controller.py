from pathlib import Path
from PySide6.QtWidgets import QFileDialog, QListWidgetItem

from model import MainModel
from view import MainView


class MainController:
    """
    ModelとViewを連携させ、アプリケーションの動作を制御するコントローラー。
    """
    def __init__(self, model: MainModel, view: MainView):
        self._model = model
        self._view = view
        self._connect_signals()
        
    def _connect_signals(self):
        """
        ModelのシグナルをViewのスロットに、Viewのシグナルをこのクラスのスロットに接続する。
        """
        # --- Model -> View ---
        self._model.render_path_changed.connect(self._view.set_render_path)
        self._model.project_path_changed.connect(self._view.set_project_path)
        self._model.render_files_changed.connect(self._view.update_render_file_list)
        self._model.aov_json_files_changed.connect(self._view.update_aov_json_list)
        self._model.aov_data_loaded.connect(self._view.aov_dialog.update_aov_checkboxes)
        
        self._model.log_message_generated.connect(self._view.append_log)
        self._model.error_message_generated.connect(self._view.append_error)

        self._model.image_presets_loaded.connect(self._view.populate_presets)
        self._model.image_formats_loaded.connect(self._view.populate_formats)
        self._model.render_engines_loaded.connect(self._view.populate_engines)

        self._model.image_size_changed.connect(self._view.update_image_size)
        self._model.current_preset_changed.connect(self._view.update_preset_selection)
        self._model.image_format_changed.connect(self._view.update_format_selection)
        self._model.render_engine_changed.connect(self._view.update_engine_selection)
        # ▼▼▼ デフォルトサンプリング値のシグナルを接続 ▼▼▼
        self._model.sampling_defaults_applied.connect(self._view.update_sampling_spinboxes)

        # --- View -> Controller ---
        if self._view.project_path_button:
            self._view.project_path_button.clicked.connect(self._on_select_project_path)
        if self._view.reload_button:
            self._view.reload_button.clicked.connect(self._model.refresh_project_files)

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
        
        if self._view.aov_button:
            self._view.aov_button.clicked.connect(self._view.aov_dialog.show)
            
        if self._view.aov_dialog.export_button:
            self._view.aov_dialog.export_button.clicked.connect(self._on_export_aov_json)

        if self._view.file_list_widget:
            self._view.file_list_widget.currentItemChanged.connect(self._on_scene_selection_changed)
            
        if self._view.render_start_button:
            self._view.render_start_button.clicked.connect(self._on_create_batch_file)

    def _on_select_project_path(self):
        """プロジェクトパス選択ダイアログを開き、選択されたパスをModelに設定する"""
        current_path = self._model.get_project_path() or ""
        dir_name = QFileDialog.getExistingDirectory(self._view, "プロジェクトフォルダを選択", current_path)
        if dir_name:
            self._model.set_project_path(dir_name)

    def _on_scene_selection_changed(self, current_item: QListWidgetItem, previous_item: QListWidgetItem):
        """シーンリストの選択が変更されたときにAOV設定を読み込む"""
        if current_item:
            scene_filename = current_item.text()
            self._model.load_aovs_for_scene(scene_filename)
            
    def _on_export_aov_json(self):
        """AOVダイアログから現在のAOV設定をJSONファイルに保存する"""
        scene_filename = self._view.get_selected_scene()
        if not scene_filename:
            self._model.add_error("AOV設定を保存するシーンが選択されていません。")
            return
        
        selected_aovs = self._view.aov_dialog.get_selected_aovs()
        self._model.save_aovs_for_scene(scene_filename, selected_aovs)
        self._view.aov_dialog.close()

    def _on_create_batch_file(self):
        """UIから設定を取得し、Modelにバッチファイル作成を依頼する"""
        scene_file = self._view.get_selected_scene()
        if not scene_file:
            self._model.add_error("バッチファイルを作成するシーンを選択してください。")
            return
            
        settings = self._view.get_current_render_settings()
        self._model.create_batch_file(settings, scene_file)

