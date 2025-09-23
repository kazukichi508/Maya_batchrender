# src/unloader.py

import sys

def unload_modules():
    """
    アプリケーションの主要モジュールをアンロードして、再読み込みを可能にします。
    開発時のホットリロードに使用します。
    """
    # アンロード対象のモジュールリスト
    modules_to_unload = [
        "model",
        "view",
        "controller",
        "style_manager",
    ]
    
    unloaded_count = 0
    for module_name in modules_to_unload:
        # sys.modulesにキャッシュされているモジュールを削除する
        if module_name in sys.modules:
            del sys.modules[module_name]
            unloaded_count += 1
            
    print(f"--- Unloaded {unloaded_count} modules for hot-reloading ---")
