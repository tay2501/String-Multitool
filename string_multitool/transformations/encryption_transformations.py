"""
暗号化変換処理を提供するモジュール

このモジュールは、RSA暗号化・復号化機能を個別クラスとして実装します。
"""

from __future__ import annotations

from ..core.transformation_base import TransformationBase
from ..core.types import ConfigDict, CryptoManagerProtocol
from ..exceptions import TransformationError


class EncryptTransformation(TransformationBase):
    """RSA暗号化を行う変換クラス"""

    def __init__(self, config: ConfigDict | None = None) -> None:
        """初期化

        Args:
            config: 変換設定辞書（オプション）
        """
        super().__init__(config)
        self._rule: str = "enc"
        self._input_text: str = ""
        self._output_text: str = ""
        self._crypto_manager: CryptoManagerProtocol | None = None

    def set_crypto_manager(self, crypto_manager: CryptoManagerProtocol) -> None:
        """暗号化マネージャーを設定

        Args:
            crypto_manager: 暗号化マネージャーインスタンス
        """
        self._crypto_manager = crypto_manager

    def transform(self, text: str) -> str:
        """RSA暗号化を実行

        Args:
            text: 変換対象のテキスト

        Returns:
            暗号化されたテキスト

        Raises:
            TransformationError: 暗号化処理に失敗した場合
        """
        try:
            if self._crypto_manager is None:
                raise TransformationError(
                    "暗号化マネージャーが設定されていません", {"rule": self._rule}
                )

            self._input_text = text
            print("Using existing RSA key pair")
            self._output_text = self._crypto_manager.encrypt_text(text)
            print(f"Text encrypted successfully (AES-256+RSA-4096, {len(text)} bytes)")
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
                f"暗号化処理に失敗: {e}", self.get_error_context()
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


class DecryptTransformation(TransformationBase):
    """RSA復号化を行う変換クラス"""

    def __init__(self, config: ConfigDict | None = None) -> None:
        """初期化

        Args:
            config: 変換設定辞書（オプション）
        """
        super().__init__(config)
        self._rule: str = "dec"
        self._input_text: str = ""
        self._output_text: str = ""
        self._crypto_manager: CryptoManagerProtocol | None = None

    def set_crypto_manager(self, crypto_manager: CryptoManagerProtocol) -> None:
        """暗号化マネージャーを設定

        Args:
            crypto_manager: 暗号化マネージャーインスタンス
        """
        self._crypto_manager = crypto_manager

    def transform(self, text: str) -> str:
        """RSA復号化を実行

        Args:
            text: 変換対象のテキスト

        Returns:
            復号化されたテキスト

        Raises:
            TransformationError: 復号化処理に失敗した場合
        """
        try:
            if self._crypto_manager is None:
                raise TransformationError(
                    "暗号化マネージャーが設定されていません", {"rule": self._rule}
                )

            self._input_text = text
            print("Using existing RSA key pair")
            self._output_text = self._crypto_manager.decrypt_text(text)
            print(
                f"Text decrypted successfully (AES-256+RSA-4096, {len(self._output_text)} chars)"
            )
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
                f"復号化処理に失敗: {e}", self.get_error_context()
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
