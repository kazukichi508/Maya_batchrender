import json
from pathlib import Path

from PySide6.QtCore import QObject, Signal


class MainModel(QObject):
    """
    アプリケーションのデータとビジネスロジックを管理するクラス。
    """
    # --- データ変更を通知するためのシグナル定義 ---
    render_path_changed = Signal(str)
    project_path_changed = Signal(str)
    render_files_changed = Signal(list)
    
    log_message_generated = Signal(str)
    error_message_generated = Signal(str)
    image_presets_loaded = Signal(list)
    image_formats_loaded = Signal(list)
    render_engines_loaded = Signal(list)
    
    image_size_changed = Signal(int, int)
    current_preset_changed = Signal(str)
    image_format_changed = Signal(str)
    render_engine_changed = Signal(str)

    def __init__(self):
        super().__init__()
        self._render_exe_path = ""
        self._project_path: Path | None = None # PathオブジェクトまたはNoneを保持
        self._render_files = []

        self._image_presets_data = {}
        self._image_presets = {}
        self._image_formats = []
        self._render_engines = []

        self._image_width = 0
        self._image_height = 0
        self._current_preset = "HD_720"
        self._image_format = "exr"
        self._render_engine = "cpu"

        # AOV JSONのパスを固定にする
        src_dir = Path(__file__).resolve().parent
        self._aov_json_path = src_dir / "JSON" / "aov_settings.json"
        
        self._settings_file_path = None

    def set_settings_file_path(self, settings_path: Path):
        """設定ファイルのパスを初期化し、最後のプロジェクトパスを読み込む"""
        self._settings_file_path = settings_path
        self.load_settings()

    def find_and_set_render_path(self):
        """MayaのRender.exeを一般的なインストールパスから検索して設定する"""
        maya_versions = range(2026, 2020, -1)
        base_path = Path("C:/Program Files/Autodesk")
        for version in maya_versions:
            render_path = base_path / f"Maya{version}" / "bin" / "Render.exe"
            if render_path.exists():
                self._render_exe_path = str(render_path)
                self.add_log(f"Render.exe を発見: {self._render_exe_path}")
                self.render_path_changed.emit(self._render_exe_path)
                return
        self.add_error("Render.exe が見つかりませんでした。")
        self.render_path_changed.emit("")

    def get_project_path(self) -> str:
        """プロジェクトパスを文字列として返す"""
        return str(self._project_path) if self._project_path else ""

    def set_project_path(self, path: str):
        """文字列のパスを受け取り、Pathオブジェクトとして検証・保存する"""
        if not path:
            return
            
        new_path = Path(path)
        if new_path.is_dir() and new_path != self._project_path:
            self._project_path = new_path # Pathオブジェクトとして保存
            self.add_log(f"プロジェクトパス設定: {self._project_path}")
            self.project_path_changed.emit(str(self._project_path))
            self._save_settings()
            self.refresh_render_files()
        elif not new_path.is_dir():
            self.add_error(f"指定されたパスはフォルダではありません: {path}")

    def get_aov_json_path(self) -> Path | None:
        """AOV設定を保存するJSONファイルのパスを返す"""
        return self._aov_json_path

    def load_settings(self):
        """設定ファイルから最後のプロジェクトパスを読み込む"""
        try:
            if self._settings_file_path and self._settings_file_path.exists():
                with self._settings_file_path.open('r', encoding='utf-8') as f:
                    settings = json.load(f)
                    last_path = settings.get("last_project_path")
                    # set_project_pathは文字列を期待するので、そのまま渡す
                    if last_path:
                        self.set_project_path(last_path)
        except (json.JSONDecodeError, Exception) as e:
            self.add_error(f"設定ファイルの読み込みに失敗: {e}")

    def _save_settings(self):
        """現在のプロジェクトパスをフォワードスラッシュ形式で設定ファイルに保存する"""
        try:
            if self._settings_file_path and self._project_path:
                # as_posix() を使って確実にフォワードスラッシュのパス文字列を取得
                settings = {"last_project_path": self._project_path.as_posix()}
                self._settings_file_path.parent.mkdir(parents=True, exist_ok=True)
                with self._settings_file_path.open('w', encoding='utf-8') as f:
                    # ensure_ascii=False を追加して日本語がそのまま保存されるようにする
                    json.dump(settings, f, indent=4, ensure_ascii=False)
        except Exception as e:
            self.add_error(f"設定の保存に失敗: {e}")

    def refresh_render_files(self):
        if not self._project_path:
            self.add_log("プロジェクトパスが設定されていません。")
            self.render_files_changed.emit([])
            return
        
        self.add_log("ファイルリストを更新しています...")
        render_folder_path = self._project_path / "render"
        self._render_files = []
        if render_folder_path.is_dir():
            files = list(render_folder_path.glob("*.mb")) + list(render_folder_path.glob("*.ma"))
            self._render_files = sorted([f.name for f in files])
            self.add_log(f"{len(self._render_files)}個のシーンファイルが見つかりました。")
        else:
            self.add_log(f"render フォルダが見つかりません: {render_folder_path}")
        self.render_files_changed.emit(self._render_files)

    def load_presets_from_file(self, file_path: Path):
        """プリセットファイルを読み込み、関連するデータを初期化する"""
        try:
            with file_path.open('r', encoding='utf-8') as f:
                self._image_presets_data = json.load(f)
                
                self._image_presets = self._image_presets_data.get("image_presets", {})
                self.image_presets_loaded.emit(list(self._image_presets.keys()))
                
                self._image_formats = self._image_presets_data.get("image_formats", [])
                self.image_formats_loaded.emit(self._image_formats)

                self._render_engines = self._image_presets_data.get("render_engines", [])
                self.render_engines_loaded.emit(self._render_engines)

                self.add_log(f"プリセットを読み込みました: {file_path}")
        except Exception as e:
            self.add_error(f"プリセットファイルの読み込みに失敗: {e}")
            self.image_presets_loaded.emit([])

    def apply_default_settings(self):
        """
        アプリケーションのデフォルト設定を適用する。
        UIの初期表示をモデルのデフォルト状態に強制的に同期させる。
        """
        # プリセットとサイズの初期値を設定
        self.set_image_size_from_preset(self._current_preset)
        
        # フォーマットとエンジンの初期値をシグナルでUIに直接通知
        self.image_format_changed.emit(self._image_format)
        self.render_engine_changed.emit(self._render_engine)

    def set_image_size_from_preset(self, preset_name: str):
        if not preset_name:
            return
        
        preset = self._image_presets.get(preset_name)
        if preset:
            self._current_preset = preset_name
            new_width = preset.get("width", 0)
            new_height = preset.get("height", 0)
            
            if self._image_width != new_width or self._image_height != new_height:
                self._image_width = new_width
                self._image_height = new_height
                self.add_log(f"プリセット '{preset_name}' を適用: {self._image_width}x{self._image_height}")
                self.image_size_changed.emit(self._image_width, self._image_height)
            
            # プリセットの表示を同期するために、常にシグナルを発行
            self.current_preset_changed.emit(self._current_preset)

    def set_image_width(self, width_text: str):
        try:
            width = int(width_text) if width_text else 0
            if self._image_width != width:
                self._image_width = width
                self._check_and_update_preset_selection()
        except ValueError: pass

    def set_image_height(self, height_text: str):
        try:
            height = int(height_text) if height_text else 0
            if self._image_height != height:
                self._image_height = height
                self._check_and_update_preset_selection()
        except ValueError: pass

    def _check_and_update_preset_selection(self):
        current_size = {"width": self._image_width, "height": self._image_height}
        matching_preset_name = ""
        for name, values in self._image_presets.items():
            if values == current_size:
                matching_preset_name = name
                break
        
        new_preset = matching_preset_name if matching_preset_name else "Custom"
        if self._current_preset != new_preset:
            self._current_preset = new_preset
            if new_preset == "Custom":
                 self.add_log("手動でのサイズ変更によりプリセットが 'Custom' になりました。")
            self.current_preset_changed.emit(self._current_preset)
            
    def set_image_format(self, format_name: str):
        if format_name and self._image_format != format_name:
            self._image_format = format_name
            self.image_format_changed.emit(self._image_format)

    def set_render_engine(self, engine: str):
        if not engine: return
        engine_lower = engine.lower()
        if engine_lower in self._render_engines and self._render_engine != engine_lower:
            self._render_engine = engine_lower
            self.add_log(f"レンダリングエンジンを '{self._render_engine}' に変更しました。")
            self.render_engine_changed.emit(self._render_engine)

    def add_log(self, message: str):
        self.log_message_generated.emit(message)

    def add_error(self, message: str):
        self.error_message_generated.emit(message)

