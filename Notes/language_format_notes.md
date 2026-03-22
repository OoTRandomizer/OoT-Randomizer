# `Language` Syntax Rules

## Overview

The formatter supports two kinds of placeholders:

* `[]` → evaluate an **internal expression / path**
* `{}` → insert an **external value**

In the source file, the intended rule is:

```text
[] >> replace using internal dict phrase / expression
{} >> replace using external phrase
```

---

## 1. Curly braces: external placeholders

Use `{name}` to insert a value from the `external` dictionary passed to `format_from_text()` or `format_from_id()`.

### Example

```text
"{dungeon_name}"
```

with:

```python
external = {"dungeon_name": "Forest Temple"}
```

becomes:

```text
Forest Temple
```

### Notes

* Numeric keys are also supported:

  ```text
  "{0}"
  ```
* Outside expression mode, the value is converted with `str(...)`
* In Japanese base mode, integers are converted to full-width digits

---

## 2. Square brackets: internal expressions

`[]` evaluates an expression using a restricted AST evaluator.

### Example

```text
"[PATCH_TEXTS.ordinary]"
"[prefix.prefix.definite.accusative.feminine]"
"['Das' if dungeon_state == [PATCH_TEXTS.ordinary] else 'Es']"
```

---

## 3. Supported expression features inside `[]`

The evaluator supports:

* constants
* names
* attribute access
* subscript access
* lists / tuples / dicts / sets
* boolean operators
* comparisons
* unary `not`
* conditional expressions

### Supported examples

```text
"[prefix.prefix.definite.accusative.feminine]"
"[items.0]"
"[foo['bar']]"          # if produced as valid Python expression
"['Das' if x == y else 'Es']"
```

---

## 4. Path-style shorthand

A common use of `[]` is the dot-path shorthand:

```text
[prefix.prefix.definite.accusative.feminine]
```

This is translated internally into a Python-style access chain.

### Special path token rules

* numeric path tokens become indexes:

  ```text
  [items.0]
  ```

* `{name}` inside a path becomes dynamic indexing:

  ```text
  [prefix.prefix.definite.{position}.feminine]
  ```

  which is treated like:

  ```python
  prefix.prefix.definite[position].feminine
  ```

* `None`, `True`, `False` used as path tokens are treated as literal keys/indexes:

  ```text
  [prefix.prefix.definite.accusative.None]
  ```

---

## 5. Allowed zero-argument string methods

Inside `[]`, these zero-argument methods are allowed:

* `capitalize()`
* `lower()`
* `upper()`
* `title()`
* `swapcase()`
* `casefold()`
* `strip()`
* `lstrip()`
* `rstrip()`

### Example

```text
"[format({location_text}, {'position': 'nominative'}).capitalize()]"
```

### Important caveat

`capitalize()` is Python’s normal `str.capitalize()`, so it:

* uppercases the first character
* lowercases the rest

So:

```python
"Ganons Schloß".capitalize()
```

becomes:

```text
Ganons schloß
```

---

## 6. Allowed function calls inside `[]`

Currently, the allowed named function is:

* `format(...)`

### Syntax

```text
[format({item_text}, {'position': 'accusative'})]
```

### Meaning

This calls `Language.format_from_text()` again on the first argument, using the second argument as a new external dictionary.

So this:

```text
[format({item_text}, {'position': 'accusative'})]
```

is intended for values like:

```text
"[prefix.prefix.definite.{position}.masculine] Kokiri-Smaragd"
```

which then resolve to something like:

```text
den Kokiri-Smaragd
```

### Current behavior

* first argument: any value, converted to `str(...)`
* second argument: must be `dict` or `None`

---

## 7. Dict literals inside `[]`

When parsing `[]`, the formatter distinguishes between:

* simple external placeholders like `{item_text}`
* actual dict literals like `{'position': 'accusative'}`

This is necessary so expressions like this work:

```text
[format({item_text}, {'position': 'accusative'})]
```

and the second `{...}` is **not** mistaken for an external placeholder.

### Rule

In expression mode:

* `{name}` or `{0}` → treated as external placeholder
* more complex `{...}` → left as Python dict/object syntax

---

## 8. Nested formatting with `format(...)`

This is the main pattern for grammar-aware text.

### Example

```text
"Er birgt [format({dungeon_reward}, {'position': 'accusative'})]!"
```

If:

```python
external = {
    "dungeon_reward": "[prefix.prefix.definite.{position}.masculine] Kokiri-Smaragd"
}
```

then the nested `format(...)` resolves the inner grammar placeholder.

---

## 9. Escaping special characters

The parser supports escaping these characters:

* `\[`
* `\]`
* `\{`
* `\}`

After formatting, these are unescaped back into literal characters.

### Example

```text
"\[Not a tag\]"
```

becomes:

```text
[Not a tag]
```

---

## 10. `format_from_text()` behavior

### Signature

```python
format_from_text(text: str, external: dict | None = None)
```

### Flow

1. resolve `[]` and `{}`
2. unescape `\[` `\]` `\{` `\}`
3. apply `language_specific_replace_table`
4. return final string

---

## 11. `format_from_id()` behavior

### Signature

```python
format_from_id(id: str, external: dict | None = None)
```

### Meaning

It resolves a dotted ID path from the loaded language data, then passes that text into `format_from_text()`.

### Example

```python
format_from_id("PATCH_TEXTS.map", external=...)
```

---

## 12. Current practical conventions

### Item / reward strings

Use embedded grammar placeholders inside the stored text:

```text
"[prefix.prefix.definite.{position}.masculine] Kokiri-Smaragd"
```

Then resolve them at call site:

```text
[format({dungeon_reward}, {'position': 'accusative'})]
```

### Location strings

If a location string is stored as a format-ready phrase, use:

```text
[format({location_text}, {'position': 'nominative'})]
[format({location_text}, {'position': 'dative'})]
```

### Capitalized sentence starts

Current convention is:

```text
[format({location_text}, {'position': 'nominative'}).capitalize()]
```

---

## 13. Common failure modes

### A. Raw object in `{}` inside `[]`

If an external value is not a plain string and gets inserted inside `[]`, it can become invalid Python syntax.

Example failure:

```text
format(<Hints.GossipText object at 0x...>, {'position': 'accusative'})
```

This causes `SyntaxError`.

### B. Missing keys in grammar paths

Example:

```text
[prefix.prefix.definite.{position}.feminine]
```

If `position` or a required nested key is missing, evaluation fails.

### C. `capitalize()` lowercasing the rest

This may unintentionally damage proper nouns.

### D. Passing only partial external data to nested `format(...)`

If the inner text needs more than the second-argument dict provides, formatting may fail unless the implementation merges outer and inner external values.

---

## 14. Recommended writing style for templates

### Good

```text
"Er birgt [format({dungeon_reward}, {'position': 'accusative'})]!"
```

```text
"[prefix.prefix.definite.{position}.feminine] Eishöhle"
```

```text
"[format({location_text}, {'position': 'nominative'}).capitalize()] liegt auf dem Weg des Helden."
```

### Avoid

```text
"{dungeon_reward}.external(...)"
```

because that is not part of the current implementation.

---

## 15. Summary

### `{}`

Use for **external values**

### `[]`

Use for:

* internal lookups
* restricted expressions
* grammar-aware nested formatting
* allowed string methods
* `format(...)`

### Current core grammar pattern

```text
stored text:  "[prefix.prefix.definite.{position}.masculine] Kokiri-Smaragd"
usage:        [format({item_text}, {'position': 'accusative'})]
result:       den Kokiri-Smaragd
```