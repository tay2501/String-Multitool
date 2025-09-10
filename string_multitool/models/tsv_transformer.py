"""
TSV変換専用のトランスフォーマーモジュール

TextTransformationEngineから分離し、単一責任原則を適用
"""

from __future__ import annotations

import csv
import re
from collections.abc import Callable
from pathlib import Path
from typing import Any

from ..exceptions import TransformationError, ValidationError
from .constants import ERROR_CONTEXT_KEYS
from .transformation_base import TransformationBase
from .types import ConfigDict, TSVConversionOptions


class TSVTransformer(TransformationBase):
    """TSV変換専用クラス

    単一責任原則に基づき、TSVファイルを使った変換処理のみを担当
    """

    def __init__(
        self,
        tsv_file_path: str,
        options: TSVConversionOptions | None = None,
        config: ConfigDict | None = None,
    ) -> None:
        """TSV変換インスタンスを初期化

        Args:
            tsv_file_path: TSVファイルのパス
            options: TSV変換オプション（デフォルト設定を使用）
            config: 変換設定辞書（オプション）

        Raises:
            ValidationError: TSVファイルパスが無効な場合
            TransformationError: 初期化に失敗した場合
        """
        super().__init__(config)

        # 型アノテーション（PEP 526準拠）
        self._tsv_file_path: Path = Path(tsv_file_path)
        self._conversion_dict: dict[str, str] = {}
        self._input_text: str = ""
        self._output_text: str = ""

        # オプションの検証と設定
        if options is None:
            self._options: TSVConversionOptions = self._create_default_options()
        else:
            if not isinstance(options, TSVConversionOptions):
                raise ValidationError(
                    f"Invalid options type: {type(options).__name__}. Expected TSVConversionOptions.",
                    {"provided_type": type(options).__name__},
                )
            self._options = options

        # 関数ベース変換実装
        self._conversion_function = self._get_conversion_function()

        # TSVファイルの妥当性検証とロード
        self._load_tsv_rules()

    def _create_default_options(self) -> TSVConversionOptions:
        """デフォルトのTSV変換オプションを作成

        Returns:
            デフォルト設定のTSVConversionOptionsインスタンス
        """
        return TSVConversionOptions()

    def transform(self, text: str) -> str:
        """テキスト変換を実行

        関数ベース変換処理を使用して、設定に応じた適切な変換アルゴリズムを適用します。

        Args:
            text: 変換対象のテキスト

        Returns:
            変換されたテキスト

        Raises:
            TransformationError: 変換処理に失敗した場合
        """
        try:
            # 入力検証
            if not self.validate_input(text):
                raise ValidationError(
                    f"無効な入力タイプ: {type(text).__name__}",
                    {ERROR_CONTEXT_KEYS.TEXT_LENGTH: type(text).__name__},
                )

            # 入力テキストを記録
            self._input_text = text

            # 関数ベース変換処理
            result: str = str(
                self._conversion_function(text, self._conversion_dict, self._options)
            )

            # 出力テキストを記録
            self._output_text = result

            return result

        except (ValidationError, TransformationError):
            raise
        except Exception as e:
            self.set_error_context(
                {
                    ERROR_CONTEXT_KEYS.TEXT_LENGTH: (len(text) if isinstance(text, str) else 0),
                    ERROR_CONTEXT_KEYS.TSV_FILE: str(self._tsv_file_path),
                    "conversion_function": getattr(
                        self._conversion_function, "__name__", "unknown"
                    ),
                    "options": {
                        "case_insensitive": self._options.case_insensitive,
                        "preserve_original_case": self._options.preserve_original_case,
                    },
                    ERROR_CONTEXT_KEYS.ERROR_TYPE: type(e).__name__,
                }
            )
            raise TransformationError(f"TSV変換処理に失敗: {e}", self.get_error_context()) from e

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

    def get_transformation_rule(self) -> str:
        """適用される変換ルールを取得

        Returns:
            変換ルール文字列
        """
        base_rule = f"tsvtr {self._tsv_file_path}"

        if self._options.case_insensitive:
            base_rule += " --case-insensitive"

        if not self._options.preserve_original_case:
            base_rule += " --no-preserve-case"

        return base_rule

    def _load_tsv_rules(self) -> None:
        """TSVファイルから変換ルールをロード

        Raises:
            ValidationError: TSVファイルが見つからない、または無効な場合
            TransformationError: TSVファイルの読み込みに失敗した場合
        """
        try:
            # EAFP style: try to open the file directly
            with self._tsv_file_path.open("r", encoding="utf-8") as file:
                csv_reader = csv.reader(file, delimiter="\t")

                for line_num, row in enumerate(csv_reader, 1):
                    # 空行をスキップ
                    if not row or len(row) < 2:
                        continue

                    # キーと値を抽出（最初の2列のみ使用）
                    key = row[0].strip()
                    value = row[1].strip()

                    # 空キーも変換対象として登録
                    self._conversion_dict[key] = value

            # 変換辞書が空の場合は警告
            if not self._conversion_dict:
                self.set_error_context({"file_path": str(self._tsv_file_path), "rules_count": 0})
                # 空でも処理を続行（変換は行われない）

        except ValidationError:
            raise
        except Exception as e:
            self.set_error_context(
                {"file_path": str(self._tsv_file_path), "error_type": type(e).__name__}
            )
            raise TransformationError(
                f"TSVファイルの読み込みに失敗: {e}", self.get_error_context()
            ) from e

    def update_options(self, new_options: TSVConversionOptions) -> None:
        """TSV変換オプションを更新し、変換関数を再選択

        Args:
            new_options: 新しいTSV変換オプション

        Raises:
            TransformationError: オプション更新に失敗した場合
        """
        try:
            # オプションの妥当性を検証
            if not self._validate_options(new_options):
                raise ValidationError("無効なTSV変換オプション", {"options": str(new_options)})

            # オプションと変換関数を更新
            self._options = new_options
            self._conversion_function = self._get_conversion_function()

        except Exception as e:
            raise TransformationError(
                f"TSV変換オプションの更新に失敗: {e}", {"error_type": type(e).__name__}
            ) from e

    def get_current_options(self) -> TSVConversionOptions:
        """現在のTSV変換オプションを取得

        Returns:
            現在のTSV変換オプション
        """
        return self._options

    def _get_conversion_function(self) -> Callable[[str, dict[str, str], Any], str]:
        """変換オプションに基づいて適切な変換関数を返す

        Returns:
            変換関数
        """
        if self._options.case_insensitive:
            return self._case_insensitive_conversion
        else:
            return self._exact_match_conversion

    def _validate_options(self, options: TSVConversionOptions) -> bool:
        """TSV変換オプションの妥当性を検証

        Args:
            options: 検証対象のオプション

        Returns:
            妥当性の判定結果
        """
        try:
            # オプションの基本的な型チェック
            return (
                hasattr(options, "case_insensitive")
                and hasattr(options, "preserve_original_case")
                and isinstance(options.case_insensitive, bool)
                and isinstance(options.preserve_original_case, bool)
            )
        except Exception:
            return False

    def _exact_match_conversion(
        self, text: str, conversion_dict: dict[str, str], options: TSVConversionOptions
    ) -> str:
        """完全一致での変換（デフォルト）

        Args:
            text: 変換対象テキスト
            conversion_dict: 変換辞書
            options: 変換オプション

        Returns:
            変換されたテキスト
        """
        result = text
        for key, value in conversion_dict.items():
            if key == "":
                # 空文字列の場合は直接変換
                if text == "":
                    result = value
            elif key:
                # 完全一致での置換（単語境界を考慮）
                pattern = r"\b" + re.escape(key) + r"\b"
                result = re.sub(pattern, value, result)

        return result

    def _case_insensitive_conversion(
        self, text: str, conversion_dict: dict[str, str], options: TSVConversionOptions
    ) -> str:
        """大文字小文字を区別しない変換

        Args:
            text: 変換対象テキスト
            conversion_dict: 変換辞書
            options: 変換オプション

        Returns:
            変換されたテキスト
        """
        result = text
        for key, value in conversion_dict.items():
            if key == "":
                # 空文字列の場合は直接変換
                if text == "":
                    result = value
            elif key:
                # 大文字小文字を区別しない置換
                pattern = r"\b" + re.escape(key) + r"\b"

                if options.preserve_original_case:
                    # 元の文字のケースを保持
                    def replacement(match: re.Match[str]) -> str:
                        original = match.group(0)
                        if original.isupper():
                            return value.upper()
                        elif original.islower():
                            return value.lower()
                        elif original.istitle():
                            return value.capitalize()
                        else:
                            return value

                    result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)
                else:
                    # 変換値をそのまま使用
                    result = re.sub(pattern, value, result, flags=re.IGNORECASE)

        return result
