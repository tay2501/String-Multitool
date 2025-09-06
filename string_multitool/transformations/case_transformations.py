"""
大文字・小文字変換処理を提供するモジュール

このモジュールは、大文字・小文字変換、PascalCase、camelCase、snake_case、
Capitalize変換などの文字ケース変換機能を個別クラスとして実装します。
"""

from __future__ import annotations

import re

from ..models.transformation_base import TransformationBase
from ..models.types import ConfigDict
from ..exceptions import TransformationError


class LowercaseTransformation(TransformationBase):
    """文字列を小文字に変換する変換クラス"""

    def __init__(self, config: ConfigDict | None = None) -> None:
        """初期化

        Args:
            config: 変換設定辞書（オプション）
        """
        super().__init__(config)
        self._rule: str = "l"
        self._input_text: str = ""
        self._output_text: str = ""

    def transform(self, text: str) -> str:
        """文字列を小文字に変換

        Args:
            text: 変換対象のテキスト

        Returns:
            変換されたテキスト

        Raises:
            TransformationError: 変換処理に失敗した場合
        """
        try:
            self._input_text = text
            self._output_text = text.lower()
            return self._output_text
        except Exception as e:
            self.set_error_context(
                {
                    "rule": self._rule,
                    "input_length": len(text) if isinstance(text, str) else 0,
                    "error_type": type(e).__name__,
                }
            )
            raise TransformationError(f"小文字変換に失敗: {e}", self.get_error_context()) from e

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


class UppercaseTransformation(TransformationBase):
    """文字列を大文字に変換する変換クラス"""

    def __init__(self, config: ConfigDict | None = None) -> None:
        """初期化

        Args:
            config: 変換設定辞書（オプション）
        """
        super().__init__(config)
        self._rule: str = "u"
        self._input_text: str = ""
        self._output_text: str = ""

    def transform(self, text: str) -> str:
        """文字列を大文字に変換

        Args:
            text: 変換対象のテキスト

        Returns:
            変換されたテキスト

        Raises:
            TransformationError: 変換処理に失敗した場合
        """
        try:
            self._input_text = text
            self._output_text = text.upper()
            return self._output_text
        except Exception as e:
            self.set_error_context(
                {
                    "rule": self._rule,
                    "input_length": len(text) if isinstance(text, str) else 0,
                    "error_type": type(e).__name__,
                }
            )
            raise TransformationError(f"大文字変換に失敗: {e}", self.get_error_context()) from e

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


class PascalCaseTransformation(TransformationBase):
    """文字列をPascalCaseに変換する変換クラス"""

    def __init__(self, config: ConfigDict | None = None) -> None:
        """初期化

        Args:
            config: 変換設定辞書（オプション）
        """
        super().__init__(config)
        self._rule: str = "p"
        self._input_text: str = ""
        self._output_text: str = ""

    def transform(self, text: str) -> str:
        """文字列をPascalCaseに変換

        Args:
            text: 変換対象のテキスト

        Returns:
            変換されたテキスト

        Raises:
            TransformationError: 変換処理に失敗した場合
        """
        try:
            self._input_text = text
            self._output_text = self._to_pascal_case(text)
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
                f"PascalCase変換に失敗: {e}", self.get_error_context()
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

    def _to_pascal_case(self, text: str) -> str:
        """文字列をPascalCaseに変換するヘルパーメソッド

        Args:
            text: 変換対象のテキスト

        Returns:
            変換されたテキスト
        """
        words = re.findall(r"\w+", text)
        return "".join(word.capitalize() for word in words)


class CamelCaseTransformation(TransformationBase):
    """文字列をcamelCaseに変換する変換クラス"""

    def __init__(self, config: ConfigDict | None = None) -> None:
        """初期化

        Args:
            config: 変換設定辞書（オプション）
        """
        super().__init__(config)
        self._rule: str = "c"
        self._input_text: str = ""
        self._output_text: str = ""

    def transform(self, text: str) -> str:
        """文字列をcamelCaseに変換

        Args:
            text: 変換対象のテキスト

        Returns:
            変換されたテキスト

        Raises:
            TransformationError: 変換処理に失敗した場合
        """
        try:
            self._input_text = text
            self._output_text = self._to_camel_case(text)
            return self._output_text
        except Exception as e:
            self.set_error_context(
                {
                    "rule": self._rule,
                    "input_length": len(text) if isinstance(text, str) else 0,
                    "error_type": type(e).__name__,
                }
            )
            raise TransformationError(f"camelCase変換に失敗: {e}", self.get_error_context()) from e

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

    def _to_camel_case(self, text: str) -> str:
        """文字列をcamelCaseに変換するヘルパーメソッド

        Args:
            text: 変換対象のテキスト

        Returns:
            変換されたテキスト
        """
        words = re.findall(r"\w+", text)
        if not words:
            return text
        first_word: str = words[0].lower()
        capitalized_words: str = "".join(word.capitalize() for word in words[1:])
        return first_word + capitalized_words


class SnakeCaseTransformation(TransformationBase):
    """文字列をsnake_caseに変換する変換クラス"""

    def __init__(self, config: ConfigDict | None = None) -> None:
        """初期化

        Args:
            config: 変換設定辞書（オプション）
        """
        super().__init__(config)
        self._rule: str = "s"
        self._input_text: str = ""
        self._output_text: str = ""

    def transform(self, text: str) -> str:
        """文字列をsnake_caseに変換

        Args:
            text: 変換対象のテキスト

        Returns:
            変換されたテキスト

        Raises:
            TransformationError: 変換処理に失敗した場合
        """
        try:
            self._input_text = text
            self._output_text = self._to_snake_case(text)
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
                f"snake_case変換に失敗: {e}", self.get_error_context()
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

    def _to_snake_case(self, text: str) -> str:
        """文字列をsnake_caseに変換するヘルパーメソッド

        Args:
            text: 変換対象のテキスト

        Returns:
            変換されたテキスト
        """
        words = re.findall(r"\w+", text)
        return "_".join(word.lower() for word in words)


class CapitalizeTransformation(TransformationBase):
    """各単語の先頭文字を大文字にする変換クラス"""

    def __init__(self, config: ConfigDict | None = None) -> None:
        """初期化

        Args:
            config: 変換設定辞書（オプション）
        """
        super().__init__(config)
        self._rule: str = "a"
        self._input_text: str = ""
        self._output_text: str = ""

    def transform(self, text: str) -> str:
        """各単語の先頭文字を大文字に変換

        Args:
            text: 変換対象のテキスト

        Returns:
            変換されたテキスト

        Raises:
            TransformationError: 変換処理に失敗した場合
        """
        try:
            self._input_text = text
            self._output_text = text.title()
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
                f"Capitalize変換に失敗: {e}", self.get_error_context()
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
