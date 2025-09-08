"""
文字列操作変換処理を提供するモジュール

このモジュールは、文字列のトリム、リバース、SQL IN句形式変換、
改行削除などの文字列操作機能を個別クラスとして実装します。
"""

from __future__ import annotations

from ..exceptions import TransformationError
from ..models.transformation_base import TransformationBase
from ..models.types import ConfigDict


class TrimTransformation(TransformationBase):
    """文字列の前後の空白または指定文字を削除する変換クラス"""

    def __init__(self, config: ConfigDict | None = None) -> None:
        """初期化

        Args:
            config: 変換設定辞書（オプション）
        """
        super().__init__(config)
        self._rule: str = "t"
        self._input_text: str = ""
        self._output_text: str = ""
        self._trim_chars: str | None = None

    def set_arguments(self, args: list[str]) -> None:
        """引数を設定

        Args:
            args: 削除対象の文字列リスト
        """
        if args:
            self._trim_chars = args[0]

    def transform(self, text: str) -> str:
        """文字列の前後の空白または指定文字を削除

        Args:
            text: 変換対象のテキスト

        Returns:
            変換されたテキスト

        Raises:
            TransformationError: 変換処理に失敗した場合
        """
        try:
            self._input_text = text
            if self._trim_chars is not None:
                # Use strip() with specific characters for optimal performance
                self._output_text = text.strip(self._trim_chars)
            else:
                # Default whitespace trimming
                self._output_text = text.strip()
            return self._output_text
        except Exception as e:
            self.set_error_context(
                {
                    "rule": self._rule,
                    "input_length": len(text) if isinstance(text, str) else 0,
                    "trim_chars": self._trim_chars,
                    "error_type": type(e).__name__,
                }
            )
            raise TransformationError(f"トリム処理に失敗: {e}", self.get_error_context()) from e

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


class ReverseTransformation(TransformationBase):
    """文字列を逆順にする変換クラス"""

    def __init__(self, config: ConfigDict | None = None) -> None:
        """初期化

        Args:
            config: 変換設定辞書（オプション）
        """
        super().__init__(config)
        self._rule: str = "R"
        self._input_text: str = ""
        self._output_text: str = ""

    def transform(self, text: str) -> str:
        """文字列を逆順にする

        Args:
            text: 変換対象のテキスト

        Returns:
            変換されたテキスト

        Raises:
            TransformationError: 変換処理に失敗した場合
        """
        try:
            self._input_text = text
            self._output_text = text[::-1]
            return self._output_text
        except Exception as e:
            self.set_error_context(
                {
                    "rule": self._rule,
                    "input_length": len(text) if isinstance(text, str) else 0,
                    "error_type": type(e).__name__,
                }
            )
            raise TransformationError(f"リバース処理に失敗: {e}", self.get_error_context()) from e

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


class SqlInClauseTransformation(TransformationBase):
    """SQL IN句形式に変換する変換クラス"""

    def __init__(self, config: ConfigDict | None = None) -> None:
        """初期化

        Args:
            config: 変換設定辞書（オプション）
        """
        super().__init__(config)
        self._rule: str = "si"
        self._input_text: str = ""
        self._output_text: str = ""

    def transform(self, text: str) -> str:
        """SQL IN句形式に変換

        Args:
            text: 変換対象のテキスト

        Returns:
            変換されたテキスト

        Raises:
            TransformationError: 変換処理に失敗した場合
        """
        try:
            self._input_text = text
            self._output_text = self._to_sql_in_clause(text)
            return self._output_text
        except Exception as e:
            self.set_error_context(
                {
                    "rule": self._rule,
                    "input_length": len(text) if isinstance(text, str) else 0,
                    "error_type": type(e).__name__,
                }
            )
            raise TransformationError(f"SQL IN句変換に失敗: {e}", self.get_error_context()) from e

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

    def _to_sql_in_clause(self, text: str) -> str:
        """SQL IN句形式に変換するヘルパーメソッド

        Args:
            text: 変換対象のテキスト

        Returns:
            変換されたテキスト
        """
        lines = text.replace("\r\n", "\n").replace("\r", "\n").split("\n")
        quoted_lines = [f"'{line.strip()}'" for line in lines if line.strip()]
        return ",\r\n".join(quoted_lines)


class DeleteLineBreaksTransformation(TransformationBase):
    """改行を削除する変換クラス"""

    def __init__(self, config: ConfigDict | None = None) -> None:
        """初期化

        Args:
            config: 変換設定辞書（オプション）
        """
        super().__init__(config)
        self._rule: str = "dlb"
        self._input_text: str = ""
        self._output_text: str = ""

    def transform(self, text: str) -> str:
        """改行を削除

        Args:
            text: 変換対象のテキスト

        Returns:
            変換されたテキスト

        Raises:
            TransformationError: 変換処理に失敗した場合
        """
        try:
            self._input_text = text
            self._output_text = text.replace("\r\n", "").replace("\n", "").replace("\r", "")
            return self._output_text
        except Exception as e:
            self.set_error_context(
                {
                    "rule": self._rule,
                    "input_length": len(text) if isinstance(text, str) else 0,
                    "error_type": type(e).__name__,
                }
            )
            raise TransformationError(f"改行削除処理に失敗: {e}", self.get_error_context()) from e

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
