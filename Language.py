"""
text rule:
[] >> replace using internal dict phrase / expression
{} >> replace using external phrase
"""

from __future__ import annotations
import ast
import json
import os
import re
import unicodedata
from copy import deepcopy
from functools import reduce
from typing import TypedDict

from Utils import lang_path


class ItemMessage(TypedDict):
    id: int
    text: str


def half_to_full_width(s: str) -> str:
    out = []
    for ch in s:
        code = ord(ch)
        if code == 0x20:
            out.append('\u3000')
        elif 0x30 <= code <= 0x39 or 0x41 <= code <= 0x5A or 0x61 <= code <= 0x7A:
            out.append(chr(code + 0xFEE0))
        elif 0xFF61 <= code <= 0xFF9F:
            out.append(unicodedata.normalize('NFKC', ch))
        else:
            out.append(ch)
    return ''.join(out)


_TEMP_LITERAL_NAME_RE = re.compile(r'(None|True|False)\Z')

_METHOD_TOKEN_RE = re.compile(r'([A-Za-z_]\w*)\(\)\Z')
_NAME_RE = re.compile(r'[A-Za-z_]\w*\Z')

_ALLOWED_METHODS = {
    "capitalize",
    "lower",
    "upper",
    "title",
    "swapcase",
    "casefold",
    "strip",
    "lstrip",
    "rstrip",
}

_ALLOWED_FUNCTIONS = {
    "format",
}

