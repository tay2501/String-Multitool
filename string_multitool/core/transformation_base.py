"""
抽象基底クラスとテキスト変換プロトコルの定義

このモジュールは、すべてのテキスト変換クラスが継承すべき抽象基底クラスと
型安全性を保証するプロトコルを提供します。
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Protocol, runtime_checkable

from ..exceptions import TransformationError, ValidationError
from .types import ConfigDict, ErrorContext


class TransformationBase(ABC):
    """すべてのテキスト変換クラスの抽象基底クラス
    
    このクラスは変換処理の共通インターフェースを定義し、
    実装クラスが必須メソッドを持つことを保証します。
    """

    def __init__(self, config: ConfigDict | None = None) -> None:
        """抽象基底クラスの初期化
        
        Args:
            config: 変換設定辞書（オプション）
        """
        self._config: ConfigDict = config or {}
        self._is_initialized: bool = False
        self._error_context: ErrorContext = {}

    @abstractmethod
    def transform(self, text: str) -> str:
        """テキスト変換を実行する抽象メソッド
        
        Args:
            text: 変換対象のテキスト
            
        Returns:
            変換されたテキスト
            
        Raises:
            TransformationError: 変換処理に失敗した場合
        """
        ...

    def validate_input(self, text: str) -> bool:
        """入力テキストの妥当性を検証
        
        Args:
            text: 検証対象のテキスト
            
        Returns:
            入力が妥当な場合True
        """
        try:
            if not isinstance(text, str):
                return False
            return True
        except Exception:
            # EAFPスタイル: 例外が発生した場合は無効とみなす
            return False

    def get_config_value(self, key: str, default: Any = None) -> Any:
        """設定値を取得
        
        Args:
            key: 設定キー
            default: デフォルト値
            
        Returns:
            設定値またはデフォルト値
        """
        try:
            return self._config[key]
        except KeyError:
            # EAFPスタイル: キーが存在しない場合はデフォルトを返す
            return default

    def set_error_context(self, context: ErrorContext) -> None:
        """エラーコンテキストを設定
        
        Args:
            context: エラー情報を含む辞書
        """
        try:
            self._error_context.update(context)
        except Exception:
            # EAFPスタイル: 更新に失敗した場合は無視
            pass

    def get_error_context(self) -> ErrorContext:
        """現在のエラーコンテキストを取得
        
        Returns:
            エラーコンテキスト辞書
        """
        try:
            return self._error_context.copy()
        except Exception:
            # EAFPスタイル: コピーに失敗した場合は空辞書を返す
            return {}

    def _safe_transform(self, text: str) -> str:
        """安全な変換実行のヘルパーメソッド
        
        Args:
            text: 変換対象のテキスト
            
        Returns:
            変換されたテキスト
            
        Raises:
            ValidationError: 入力検証に失敗した場合
            TransformationError: 変換処理に失敗した場合
        """
        # EAFPスタイル: まず変換を試行し、失敗時に詳細検証
        try:
            if not self.validate_input(text):
                raise ValidationError(
                    f"入力検証に失敗: {type(text).__name__}",
                    {"input_type": type(text).__name__, "input_value": str(text)[:100]}
                )
            
            return self.transform(text)
            
        except ValidationError:
            raise
        except Exception as e:
            # 変換失敗時のエラーコンテキストを設定
            self.set_error_context({
                "transform_error": str(e),
                "error_type": type(e).__name__,
                "input_length": len(text) if isinstance(text, str) else 0
            })
            raise TransformationError(
                f"変換処理に失敗: {e}",
                self.get_error_context()
            ) from e


@runtime_checkable
class TextTransformerProtocol(Protocol):
    """テキスト変換処理のプロトコル定義
    
    このプロトコルは変換クラスが実装すべきメソッドを定義し、
    型安全性を保証します。
    """

    def transform(self, text: str) -> str:
        """テキスト変換を実行
        
        Args:
            text: 変換対象のテキスト
            
        Returns:
            変換されたテキスト
        """
        ...

    def validate_input(self, text: str) -> bool:
        """入力テキストの妥当性を検証
        
        Args:
            text: 検証対象のテキスト
            
        Returns:
            入力が妥当な場合True
        """
        ...


@runtime_checkable
class ConfigurableTransformerProtocol(TextTransformerProtocol, Protocol):
    """設定可能な変換処理のプロトコル定義
    
    このプロトコルは設定を持つ変換クラスが実装すべき
    メソッドを定義します。
    """

    def get_config_value(self, key: str, default: Any = None) -> Any:
        """設定値を取得
        
        Args:
            key: 設定キー
            default: デフォルト値
            
        Returns:
            設定値またはデフォルト値
        """
        ...

    def set_error_context(self, context: ErrorContext) -> None:
        """エラーコンテキストを設定
        
        Args:
            context: エラー情報を含む辞書
        """
        ...


class ChainableTransformationBase(TransformationBase):
    """チェイン可能な変換処理の抽象基底クラス
    
    複数の変換を連鎖して実行できる機能を提供します。
    """

    def __init__(self, config: ConfigDict | None = None) -> None:
        """チェイン可能変換クラスの初期化
        
        Args:
            config: 変換設定辞書（オプション）
        """
        super().__init__(config)
        self._chain: list[TransformationBase] = []

    def add_transformer(self, transformer: TransformationBase) -> None:
        """変換処理をチェインに追加
        
        Args:
            transformer: 追加する変換処理
        """
        try:
            if not isinstance(transformer, TransformationBase):
                raise ValidationError(
                    f"変換処理は TransformationBase を継承する必要があります: {type(transformer).__name__}"
                )
            self._chain.append(transformer)
        except Exception as e:
            # EAFPスタイル: 追加に失敗した場合はエラーを記録
            self.set_error_context({
                "chain_add_error": str(e),
                "transformer_type": type(transformer).__name__
            })
            raise

    def chain_transform(self, text: str) -> str:
        """チェインされた変換を順次実行
        
        Args:
            text: 変換対象のテキスト
            
        Returns:
            チェイン変換されたテキスト
            
        Raises:
            TransformationError: チェイン変換に失敗した場合
        """
        try:
            result: str = text
            
            for i, transformer in enumerate(self._chain):
                try:
                    result = transformer._safe_transform(result)
                except Exception as e:
                    # チェイン内の変換失敗時のコンテキスト
                    self.set_error_context({
                        "chain_position": i,
                        "transformer_type": type(transformer).__name__,
                        "chain_error": str(e)
                    })
                    raise TransformationError(
                        f"チェイン変換の第{i+1}段階で失敗: {e}",
                        self.get_error_context()
                    ) from e
                    
            return result
            
        except TransformationError:
            raise
        except Exception as e:
            raise TransformationError(
                f"チェイン変換処理に失敗: {e}",
                self.get_error_context()
            ) from e

    def clear_chain(self) -> None:
        """変換チェインをクリア"""
        try:
            self._chain.clear()
        except Exception:
            # EAFPスタイル: クリアに失敗した場合は無視
            pass

    def get_chain_length(self) -> int:
        """チェインの長さを取得
        
        Returns:
            チェインに含まれる変換処理の数
        """
        try:
            return len(self._chain)
        except Exception:
            # EAFPスタイル: 長さ取得に失敗した場合は0を返す
            return 0


def is_text_transformer(obj: Any) -> bool:
    """オブジェクトが TextTransformerProtocol を実装しているか検証
    
    Args:
        obj: 検証対象のオブジェクト
        
    Returns:
        プロトコルを実装している場合True
    """
    try:
        return isinstance(obj, TextTransformerProtocol)
    except Exception:
        # EAFPスタイル: 検証に失敗した場合はFalseを返す
        return False


def is_configurable_transformer(obj: Any) -> bool:
    """オブジェクトが ConfigurableTransformerProtocol を実装しているか検証
    
    Args:
        obj: 検証対象のオブジェクト
        
    Returns:
        プロトコルを実装している場合True
    """
    try:
        return isinstance(obj, ConfigurableTransformerProtocol)
    except Exception:
        # EAFPスタイル: 検証に失敗した場合はFalseを返す
        return False


def create_safe_transformer(
    transformer_class: type[TransformationBase], 
    config: ConfigDict | None = None
) -> TransformationBase:
    """安全な変換クラスのファクトリ関数
    
    Args:
        transformer_class: 生成する変換クラス
        config: 変換設定辞書
        
    Returns:
        生成された変換クラスのインスタンス
        
    Raises:
        ValidationError: 無効なクラスまたは設定の場合
        TransformationError: インスタンス生成に失敗した場合
    """
    try:
        # EAFPスタイル: まずインスタンス生成を試行
        if not issubclass(transformer_class, TransformationBase):
            raise ValidationError(
                f"変換クラスは TransformationBase を継承する必要があります: {transformer_class.__name__}"
            )
            
        instance = transformer_class(config)
        
        # 生成されたインスタンスの検証
        if not is_text_transformer(instance):
            raise ValidationError(
                f"生成されたインスタンスがプロトコルを実装していません: {type(instance).__name__}"
            )
            
        return instance
        
    except ValidationError:
        raise
    except Exception as e:
        raise TransformationError(
            f"変換クラスのインスタンス生成に失敗: {e}",
            {
                "class_name": transformer_class.__name__,
                "config": str(config),
                "error_type": type(e).__name__
            }
        ) from e