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
    aov_json_files_changed = Signal(list) 
    aov_data_loaded = Signal(list)
    
    log_message_generated = Signal(str)
    error_message_generated = Signal(str)
    image_presets_loaded = Signal(list)
    image_formats_loaded = Signal(list)
    render_engines_loaded = Signal(list)
    
    image_size_changed = Signal(int, int)
    current_preset_changed = Signal(str)
    image_format_changed = Signal(str)
    render_engine_changed = Signal(str)
    # ▼▼▼ デフォルトサンプリング値を通知するシグナルを追加 ▼▼▼
    sampling_defaults_applied = Signal(dict)

    def __init__(self):
        super().__init__()
        self._render_exe_path = ""
        self._project_path: Path | None = None
        self._render_files = []
        self._aov_json_files = []
        self._loaded_aovs = []

        self._image_presets_data = {}
        self._image_presets = {}
        self._image_formats = []
        self._render_engines = []

        self._image_width = 0
        self._image_height = 0
        self._current_preset = "HD_720"
        self._image_format = "exr"
        self._render_engine = "cpu"
        
        self._settings_file_path = None

    def set_settings_file_path(self, settings_path: Path):
        self._settings_file_path = settings_path
        self.load_settings()

    def find_and_set_render_path(self):
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
        return str(self._project_path) if self._project_path else ""

    def set_project_path(self, path: str):
        if not path:
            return
            
        new_path = Path(path)
        if new_path.is_dir() and new_path != self._project_path:
            self._project_path = new_path
            self.add_log(f"プロジェクトパス設定: {self._project_path}")
            self.project_path_changed.emit(str(self._project_path))
            self._save_settings()
            self.refresh_project_files()
        elif not new_path.is_dir():
            self.add_error(f"指定されたパスはフォルダではありません: {path}")

    def load_settings(self):
        try:
            if self._settings_file_path and self._settings_file_path.exists():
                with self._settings_file_path.open('r', encoding='utf-8') as f:
                    settings_data = json.load(f)
                    last_path = settings_data.get("last_project_path")
                    if last_path:
                        self.set_project_path(last_path)
        except (json.JSONDecodeError, Exception) as e:
            self.add_error(f"設定ファイルの読み込みに失敗: {e}")

    def _save_settings(self):
        try:
            if self._settings_file_path and self._project_path:
                settings_data = {"last_project_path": self._project_path.as_posix()}
                self._settings_file_path.parent.mkdir(parents=True, exist_ok=True)
                with self._settings_file_path.open('w', encoding='utf-8', errors='ignore') as f:
                    json.dump(settings_data, f, indent=4, ensure_ascii=False)
        except Exception as e:
            self.add_error(f"設定の保存に失敗: {e}")

    def refresh_project_files(self):
        self._update_render_files()
        self._update_aov_json_files()

    def _update_render_files(self):
        if not self._project_path:
            self.add_log("プロジェクトパスが設定されていません。")
            self.render_files_changed.emit([])
            return
        
        self.add_log("シーンファイルリストを更新しています...")
        render_folder = self._project_path / "render"
        
        if not render_folder.is_dir():
            render_folder.mkdir(parents=True, exist_ok=True)
            self.add_log(f"render フォルダが見つからなかったため作成しました: {render_folder}")

        all_files = list(render_folder.glob("*.mb")) + list(render_folder.glob("*.ma"))
        self._render_files = sorted([f.name for f in all_files])
        self.add_log(f"発見したシーンファイル ({len(self._render_files)}個): {self._render_files}")
        self.render_files_changed.emit(self._render_files)
        
    def _update_aov_json_files(self):
        if not self._project_path:
            self.aov_json_files_changed.emit([])
            return
            
        json_folder = self._project_path / "render" / "json"
        self.add_log(f"AOV JSON フォルダを検索中: {json_folder}")
        
        if not json_folder.is_dir():
            self.add_log("AOV JSON フォルダが見つかりません。")
            self.aov_json_files_changed.emit([])
            return
            
        json_files = list(json_folder.glob("*.json"))
        self._aov_json_files = sorted([f.name for f in json_files])
        self.add_log(f"発見したAOV JSONファイル ({len(self._aov_json_files)}個): {self._aov_json_files}")
        self.aov_json_files_changed.emit(self._aov_json_files)

    def load_aovs_for_scene(self, scene_filename: str):
        if not self._project_path or not scene_filename:
            return

        scene_basename = Path(scene_filename).stem
        json_path = self._project_path / "render" / "json" / f"{scene_basename}.json"

        if json_path.exists() and json_path.is_file():
            try:
                with json_path.open('r', encoding='utf-8') as f:
                    aov_data = json.load(f)
                    self._loaded_aovs = aov_data.get("aovs", [])
                    self.add_log(f"AOV設定を読み込みました: {json_path.name} ({len(self._loaded_aovs)}個)")
                    self.aov_data_loaded.emit(self._loaded_aovs)
            except (json.JSONDecodeError, Exception) as e:
                self._loaded_aovs = []
                self.add_error(f"AOVファイル '{json_path.name}' の読み込みに失敗: {e}")
                self.aov_data_loaded.emit([])
        else:
            self._loaded_aovs = []
            self.add_log(f"AOV設定ファイルが見つかりません: {json_path.name}")
            self.aov_data_loaded.emit([])
            
    def save_aovs_for_scene(self, scene_filename: str, aov_list: list[str]):
        if not self._project_path or not scene_filename:
            self.add_error("プロジェクトパスまたはシーンファイルが指定されていません。")
            return

        scene_basename = Path(scene_filename).stem
        json_folder = self._project_path / "render" / "json"
        json_folder.mkdir(parents=True, exist_ok=True)
        json_path = json_folder / f"{scene_basename}.json"

        try:
            aov_data = {"aovs": aov_list}
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(aov_data, f, indent=4)
            self.add_log(f"AOV設定を保存しました: {json_path.name} ({len(aov_list)}個)")
            self._update_aov_json_files()
        except Exception as e:
            self.add_error(f"設定の保存に失敗: {e}")

    def create_batch_file(self, settings: dict, scene_file: str):
        if not self._render_exe_path or not Path(self._render_exe_path).exists():
            self.add_error("Render.exeのパスが正しく設定されていません。")
            return
        if not self._project_path:
            self.add_error("プロジェクトパスが設定されていません。")
            return

        scene_basename = Path(scene_file).stem
        output_path_relative = f"render\\{scene_basename}"
        scene_file_relative = f"render\\{scene_file}"
        aov_preset_relative = f"render\\json\\{scene_basename}.json"

        aov_command_line = ""
        aov_preset_setting_line = f'SET AOV_PRESET="{aov_preset_relative}"'
        aov_path = self._project_path / aov_preset_relative.replace('\\', '/')

        if not settings.get("aov_enabled"):
            aov_command_line = "rem AOV is disabled in the UI."
            aov_preset_setting_line = f"rem {aov_preset_setting_line} (AOV disabled)"
        elif not aov_path.exists():
            aov_command_line = f"rem AOV preset file not found: {aov_preset_relative}"
            aov_preset_setting_line = f"rem {aov_preset_setting_line} (File not found)"
        else:
            aov_command_line = f'    -rsa "%PROJECT_PATH%\\%AOV_PRESET%" ^'

        template = f'''@echo off
rem 日本語のパスやファイル名を正しく扱うためのおまじない
chcp 65001 > nul

:: =================================================================
:: --- ▼ 設定項目 ---
:: =================================================================

rem Maya本体の場所
SET MAYA_RENDERER="{self._render_exe_path}"

rem プロジェクトとファイルのパス
SET PROJECT_PATH="{str(self._project_path.resolve())}"
SET SCENE_FILE="{scene_file_relative}"
{aov_preset_setting_line}

rem 出力設定
SET OUTPUT_PATH="{output_path_relative}"
SET FILENAME="{settings.get("file_name") or scene_basename}"

rem レンダリング詳細設定
SET RENDERER_ENGINE=arnold
SET START_FRAME={settings.get("start_frame", 1)}
SET END_FRAME={settings.get("end_frame", 1)}
SET RESOLUTION_X={settings.get("width", 1280)}
SET RESOLUTION_Y={settings.get("height", 720)}
SET CAMERA="{settings.get("camera", "perspShape")}"


:: =================================================================
:: --- ▼ レンダリングコマンド本体 ---
:: =================================================================

echo Starting Maya Batch Render...
echo Project: %PROJECT_PATH%
echo Scene:   %SCENE_FILE%
echo =================================================================

%MAYA_RENDERER% ^
    -r %RENDERER_ENGINE% ^
    -proj %PROJECT_PATH% ^
    -s %START_FRAME% -e %END_FRAME% ^
    -x %RESOLUTION_X% -y %RESOLUTION_Y% ^
    -cam %CAMERA% ^
    -rd "%PROJECT_PATH%\\%OUTPUT_PATH%" ^
    -im "%FILENAME%" ^
    -ai:as {settings.get("cam_aa", 3)} ^
    -ai:hs {settings.get("diffuse", 2)} ^
    -ai:gs {settings.get("specular", 2)} ^
    -ai:rs {settings.get("transmission", 2)} ^
    -ai:bssrdfs {settings.get("sss", 2)} ^
{aov_command_line}
    "%PROJECT_PATH%\\%SCENE_FILE%"

echo =================================================================
echo Render process finished.
echo Press any key to exit.
pause
'''

        bat_file_path = self._project_path / f"render_{scene_basename}.bat"
        try:
            with open(bat_file_path, "w", encoding="cp932", errors='ignore') as f:
                f.write(template)
                
            self.add_log("="*50)
            self.add_log(f"バッチファイルを作成しました: {bat_file_path}")
            self.add_log("="*50)
            self.add_log("--- バッチファイルの内容 ---")
            for line in template.splitlines():
                self.add_log(line)
            self.add_log("--- 内容ここまで ---")

        except Exception as e:
            self.add_error(f"バッチファイルの保存に失敗しました: {e}")

    def load_presets_from_file(self, file_path: Path):
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

    # ▼▼▼ デフォルト設定適用時にサンプリング値も通知するように変更 ▼▼▼
    def apply_default_settings(self):
        """アプリケーションのデフォルト設定を適用し、UIに通知する"""
        self.set_image_size_from_preset(self._current_preset)
        self.image_format_changed.emit(self._image_format)
        self.render_engine_changed.emit(self._render_engine)
        
        default_sampling = {
            "cam_aa": 3,
            "diffuse": 2,
            "specular": 2,
            "transmission": 2,
            "sss": 2,
            "volume_indirect": 2,
        }
        self.sampling_defaults_applied.emit(default_sampling)

    def set_image_size_from_preset(self, preset_name: str):
        if not preset_name: return
        preset = self._image_presets.get(preset_name)
        if preset:
            self._current_preset = preset_name
            new_width, new_height = preset.get("width", 0), preset.get("height", 0)
            if self._image_width != new_width or self._image_height != new_height:
                self._image_width, self._image_height = new_width, new_height
                self.add_log(f"プリセット '{preset_name}' を適用: {self._image_width}x{self._image_height}")
                self.image_size_changed.emit(self._image_width, self._image_height)
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
        matching_preset_name = next((name for name, values in self._image_presets.items() if values == current_size), "Custom")
        if self._current_preset != matching_preset_name:
            self._current_preset = matching_preset_name
            if self._current_preset == "Custom":
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

