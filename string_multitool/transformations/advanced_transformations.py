"""
高度な変換処理を提供するモジュール

このモジュールは、引数を必要とする高度な変換機能（置換、スラグ化など）を
個別クラスとして実装します。
"""

from __future__ import annotations

import codecs
import re

from ..exceptions import TransformationError
from ..models.transformation_base import TransformationBase
from ..models.types import ConfigDict


class ReplaceTransformation(TransformationBase):
    """文字列置換を行う変換クラス"""

    def __init__(self, config: ConfigDict | None = None) -> None:
        """初期化

        Args:
            config: 変換設定辞書（オプション）
        """
        super().__init__(config)
        self._rule: str = "r"
        self._input_text: str = ""
        self._output_text: str = ""
        self._search_text: str = ""
        self._replace_text: str = ""

    def set_arguments(self, args: list[str]) -> None:
        """置換用の引数を設定

        Args:
            args: [検索文字列, 置換文字列] のリスト
        """
        if len(args) >= 2:
            self._search_text = args[0]
            self._replace_text = args[1]
        elif len(args) == 1:
            self._search_text = args[0]
            self._replace_text = ""
        else:
            raise TransformationError(
                "置換処理には最低1つの引数が必要です",
                {"rule": self._rule, "args_count": len(args)},
            )

    def transform(self, text: str) -> str:
        """文字列置換を実行

        Args:
            text: 変換対象のテキスト

        Returns:
            置換されたテキスト

        Raises:
            TransformationError: 置換処理に失敗した場合
        """
        try:
            self._input_text = text
            # Decode escape sequences in search and replace strings
            search_decoded = self._decode_escape_sequences(self._search_text)
            replace_decoded = self._decode_escape_sequences(self._replace_text)
            self._output_text = text.replace(search_decoded, replace_decoded)
            return self._output_text
        except Exception as e:
            self.set_error_context(
                {
                    "rule": self._rule,
                    "search_text": self._search_text,
                    "replace_text": self._replace_text,
                    "input_length": len(text) if isinstance(text, str) else 0,
                    "error_type": type(e).__name__,
                }
            )
            raise TransformationError(f"文字列置換に失敗: {e}", self.get_error_context()) from e

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

    def _decode_escape_sequences(self, text: str) -> str:
        """Decode escape sequences in text using Python's codecs.decode

        Supports standard escape sequences including:
        - \\n: newline (LF)
        - \\r: carriage return (CR)
        - \\r\\n: CRLF
        - \\t: tab
        - \\\\: backslash
        - \\': single quote
        - \\": double quote

        Args:
            text: Text potentially containing escape sequences

        Returns:
            Text with escape sequences decoded

        Raises:
            TransformationError: If escape sequence decoding fails
        """
        try:
            # Use codecs.decode with 'unicode_escape' encoding for standard Python escape sequences
            return codecs.decode(text, "unicode_escape")
        except Exception as e:
            # If decoding fails, return original text (graceful degradation)
            self.set_error_context(
                {
                    "decode_error": str(e),
                    "original_text": text,
                    "error_type": type(e).__name__,
                }
            )
            # Return original text instead of raising error for backward compatibility
            return text


class SlugifyTransformation(TransformationBase):
    """URLフレンドリーなスラグに変換する変換クラス"""

    def __init__(self, config: ConfigDict | None = None) -> None:
        """初期化

        Args:
            config: 変換設定辞書（オプション）
        """
        super().__init__(config)
        self._rule: str = "S"
        self._input_text: str = ""
        self._output_text: str = ""
        self._separator: str = "-"

    def set_arguments(self, args: list[str]) -> None:
        """スラグ化用の引数を設定

        Args:
            args: [セパレータ文字列] のリスト（オプション）
        """
        if args:
            self._separator = args[0]
        else:
            self._separator = "-"

    def transform(self, text: str) -> str:
        """URLフレンドリーなスラグに変換

        Args:
            text: 変換対象のテキスト

        Returns:
            スラグ化されたテキスト

        Raises:
            TransformationError: スラグ化処理に失敗した場合
        """
        try:
            self._input_text = text
            self._output_text = self._to_slug(text)
            return self._output_text
        except Exception as e:
            self.set_error_context(
                {
                    "rule": self._rule,
                    "separator": self._separator,
                    "input_length": len(text) if isinstance(text, str) else 0,
                    "error_type": type(e).__name__,
                }
            )
            raise TransformationError(f"スラグ化処理に失敗: {e}", self.get_error_context()) from e

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

    def _to_slug(self, text: str) -> str:
        """URLフレンドリーなスラグに変換するヘルパーメソッド

        Args:
            text: 変換対象のテキスト

        Returns:
            スラグ化されたテキスト
        """
        # Convert to lowercase, replace non-alphanumeric with separator
        result = re.sub(r"[^a-zA-Z0-9]+", self._separator, text.lower())
        return result.strip(self._separator)
