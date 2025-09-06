"""
フォーマット変換処理を提供するモジュール

このモジュールは、JSON整形などのフォーマット変換機能を個別クラスとして実装します。
"""

from __future__ import annotations

import json

from ..models.transformation_base import TransformationBase
from ..models.types import ConfigDict
from ..exceptions import TransformationError


class JsonFormatTransformation(TransformationBase):
    """JSON文字列を整形する変換クラス"""

    def __init__(self, config: ConfigDict | None = None) -> None:
        """初期化

        Args:
            config: 変換設定辞書（オプション）
        """
        super().__init__(config)
        self._rule: str = "formatjson"
        self._input_text: str = ""
        self._output_text: str = ""

    def transform(self, text: str) -> str:
        """JSON文字列を整形

        Args:
            text: 変換対象のテキスト

        Returns:
            整形されたJSON文字列

        Raises:
            TransformationError: 整形処理に失敗した場合
        """
        try:
            self._input_text = text
            self._output_text = self._format_json(text)
            return self._output_text
        except Exception as e:
            self.set_error_context(
                {
                    "rule": self._rule,
                    "input_length": len(text) if isinstance(text, str) else 0,
                    "error_type": type(e).__name__,
                }
            )
            raise TransformationError(f"JSON整形に失敗: {e}", self.get_error_context()) from e

    def get_transformation_rule(self) -> str:
        """適用される変換ルールを取得

        Returns:
            変換ルール文字列
        """
        return self._rule

    def get_input_text(self) -> str:
        """変換前の文字列を取得

        Returns:
            変換前の文字列
        """
        return self._input_text

    def get_output_text(self) -> str:
        """変換後の文字列を取得

        Returns:
            変換後の文字列
        """
        return self._output_text

    def _format_json(self, text: str) -> str:
        """JSON文字列を整形するヘルパーメソッド

        Args:
            text: 整形対象のJSON文字列

        Returns:
            整形されたJSON文字列

        Raises:
            TransformationError: 整形に失敗した場合
        """
        try:
            # Parse JSON
            parsed = json.loads(text)
            # Format with 2-space indentation
            return json.dumps(parsed, indent=2, ensure_ascii=False)
        except json.JSONDecodeError as e:
            # JSONパーシングエラーの場合
            self.set_error_context(
                {
                    "json_error": str(e),
                    "error_line": getattr(e, "lineno", "unknown"),
                    "error_pos": getattr(e, "pos", "unknown"),
                    "text_preview": text[:100],
                }
            )
            raise TransformationError(
                f"不正なJSONフォーマット: {e}", self.get_error_context()
            ) from e
        except Exception as e:
            # その他のエラー
            self.set_error_context({"error_type": type(e).__name__})
            raise TransformationError(f"JSON整形に失敗: {e}", self.get_error_context()) from e
