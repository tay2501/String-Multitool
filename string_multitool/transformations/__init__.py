"""
変換処理モジュールのパッケージ初期化

このパッケージは、個別の変換クラスを提供し、各変換ルールを
TransformationBaseを継承したクラスとして実装します。
"""

from __future__ import annotations

# 基本変換
from .basic_transformations import (
    UnderbarToHyphenTransformation,
    HyphenToUnderbarTransformation,
    FullToHalfWidthTransformation,
    HalfToFullWidthTransformation,
)

# ケース変換
from .case_transformations import (
    LowercaseTransformation,
    UppercaseTransformation,
    PascalCaseTransformation,
    CamelCaseTransformation,
    SnakeCaseTransformation,
    CapitalizeTransformation,
)

# 文字列操作
from .string_operations import (
    TrimTransformation,
    ReverseTransformation,
    SqlInClauseTransformation,
    DeleteLineBreaksTransformation,
)

# 暗号化変換
from .encryption_transformations import (
    EncryptTransformation,
    DecryptTransformation,
)

# ハッシュ変換
from .hash_transformations import (
    Sha256HashTransformation,
)

# エンコード変換
from .encoding_transformations import (
    Base64EncodeTransformation,
    Base64DecodeTransformation,
)

# フォーマット変換
from .formatting_transformations import (
    JsonFormatTransformation,
)

# 高度な変換
from .advanced_transformations import (
    ReplaceTransformation,
    SlugifyTransformation,
)

__all__ = [
    # 基本変換
    "UnderbarToHyphenTransformation",
    "HyphenToUnderbarTransformation", 
    "FullToHalfWidthTransformation",
    "HalfToFullWidthTransformation",
    
    # ケース変換
    "LowercaseTransformation",
    "UppercaseTransformation",
    "PascalCaseTransformation",
    "CamelCaseTransformation",
    "SnakeCaseTransformation",
    "CapitalizeTransformation",
    
    # 文字列操作
    "TrimTransformation",
    "ReverseTransformation",
    "SqlInClauseTransformation",
    "DeleteLineBreaksTransformation",
    
    # 暗号化変換
    "EncryptTransformation",
    "DecryptTransformation",
    
    # ハッシュ変換
    "Sha256HashTransformation",
    
    # エンコード変換
    "Base64EncodeTransformation",
    "Base64DecodeTransformation",
    
    # フォーマット変換
    "JsonFormatTransformation",
    
    # 高度な変換
    "ReplaceTransformation",
    "SlugifyTransformation",
]


def get_transformation_class_map() -> dict[str, type]:
    """変換ルール名とクラスのマッピングを取得
    
    Returns:
        変換ルール名をキーとし、対応するクラスを値とする辞書
    """
    return {
        # 基本変換
        "uh": UnderbarToHyphenTransformation,
        "hu": HyphenToUnderbarTransformation,
        "fh": FullToHalfWidthTransformation,
        "hf": HalfToFullWidthTransformation,
        
        # ケース変換
        "l": LowercaseTransformation,
        "u": UppercaseTransformation,
        "p": PascalCaseTransformation,
        "c": CamelCaseTransformation,
        "s": SnakeCaseTransformation,
        "a": CapitalizeTransformation,
        
        # 文字列操作
        "t": TrimTransformation,
        "R": ReverseTransformation,
        "si": SqlInClauseTransformation,
        "dlb": DeleteLineBreaksTransformation,
        
        # 暗号化変換
        "enc": EncryptTransformation,
        "dec": DecryptTransformation,
        
        # ハッシュ変換
        "hash": Sha256HashTransformation,
        
        # エンコード変換
        "base64enc": Base64EncodeTransformation,
        "base64dec": Base64DecodeTransformation,
        
        # フォーマット変換
        "formatjson": JsonFormatTransformation,
        
        # 高度な変換
        "r": ReplaceTransformation,
        "S": SlugifyTransformation,
    }