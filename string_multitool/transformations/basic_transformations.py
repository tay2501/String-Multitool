"""
Basic text transformation module.

This module provides fundamental text transformation functionality
including underscore-to-hyphen conversion, full-width to half-width
conversion, and other basic text operations as individual classes.
"""

from __future__ import annotations

from ..models.transformation_base import TransformationBase
from ..models.types import ConfigDict
from ..exceptions import TransformationError


class UnderbarToHyphenTransformation(TransformationBase):
    """Transformation class to convert underscores to hyphens."""

    def __init__(self, config: ConfigDict | None = None) -> None:
        """Initialize the transformation.

        Args:
            config: Optional transformation configuration dictionary
        """
        super().__init__(config)
        self._rule: str = "uh"
        self._input_text: str = ""
        self._output_text: str = ""

    def transform(self, text: str) -> str:
        """Convert underscores to hyphens.

        Args:
            text: Text to be transformed

        Returns:
            Transformed text with underscores replaced by hyphens

        Raises:
            TransformationError: If transformation process fails
        """
        try:
            self._input_text = text
            self._output_text = text.replace("_", "-")
            return self._output_text
        except Exception as e:
            self.set_error_context(
                {
                    "rule": self._rule,
                    "input_length": len(text) if isinstance(text, str) else 0,
                    "error_type": type(e).__name__,
                }
            )
            raise TransformationError(
                f"アンダーバー→ハイフン変換に失敗: {e}", self.get_error_context()
            ) from e

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


class HyphenToUnderbarTransformation(TransformationBase):
    """ハイフンをアンダーバーに変換する変換クラス"""

    def __init__(self, config: ConfigDict | None = None) -> None:
        """初期化

        Args:
            config: 変換設定辞書（オプション）
        """
        super().__init__(config)
        self._rule: str = "hu"
        self._input_text: str = ""
        self._output_text: str = ""

    def transform(self, text: str) -> str:
        """ハイフンをアンダーバーに変換

        Args:
            text: 変換対象のテキスト

        Returns:
            変換されたテキスト

        Raises:
            TransformationError: 変換処理に失敗した場合
        """
        try:
            self._input_text = text
            self._output_text = text.replace("-", "_")
            return self._output_text
        except Exception as e:
            self.set_error_context(
                {
                    "rule": self._rule,
                    "input_length": len(text) if isinstance(text, str) else 0,
                    "error_type": type(e).__name__,
                }
            )
            raise TransformationError(
                f"ハイフン→アンダーバー変換に失敗: {e}", self.get_error_context()
            ) from e

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


class FullToHalfWidthTransformation(TransformationBase):
    """全角文字を半角文字に変換する変換クラス"""

    def __init__(self, config: ConfigDict | None = None) -> None:
        """初期化

        Args:
            config: 変換設定辞書（オプション）
        """
        super().__init__(config)
        self._rule: str = "fh"
        self._input_text: str = ""
        self._output_text: str = ""

    def transform(self, text: str) -> str:
        """全角文字を半角文字に変換

        Args:
            text: 変換対象のテキスト

        Returns:
            変換されたテキスト

        Raises:
            TransformationError: 変換処理に失敗した場合
        """
        try:
            self._input_text = text
            self._output_text = self._full_to_half_width(text)
            return self._output_text
        except Exception as e:
            self.set_error_context(
                {
                    "rule": self._rule,
                    "input_length": len(text) if isinstance(text, str) else 0,
                    "error_type": type(e).__name__,
                }
            )
            raise TransformationError(f"全角→半角変換に失敗: {e}", self.get_error_context()) from e

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

    def _full_to_half_width(self, text: str) -> str:
        """全角文字を半角文字に変換するヘルパーメソッド

        Args:
            text: 変換対象のテキスト

        Returns:
            変換されたテキスト
        """
        result = ""
        for char in text:
            code = ord(char)
            if 0xFF01 <= code <= 0xFF5E:  # Full-width ASCII range
                result += chr(code - 0xFEE0)
            elif code == 0x3000:  # Full-width space
                result += " "
            else:
                result += char
        return result


class HalfToFullWidthTransformation(TransformationBase):
    """半角文字を全角文字に変換する変換クラス"""

    def __init__(self, config: ConfigDict | None = None) -> None:
        """初期化

        Args:
            config: 変換設定辞書（オプション）
        """
        super().__init__(config)
        self._rule: str = "hf"
        self._input_text: str = ""
        self._output_text: str = ""

    def transform(self, text: str) -> str:
        """半角文字を全角文字に変換

        Args:
            text: 変換対象のテキスト

        Returns:
            変換されたテキスト

        Raises:
            TransformationError: 変換処理に失敗した場合
        """
        try:
            self._input_text = text
            self._output_text = self._half_to_full_width(text)
            return self._output_text
        except Exception as e:
            self.set_error_context(
                {
                    "rule": self._rule,
                    "input_length": len(text) if isinstance(text, str) else 0,
                    "error_type": type(e).__name__,
                }
            )
            raise TransformationError(f"半角→全角変換に失敗: {e}", self.get_error_context()) from e

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

    def _half_to_full_width(self, text: str) -> str:
        """半角文字を全角文字に変換するヘルパーメソッド

        Args:
            text: 変換対象のテキスト

        Returns:
            変換されたテキスト
        """
        result = ""
        for char in text:
            code = ord(char)
            if 0x21 <= code <= 0x7E:  # Half-width ASCII range
                result += chr(code + 0xFEE0)
            elif char == " ":  # Half-width space
                result += "　"
            else:
                result += char
        return result