class _SafeExprEvaluator(ast.NodeVisitor):
    def __init__(self, env: dict):
        self.env = env

    def visit(self, node):
        allowed = (
            ast.Expression,
            ast.Constant,
            ast.Name,
            ast.Attribute,
            ast.Subscript,
            ast.Call,
            ast.List,
            ast.Tuple,
            ast.Dict,
            ast.Set,
            ast.Compare,
            ast.BoolOp,
            ast.UnaryOp,
            ast.IfExp,
            ast.Load,
            ast.Slice,
            ast.Eq,
            ast.NotEq,
            ast.In,
            ast.NotIn,
            ast.Is,
            ast.IsNot,
            ast.Lt,
            ast.LtE,
            ast.Gt,
            ast.GtE,
            ast.And,
            ast.Or,
            ast.Not,
        )
        if not isinstance(node, allowed):
            raise ValueError(f"Unsupported expression node: {type(node).__name__}")
        return super().visit(node)

    def generic_visit(self, node):
        raise ValueError(f"Unsupported expression: {type(node).__name__}")

    def visit_Expression(self, node: ast.Expression):
        return self.visit(node.body)

    def visit_Constant(self, node: ast.Constant):
        return node.value

    def visit_Name(self, node: ast.Name):
        if node.id in self.env:
            return self.env[node.id]
        raise NameError(f"Unknown name: {node.id}")

    def visit_Attribute(self, node: ast.Attribute):
        base = self.visit(node.value)
        if isinstance(base, dict):
            if node.attr in base:
                return base[node.attr]
            raise KeyError(
                f"KeyError: '{node.attr}' not found while resolving attribute. "
                f"Available keys: {list(base.keys())}"
            )
        return getattr(base, node.attr)

    def visit_Subscript(self, node: ast.Subscript):
        value = self.visit(node.value)
        index = self.visit(node.slice)
        if isinstance(value, dict) and index is None and "None" in value:
            index = "None"
        return value[index]

    def visit_Slice(self, node: ast.Slice):
        return slice(
            self.visit(node.lower) if node.lower else None,
            self.visit(node.upper) if node.upper else None,
            self.visit(node.step) if node.step else None,
        )

    def visit_List(self, node: ast.List):
        return [self.visit(e) for e in node.elts]

    def visit_Tuple(self, node: ast.Tuple):
        return tuple(self.visit(e) for e in node.elts)

    def visit_Set(self, node: ast.Set):
        return {self.visit(e) for e in node.elts}

    def visit_Dict(self, node: ast.Dict):
        return {
            self.visit(k): self.visit(v)
            for k, v in zip(node.keys, node.values)
        }

    def visit_BoolOp(self, node: ast.BoolOp):
        if isinstance(node.op, ast.And):
            result = True
            for v in node.values:
                result = self.visit(v)
                if not result:
                    return result
            return result

        if isinstance(node.op, ast.Or):
            result = False
            for v in node.values:
                result = self.visit(v)
                if result:
                    return result
            return result

        raise ValueError("Unsupported boolean operator")

    def visit_UnaryOp(self, node: ast.UnaryOp):
        val = self.visit(node.operand)
        if isinstance(node.op, ast.Not):
            return not val
        raise ValueError("Unsupported unary operator")

    def visit_IfExp(self, node: ast.IfExp):
        return self.visit(node.body) if self.visit(node.test) else self.visit(node.orelse)

    def visit_Compare(self, node: ast.Compare):
        left = self.visit(node.left)
        for op, comp in zip(node.ops, node.comparators):
            right = self.visit(comp)

            if isinstance(op, ast.Eq):
                ok = (left == right)
            elif isinstance(op, ast.NotEq):
                ok = (left != right)
            elif isinstance(op, ast.In):
                ok = (left in right)
            elif isinstance(op, ast.NotIn):
                ok = (left not in right)
            elif isinstance(op, ast.Is):
                ok = (left is right)
            elif isinstance(op, ast.IsNot):
                ok = (left is not right)
            elif isinstance(op, ast.Lt):
                ok = (left < right)
            elif isinstance(op, ast.LtE):
                ok = (left <= right)
            elif isinstance(op, ast.Gt):
                ok = (left > right)
            elif isinstance(op, ast.GtE):
                ok = (left >= right)
            else:
                raise ValueError(f"Unsupported compare operator: {type(op).__name__}")

            if not ok:
                return False
            left = right

        return True

    def visit_Call(self, node: ast.Call):
        if isinstance(node.func, ast.Attribute):
            if node.args or node.keywords:
                raise ValueError("Only zero-argument method calls are allowed")

            obj = self.visit(node.func.value)
            method_name = node.func.attr
            if method_name not in _ALLOWED_METHODS:
                raise ValueError(f"Method not allowed: {method_name}")

            method = getattr(obj, method_name, None)
            if method is None or not callable(method):
                raise ValueError(f"Object has no callable method: {method_name}")

            return method()

        if isinstance(node.func, ast.Name):
            func_name = node.func.id
            if func_name not in _ALLOWED_FUNCTIONS:
                raise ValueError(f"Function not allowed: {func_name}")

            func = self.env.get(func_name)
            if func is None or not callable(func):
                raise ValueError(f"Unknown callable: {func_name}")

            args = [self.visit(arg) for arg in node.args]
            kwargs = {}
            for kw in node.keywords:
                if kw.arg is None:
                    raise ValueError("Keyword expansion is not allowed")
                kwargs[kw.arg] = self.visit(kw.value)

            return func(*args, **kwargs)

        raise ValueError("Only method calls or allowed function calls are allowed")


# Character width table used by the original message renderer.
# The table is indexed as (message_character - 0x20), so it has 144 f32 entries.
CHAR_WIDTH_TABLE_LENGTH = 144
CHAR_WIDTH_TABLE_BYTES = CHAR_WIDTH_TABLE_LENGTH * 4

CHAR_WIDTH_ORDER = (
    [chr(i) for i in range(0x20, 0x7F)] +
    [
        "extra_space",
        "À", "î", "Â", "Ä", "Ç", "È", "É", "Ê", "Ë", "Ï",
        "Ô", "Ö", "Ù", "Û", "Ü", "ß",
        "à", "á", "â", "ä", "ç", "è", "é", "ê", "ë", "ï",
        "ô", "ö", "ù", "û", "ü",
        "[A]", "[B]", "[C]", "[L]", "[R]", "[Z]",
        "[C-Up]", "[C-Down]", "[C-Left]", "[C-Right]",
        "▼", "[Control-Pad]", "[D-Pad]",
        "index:140", "index:141", "index:142", "index:143",
    ]
)

