"""
text rule:
[] >> replace using internal dict phrase
{} >> replace using external phrase
"""

from __future__ import annotations
import json, re, os
import unicodedata
from functools import reduce

from Utils import lang_path

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

class Language:
    def __init__(self, lang: str):
        message = json.load(open(os.path.join(lang_path(lang), "property.json"), mode="r+", encoding="utf-8"))
        self.__dict__.update(message)
        self.base = self.lang_property["base"]
        extensions = (".bin", ".ia4", ".zobj")
        self.path = lang_path(lang)
        self.data = {
            fname: os.path.join(lang_path(lang), fname)
            for fname in os.listdir(lang_path(lang))
            if fname.lower().endswith(extensions)
        }

    def _dict_get(self, obj: dict, key):
        if isinstance(obj, (list, tuple)):
            return obj[int(key, 0)]
        return obj[key]

    def format_from_text(self, text: str, external: dict = None):
        pattern = re.compile(r'(?<!\\)\[([.\w]+)\]|(?<!\\)\{(\w+)\}')
        def repl(m):
            a, k = m.group(1), m.group(2)
            if a:
                keys = a.split('.')
                key = keys.pop(0) if len(keys) > 1 else keys
                for i, sub in enumerate(keys):
                    if isinstance(sub, str) and sub.isdigit():
                        keys[i] = int(sub)
                base = getattr(self, key)
                result = reduce(self._dict_get, keys, base)
                s = str(result)
                if self.base == "jp":
                    if type(result) is int:
                        s = half_to_full_width(s)
            else:
                real_key = int(k) if k.isdigit() else k
                val = (external or {})[real_key]
                s = str(val)
                if self.base == "jp":
                    if type(val) is int:
                        s = half_to_full_width(s)
            return s

        out = text
        while True:
            nxt = pattern.sub(repl, out)
            if nxt == out:
                break
            out = nxt
        return re.sub(r'\\([\[\]\{\}])', r'\1', out)

    def format_from_id(self, id: str, external: dict = None):
        keys = id.split('.')
        if len(keys)>1:
            key = keys.pop(0)
        else:
            key = keys
        base = getattr(self, key)
        i = 0
        while i < len(keys):
            if keys[i].isdigit():
                keys[i] = int(keys[i])
            i += 1
        txt = reduce(self._dict_get, keys, base)
        return self.format_from_text(str(txt), external)
