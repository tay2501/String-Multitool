"""
Japanese character encoding conversion transformations.

This module provides functionality for converting between different Japanese
character encodings using iconv-compatible syntax. Supports conversion between
Shift_JIS, CP932/MS932, EUC-JP, and UTF-8 with automatic encoding detection.

Design principles:
- Simple and loosely coupled architecture
- Leverages Python standard library codecs (no wheel reinvention)
- iconv-compatible command interface
- EAFP (Easier to Ask for Forgiveness than Permission) error handling style
"""

import codecs
import re
from typing import Dict, Optional, Tuple

import structlog

logger = structlog.get_logger(__name__)


class JapaneseEncodingTransformation:
    """
    Handles Japanese character encoding conversions with iconv-compatible syntax.

    Supports conversions between:
    - SJIS ⇔ MS932 (CP932)
    - SJIS ⇔ EUC-JP
    - SJIS ⇔ UTF-8
    - Auto-detection for source encoding when -f is omitted
    """

    # Encoding aliases mapping for iconv compatibility
    ENCODING_ALIASES: Dict[str, str] = {
        "sjis": "shift_jis",
        "shift_jis": "shift_jis",
        "ms932": "cp932",
        "cp932": "cp932",
        "eucjp": "euc_jp",
        "euc-jp": "euc_jp",
        "euc_jp": "euc_jp",
        "utf8": "utf-8",
        "utf-8": "utf-8",
    }

    # Character patterns for encoding detection heuristics
    DETECTION_PATTERNS = {
        "shift_jis": [
            # Hiragana range
            r"[\u3040-\u309F]",
            # Katakana range
            r"[\u30A0-\u30FF]",
            # Kanji range (CJK Unified Ideographs)
            r"[\u4E00-\u9FAF]",
        ],
        "cp932": [
            # Similar patterns to shift_jis but with MS extensions
            r"[\u3040-\u309F]",
            r"[\u30A0-\u30FF]",
            r"[\u4E00-\u9FAF]",
            # MS932 specific characters
            r"[\u2160-\u216F]",  # Roman numerals
        ],
        "euc_jp": [
            # EUC-JP specific patterns
            r"[\u3040-\u309F]",
            r"[\u30A0-\u30FF]",
            r"[\u4E00-\u9FAF]",
        ],
    }

    def __init__(self) -> None:
        """Initialize the Japanese encoding transformation handler."""
        self.logger = logger.bind(component="japanese_encoding")

    def convert_encoding(self, text: str, from_encoding: str, to_encoding: str) -> str:
        """
        Convert text from one encoding to another.

        Args:
            text: Input text to convert
            from_encoding: Source encoding (e.g., 'sjis', 'ms932', 'eucjp', 'utf8')
            to_encoding: Target encoding (e.g., 'sjis', 'ms932', 'eucjp', 'utf8')

        Returns:
            Converted text string

        Raises:
            ValueError: If encoding is not supported
            UnicodeError: If conversion fails
        """
        try:
            # Normalize encoding names
            from_enc = self._normalize_encoding_name(from_encoding)
            to_enc = self._normalize_encoding_name(to_encoding)

            self.logger.info(
                "Converting encoding",
                from_encoding=from_enc,
                to_encoding=to_enc,
                text_length=len(text),
            )

            # Since clipboard text is already Unicode, we simulate the conversion
            # by encoding to bytes and then decoding with target encoding
            if from_enc == to_enc:
                return text

            # Convert via bytes to simulate encoding conversion
            try:
                # First encode with source encoding to get bytes
                byte_data = text.encode(from_enc, errors="replace")
                # Then decode with target encoding
                result = byte_data.decode(to_enc, errors="replace")

                self.logger.info("Encoding conversion successful", result_length=len(result))
                return result

            except (UnicodeEncodeError, UnicodeDecodeError) as e:
                self.logger.warning(
                    "Encoding conversion failed, using replacement characters", error=str(e)
                )
                # Fallback: use replacement characters
                byte_data = text.encode(from_enc, errors="replace")
                return byte_data.decode(to_enc, errors="replace")

        except Exception as e:
            self.logger.error(
                "Encoding conversion error",
                error=str(e),
                from_encoding=from_encoding,
                to_encoding=to_encoding,
            )
            raise ValueError(f"Failed to convert from {from_encoding} to {to_encoding}: {e}")

    def detect_likely_encoding(self, text: str) -> str:
        """
        Detect the most likely source encoding for Japanese text.

        Uses heuristic analysis based on character patterns and frequency.
        Note: Since clipboard text is pre-converted to Unicode, this provides
        educated guess based on character distribution patterns.

        Args:
            text: Text to analyze

        Returns:
            Most likely encoding name ('shift_jis', 'cp932', 'euc_jp', or 'utf-8')
        """
        try:
            self.logger.info("Detecting encoding for text", text_length=len(text))

            # If text contains only ASCII, assume UTF-8
            if text.isascii():
                self.logger.info("Text is ASCII, defaulting to UTF-8")
                return "utf-8"

            # Count Japanese character patterns
            pattern_scores = {}

            for encoding, patterns in self.DETECTION_PATTERNS.items():
                score = 0
                for pattern in patterns:
                    matches = len(re.findall(pattern, text))
                    score += matches
                pattern_scores[encoding] = score

            # Find encoding with highest score
            if pattern_scores:
                best_encoding = max(pattern_scores, key=lambda k: pattern_scores[k])
                max_score = pattern_scores[best_encoding]

                self.logger.info(
                    "Encoding detection completed",
                    scores=pattern_scores,
                    detected_encoding=best_encoding,
                )

                # If no Japanese characters detected, default to UTF-8
                if max_score == 0:
                    return "utf-8"

                return best_encoding

            # Fallback to UTF-8
            self.logger.info("No pattern matches, defaulting to UTF-8")
            return "utf-8"

        except Exception as e:
            self.logger.warning("Encoding detection failed, defaulting to UTF-8", error=str(e))
            return "utf-8"

    def parse_iconv_args(self, args: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Parse iconv-style arguments to extract source and target encodings.

        Supports formats:
        - "-f SJIS -t UTF8"
        - "-t UTF8" (auto-detect source)
        - "SJIS UTF8" (positional arguments)

        Args:
            args: Argument string to parse

        Returns:
            Tuple of (from_encoding, to_encoding). from_encoding may be None for auto-detection.
        """
        try:
            self.logger.info("Parsing iconv arguments", args=args)

            from_encoding = None
            to_encoding = None

            # Split arguments
            arg_parts = args.strip().split()

            # Parse flag-style arguments (-f, -t)
            i = 0
            while i < len(arg_parts):
                arg = arg_parts[i]

                if arg == "-f" and i + 1 < len(arg_parts):
                    from_encoding = arg_parts[i + 1].lower()
                    i += 2
                elif arg == "-t" and i + 1 < len(arg_parts):
                    to_encoding = arg_parts[i + 1].lower()
                    i += 2
                elif arg.startswith("-f"):
                    # Handle -fSJIS format
                    from_encoding = arg[2:].lower()
                    i += 1
                elif arg.startswith("-t"):
                    # Handle -tUTF8 format
                    to_encoding = arg[2:].lower()
                    i += 1
                else:
                    # Positional arguments: assume "from to" format
                    if from_encoding is None:
                        from_encoding = arg.lower()
                    elif to_encoding is None:
                        to_encoding = arg.lower()
                    i += 1

            self.logger.info(
                "Parsed iconv arguments", from_encoding=from_encoding, to_encoding=to_encoding
            )

            return from_encoding, to_encoding

        except Exception as e:
            self.logger.error("Failed to parse iconv arguments", error=str(e), args=args)
            return None, None

    def _normalize_encoding_name(self, encoding: str) -> str:
        """
        Normalize encoding name to Python codecs format.

        Args:
            encoding: Encoding name to normalize

        Returns:
            Normalized encoding name

        Raises:
            ValueError: If encoding is not supported
        """
        normalized = encoding.lower().replace("-", "_")

        if normalized in self.ENCODING_ALIASES:
            result = self.ENCODING_ALIASES[normalized]

            # Verify the encoding is available in Python
            try:
                codecs.lookup(result)
                return result
            except LookupError:
                raise ValueError(
                    f"Encoding '{encoding}' is not supported by this Python installation"
                )

        raise ValueError(f"Unsupported encoding: {encoding}")

    def get_supported_encodings(self) -> Dict[str, str]:
        """
        Get list of supported encodings.

        Returns:
            Dictionary mapping alias names to Python codec names
        """
        return self.ENCODING_ALIASES.copy()