DEFAULT_CHAR_WIDTHS_NTSC = [
    8, 8, 6, 9, 9, 14, 12, 3, 7, 7, 7, 9, 4, 6, 4, 9,
    10, 5, 9, 9, 10, 9, 9, 9, 9, 9, 6, 6, 9, 11, 9, 11,
    13, 12, 9, 11, 11, 8, 8, 12, 10, 4, 8, 10, 8, 13, 11, 13,
    9, 13, 10, 10, 9, 10, 11, 15, 11, 10, 10, 7, 10, 7, 10, 9,
    5, 8, 9, 8, 9, 9, 6, 9, 8, 4, 6, 8, 4, 12, 9, 9,
    9, 9, 7, 8, 7, 8, 9, 12, 8, 9, 8, 7, 5, 7, 10, 10,
    12, 12, 12, 12, 11, 8, 8, 8, 6, 6, 13, 13, 10, 10, 10, 9,
    8, 8, 8, 8, 8, 9, 9, 9, 9, 6, 9, 9, 9, 9, 9, 14,
    14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14,
]
DEFAULT_CHAR_WIDTHS_PAL = DEFAULT_CHAR_WIDTHS_NTSC.copy()
DEFAULT_CHAR_WIDTHS_PAL[CHAR_WIDTH_ORDER.index("î")] = 6

CHAR_WIDTH_NAME_TO_INDEX = {name: i for i, name in enumerate(CHAR_WIDTH_ORDER)}


# Wide/Japanese text mode character widths.
# Runtime default is always 16 pixels; only overrides are written to ROM.
WIDE_CHAR_DEFAULT_WIDTH = 16
WIDE_CHAR_WIDTH_ENTRY_BYTES = 4


# Text control codes must be protected while replace_table is applied.
# The value is the total byte/character length of the code sequence inside the
# decoded Python string, including argument bytes that may look like ordinary
# printable letters.
_TEXT_CONTROL_CODE_LENGTHS = {
    0x00: 1,  # pad
    0x01: 1,  # line break
    0x02: 1,  # end
    0x04: 1,  # box break
    0x05: 2,  # color + color id
    0x06: 2,  # gap + size
    0x07: 3,  # goto + u16
    0x08: 1,  # instant
    0x09: 1,  # un-instant
    0x0A: 1,  # keep open
    0x0B: 1,  # event
    0x0C: 2,  # box break delay + frames
    0x0E: 2,  # fade out + frames
    0x0F: 1,  # player name
    0x10: 1,  # ocarina
    0x12: 3,  # sound + u16
    0x13: 2,  # icon + icon id
    0x14: 2,  # speed/control argument
}
_REPLACE_PROTECT_START = "\uE000"
_REPLACE_PROTECT_END = "\uE001"

_SJIS_CODEPOINT_RE = re.compile(r'(?i)\A(?:sjis:|shift-jis:)?0x([0-9a-f]{2}|[0-9a-f]{4})\Z')

def _decode_sjis_codepoint_token(value: str) -> str:
    """Decode replace_table values such as 0x819F as Shift-JIS bytes.

    This is intentionally narrow: only a whole value in the form 0xNN or
    0xNNNN is treated as a Shift-JIS byte sequence. Other strings containing
    those characters remain literal text.
    """
    text = str(value)
    match = _SJIS_CODEPOINT_RE.fullmatch(text.strip())
    if not match:
        return text
    hex_text = match.group(1)
    try:
        raw = bytes.fromhex(hex_text)
        return raw.decode('shift_jis')
    except (ValueError, UnicodeDecodeError):
        # Keep invalid values literal so a bad property file does not make the
        # language loader unusable. The editor validator reports these instead.
        return text

