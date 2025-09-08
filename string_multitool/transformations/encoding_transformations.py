"""
エンコード変換処理を提供するモジュール

このモジュールは、Base64エンコード・デコード機能を個別クラスとして実装します。
"""

from __future__ import annotations

import base64

from ..exceptions import TransformationError
from ..models.transformation_base import TransformationBase
from ..models.types import ConfigDict


class Base64EncodeTransformation(TransformationBase):
    """Base64エンコードを行う変換クラス"""

    def __init__(self, config: ConfigDict | None = None) -> None:
        """初期化

        Args:
            config: 変換設定辞書（オプション）
        """
        super().__init__(config)
        self._rule: str = "base64enc"
        self._input_text: str = ""
        self._output_text: str = ""

    def transform(self, text: str) -> str:
        """Base64エンコードを実行

        Args:
            text: 変換対象のテキスト

        Returns:
            Base64エンコードされたテキスト

        Raises:
            TransformationError: エンコード処理に失敗した場合
        """
        try:
            self._input_text = text
            self._output_text = self._base64_encode(text)
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
                f"Base64エンコードに失敗: {e}", self.get_error_context()
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

    def _base64_encode(self, text: str) -> str:
        """Base64エンコードを実行するヘルパーメソッド

        Args:
            text: エンコード対象のテキスト

        Returns:
            Base64エンコードされたテキスト

        Raises:
            TransformationError: エンコードに失敗した場合
        """
        try:
            encoded_bytes = base64.b64encode(text.encode("utf-8"))
            return encoded_bytes.decode("ascii")
        except UnicodeEncodeError as e:
            self.set_error_context({"encoding_error": str(e), "text_preview": text[:50]})
            raise TransformationError(
                f"テキストエンコードに失敗: {e}", self.get_error_context()
            ) from e
        except Exception as e:
            self.set_error_context({"error_type": type(e).__name__})
            raise TransformationError(
                f"Base64エンコードに失敗: {e}", self.get_error_context()
            ) from e


class Base64DecodeTransformation(TransformationBase):
    """Base64デコードを行う変換クラス"""

    def __init__(self, config: ConfigDict | None = None) -> None:
        """初期化

        Args:
            config: 変換設定辞書（オプション）
        """
        super().__init__(config)
        self._rule: str = "base64dec"
        self._input_text: str = ""
        self._output_text: str = ""

    def transform(self, text: str) -> str:
        """Base64デコードを実行

        Args:
            text: 変換対象のテキスト

        Returns:
            Base64デコードされたテキスト

        Raises:
            TransformationError: デコード処理に失敗した場合
        """
        try:
            self._input_text = text
            self._output_text = self._base64_decode(text)
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
                f"Base64デコードに失敗: {e}", self.get_error_context()
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

    def _base64_decode(self, text: str) -> str:
        """Base64デコードを実行するヘルパーメソッド

        Args:
            text: デコード対象のテキスト

        Returns:
            Base64デコードされたテキスト

        Raises:
            TransformationError: デコードに失敗した場合
        """
        try:
            clean_text = text.strip()
            decoded_bytes = base64.b64decode(clean_text)
            return decoded_bytes.decode("utf-8")
        except UnicodeDecodeError as e:
            self.set_error_context({"unicode_error": str(e)})
            raise TransformationError(
                f"テキストデコードに失敗: {e}", self.get_error_context()
            ) from e
        except Exception as e:
            self.set_error_context({"decode_error": str(e), "text_preview": text[:50]})
            raise TransformationError(
                f"Base64デコードに失敗: {e}", self.get_error_context()
            ) from e
