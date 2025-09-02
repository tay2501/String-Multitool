"""
TSV変換戦略の実装モジュール.

Strategy Patternを使用して、異なる変換アルゴリズムを
疎結合で実装し、高いパフォーマンスと拡張性を提供します。

Enterprise-gradeの設計原則:
- Single Responsibility Principle (SRP)
- Open/Closed Principle (OCP)
- Dependency Inversion Principle (DIP)
- Strategy Pattern for algorithm variation
- Factory Pattern for object creation
"""

from __future__ import annotations

import re
from abc import ABC, abstractmethod
from typing import Any

from ..exceptions import TransformationError, ValidationError
from .types import TSVConversionOptions, TSVConversionStrategyProtocol


class AbstractTSVConversionStrategy(ABC):
    """TSV変換戦略の抽象基底クラス.

    Template Method Patternと組み合わせて、
    共通の処理フローを提供しつつ、具体的なアルゴリズムを
    サブクラスで実装できるよう設計されています。
    """

    def __init__(self) -> None:
        """戦略インスタンスを初期化."""
        # パフォーマンス最適化のためのキャッシュ
        self._prepared_dict_cache: dict[str, dict[str, str]] = {}
        self._last_options_hash: int | None = None

    def convert_text(
        self, text: str, conversion_dict: dict[str, str], options: TSVConversionOptions
    ) -> str:
        """テキスト変換を実行（Template Method）.

        Args:
            text: 変換対象のテキスト
            conversion_dict: 変換辞書
            options: 変換オプション

        Returns:
            変換されたテキスト

        Raises:
            TransformationError: 変換処理に失敗した場合
        """
        try:
            # 入力検証
            self._validate_inputs(text, conversion_dict, options)

            # 変換辞書の前処理（キャッシュ活用）
            prepared_dict = self._get_prepared_dict(conversion_dict, options)

            # 具体的な変換処理を実行
            return self._perform_conversion(text, prepared_dict, options)

        except (ValidationError, TransformationError):
            raise
        except Exception as e:
            raise TransformationError(
                f"TSV変換戦略 {self.__class__.__name__} でエラーが発生: {e}",
                {
                    "strategy": self.__class__.__name__,
                    "text_length": len(text),
                    "dict_size": len(conversion_dict),
                    "error_type": type(e).__name__,
                },
            ) from e

    def prepare_conversion_dict(
        self, raw_dict: dict[str, str], options: TSVConversionOptions
    ) -> dict[str, str]:
        """変換辞書を前処理.

        Args:
            raw_dict: 元の変換辞書
            options: 変換オプション

        Returns:
            前処理済みの変換辞書
        """
        return self._prepare_dict_internal(raw_dict, options)

    def _validate_inputs(
        self, text: str, conversion_dict: dict[str, str], options: TSVConversionOptions
    ) -> None:
        """入力パラメータの検証.

        Args:
            text: 変換対象のテキスト
            conversion_dict: 変換辞書
            options: 変換オプション

        Raises:
            ValidationError: 入力が無効な場合
        """
        if not isinstance(text, str):
            raise ValidationError(
                f"無効な入力テキスト型: {type(text).__name__}",
                {"input_type": type(text).__name__},
            )

        if not isinstance(conversion_dict, dict):
            raise ValidationError(
                f"無効な変換辞書型: {type(conversion_dict).__name__}",
                {"dict_type": type(conversion_dict).__name__},
            )

        if not isinstance(options, TSVConversionOptions):
            raise ValidationError(
                f"無効なオプション型: {type(options).__name__}",
                {"options_type": type(options).__name__},
            )

    def _get_prepared_dict(
        self, conversion_dict: dict[str, str], options: TSVConversionOptions
    ) -> dict[str, str]:
        """前処理済み変換辞書を取得（キャッシュ対応）.

        Args:
            conversion_dict: 元の変換辞書
            options: 変換オプション

        Returns:
            前処理済みの変換辞書
        """
        # オプションのハッシュ値でキャッシュ判定
        options_hash = hash(
            (
                options.case_insensitive,
                options.preserve_original_case,
                options.match_whole_words_only,
                options.enable_regex_patterns,
            )
        )

        cache_key = f"{id(conversion_dict)}_{options_hash}"

        # キャッシュヒット確認
        if cache_key in self._prepared_dict_cache:
            return self._prepared_dict_cache[cache_key]

        # 新規作成してキャッシュ
        prepared_dict = self._prepare_dict_internal(conversion_dict, options)
        self._prepared_dict_cache[cache_key] = prepared_dict

        return prepared_dict

    @abstractmethod
    def _prepare_dict_internal(
        self, conversion_dict: dict[str, str], options: TSVConversionOptions
    ) -> dict[str, str]:
        """変換辞書の内部前処理（サブクラスで実装）.

        Args:
            conversion_dict: 元の変換辞書
            options: 変換オプション

        Returns:
            前処理済みの変換辞書
        """
        pass

    @abstractmethod
    def _perform_conversion(
        self, text: str, prepared_dict: dict[str, str], options: TSVConversionOptions
    ) -> str:
        """具体的な変換処理を実行（サブクラスで実装）.

        Args:
            text: 変換対象のテキスト
            prepared_dict: 前処理済み変換辞書
            options: 変換オプション

        Returns:
            変換されたテキスト
        """
        pass


