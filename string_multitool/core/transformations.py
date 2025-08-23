"""
Text transformation engine for String_Multitool.

This module provides the core text transformation functionality with
configurable rules and comprehensive error handling.
"""

from __future__ import annotations

import base64
import hashlib
import json
import re
from pathlib import Path
from typing import Any

from ..exceptions import TransformationError, ValidationError
from .transformation_base import TransformationBase
from .types import (
    ConfigManagerProtocol,
    ConfigurableComponent,
    CryptoManagerProtocol,
    TransformationEngineProtocol,
    TransformationRule,
    TransformationRuleType,
)


class TSVTransformation(TransformationBase):
    """TSVファイルを使用したテキスト変換クラス
    
    Enterprise-grade疎結合設計により、TSV変換ルールを独立して管理し、
    Strategy Patternを活用した高いパフォーマンスと拡張性を提供します。
    
    主要な設計パターン:
    - Strategy Pattern: 変換アルゴリズムの動的選択
    - Factory Pattern: 戦略インスタンスの生成
    - Template Method Pattern: 共通処理フローの定義
    """

    def __init__(
        self, 
        tsv_file_path: str, 
        options: "TSVConversionOptions | None" = None,
        config: dict[str, Any] | None = None
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
            self._options: "TSVConversionOptions" = self._create_default_options()
        else:
            from .types import TSVConversionOptions
            if not isinstance(options, TSVConversionOptions):
                raise ValidationError(
                    f"Invalid options type: {type(options).__name__}. Expected TSVConversionOptions.",
                    {"provided_type": type(options).__name__}
                )
            self._options = options
        
        self._transformation_rule: str = self._build_transformation_rule()
        
        # Strategy Pattern: 変換戦略を動的に選択
        from .tsv_conversion_strategies import TSVConversionStrategyFactory
        self._conversion_strategy = TSVConversionStrategyFactory.create_strategy(self._options)
        
        # TSVファイルの妥当性検証とロード
        self._load_tsv_rules()
    
    def _create_default_options(self) -> "TSVConversionOptions":
        """デフォルトのTSV変換オプションを作成
        
        Returns:
            デフォルト設定のTSVConversionOptionsインスタンス
        """
        from .types import TSVConversionOptions
        return TSVConversionOptions()
    
    def _build_transformation_rule(self) -> str:
        """変換ルール文字列を構築
        
        Returns:
            オプションを含む変換ルール文字列
        """
        base_rule = f"convertbytsv {self._tsv_file_path}"
        
        if self._options.case_insensitive:
            base_rule += " --case-insensitive"
        
        if not self._options.preserve_original_case:
            base_rule += " --no-preserve-case"
            
        return base_rule

    def transform(self, text: str) -> str:
        """テキスト変換を実行
        
        Strategy Patternを使用して、設定に応じた適切な変換アルゴリズムを適用します。
        
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
                    {"input_type": type(text).__name__}
                )
            
            # 入力テキストを記録
            self._input_text = text
            
            # Strategy Patternによる高度な変換処理
            result = self._conversion_strategy.convert_text(
                text, 
                self._conversion_dict, 
                self._options
            )
            
            # 出力テキストを記録
            self._output_text = result
            
            return result
            
        except (ValidationError, TransformationError):
            raise
        except Exception as e:
            self.set_error_context({
                "text_length": len(text) if isinstance(text, str) else 0,
                "tsv_file": str(self._tsv_file_path),
                "strategy": self._conversion_strategy.__class__.__name__,
                "options": {
                    "case_insensitive": self._options.case_insensitive,
                    "preserve_original_case": self._options.preserve_original_case
                },
                "error_type": type(e).__name__
            })
            raise TransformationError(
                f"TSV変換処理に失敗: {e}",
                self.get_error_context()
            ) from e

    def get_transformation_rule(self) -> str:
        """適用される変換ルールを取得
        
        Returns:
            変換ルール文字列
        """
        return self._transformation_rule

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

    def _load_tsv_rules(self) -> None:
        """TSVファイルから変換ルールをロード
        
        Raises:
            ValidationError: TSVファイルが見つからない、または無効な場合
            TransformationError: TSVファイルの読み込みに失敗した場合
        """
        import csv
        
        try:
            # ファイル存在確認（EAFPスタイル）
            if not self._tsv_file_path.exists():
                raise ValidationError(
                    f"TSVファイルが見つかりません: {self._tsv_file_path}",
                    {"file_path": str(self._tsv_file_path)}
                )
            
            # TSVファイル読み込み
            with self._tsv_file_path.open('r', encoding='utf-8') as file:
                csv_reader = csv.reader(file, delimiter='\t')
                
                for line_num, row in enumerate(csv_reader, 1):
                    # 空行をスキップ
                    if not row or len(row) < 2:
                        continue
                    
                    # キーと値を抽出（最初の2列のみ使用）
                    key = row[0].strip()
                    value = row[1].strip()
                    
                    if key:  # 空キーは無視
                        self._conversion_dict[key] = value
            
            # 変換辞書が空の場合は警告
            if not self._conversion_dict:
                self.set_error_context({
                    "file_path": str(self._tsv_file_path),
                    "rules_count": 0
                })
                # 空でも処理を続行（変換は行われない）
                
        except ValidationError:
            raise
        except Exception as e:
            self.set_error_context({
                "file_path": str(self._tsv_file_path),
                "error_type": type(e).__name__
            })
            raise TransformationError(
                f"TSVファイルの読み込みに失敗: {e}",
                self.get_error_context()
            ) from e

    def update_options(self, new_options: "TSVConversionOptions") -> None:
        """TSV変換オプションを更新し、戦略を再選択
        
        Args:
            new_options: 新しいTSV変換オプション
            
        Raises:
            TransformationError: オプション更新に失敗した場合
        """
        try:
            from .tsv_conversion_strategies import TSVConversionStrategyFactory
            
            # オプションの妥当性を検証
            if not TSVConversionStrategyFactory.validate_options(new_options):
                raise ValidationError(
                    "無効なTSV変換オプション",
                    {"options": str(new_options)}
                )
            
            # オプションと戦略を更新
            self._options = new_options
            self._conversion_strategy = TSVConversionStrategyFactory.create_strategy(new_options)
            self._transformation_rule = self._build_transformation_rule()
            
        except Exception as e:
            raise TransformationError(
                f"TSV変換オプションの更新に失敗: {e}",
                {"error_type": type(e).__name__}
            ) from e
    
    def get_current_options(self) -> "TSVConversionOptions":
        """現在のTSV変換オプションを取得
        
        Returns:
            現在のTSV変換オプション
        """
        return self._options


class TextTransformationEngine(
    ConfigurableComponent[dict[str, Any]], TransformationBase
):
    """Advanced text transformation engine with configurable rules.

    This class provides a comprehensive set of text transformation operations
    with support for sequential rule application and custom rule definitions.
    """

    def __init__(self, config_manager: ConfigManagerProtocol) -> None:
        """Initialize transformation engine.

        Args:
            config_manager: Configuration manager instance

        Raises:
            TransformationError: If initialization fails
        """
        try:
            transformation_config = config_manager.load_transformation_rules()
            ConfigurableComponent.__init__(self, transformation_config)
            TransformationBase.__init__(self, transformation_config)

            # Instance variable annotations following PEP 526
            self.config_manager: ConfigManagerProtocol = config_manager
            self.crypto_manager: CryptoManagerProtocol | None = None
            self._available_rules: dict[str, TransformationRule] | None = None

        except Exception as e:
            raise TransformationError(
                f"Failed to initialize transformation engine: {e}",
                {"error_type": type(e).__name__},
            ) from e

    def set_crypto_manager(self, crypto_manager: CryptoManagerProtocol) -> None:
        """Set the cryptography manager for encryption/decryption operations.

        Args:
            crypto_manager: Cryptography manager instance
        """
        self.crypto_manager = crypto_manager

    def transform(self, text: str) -> str:
        """基底クラスで要求される変換メソッド（単一変換用）

        Args:
            text: 変換対象テキスト

        Returns:
            変換されたテキスト
        """
        # デフォルトではそのまま返す（サブクラスでオーバーライド）
        return text

    def apply_transformations(self, text: str, rule_string: str) -> str:
        """Apply transformation rules to text.

        Args:
            text: Input text to transform
            rule_string: Rule string (e.g., '/t/l/u')

        Returns:
            Transformed text

        Raises:
            ValidationError: If input parameters are invalid
            TransformationError: If transformation fails
        """
        # EAFPスタイル：まず変換を試行し、失敗時に詳細検証
        try:
            # 基本的な入力検証
            if not self.validate_input(text):
                raise ValidationError(
                    f"Text must be a string, got {type(text).__name__}",
                    {"text_type": type(text).__name__},
                )

            if not isinstance(rule_string, str):
                raise ValidationError(
                    f"Rule string must be a string, got {type(rule_string).__name__}",
                    {"rule_type": type(rule_string).__name__},
                )

            if not rule_string.strip():
                raise ValidationError("Rule string cannot be empty")

            if not rule_string.startswith("/"):
                raise ValidationError(
                    "Rules must start with '/'", {"rule_string": rule_string}
                )

            # Parse and apply rules sequentially
            parsed_rules = self.parse_rule_string(rule_string)
            result = text

            for rule_name, args in parsed_rules:
                result = self._apply_single_rule(result, rule_name, args)

            return result

        except (ValidationError, TransformationError):
            raise
        except Exception as e:
            # エラーコンテキストを設定
            self.set_error_context(
                {
                    "rule_string": rule_string,
                    "text_length": len(text) if isinstance(text, str) else 0,
                    "error_type": type(e).__name__,
                }
            )
            raise TransformationError(
                f"Unexpected error during transformation: {e}", self.get_error_context()
            ) from e

    def parse_rule_string(self, rule_string: str) -> list[tuple[str, list[str]]]:
        """Parse rule string into list of (rule, arguments) tuples.

        Args:
            rule_string: Rule string to parse (e.g., '/t/l/r "old" "new"')

        Returns:
            List of (rule_name, arguments) tuples

        Raises:
            ValidationError: If rule string format is invalid
        """
        try:
            if not rule_string.startswith("/"):
                raise ValidationError(
                    "Rule string must start with '/'", {"rule_string": rule_string}
                )

            # Remove leading slash and split by slash
            rules_part: str = rule_string[1:]
            if not rules_part:
                raise ValidationError("Empty rule string after '/'")

            # Handle quoted arguments
            parts: list[str] = self._parse_with_quotes(rules_part)
            parsed_rules: list[tuple[str, list[str]]] = []
            current_rule: str | None = None
            current_args: list[str] = []

            for part in parts:
                if part.startswith("/"):
                    # New rule found, save previous if exists
                    if current_rule is not None:
                        parsed_rules.append((current_rule, current_args))
                    current_rule = part[1:]  # Remove leading slash
                    current_args = []
                elif current_rule is not None:
                    # Argument for current rule
                    current_args.append(part)
                else:
                    # First part should be a rule
                    current_rule = part
                    current_args = []

            # Add the last rule
            if current_rule is not None:
                parsed_rules.append((current_rule, current_args))

            if not parsed_rules:
                raise ValidationError("No valid rules found in rule string")

            return parsed_rules

        except ValidationError:
            raise
        except Exception as e:
            raise ValidationError(
                f"Failed to parse rule string: {e}",
                {"rule_string": rule_string, "error_type": type(e).__name__},
            ) from e

    def get_available_rules(self) -> dict[str, TransformationRule]:
        """Get all available transformation rules.

        Returns:
            Dictionary mapping rule names to TransformationRule objects
        """
        if self._available_rules is None:
            self._available_rules = self._build_available_rules()

        return self._available_rules

    def _apply_single_rule(self, text: str, rule_name: str, args: list[str]) -> str:
        """Apply a single transformation rule to text.

        Args:
            text: Input text
            rule_name: Name of the rule to apply
            args: Arguments for the rule

        Returns:
            Transformed text

        Raises:
            TransformationError: If rule application fails
        """
        # EAFPスタイル：まずルール適用を試行し、失敗時に詳細検証
        try:
            available_rules = self.get_available_rules()

            # ルールの存在確認
            rule = available_rules[rule_name]  # KeyErrorが発生する可能性

            # Handle rules that require arguments
            if rule.requires_args:
                if not args and rule.default_args:
                    args = rule.default_args
                elif not args:
                    raise TransformationError(
                        f"Rule '{rule_name}' requires arguments",
                        {"rule_name": rule_name, "required_args": True},
                    )

            # Apply the transformation
            if rule_name in ["enc", "dec"]:
                return self._apply_crypto_rule(text, rule_name)
            elif args and rule.requires_args:
                return self._apply_rule_with_args(text, rule_name, args)
            elif args and not rule.requires_args:
                # Rule doesn't require arguments, ignore provided arguments
                return rule.function(text)
            else:
                return rule.function(text)

        except KeyError:
            # ルールが見つからない場合のEAFP処理
            available_rules = self.get_available_rules()
            raise TransformationError(
                f"Unknown rule: {rule_name}",
                {
                    "rule_name": rule_name,
                    "available_rules": list(available_rules.keys()),
                },
            )
        except TransformationError:
            raise
        except Exception as e:
            # エラーコンテキストを設定
            self.set_error_context(
                {
                    "rule_name": rule_name,
                    "args": args,
                    "text_length": len(text),
                    "error_type": type(e).__name__,
                }
            )
            raise TransformationError(
                f"Failed to apply rule '{rule_name}': {e}", self.get_error_context()
            ) from e

    def _apply_crypto_rule(self, text: str, rule_name: str) -> str:
        """Apply encryption or decryption rule.

        Args:
            text: Input text
            rule_name: 'enc' or 'dec'

        Returns:
            Encrypted or decrypted text

        Raises:
            TransformationError: If crypto operation fails
        """
        # EAFPスタイル：まず暗号化操作を試行
        try:
            # crypto_managerの存在を確認せずに直接使用を試みる
            if rule_name == "enc":
                if self.crypto_manager is None:
                    raise TransformationError(
                        "Cryptography manager not available for encryption",
                        {"rule": rule_name},
                    )
                print("Using existing RSA key pair")
                result = self.crypto_manager.encrypt_text(text)
                print(
                    f"Text encrypted successfully (AES-256+RSA-4096, {len(text)} bytes)"
                )
                return result
            elif rule_name == "dec":
                if self.crypto_manager is None:
                    raise TransformationError(
                        "Cryptography manager not available for decryption",
                        {"rule": rule_name},
                    )
                print("Using existing RSA key pair")
                result = self.crypto_manager.decrypt_text(text)
                print(
                    f"Text decrypted successfully (AES-256+RSA-4096, {len(result)} chars)"
                )
                return result
            else:
                raise TransformationError(f"Unknown crypto rule: {rule_name}")

        except AttributeError:
            # crypto_managerがない場合のEAFP処理
            raise TransformationError(
                "Cryptography manager not available for encryption/decryption",
                {"rule_name": rule_name},
            )
        except Exception as e:
            # エラーコンテキストを設定
            self.set_error_context(
                {
                    "rule_name": rule_name,
                    "error_type": type(e).__name__,
                    "text_length": len(text),
                }
            )
            raise TransformationError(
                f"Cryptography operation failed: {e}", self.get_error_context()
            ) from e

    def _apply_rule_with_args(self, text: str, rule_name: str, args: list[str]) -> str:
        """Apply transformation rule that requires arguments.

        Args:
            text: Input text
            rule_name: Name of the rule
            args: Arguments for the rule

        Returns:
            Transformed text
        """
        # EAFPスタイル：まず引数を使用し、不足時にエラー処理
        try:
            if rule_name == "r":  # Replace
                if len(args) >= 2:
                    return text.replace(args[0], args[1])
                elif len(args) == 1:
                    return text.replace(args[0], "")
                else:
                    # 引数不足の場合
                    raise TransformationError(
                        "Replace rule requires at least 1 argument",
                        {"rule_name": rule_name, "args_count": len(args)},
                    )

            elif rule_name == "S":  # Slugify
                separator = args[0] if args else "-"
                # Convert to lowercase, replace non-alphanumeric with separator
                result = re.sub(r"[^a-zA-Z0-9]+", separator, text.lower())
                return result.strip(separator)
            elif rule_name == "convertbytsv":  # TSV Conversion
                return self._apply_tsv_conversion(text, args)
            else:
                raise TransformationError(
                    f"Unknown rule with arguments: {rule_name}",
                    {"rule_name": rule_name},
                )

        except TransformationError:
            raise
        except Exception as e:
            # エラーコンテキストを設定
            self.set_error_context(
                {"rule_name": rule_name, "args": args, "error_type": type(e).__name__}
            )
            raise TransformationError(
                f"Failed to apply rule '{rule_name}' with arguments: {e}",
                self.get_error_context(),
            ) from e

    def _parse_with_quotes(self, text: str) -> list[str]:
        """Parse text respecting quoted strings and space-separated arguments.
        
        Enhanced to handle space-separated arguments for POSIX-compliant parsing:
        - /convertbytsv --case-insensitive technical_terms.tsv
        - /r 'old text' 'new text'

        Args:
            text: Text to parse

        Returns:
            List of parsed parts
        """
        parts: list[str] = []
        current_part: str = ""
        in_quotes: bool = False
        quote_char: str | None = None
        i: int = 0

        # EAFPスタイル：文字アクセスを直接試行
        try:
            while i < len(text):
                char: str = text[i]  # IndexErrorが発生する可能性

                if not in_quotes:
                    if char in ['"', "'"]:
                        in_quotes = True
                        quote_char = char
                    elif char == "/":
                        # 新しいルールの開始
                        if current_part:
                            parts.append(current_part)
                            current_part = ""
                        current_part = "/"
                    elif char == " ":
                        # 空白で区切られた引数
                        if current_part:
                            parts.append(current_part)
                            current_part = ""
                        # 連続する空白をスキップ
                        while i + 1 < len(text) and text[i + 1] == " ":
                            i += 1
                    else:
                        current_part += char
                else:
                    if char == quote_char:
                        in_quotes = False
                        quote_char = None
                    else:
                        current_part += char

                i += 1

            if current_part:
                parts.append(current_part)

            return parts

        except IndexError:
            # インデックスエラー時は現在までのパーツを返す
            if current_part:
                parts.append(current_part)
            return parts
        except Exception:
            # その他のエラー時は空リストを返す
            return []

    def _build_available_rules(self) -> dict[str, TransformationRule]:
        """Build dictionary of available transformation rules."""
        rules = {}

        # Basic transformations
        rules.update(
            {
                "uh": TransformationRule(
                    name="Underbar to Hyphen",
                    description="Convert underscores to hyphens",
                    example="TBL_CHA1 → TBL-CHA1",
                    function=lambda text: text.replace("_", "-"),
                    rule_type=TransformationRuleType.BASIC,
                ),
                "hu": TransformationRule(
                    name="Hyphen to Underbar",
                    description="Convert hyphens to underscores",
                    example="TBL-CHA1 → TBL_CHA1",
                    function=lambda text: text.replace("-", "_"),
                    rule_type=TransformationRuleType.BASIC,
                ),
                "fh": TransformationRule(
                    name="Full-width to Half-width",
                    description="Convert full-width characters to half-width",
                    example="ＴＢＬ－ＣＨＡ１ → TBL-CHA1",
                    function=self._full_to_half_width,
                    rule_type=TransformationRuleType.BASIC,
                ),
                "hf": TransformationRule(
                    name="Half-width to Full-width",
                    description="Convert half-width characters to full-width",
                    example="TBL-CHA1 → ＴＢＬ－ＣＨＡ１",
                    function=self._half_to_full_width,
                    rule_type=TransformationRuleType.BASIC,
                ),
            }
        )

        # Case transformations
        rules.update(
            {
                "l": TransformationRule(
                    name="Lowercase",
                    description="Convert to lowercase",
                    example="HELLO WORLD → hello world",
                    function=str.lower,
                    rule_type=TransformationRuleType.CASE,
                ),
                "u": TransformationRule(
                    name="Uppercase",
                    description="Convert to uppercase",
                    example="hello world → HELLO WORLD",
                    function=str.upper,
                    rule_type=TransformationRuleType.CASE,
                ),
                "p": TransformationRule(
                    name="PascalCase",
                    description="Convert to PascalCase",
                    example="the quick brown fox → TheQuickBrownFox",
                    function=self._to_pascal_case,
                    rule_type=TransformationRuleType.CASE,
                ),
                "c": TransformationRule(
                    name="camelCase",
                    description="Convert to camelCase",
                    example="is error state → isErrorState",
                    function=self._to_camel_case,
                    rule_type=TransformationRuleType.CASE,
                ),
                "s": TransformationRule(
                    name="snake_case",
                    description="Convert to snake_case",
                    example="is error state → is_error_state",
                    function=self._to_snake_case,
                    rule_type=TransformationRuleType.CASE,
                ),
                "a": TransformationRule(
                    name="Capitalize",
                    description="Capitalize first letter of each word",
                    example="hello world → Hello World",
                    function=str.title,
                    rule_type=TransformationRuleType.CASE,
                ),
            }
        )

        # String operations
        rules.update(
            {
                "t": TransformationRule(
                    name="Trim",
                    description="Remove leading and trailing whitespace",
                    example="  hello world   → hello world",
                    function=str.strip,
                    rule_type=TransformationRuleType.STRING_OPS,
                ),
                "R": TransformationRule(
                    name="Reverse",
                    description="Reverse the string",
                    example="hello → olleh",
                    function=lambda text: text[::-1],
                    rule_type=TransformationRuleType.STRING_OPS,
                ),
                "si": TransformationRule(
                    name="SQL IN Clause",
                    description="Format as SQL IN clause",
                    example="A0001\\r\\nA0002\\r\\nA0003 → 'A0001',\\r\\n'A0002',\\r\\n'A0003'",
                    function=self._to_sql_in_clause,
                    rule_type=TransformationRuleType.STRING_OPS,
                ),
                "dlb": TransformationRule(
                    name="Delete Line Breaks",
                    description="Remove all line breaks",
                    example="A0001\\r\\nA0002\\r\\nA0003 → A0001A0002A0003",
                    function=lambda text: text.replace("\r\n", "")
                    .replace("\n", "")
                    .replace("\r", ""),
                    rule_type=TransformationRuleType.STRING_OPS,
                ),
            }
        )

        # Encryption operations
        rules.update(
            {
                "enc": TransformationRule(
                    name="RSA Encrypt",
                    description="Encrypt text using RSA",
                    example="Secret message → Base64 encrypted text",
                    function=lambda text: text,  # Handled specially
                    rule_type=TransformationRuleType.ENCRYPTION,
                ),
                "dec": TransformationRule(
                    name="RSA Decrypt",
                    description="Decrypt text using RSA",
                    example="Base64 encrypted text → Secret message",
                    function=lambda text: text,  # Handled specially
                    rule_type=TransformationRuleType.ENCRYPTION,
                ),
            }
        )

        # Hash operations
        rules.update(
            {
                "hash": TransformationRule(
                    name="SHA-256 Hash",
                    description="Generate SHA-256 hash of input text",
                    example="password → 5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8",
                    function=self._sha256_hash,
                    rule_type=TransformationRuleType.ADVANCED,
                ),
            }
        )

        # Encoding operations
        rules.update(
            {
                "base64enc": TransformationRule(
                    name="Base64 Encode",
                    description="Encode text to Base64",
                    example="hello → aGVsbG8=",
                    function=self._base64_encode,
                    rule_type=TransformationRuleType.ADVANCED,
                ),
                "base64dec": TransformationRule(
                    name="Base64 Decode",
                    description="Decode Base64 to text",
                    example="aGVsbG8= → hello",
                    function=self._base64_decode,
                    rule_type=TransformationRuleType.ADVANCED,
                ),
            }
        )

        # Formatting operations
        rules.update(
            {
                "formatjson": TransformationRule(
                    name="Format JSON",
                    description="Format JSON with proper indentation",
                    example='{"a":1,"b":2} → formatted JSON',
                    function=self._format_json,
                    rule_type=TransformationRuleType.ADVANCED,
                ),
            }
        )

        # Advanced rules with arguments
        rules.update(
            {
                "r": TransformationRule(
                    name="Replace",
                    description="Replace text",
                    example="/r 'old' 'new' → old text → new text",
                    function=lambda text: text,  # Handled specially
                    requires_args=True,
                    rule_type=TransformationRuleType.ADVANCED,
                ),
                "S": TransformationRule(
                    name="Slugify",
                    description="Convert to URL-friendly slug",
                    example="/S '+' → http://foo.bar → http+foo+bar",
                    function=lambda text: text,  # Handled specially
                    requires_args=True,
                    default_args=["-"],
                    rule_type=TransformationRuleType.ADVANCED,
                ),
                "convertbytsv": TransformationRule(
                    name="Convert by TSV",
                    description="Convert text using TSV file rules",
                    example="/convertbytsv technical_terms.tsv → API → Application Programming Interface",
                    function=lambda text: text,  # Handled specially
                    requires_args=True,
                    rule_type=TransformationRuleType.ADVANCED,
                ),
            }
        )

        return rules

    # Helper methods for transformations
    def _full_to_half_width(self, text: str) -> str:
        """Convert full-width characters to half-width."""
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

    def _half_to_full_width(self, text: str) -> str:
        """Convert half-width characters to full-width."""
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

    def _to_pascal_case(self, text: str) -> str:
        """Convert text to PascalCase."""
        words = re.findall(r"\w+", text)
        result: str = "".join(word.capitalize() for word in words)
        return result

    def _to_camel_case(self, text: str) -> str:
        """Convert text to camelCase."""
        words = re.findall(r"\w+", text)
        if not words:
            return text
        first_word: str = words[0].lower()
        capitalized_words: str = "".join(word.capitalize() for word in words[1:])
        return first_word + capitalized_words

    def _to_snake_case(self, text: str) -> str:
        """Convert text to snake_case."""
        words = re.findall(r"\w+", text)
        return "_".join(word.lower() for word in words)

    def _to_sql_in_clause(self, text: str) -> str:
        """Convert text to SQL IN clause format."""
        lines = text.replace("\r\n", "\n").replace("\r", "\n").split("\n")
        quoted_lines = [f"'{line.strip()}'" for line in lines if line.strip()]
        return ",\r\n".join(quoted_lines)

    def _sha256_hash(self, text: str) -> str:
        """Generate SHA-256 hash of input text."""
        return hashlib.sha256(text.encode("utf-8")).hexdigest()

    def _base64_encode(self, text: str) -> str:
        """Encode text to Base64."""
        # EAFPスタイル：まずエンコードを試行
        try:
            encoded_bytes = base64.b64encode(text.encode("utf-8"))
            return encoded_bytes.decode("ascii")
        except UnicodeEncodeError as e:
            # UTF-8エンコードエラーの場合
            self.set_error_context(
                {"encoding_error": str(e), "text_preview": text[:50]}
            )
            raise TransformationError(
                f"Text encoding failed: {e}", self.get_error_context()
            ) from e
        except Exception as e:
            # その他のエラー
            self.set_error_context({"error_type": type(e).__name__})
            raise TransformationError(
                f"Base64 encoding failed: {e}", self.get_error_context()
            ) from e

    def _base64_decode(self, text: str) -> str:
        """Decode Base64 to text."""
        # EAFPスタイル：まずデコードを試行
        try:
            # Remove whitespace and padding if needed
            clean_text = text.strip()
            decoded_bytes = base64.b64decode(clean_text)
            return decoded_bytes.decode("utf-8")
        except UnicodeDecodeError as e:
            # UTF-8デコードエラーの場合
            self.set_error_context({"unicode_error": str(e)})
            raise TransformationError(
                f"Text decoding failed: {e}", self.get_error_context()
            ) from e
        except Exception as e:
            # Base64デコードエラーまたはその他のエラー
            self.set_error_context({"decode_error": str(e), "text_preview": text[:50]})
            raise TransformationError(
                f"Base64 decoding failed: {e}", self.get_error_context()
            ) from e

    def _format_json(self, text: str) -> str:
        """Format JSON with proper indentation."""
        # EAFPスタイル：まずJSONパーシングを試行
        try:
            # Parse JSON
            parsed = json.loads(text)
            # Format with 2-space indentation
            return json.dumps(parsed, indent=2, ensure_ascii=False)
        except json.JSONDecodeError as e:
            # JSONパーシングエラーの場合
            self.set_error_context(
                {
                    "json_error": str(e),
                    "error_line": getattr(e, "lineno", "unknown"),
                    "error_pos": getattr(e, "pos", "unknown"),
                    "text_preview": text[:100],
                }
            )
            raise TransformationError(
                f"Invalid JSON format: {e}", self.get_error_context()
            ) from e
        except Exception as e:
            # その他のエラー
            self.set_error_context({"error_type": type(e).__name__})
            raise TransformationError(
                f"JSON formatting failed: {e}", self.get_error_context()
            ) from e

    def validate_rule_string(self, rule_string: str) -> tuple[bool, str | None]:
        """Validate rule string format.

        Args:
            rule_string: Rule string to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        # EAFPスタイル：まずパーシングを試行し、失敗時に詳細検証
        try:
            # パーシングを直接試行
            self.parse_rule_string(rule_string)
            return True, None

        except ValidationError as e:
            # バリデーションエラーの場合はメッセージを返す
            return False, str(e)
        except AttributeError:
            # rule_stringがstrでない場合のEAFP処理
            return (
                False,
                f"Rule string must be a string, got {type(rule_string).__name__}",
            )
        except Exception as e:
            # その他のエラー
            return False, str(e)

    def get_rule_help(self, rule_name: str | None = None) -> str:
        """Get help information for rules.

        Args:
            rule_name: Specific rule name or None for all rules

        Returns:
            Help text for the rule(s)
        """
        # EAFPスタイル：まずルールのアクセスを試行
        try:
            rules = self.get_available_rules()

            if rule_name is None:
                # Return help for all rules
                help_text = "Available transformation rules:\n"
                for name, rule in rules.items():
                    help_text += f"  /{name} - {rule.name}\n"
                    if rule.example:
                        help_text += f"    Example: {rule.example}\n"
                return help_text
            else:
                # Return help for specific rule
                rule = rules[rule_name]  # KeyErrorが発生する可能性
                return f"/{rule_name} - {rule.name}\n{rule.description}\nExample: {rule.example}"

        except KeyError:
            # ルールが見つからない場合のEAFP処理
            return f"Unknown rule: {rule_name}"
        except Exception:
            # その他のエラー時はデフォルトメッセージ
            return "Help information is not available at this time."

    def _apply_tsv_conversion(self, text: str, args: list[str]) -> str:
        """TSVファイルを使用した変換を実行
        
        Enterprise-grade拡張により、--case-insensitiveなどの
        高度なオプションをサポートします。
        
        Args:
            text: 変換対象のテキスト
            args: TSVファイルパスとオプションを含む引数リスト
            
        Returns:
            変換されたテキスト
            
        Raises:
            TransformationError: TSV変換に失敗した場合
        """
        try:
            if not args:
                raise TransformationError(
                    "convertbytsv rule requires TSV file path",
                    {"rule_name": "convertbytsv", "args_count": len(args)}
                )
            
            # 引数を解析（ファイルパスとオプションを分離）
            parsed_args = self._parse_tsv_conversion_args(args)
            tsv_file_name = parsed_args["file_path"]
            options = parsed_args["options"]
            
            # TSVファイルパスを正規化
            if not tsv_file_name.endswith('.tsv'):
                tsv_file_name += '.tsv'
            
            # プロジェクトルートからの正確な相対パス
            base_path = Path(__file__).parent.parent.parent
            tsv_file_path = base_path / "config" / "tsv_rules" / tsv_file_name
            
            # TSVTransformationインスタンスを作成して変換実行
            tsv_transformer = TSVTransformation(str(tsv_file_path), options)
            return tsv_transformer.transform(text)
            
        except TransformationError:
            raise
        except Exception as e:
            self.set_error_context({
                "rule_name": "convertbytsv",
                "args": args,
                "error_type": type(e).__name__
            })
            raise TransformationError(
                f"TSV conversion failed: {e}",
                self.get_error_context()
            ) from e
    
    def _parse_tsv_conversion_args(self, args: list[str]) -> dict[str, Any]:
        """TSV変換の引数を解析（POSIX準拠：オプション優先パターン）
        
        POSIX標準に従い、オプションが引数より前に配置される形式を採用:
        /convertbytsv --case-insensitive technical_terms.tsv
        
        Args:
            args: 引数リスト
            
        Returns:
            解析済み引数辞書
            {
                "file_path": str,
                "options": TSVConversionOptions
            }
            
        Raises:
            ValidationError: 引数が無効な場合
        """
        from .types import TSVConversionOptions
        
        try:
            if not args:
                raise ValidationError(
                    "TSV file path is required",
                    {"args_provided": 0}
                )
            
            # デフォルトオプション
            case_insensitive = False
            preserve_original_case = True
            file_path = None
            
            # POSIX準拠：オプションを先頭から処理、非オプションが見つかったら終了
            i = 0
            while i < len(args):
                arg = args[i]
                arg_lower = arg.lower()
                
                # オプション判定（--で始まるか-で始まる）
                if arg.startswith("--") or (arg.startswith("-") and len(arg) > 1):
                    if arg_lower in ["--case-insensitive", "--caseinsensitive"]:
                        case_insensitive = True
                    elif arg_lower == "-i":
                        case_insensitive = True
                    elif arg_lower in ["--no-preserve-case", "--no-preserve-original-case"]:
                        preserve_original_case = False
                    elif arg_lower in ["--preserve-case", "--preserve-original-case"]:
                        preserve_original_case = True
                    else:
                        # 未知のオプションは警告として記録
                        self.set_error_context({
                            "unknown_option": arg,
                            "valid_options": [
                                "--case-insensitive", "--caseinsensitive", "-i",
                                "--no-preserve-case", "--preserve-case"
                            ]
                        })
                else:
                    # 非オプション引数（ファイルパス）が見つかった
                    file_path = arg
                    break
                
                i += 1
            
            # ファイルパスが見つからない場合
            if file_path is None:
                raise ValidationError(
                    "TSV file path is required after options",
                    {
                        "args_provided": args,
                        "parsed_options": {
                            "case_insensitive": case_insensitive,
                            "preserve_original_case": preserve_original_case
                        }
                    }
                )
            
            # TSVConversionOptionsを作成
            options = TSVConversionOptions(
                case_insensitive=case_insensitive,
                preserve_original_case=preserve_original_case
            )
            
            return {
                "file_path": file_path,
                "options": options
            }
            
        except ValidationError:
            raise
        except Exception as e:
            raise ValidationError(
                f"Failed to parse TSV conversion arguments: {e}",
                {"args": args, "error_type": type(e).__name__}
            ) from e

    # TransformationBaseの抽象メソッドの実装
    def get_input_text(self) -> str:
        """変換前の文字列を取得する抽象メソッドの実装

        Returns:
            変換前の文字列（このクラスでは空文字列）
        """
        return ""

    def get_output_text(self) -> str:
        """変換後の文字列を取得する抽象メソッドの実装

        Returns:
            変換後の文字列（このクラスでは空文字列）
        """
        return ""

    def get_transformation_rule(self) -> str:
        """適用される変換ルールを取得する抽象メソッドの実装

        Returns:
            変換ルール文字列（このクラスでは空文字列）
        """
        return ""