class Language:
    FALLBACK_LANG = "English"

    @staticmethod
    def _load_property_file(lang: str) -> dict:
        with open(os.path.join(lang_path(lang), "property.json"), mode="r", encoding="utf-8") as f:
            return json.load(f)

    @staticmethod
    def _is_id_list(value) -> bool:
        """Return True for property lists whose entries can be merged by id.

        Ordinary translation-choice lists must never be padded from the fallback
        language, because that can mix English options into another language.
        Lists whose entries are dictionaries with an ``id`` field are treated as
        keyed records instead: existing ids are overlaid and missing ids are
        filled from the fallback language.
        """
        return (
            isinstance(value, list)
            and len(value) > 0
            and all(isinstance(item, dict) and "id" in item for item in value)
        )

    @classmethod
    def _merge_id_list_with_fallback(cls, fallback: list, override: list) -> list:
        """Merge a list of ``{"id": ...}`` dictionaries by id.

        The selected language controls the visible order for translated entries.
        Fallback-only records are appended afterward in fallback order.
        """
        fallback_by_id = {item["id"]: item for item in fallback}
        override_ids = set()
        merged = []

        for item in override:
            item_id = item["id"]
            override_ids.add(item_id)
            if item_id in fallback_by_id:
                merged.append(cls._merge_with_fallback(fallback_by_id[item_id], item))
            else:
                merged.append(deepcopy(item))

        for item in fallback:
            if item["id"] not in override_ids:
                merged.append(deepcopy(item))

        return merged

    @classmethod
    def _merge_with_fallback(cls, fallback, override):
        """Return fallback recursively overlaid by override.

        Dicts are merged by key. Lists are normally replaced wholesale by the
        selected language to prevent fallback-language strings from being mixed
        into translated choice lists. The one exception is a list of dictionaries
        with an ``id`` field, which is merged by id so missing records can still
        be filled from the fallback language. Existing override values,
        including empty strings and null, are treated as intentional translations.
        """
        if isinstance(fallback, dict) and isinstance(override, dict):
            merged = {k: deepcopy(v) for k, v in fallback.items()}
            for key, value in override.items():
                if key in merged:
                    merged[key] = cls._merge_with_fallback(merged[key], value)
                else:
                    merged[key] = deepcopy(value)
            return merged

        if isinstance(fallback, list) and isinstance(override, list):
            if cls._is_id_list(fallback) and (cls._is_id_list(override) or len(override) == 0):
                return cls._merge_id_list_with_fallback(fallback, override)
            return deepcopy(override)

        return deepcopy(override)

    @classmethod
    def _load_property_with_fallback(cls, lang: str) -> dict:
        if lang == cls.FALLBACK_LANG:
            return cls._load_property_file(lang)

        fallback_message = cls._load_property_file(cls.FALLBACK_LANG)

        try:
            message = cls._load_property_file(lang)
        except FileNotFoundError:
            return fallback_message

        return cls._merge_with_fallback(fallback_message, message)

    @staticmethod
    def _collect_language_data(lang: str, extensions: tuple[str, ...]) -> dict[str, str]:
        path = lang_path(lang)
        if not os.path.isdir(path):
            return {}
        return {
            fname: os.path.join(path, fname)
            for fname in os.listdir(path)
            if fname.lower().endswith(extensions)
        }

    def __init__(self, lang: str):
        message = self._load_property_with_fallback(lang)

        self._normalize_replace_table(message)
        self.__dict__.update(message)
        self.base = self.lang_property["base"]

        extensions = (".bin", ".ia4", ".zobj")
        self.lang = lang
        self.path = lang_path(lang)
        # Do not globally fall back binary/texture/object data files.
        # Register only files that actually exist in the selected language.
        # Individual patch sites that need a fallback should resolve it explicitly.
        self.data = self._collect_language_data(lang, extensions)

    def blue_fire_arrow_item_name_path(self) -> str:
        """Return the Blue Fire Arrow item-name texture for this language base.

        This is intentionally the only lang.data-style asset fallback.
        Use the selected language's matching-base file when present; otherwise
        fall back to Japanese for jp-base languages and English for all others.
        """
        if self.base == "jp":
            filename = "blue_fire_arrow_item_name_jap.ia4"
            fallback_lang = "Japanese"
        else:
            filename = "blue_fire_arrow_item_name_eng.ia4"
            fallback_lang = self.FALLBACK_LANG

        local_file = self.data.get(filename)
        if local_file is not None and os.path.isfile(local_file):
            return local_file

        return os.path.join(lang_path(fallback_lang), filename)


    def _normalize_replace_table(self, message: dict) -> None:
        """Normalize the optional language-wide replacement table.

        Current property.json files should use replace_table as a list of
        {"from": str, "to": str} objects. Older files using replace_list or
        language_specific_replace_table are accepted as input and rewritten in
        memory as replace_table.
        """
        replace_table = message.get("replace_table", None)
        if replace_table is None:
            replace_table = message.get("replace_list", message.get("language_specific_replace_table", []))
        if replace_table is None:
            replace_table = []
        if isinstance(replace_table, dict):
            replace_table = [
                {"from": str(k), "to": str(v)}
                for k, v in replace_table.items()
            ]
        normalized = []
        if isinstance(replace_table, list):
            for item in replace_table:
                if isinstance(item, dict):
                    normalized.append({
                        "from": str(item.get("from", "")),
                        "to": str(item.get("to", "")),
                    })
                elif isinstance(item, (list, tuple)) and len(item) >= 2:
                    normalized.append({"from": str(item[0]), "to": str(item[1])})
        message["replace_table"] = normalized
        message.pop("replace_list", None)
        message.pop("language_specific_replace_table", None)

    def _protect_text_control_codes(self, text: str, tokens: list[str]) -> str:
        out = []
        i = 0
        while i < len(text):
            ch = text[i]
            code = ord(ch)
            if code < 0x20:
                length = _TEXT_CONTROL_CODE_LENGTHS.get(code, 1)
                seq = text[i:min(len(text), i + length)]
                token = f"{_REPLACE_PROTECT_START}{len(tokens)}{_REPLACE_PROTECT_END}"
                tokens.append(seq)
                out.append(token)
                i += len(seq)
                continue
            out.append(ch)
            i += 1
        return "".join(out)

    def _restore_text_control_codes(self, text: str, tokens: list[str]) -> str:
        for i, seq in enumerate(tokens):
            text = text.replace(f"{_REPLACE_PROTECT_START}{i}{_REPLACE_PROTECT_END}", seq)
        return text

    def _contains_text_control_code(self, text: str) -> bool:
        return any(ord(ch) < 0x20 for ch in text)

    def _apply_replace_table(self, text: str) -> str:
        entries = getattr(self, "replace_table", []) or []
        if not entries:
            return text

        tokens: list[str] = []
        protected = self._protect_text_control_codes(text, tokens)

        # Apply all replacement rules simultaneously against the original
        # protected text. Replacement output must not be processed again by
        # later rules. For example, A=>B and B=>C turns ABCD into BCCD, not CCCD.
        rules: list[tuple[str, str, int]] = []
        seen: set[str] = set()
        for order, item in enumerate(entries):
            if not isinstance(item, dict):
                continue
            src = _decode_sjis_codepoint_token(str(item.get("from", "")))
            dst = _decode_sjis_codepoint_token(str(item.get("to", "")))
            if not src or src in seen:
                continue
            # Do not allow replacement rules to match or create text control
            # codes. replace_table is a text replacement table, not a control-code
            # authoring mechanism. This prevents rules such as A => B from
            # corrupting color control codes like \x05A, and also prevents
            # replacement output from injecting control bytes.
            if self._contains_text_control_code(src) or self._contains_text_control_code(dst):
                continue
            rules.append((src, dst, order))
            seen.add(src)

        if not rules:
            return self._restore_text_control_codes(protected, tokens)

        # If multiple rules can match at the same location, prefer the longest
        # source string, then the earlier replace_table entry for stable results.
        rules.sort(key=lambda item: (-len(item[0]), item[2]))
        replacement_by_source = {src: dst for src, dst, _ in rules}
        pattern = re.compile("|".join(re.escape(src) for src, _, _ in rules))
        protected = pattern.sub(lambda m: replacement_by_source[m.group(0)], protected)

        return self._restore_text_control_codes(protected, tokens)

    def _default_char_widths(self, variant: str = "ntsc") -> list[float]:
        if variant.lower() == "pal":
            return [float(x) for x in DEFAULT_CHAR_WIDTHS_PAL]
        return [float(x) for x in DEFAULT_CHAR_WIDTHS_NTSC]

    def _char_width_key_to_index(self, key) -> int:
        if isinstance(key, int):
            index = key
        elif isinstance(key, str):
            key = key.strip()
            if key.startswith("index:"):
                index = int(key.split(":", 1)[1], 0)
            elif key.startswith("0x"):
                # Message byte value. 0x20 maps to table index 0.
                index = int(key, 16) - 0x20
            elif len(key) == 1 and 0x20 <= ord(key) <= 0x7E:
                index = ord(key) - 0x20
            elif key in CHAR_WIDTH_NAME_TO_INDEX:
                index = CHAR_WIDTH_NAME_TO_INDEX[key]
            else:
                raise ValueError(f"Unknown CHAR_WIDTHS key: {key!r}")
        else:
            raise TypeError(f"CHAR_WIDTHS key must be str or int, got {type(key).__name__}")

        if not 0 <= index < CHAR_WIDTH_TABLE_LENGTH:
            raise ValueError(f"CHAR_WIDTHS index out of range: {index}")
        return index

    def get_char_widths(self, variant: str = "ntsc") -> list[float]:
        """Return the 144 f32 character widths used by the message renderer.

        property.json may define CHAR_WIDTHS as either:
        - a list of 144 numbers, replacing the whole table
        - a dict of per-character overrides, e.g. {"A": 12, "index:143": 14}
          Values may also be {"default": 12, "ntsc": 12, "pal": 6}.
        """
        if self.uses_wide_text():
            # Wide/Japanese mode uses get_wide_char_width_overrides() instead.
            # Keep this function narrow-only so the ROM patcher can branch cleanly.
            return self._default_char_widths(variant)

        widths = self._default_char_widths(variant)
        overrides = getattr(self, "CHAR_WIDTHS", None)

        if overrides in (None, {}):
            return widths

        if isinstance(overrides, list):
            if len(overrides) != CHAR_WIDTH_TABLE_LENGTH:
                raise ValueError(
                    f"CHAR_WIDTHS list must contain {CHAR_WIDTH_TABLE_LENGTH} entries, "
                    f"got {len(overrides)}"
                )
            width_items = enumerate(overrides)
        elif isinstance(overrides, dict):
            width_items = overrides.items()
        else:
            raise TypeError("CHAR_WIDTHS must be a list or dict")

        variant_key = variant.lower()
        for key, value in width_items:
            if isinstance(value, dict):
                value = value.get(variant_key, value.get("default"))
                if value is None:
                    continue

            index = key if isinstance(overrides, list) else self._char_width_key_to_index(key)
            width = float(value)
            if not 0.0 <= width <= 32.0:
                raise ValueError(f"CHAR_WIDTHS[{key!r}] must be between 0 and 32, got {width}")
            widths[index] = width

        return widths


    def uses_wide_text(self):
        return self.base == "jp"

    def uses_wide_english_metrics(self):
        return bool(self.lang_property.get("wide_text_english_metrics", False))

    def _char_width_value_for_variant(self, key, value, variant):
        if isinstance(value, dict):
            variant_key = variant.lower()
            value = value.get(variant_key, value.get("default"))
            if value is None:
                return None
        width = int(value)
        if width != float(value):
            raise ValueError(f"CHAR_WIDTHS[{key!r}] must be an integer width, got {value!r}")
        if not 0 <= width <= 32:
            raise ValueError(f"CHAR_WIDTHS[{key!r}] must be between 0 and 32, got {width}")
        return width

    def _wide_char_width_key_to_code(self, key):
        if isinstance(key, int):
            code = key
        elif isinstance(key, str):
            key = key.strip()
            if not key.lower().startswith("0x"):
                raise ValueError(
                    f"Wide/Japanese CHAR_WIDTHS keys must be hex strings such as '0x824F', got {key!r}"
                )
            code = int(key, 16)
        else:
            raise TypeError(f"Wide CHAR_WIDTHS key must be a hex string or int, got {type(key).__name__}")

        if not 0 <= code <= 0xFFFF:
            raise ValueError(f"Wide CHAR_WIDTHS code out of range: 0x{code:X}")
        return code

    def get_wide_char_width_overrides(self, variant="ntsc"):
        """Return compact wide-mode CHAR_WIDTHS overrides as [(u16_code, u8_width), ...].

        In wide/Japanese mode, CHAR_WIDTHS is intentionally pseudo-variable length:
        - keys must be hex codepoints such as "0x824F"
        - unlisted characters use the fixed runtime default width 16
        - entries equal to the default are omitted to save ROM space
        """
        overrides = getattr(self, "CHAR_WIDTHS", None)
        if overrides in (None, {}):
            return []
        if not isinstance(overrides, dict):
            raise TypeError("Wide/Japanese CHAR_WIDTHS must be a dict of hex codepoint overrides")

        entries = {}
        for key, value in overrides.items():
            width = self._char_width_value_for_variant(key, value, variant)
            if width is None:
                continue
            code = self._wide_char_width_key_to_code(key)
            if width == WIDE_CHAR_DEFAULT_WIDTH:
                entries.pop(code, None)
            else:
                entries[code] = width

        return sorted(entries.items())

    def _dict_get(self, obj, key):
        if isinstance(obj, (list, tuple)):
            if isinstance(key, str):
                key = int(key, 0)
            return obj[key]
        if isinstance(obj, dict):
            return obj[key]
        return getattr(obj, key)

    def _to_output_string(self, value):
        s = str(value)
        if self.base == "jp" and type(value) is int:
            s = half_to_full_width(s)
        return s

    def _to_expr_literal(self, value):
        value = self._coerce_expr_value(value)
        if self.base == "jp" and type(value) is int:
            return repr(half_to_full_width(str(value)))
        return repr(value)

    def _coerce_expr_value(self, value):
        if isinstance(value, (str, int, float, bool, type(None), list, tuple, dict, set)):
            return value
        return str(value)

    def _format_expr_function(self, value, external=None):
        if external is not None and not isinstance(external, dict):
            raise ValueError("format(text, external_dict) requires dict or None as second argument")
        try:
            return self.format_from_text(str(value), external)
        except (KeyError, NameError, ValueError, IndexError, AttributeError, SyntaxError) as e:
            print("FORMAT FAIL")
            print("VALUE   =", repr(value))
            print("EXTERNAL=", repr(external))
            print("ERROR   =", repr(e))
            return str(value)

    def _is_simple_external_key(self, key_text: str) -> bool:
        key_text = key_text.strip()
        return key_text.isdigit() or _NAME_RE.fullmatch(key_text) is not None

    def _build_expr_env(self, external: dict | None):
        env = {
            k: v
            for k, v in self.__dict__.items()
            if not k.startswith("_") and not callable(v)
        }
        env["format"] = self._format_expr_function
        if external:
            env.update(external)
        return env

    def _safe_eval_expr(self, expr: str, external: dict | None):
        tree = ast.parse(expr, mode="eval")
        return _SafeExprEvaluator(self._build_expr_env(external)).visit(tree)

    def _read_group(self, text: str, start: int, opener: str, closer: str):
        depth = 1
        i = start + 1
        buff = []

        while i < len(text):
            ch = text[i]

            if ch == "\\" and i + 1 < len(text):
                buff.append(text[i:i + 2])
                i += 2
                continue

            if ch == opener:
                depth += 1
                buff.append(ch)
                i += 1
                continue

            if ch == closer:
                depth -= 1
                if depth == 0:
                    return "".join(buff), i + 1
                buff.append(ch)
                i += 1
                continue

            buff.append(ch)
            i += 1

        return None, start + 1

    def _split_dot_tokens(self, text: str):
        tokens = []
        buff = []
        brace_depth = 0
        paren_depth = 0
        quote = None
        i = 0

        while i < len(text):
            ch = text[i]

            if quote:
                buff.append(ch)
                if ch == "\\" and i + 1 < len(text):
                    buff.append(text[i + 1])
                    i += 2
                    continue
                if ch == quote:
                    quote = None
                i += 1
                continue

            if ch in ("'", '"'):
                quote = ch
                buff.append(ch)
                i += 1
                continue

            if ch == "{":
                brace_depth += 1
                buff.append(ch)
                i += 1
                continue

            if ch == "}":
                brace_depth -= 1
                buff.append(ch)
                i += 1
                continue

            if ch == "(":
                paren_depth += 1
                buff.append(ch)
                i += 1
                continue

            if ch == ")":
                paren_depth -= 1
                buff.append(ch)
                i += 1
                continue

            if ch == "." and brace_depth == 0 and paren_depth == 0:
                token = "".join(buff).strip()
                if token:
                    tokens.append(token)
                buff = []
                i += 1
                continue

            buff.append(ch)
            i += 1

        token = "".join(buff).strip()
        if token:
            tokens.append(token)
        return tokens

    def _translate_path_ops_to_python(self, content: str):
        tokens = self._split_dot_tokens(content.strip())
        if not tokens:
            raise ValueError("Empty path")

        head = tokens[0]
        if not _NAME_RE.fullmatch(head):
            raise ValueError("Not a path-op expression")

        expr = head
        for token in tokens[1:]:
            if token.startswith("{") and token.endswith("}"):
                inner = token[1:-1].strip()
                if inner.isdigit():
                    expr += f"[{int(inner)}]"
                elif _NAME_RE.fullmatch(inner):
                    expr += f"[{inner}]"
                else:
                    raise ValueError(f"Unsupported external key token: {token}")
                continue

            if _TEMP_LITERAL_NAME_RE.fullmatch(token):
                expr += f"[{token}]"
                continue

            if token.isdigit():
                expr += f"[{int(token)}]"
                continue

            m = _METHOD_TOKEN_RE.fullmatch(token)
            if m:
                method_name = m.group(1)
                if method_name not in _ALLOWED_METHODS:
                    raise ValueError(f"Unsupported method: {method_name}")
                expr += f".{method_name}()"
                continue

            if _NAME_RE.fullmatch(token):
                expr += f".{token}"
                continue

            raise ValueError(f"Unsupported token in path-op expression: {token}")

        return expr

    def _replace_placeholders(self, text: str, external: dict | None, for_expr: bool):
        out = []
        i = 0

        while i < len(text):
            ch = text[i]

            if ch == "\\" and i + 1 < len(text) and text[i + 1] in "[]{}":
                out.append(text[i:i + 2])
                i += 2
                continue

            if ch == "[":
                content, nxt = self._read_group(text, i, "[", "]")
                if content is None:
                    out.append(ch)
                    i += 1
                    continue
                out.append(self._resolve_square(content, external, for_expr))
                i = nxt
                continue

            if ch == "{":
                if i != 0 and text[i - 1] == "$":
                    out.append(ch)
                    i += 1
                    continue

                content, nxt = self._read_group(text, i, "{", "}")
                if content is None:
                    out.append(ch)
                    i += 1
                    continue

                if for_expr and not self._is_simple_external_key(content):
                    out.append("{")
                    out.append(content)
                    out.append("}")
                    i = nxt
                    continue

                if for_expr and not self._is_simple_external_key(content):
                    out.append("{")
                    out.append(content)
                    out.append("}")
                    i = nxt
                    continue

                out.append(self._resolve_external(content, external, for_expr))
                i = nxt
                continue

            out.append(ch)
            i += 1

        return "".join(out)

    def _resolve_external(self, key_text: str, external: dict | None, for_expr: bool):
        key_text = key_text.strip()
        real_key = int(key_text) if key_text.isdigit() else key_text
        value = (external or {})[real_key]
        return self._to_expr_literal(value) if for_expr else self._to_output_string(value)

    def _resolve_square(self, content: str, external: dict | None, for_expr: bool):
        content = content.strip()

        try:
            translated = self._translate_path_ops_to_python(content)
        except Exception:
                    translated = None

        if translated is not None:
            value = self._safe_eval_expr(translated, external)
            return self._to_expr_literal(value) if for_expr else self._to_output_string(value)

        expr = self._replace_placeholders(content, external, for_expr=True)
        value = self._safe_eval_expr(expr, external)
        return self._to_expr_literal(value) if for_expr else self._to_output_string(value)

    def format_from_text(self, text: str, external: dict | None = None):
        get = self._replace_placeholders(text, external or {}, for_expr=False)
        get = re.sub(r'\\([\[\]\{\}])', r'\1', get)

        return self._apply_replace_table(get)

    def format_from_id(self, id: str, external: dict = None):
        keys = id.split('.')
        key = keys.pop(0)
        base = getattr(self, key)
        i = 0
        while i < len(keys):
            if keys[i].isdigit():
                keys[i] = int(keys[i])
            i += 1
        txt = reduce(self._dict_get, keys, base)
        return self.format_from_text(str(txt), external)
