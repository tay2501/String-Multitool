"""
ハッシュ変換処理を提供するモジュール

このモジュールは、SHA-256ハッシュ変換機能を個別クラスとして実装します。
"""

from __future__ import annotations

import hashlib

from ..core.transformation_base import TransformationBase
from ..core.types import ConfigDict
from ..exceptions import TransformationError


class Sha256HashTransformation(TransformationBase):
    """SHA-256ハッシュを生成する変換クラス"""

    def __init__(self, config: ConfigDict | None = None) -> None:
        """初期化
        
        Args:
            config: 変換設定辞書（オプション）
        """
        super().__init__(config)
        self._rule: str = "hash"
        self._input_text: str = ""
        self._output_text: str = ""

    def transform(self, text: str) -> str:
        """SHA-256ハッシュを生成
        
        Args:
            text: 変換対象のテキスト
            
        Returns:
            SHA-256ハッシュ文字列
            
        Raises:
            TransformationError: ハッシュ生成に失敗した場合
        """
        try:
            self._input_text = text
            self._output_text = self._sha256_hash(text)
            return self._output_text
        except Exception as e:
            self.set_error_context({
                "rule": self._rule,
                "input_length": len(text) if isinstance(text, str) else 0,
                "error_type": type(e).__name__
            })
            raise TransformationError(
                f"SHA-256ハッシュ生成に失敗: {e}",
                self.get_error_context()
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

    def _sha256_hash(self, text: str) -> str:
        """SHA-256ハッシュを生成するヘルパーメソッド
        
        Args:
            text: ハッシュ対象のテキスト
            
        Returns:
            SHA-256ハッシュ文字列（16進数）
        """
        return hashlib.sha256(text.encode("utf-8")).hexdigest()