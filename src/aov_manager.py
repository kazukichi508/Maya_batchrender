import json
from pathlib import Path
from PySide6.QtWidgets import QDialog, QCheckBox

class AovManager:
    """
    AOV (Arbitrary Output Variables) の状態を管理し、
    JSONファイルへのエクスポートを行うクラス。
    """
    def __init__(self, aov_dialog: QDialog):
        self._dialog = aov_dialog
        # AOVダイアログ内の全てのQCheckBoxを検索して保持する
        self._checkboxes = self._dialog.findChildren(QCheckBox)

    def get_checked_aovs(self) -> list[str]:
        """
        現在チェックされているAOVの名前のリストを返す。
        チェックボックスの objectName をAOV名として使用する。
        """
        return [cb.objectName() for cb in self._checkboxes if cb.isChecked()]

    def export_aov_settings(self, output_path: Path):
        """
        チェックされているAOV設定をJSONファイルに書き出す。
        Arnoldの -rsa フラグが期待するフォーマットで出力する。
        """
        checked_aovs = self.get_checked_aovs()
        
        # Arnoldが想定するJSON構造を作成
        # ここでは単純なリストとしていますが、必要に応じて
        # より複雑な構造（例：ドライバやフィルタ設定）を追加できます。
        aov_data = {
            "aovs": checked_aovs
        }

        try:
            with output_path.open('w', encoding='utf-8') as f:
                json.dump(aov_data, f, indent=4)
            return f"AOV設定を {output_path} に保存しました。"
        except Exception as e:
            return f"AOV設定の保存に失敗しました: {e}"
