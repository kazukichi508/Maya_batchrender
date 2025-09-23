# Filename: create_batch_file.py
import os
from pathlib import Path

# --- 設定項目 ---
# ユーザーはこのセクションを自分の環境に合わせて変更します。

# 1. Mayaプロジェクトのルートフォルダを指定
# 例: r"C:\Users\YourName\Documents\maya\projects\default"
PROJECT_PATH = Path(r"C:\Users\ohs20343\Desktop\New_Project")

# 2. Render.exeのフルパスを指定
# 例: r"C:\Program Files\Autodesk\Maya2025\bin\Render.exe"
RENDER_EXE_PATH = Path(r"C:\Program Files\Autodesk\Maya2025\bin\Render.exe")

# 3. (オプション) MAYA_MODULE_PATHに設定したいパスをリストで指定
#    複数指定すると、それぞれのパスでレンダリングが実行されます。
#    不要な場合は空リスト [] にします。
# 例: [r"C:\Modules\PluginVersion_100", r"C:\Modules\PluginVersion_130"]
MODULE_PATHS = [
    r"C:\Modules\PluginVersion_100",
    r"C:\Modules\PluginVersion_130",
    r"C:\Modules\PluginVersion_151",
]

# 4. レンダリング設定
RENDER_SETTINGS = {
    "start_frame": 1,
    "end_frame": 5,
    "width": 1920,
    "height": 1080,
    "format": "exr",
    # イメージファイル名の接頭辞 (レンダリングバージョンごとに自動でサフィックスが付きます)
    "image_name_prefix": "shot_010", 
    # Arnoldサンプリング設定
    "cam_aa": 3,
    "diffuse": 2,
    "specular": 2,
    "transmission": 2,
    "sss": 2,
    # その他
    "motion_blur": False,
    "ray_tracing": True,
    "reflection_depth": 8,
    "refraction_depth": 8,
}

# --- スクリプト本体 ---

def create_batch_file():
    """
    設定に基づいてレンダリング用のWindowsバッチファイルを作成します。
    """
    if not PROJECT_PATH.is_dir():
        print(f"エラー: 指定されたプロジェクトパスが見つかりません: {PROJECT_PATH}")
        return

    if not RENDER_EXE_PATH.is_file():
        print(f"エラー: Render.exeが見つかりません: {RENDER_EXE_PATH}")
        return
        
    render_folder = PROJECT_PATH / "render"
    if not render_folder.is_dir():
        print(f"エラー: 'render' フォルダがプロジェクト内に見つかりません: {render_folder}")
        return
        
    scene_files = sorted(list(render_folder.glob("*.mb")) + list(render_folder.glob("*.ma")))
    if not scene_files:
        print(f"エラー: 'render' フォルダ内にレンダリング対象のシーンファイル (.ma, .mb) が見つかりません。")
        return

    batch_commands = ["@echo off", ""]
    
    module_paths_to_run = MODULE_PATHS if MODULE_PATHS else [None]

    for i, module_path in enumerate(module_paths_to_run):
        if module_path:
            batch_commands.append(f"SET MAYA_MODULE_PATH={module_path}")
            batch_commands.append(f'echo --- MAYA_MODULE_PATH set to: "{module_path}" ---')
            batch_commands.append("")

        for scene_path in scene_files:
            scene_basename = scene_path.stem
            output_dir = render_folder / scene_basename
            
            batch_commands.append(f'if not exist "{output_dir}" mkdir "{output_dir}"')

            args = []
            args.extend(["-r", "arnold"])
            args.extend(["-proj", f'"{str(PROJECT_PATH.resolve())}"'])
            args.extend(["-rd", f'"{str(output_dir.resolve())}"'])
            
            args.extend(["-s", str(RENDER_SETTINGS["start_frame"])])
            args.extend(["-e", str(RENDER_SETTINGS["end_frame"])])
            args.extend(["-x", str(RENDER_SETTINGS["width"])])
            args.extend(["-y", str(RENDER_SETTINGS["height"])])
            
            base_prefix = RENDER_SETTINGS["image_name_prefix"] or scene_basename
            suffix = f"v{i+1:03d}" if module_path else "default"
            file_prefix = f"{base_prefix}_{suffix}"
            args.extend(["-im", f'"{file_prefix}"'])
            
            args.extend(["-of", RENDER_SETTINGS["format"]])

            aov_json_path = render_folder / "json" / f"{scene_basename}.json"
            if aov_json_path.exists():
                args.extend(["-rsa", f'"{str(aov_json_path.resolve())}"'])
            
            args.extend(["-ai:as", str(RENDER_SETTINGS["cam_aa"])])
            args.extend(["-ai:hs", str(RENDER_SETTINGS["diffuse"])])
            args.extend(["-ai:gs", str(RENDER_SETTINGS["specular"])])
            args.extend(["-ai:rs", str(RENDER_SETTINGS["transmission"])])
            args.extend(["-ai:bssrdfs", str(RENDER_SETTINGS["sss"])])
            args.extend(["-ai:mben", "1" if RENDER_SETTINGS["motion_blur"] else "0"])
            if RENDER_SETTINGS["ray_tracing"]:
                args.extend(["-ai:td", str(RENDER_SETTINGS["reflection_depth"])])
                args.extend(["-ai:rfr", str(RENDER_SETTINGS["refraction_depth"])])

            args.append(f'"{str(scene_path.resolve())}"')
            
            batch_commands.append(f'echo Rendering {scene_path.name} with settings "{suffix}"...')
            full_command = f'"{RENDER_EXE_PATH}" {" ".join(args)}'
            batch_commands.append(full_command)
            batch_commands.append("")

        if module_path:
             batch_commands.append("echo Clearing MAYA_MODULE_PATH...")
             batch_commands.append("SET MAYA_MODULE_PATH=")
             batch_commands.append("")

    batch_commands.append("echo --- All render tasks have been issued. ---")
    batch_commands.append("cmd /k")

    bat_file_path = PROJECT_PATH / "render_batch.bat"
    try:
        with open(bat_file_path, "w", encoding="cp932", errors='ignore') as f:
            f.write("\n".join(batch_commands))
            
        print("="*50)
        print(f"バッチファイルを作成しました: {bat_file_path}")
        print("="*50)
        print("--- バッチファイルの内容 ---")
        print("\n".join(batch_commands))
        print("--- 内容ここまで ---")
        print("\n上記パスの `render_batch.bat` をダブルクリックして実行してください。")

    except Exception as e:
        print(f"エラー: バッチファイルの保存に失敗しました: {e}")


if __name__ == "__main__":
    create_batch_file()