class CaseSensitiveConversionStrategy(AbstractTSVConversionStrategy):
    """大文字小文字を区別するTSV変換戦略.

    従来の動作と完全に互換性を保ちつつ、
    新しいアーキテクチャに対応したstraetgy実装です。
    """

    def _prepare_dict_internal(
        self, conversion_dict: dict[str, str], options: TSVConversionOptions
    ) -> dict[str, str]:
        """変換辞書をそのまま返す（大文字小文字区別）.

        Args:
            conversion_dict: 元の変換辞書
            options: 変換オプション（使用しない）

        Returns:
            元の変換辞書（変更なし）
        """
        return conversion_dict.copy()

    def _perform_conversion(
        self, text: str, prepared_dict: dict[str, str], options: TSVConversionOptions
    ) -> str:
        """大文字小文字を区別した高速変換処理.

        Args:
            text: 変換対象のテキスト
            prepared_dict: 前処理済み変換辞書
            options: 変換オプション

        Returns:
            変換されたテキスト
        """
        if not prepared_dict:
            return text

        result = text

        # パフォーマンス最適化：最長マッチ優先でソート
        sorted_keys = sorted(prepared_dict.keys(), key=len, reverse=True)

        # 効率的な文字列置換
        for key in sorted_keys:
            if key in result:
                result = result.replace(key, prepared_dict[key])

        return result


class CaseInsensitiveConversionStrategy(AbstractTSVConversionStrategy):
    """大文字小文字を無視するTSV変換戦略.

    高度なアルゴリズムにより、大文字小文字を無視した
    効率的なマッチングと、元の大文字小文字の保持を実現します。
    """

    def _prepare_dict_internal(
        self, conversion_dict: dict[str, str], options: TSVConversionOptions
    ) -> dict[str, str]:
        """大文字小文字無視用の変換辞書を準備.

        Args:
            conversion_dict: 元の変換辞書
            options: 変換オプション

        Returns:
            小文字キーの変換辞書
        """
        # すべてのキーを小文字化した辞書を作成
        lowercase_dict = {}
        for key, value in conversion_dict.items():
            lowercase_key = key.lower()
            lowercase_dict[lowercase_key] = value

        return lowercase_dict

    def _perform_conversion(
        self, text: str, prepared_dict: dict[str, str], options: TSVConversionOptions
    ) -> str:
        """大文字小文字を無視した高度な変換処理.

        Args:
            text: 変換対象のテキスト
            prepared_dict: 前処理済み変換辞書（小文字キー）
            options: 変換オプション

        Returns:
            変換されたテキスト
        """
        if not prepared_dict:
            return text

        result = text

        # パフォーマンス最適化：最長マッチ優先でソート
        sorted_keys = sorted(prepared_dict.keys(), key=len, reverse=True)

        # 大文字小文字を無視した効率的な置換
        for lowercase_key in sorted_keys:
            replacement_value = prepared_dict[lowercase_key]

            # 大文字小文字を無視したマッチングを実行
            result = self._replace_case_insensitive(
                result, lowercase_key, replacement_value, options
            )

        return result

    def _replace_case_insensitive(
        self,
        text: str,
        lowercase_pattern: str,
        replacement: str,
        options: TSVConversionOptions,
    ) -> str:
        """大文字小文字を無視した文字列置換 (ケース保持機能付き).

        Args:
            text: 対象テキスト
            lowercase_pattern: 小文字のパターン
            replacement: 置換文字列
            options: 変換オプション

        Returns:
            置換後のテキスト
        """
        # 正規表現を使用して大文字小文字を無視したマッチング
        pattern = re.escape(lowercase_pattern)
        flags = re.IGNORECASE

        def preserve_case_replace(match):
            """元のケースを保持した置換関数."""
            original = match.group(0)

            # オリジナルケース保持が無効の場合、置換文字列をそのまま返す
            if not options.preserve_original_case:
                return replacement

            # 元のケースパターンを保持（より精密な判定）
            if original.isupper():
                return replacement.upper()
            elif original.istitle():
                return replacement.title()
            elif original.islower():
                return replacement.lower()
            elif original[0].isupper():
                # 最初が大文字の場合はタイトルケースにする
                return replacement.title()
            else:
                # その他の場合は小文字
                return replacement.lower()

        return re.sub(pattern, preserve_case_replace, text, flags=flags)


class TSVConversionStrategyFactory:
    """TSV変換戦略のファクトリークラス.

    Factory Patternにより、実行時に適切な変換戦略を
    動的に選択・生成します。将来の拡張にも対応可能な設計です。
    """

    @staticmethod
    def create_strategy(options: TSVConversionOptions) -> TSVConversionStrategyProtocol:
        """変換オプションに基づいて適切な戦略を作成.

        Args:
            options: TSV変換オプション

        Returns:
            適切な変換戦略インスタンス

        Raises:
            TransformationError: 不明なオプション組み合わせの場合
        """
        if options.case_insensitive:
            return CaseInsensitiveConversionStrategy()
        else:
            return CaseSensitiveConversionStrategy()

    @staticmethod
    def get_available_strategies() -> list[str]:
        """利用可能な戦略の一覧を取得.

        Returns:
            戦略名のリスト
        """
        return ["CaseSensitiveConversionStrategy", "CaseInsensitiveConversionStrategy"]

    @staticmethod
    def validate_options(options: TSVConversionOptions) -> bool:
        """オプションの有効性を検証.

        Args:
            options: 検証するオプション

        Returns:
            オプションが有効かどうか
        """
        try:
            # 基本的なオプション検証は型アノテーションにより保証される

            # 論理的整合性の検証
            if options.preserve_original_case and not options.case_insensitive:
                # preserve_original_case は case_insensitive が有効な時のみ意味を持つ
                # ただし、無効ではないので警告程度
                return True  # Warning condition but still valid

            return True

        except Exception:
            return False
