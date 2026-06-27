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

class Language:
    def __init__(self, lang: str):
        with open(os.path.join(lang_path(lang), "property.json"), mode="r", encoding="utf-8") as f:
            message = json.load(f)

        self.__dict__.update(message)
        self.base = self.lang_property["base"]

        extensions = (".bin", ".ia4", ".zobj")
        self.path = lang_path(lang)
        self.data = {
            fname: os.path.join(lang_path(lang), fname)
            for fname in os.listdir(lang_path(lang))
            if fname.lower().endswith(extensions)
        }


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

        for a, k in self.language_specific_replace_table:
            get = get.replace(a, k)

        return get

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
