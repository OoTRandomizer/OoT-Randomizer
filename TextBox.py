from __future__ import annotations
import re
from typing import TYPE_CHECKING

import Messages

if TYPE_CHECKING:
    from Messages import TextCode

# Least common multiple of all possible character widths. A line wrap must occur when the combined widths of all of the
# characters on a line reach this value.
NORMAL_LINE_WIDTH: int = 1801800
NORMAL_LINE_WIDTH_JP: int = 16*16

# Attempting to display more lines in a single text box will cause additional lines to bleed past the bottom of the box.
LINES_PER_BOX: int = 4
LINES_PER_BOX_JP: int = 3

# Attempting to display more characters in a single text box will cause buffer overflows. First, visual artifacts will
# appear in lower areas of the text box. Eventually, the text box will become uncloseable.
MAX_CHARACTERS_PER_BOX: int = 200

CONTROL_CHARS: dict[str, list[str]] = {
    'LINE_BREAK':   ['&', '\x01'],
    'BOX_BREAK':    ['^', '\x04'],
    'NAME':         ['@', '\x0F'],
    'COLOR':        ['#', '\x05\x00'],
}
TEXT_END: str = '\x02'


hex_string_regex: re.Pattern = re.compile(r"\$\{((?:[0-9a-f][0-9a-f] ?)+)}", flags=re.IGNORECASE)


def line_wrap(text: str, lang: str, strip_existing_lines: bool = False, strip_existing_boxes: bool = False, replace_control_chars: bool = True, align: str = "Left"):
    # Replace stand-in characters with their actual control code.
    lang_index = 0 if lang == "jp" else 1
    line_box = LINES_PER_BOX if lang_index else LINES_PER_BOX_JP

    skip_align = [0x81BC, 0x81B8, 0x819A]
    if replace_control_chars and lang_index:
        def replace_bytes(match: re.Match) -> str:
            return ''.join(chr(x) for x in bytes.fromhex(match[1]))

        for char in CONTROL_CHARS.values():
            text = text.replace(char[0], char[1])

        text = hex_string_regex.sub(replace_bytes, text)

    # Parse the text into a list of control codes.
    text_codes = Messages.parse_control_codes(text, lang_index)

    # Existing line/box break codes to strip.
    strip_codes = []
    if strip_existing_boxes:
        strip_codes.append([0x81A5, 0x04][lang_index])
    if strip_existing_lines:
        strip_codes.append([0x0A, 0x01][lang_index])

    # Replace stripped codes with a space.
    if strip_codes:
        index = 0
        while index < len(text_codes):
            text_code = text_codes[index]
            if text_code.code in strip_codes:
                # Check for existing whitespace near this control code.
                # If one is found, simply remove this text code.
                if index > 0 and text_codes[index - 1].code == [0x8170, 0x20][lang_index]:
                    text_codes.pop(index)
                    continue
                if index + 1 < len(text_codes) and text_codes[index + 1].code == [0x8170, 0x20][lang_index]:
                    text_codes.pop(index)
                    continue
                # Replace this text code with a space.
                text_codes[index] = Messages.TextCode([0x8170, 0x20][lang_index], 0, lang_index)
            index += 1

    # Split the text codes by current box breaks.
    boxes = []
    start_index = 0
    end_index = 0
    for text_code in text_codes:
        end_index += 1
        if text_code.code == [0x81A5, 0x04][lang_index]:
            boxes.append(text_codes[start_index:end_index])
            start_index = end_index
    boxes.append(text_codes[start_index:end_index])

    # Split the boxes into lines and words.
    processed_boxes = []
    for box_codes in boxes:
        line_width = NORMAL_LINE_WIDTH if lang_index else NORMAL_LINE_WIDTH_JP
        icon_code = None
        words = []

        # Group the text codes into words.
        index = 0
        align_box = align
        while index < len(box_codes):
            text_code = box_codes[index]
            index += 1

            # Check for an icon code and lower the width of this box if one is found.
            if text_code.code == [0x819A, 0x13][lang_index]:
                line_width = 1441440 if lang_index else 16 * 14
                icon_code = text_code

            if any([tc.code in skip_align for tc in box_codes[index:]]) and not any([tc.code == 0x81A5 for tc in box_codes[index:]]):
                align_box = "Left"

            if calculate_width([box_codes[:index - 1]], lang_index) >= line_width and not lang_index:
                words.append(calculate_align(box_codes[:index], lang_index, line_width, align_box))
                box_codes = box_codes[index:]
                if text_code.code == 0x81A5:
                    align_box = align
                index = 0

            # Find us a whole word.
            if text_code.code in [[0x0A, 0x81A5, 0x8170],[0x01, 0x04, 0x20]][lang_index]:
                if index > 1:
                    words.append(calculate_align(box_codes[:index - 1], lang_index, line_width, align_box))
                if text_code.code in [[0x0A, 0x81A5],[0x01, 0x04]][lang_index]:
                    # If we have run into a line or box break, add it as a "word" as well.
                    words.append([box_codes[index - 1]])
                box_codes = box_codes[index:]
                if text_code.code == 0x81A5:
                    align_box = align
                index = 0
            if index > 0 and index == len(box_codes):
                words.append(calculate_align(box_codes, lang_index, line_width, align_box))
                box_codes = []
                align_box = align

        # Arrange our words into lines.
        lines = []
        start_index = 0
        end_index = 0
        box_count = 1
        while end_index < len(words):
            # Our current confirmed line.
            end_index += 1
            line = words[start_index:end_index]

            # If this word is a line/box break, trim our line back a word and deal with it later.
            break_char = False
            if words[end_index - 1][0].code in [[0x0A, 0x81A5],[0x01, 0x04]][lang_index]:
                line = words[start_index:end_index - 1]
                break_char = True

            # Check the width of the line after adding one more word.
            if end_index == len(words) or break_char or (calculate_width(words[start_index:end_index + 1], lang_index) >= line_width):
                if line or lines:
                    lines.append(line)
                start_index = end_index

            # If we've reached the end of the box, finalize it.
            if end_index == len(words) or words[end_index - 1][0].code == [0x81A5, 0x04][lang_index] or len(lines) == line_box:
                # Append the same icon to any wrapped boxes.
                if icon_code and box_count > 1:
                    lines[0][0] = [icon_code] + lines[0][0]
                processed_boxes.append(lines)
                lines = []
                box_count += 1
    # Construct our final string.
    # This is a hideous level of list comprehension. Sorry.
    if lang_index: return '\x04'.join(['\x01'.join([' '.join([''.join([code.get_string() for code in word]) for word in line]) for line in box]) for box in processed_boxes])
    else: return '^'.join(['&'.join([''.join([''.join([code.get_string() for code in word]) for word in line]) for line in box]) for box in processed_boxes]).replace("&&", "&").replace("^^", "^").replace("&^", "^")


def calculate_width(words: list[list[TextCode]], lang: str|int):
    words_width = 0
    lang_index = 1 if lang in ["en", 1] else 0
    CC = Messages.CONTROL_CODES if lang_index else Messages.CC_PARSE_JP
    for word in words:
        index = 0
        while index < len(word):
            character = word[index]
            index += 1
            if character.code in CC:
                if character.code == [0x86C7, 0x06][lang_index]:
                    words_width += character.data
            words_width += get_character_width(chr(character.code) if lang_index else character.code, lang_index)
    spaces_width = get_character_width(' ', lang_index) * (len(words) - 1) if lang_index else 0
    return words_width + spaces_width


def get_character_width(character: str|int, lang: str|int) -> int:
    if lang in ["en", 1]:
        try:
            return character_table[character]
        except KeyError:
            if character in Messages.CONTROL_CODES:
                if character in control_code_width:
                    return sum([character_table[c] for c in control_code_width[character]])
                else:
                    return 0
            else:
                # A sane default with the most common character width
                return character_table[' ']
    else:
        if character in Messages.CC_PARSE_JP:
            if character in control_code_width:
                return 16 * len(control_code_width[character])
            else:
                return 0
        else:
            # A sane default with the most common character width
            if character in character_table:
                return character_table[character]
            return 16

def calculate_align(words, lang: int, line_width:int, align:str="Left"):
    if align == "Left":
        return words
    word_codes = [w.code for w in words]
    if [0x86C7, 0x06][lang] in word_codes:
        words.pop(word_codes.index([0x86C7, 0x06][lang]))
    h = calculate_width([words], lang)
    g = line_width - h
    if g <= 0:
        return words
    if lang:
        g = g * 16 // 120120
    align_code = Messages.TextCode([0x86C7, 0x06][lang], int(g // 2 if align == "Center" else g), lang)
    return [align_code] + words

control_code_width: dict[str|int, str] = {
    '\x0F': '00000000',
    '\x16': '00\'00"',
    '\x17': '00\'00"',
    '\x18': '00000',
    '\x19': '100',
    '\x1D': '00',
    '\x1E': '00000',
    '\x1F': '00\'00"',
    '\xF0': '10',
    '\xF1': '0',
    '\xF2': '00000000',
    0x874F: '00000000',
    0x8791: '00\'00"',
    0x8792: '00\'00"',
    0x879B: '00000',
    0x86A3: '100',
    0x86A4: '00',
    0x869F: '00000',
    0x81A1: '00\'00"',
    0x87F0: '10',
    0x87F1: '0',
    0x87F2: '00000000',
}


# Tediously measured by filling a full line of a gossip stone's text box with one character until it is reasonably full
# (with a right margin) and counting how many characters fit. OoT does not appear to use any kerning, but, if it does,
# it will only make the characters more space-efficient, so this is an underestimate of the number of letters per line,
# at worst. This ensures that we will never bleed text out of the text box while line wrapping.
# Larger numbers in the denominator mean more of that character fits on a line; conversely, larger values in this table
# mean the character is wider and can't fit as many on one line.
character_table: dict[str|int, int] = {
    '\x0F': 655200,
    '\x16': 292215,
    '\x17': 292215,
    '\x18': 300300,
    '\x19': 145860,
    '\x1D': 85800,
    '\x1E': 300300,
    '\x1F': 265980,
    'a':  51480,  # LINE_WIDTH /  35
    'b':  51480,  # LINE_WIDTH /  35
    'c':  51480,  # LINE_WIDTH /  35
    'd':  51480,  # LINE_WIDTH /  35
    'e':  51480,  # LINE_WIDTH /  35
    'f':  34650,  # LINE_WIDTH /  52
    'g':  51480,  # LINE_WIDTH /  35
    'h':  51480,  # LINE_WIDTH /  35
    'i':  25740,  # LINE_WIDTH /  70
    'j':  34650,  # LINE_WIDTH /  52
    'k':  51480,  # LINE_WIDTH /  35
    'l':  25740,  # LINE_WIDTH /  70
    'm':  81900,  # LINE_WIDTH /  22
    'n':  51480,  # LINE_WIDTH /  35
    'o':  51480,  # LINE_WIDTH /  35
    'p':  51480,  # LINE_WIDTH /  35
    'q':  51480,  # LINE_WIDTH /  35
    'r':  42900,  # LINE_WIDTH /  42
    's':  51480,  # LINE_WIDTH /  35
    't':  42900,  # LINE_WIDTH /  42
    'u':  51480,  # LINE_WIDTH /  35
    'v':  51480,  # LINE_WIDTH /  35
    'w':  81900,  # LINE_WIDTH /  22
    'x':  51480,  # LINE_WIDTH /  35
    'y':  51480,  # LINE_WIDTH /  35
    'z':  51480,  # LINE_WIDTH /  35
    'A':  81900,  # LINE_WIDTH /  22
    'B':  51480,  # LINE_WIDTH /  35
    'C':  72072,  # LINE_WIDTH /  25
    'D':  72072,  # LINE_WIDTH /  25
    'E':  51480,  # LINE_WIDTH /  35
    'F':  51480,  # LINE_WIDTH /  35
    'G':  81900,  # LINE_WIDTH /  22
    'H':  60060,  # LINE_WIDTH /  30
    'I':  25740,  # LINE_WIDTH /  70
    'J':  51480,  # LINE_WIDTH /  35
    'K':  60060,  # LINE_WIDTH /  30
    'L':  51480,  # LINE_WIDTH /  35
    'M':  81900,  # LINE_WIDTH /  22
    'N':  72072,  # LINE_WIDTH /  25
    'O':  81900,  # LINE_WIDTH /  22
    'P':  51480,  # LINE_WIDTH /  35
    'Q':  81900,  # LINE_WIDTH /  22
    'R':  60060,  # LINE_WIDTH /  30
    'S':  60060,  # LINE_WIDTH /  30
    'T':  51480,  # LINE_WIDTH /  35
    'U':  60060,  # LINE_WIDTH /  30
    'V':  72072,  # LINE_WIDTH /  25
    'W': 100100,  # LINE_WIDTH /  18
    'X':  72072,  # LINE_WIDTH /  25
    'Y':  60060,  # LINE_WIDTH /  30
    'Z':  60060,  # LINE_WIDTH /  30
    ' ':  51480,  # LINE_WIDTH /  35
    '1':  25740,  # LINE_WIDTH /  70
    '2':  51480,  # LINE_WIDTH /  35
    '3':  51480,  # LINE_WIDTH /  35
    '4':  60060,  # LINE_WIDTH /  30
    '5':  51480,  # LINE_WIDTH /  35
    '6':  51480,  # LINE_WIDTH /  35
    '7':  51480,  # LINE_WIDTH /  35
    '8':  51480,  # LINE_WIDTH /  35
    '9':  51480,  # LINE_WIDTH /  35
    '0':  60060,  # LINE_WIDTH /  30
    '!':  51480,  # LINE_WIDTH /  35
    '?':  72072,  # LINE_WIDTH /  25
    '\'': 17325,  # LINE_WIDTH / 104
    '"':  34650,  # LINE_WIDTH /  52
    '.':  25740,  # LINE_WIDTH /  70
    ',':  25740,  # LINE_WIDTH /  70
    '/':  51480,  # LINE_WIDTH /  35
    '-':  34650,  # LINE_WIDTH /  52
    '_':  51480,  # LINE_WIDTH /  35
    '(':  42900,  # LINE_WIDTH /  42
    ')':  42900,  # LINE_WIDTH /  42
    '$':  51480,  # LINE_WIDTH /  35
    '\xF2': 655200,
    0x8140: 6, # '　'
    0x8141: 7, # '、'
    0x8142: 7, # '。'
    0x8144: 3, # '．'
    0x8145: 7, # '・'
    0x8148: 14,# '？'
    0x8149: 14,# '！'
    0x814F: 7, # '＾'
    0x8167: 7, # '“'
    0x8168: 7, # '”'
    0x8169: 10, # '（'
    0x816A: 5, # '）'
    0x8175: 10, # '「'
    0x8176: 5, # '」'
    0x8194: 9, # '＃'
    0x8196: 9, # '＊'
    0x8250: 14 # '１'
}

trans_map = str.maketrans(
    { chr(0x21 + i): chr(0xFF01 + i) for i in range(94) }
)

character_table_jp = {}
for ch, ap in character_table.items():
    if type(ch) != str: continue
    if len(ch) == 1 and not ch.isprintable():
        continue
    try:
        key = str(ch).translate(trans_map).encode("cp932")
    except:
        continue

    character_table_jp[key] = ap

# To run tests, enter the following into a python3 REPL:
# >>> import Messages
# >>> from TextBox import line_wrap_tests
# >>> line_wrap_tests()
def line_wrap_tests(lang) -> None:
    test_wrap_simple_line(lang)
    test_honor_forced_line_wraps(lang)
    test_honor_box_breaks(lang)
    test_honor_control_characters(lang)
    test_honor_player_name(lang)
    test_maintain_multiple_forced_breaks(lang)
    test_trim_whitespace(lang)
    test_support_long_words(lang)


def test_wrap_simple_line(lang) -> None:
    if lang == "jp":
        words = 'あいうえおかきくけこさしすせそたちつてと'
        expected = 'あいうえおかきくけこさしすせそた&ちつてと'
    else:
        words = 'Hello World! Hello World! Hello World!'
        expected = 'Hello World! Hello World! Hello\x01World!'
    result = line_wrap(words, lang)

    if result != expected:
        print('"Wrap Simple Line" test failed: Got ' + result + ', wanted ' + expected)
    else:
        print('"Wrap Simple Line" test passed!')


def test_honor_forced_line_wraps(lang) -> None:
    if lang == "jp":
        words = 'あいう&えおかきくけこさしすせそたちつてとなにぬねの'
        expected = 'あいう&えおかきくけこさしすせそたちつて&と'
    else:
        words = 'Hello World! Hello World!&Hello World! Hello World! Hello World!'
        expected = 'Hello World! Hello World!\x01Hello World! Hello World! Hello\x01World!'
    result = line_wrap(words, lang)

    if result != expected:
        print('"Honor Forced Line Wraps" test failed: Got ' + result + ', wanted ' + expected)
    else:
        print('"Honor Forced Line Wraps" test passed!')


def test_honor_box_breaks(lang) -> None:
    if lang == "jp":
        words = 'あいう^えおかきくけこさしすせそたちつてとなにぬねの'
        expected = 'あいう^えおかきくけこさしすせそたちつて&と'
    else:
        words = 'Hello World! Hello World!^Hello World! Hello World! Hello World!'
        expected = 'Hello World! Hello World!\x04Hello World! Hello World! Hello\x01World!'
    result = line_wrap(words, lang)

    if result != expected:
        print('"Honor Box Breaks" test failed: Got ' + result + ', wanted ' + expected)
    else:
        print('"Honor Box Breaks" test passed!')


def test_honor_control_characters(lang) -> None:
    if lang == "jp":
        words = 'あいうえお#01かきくけこ#00さしすせそたちつてと'
        expected = 'あいうえお#01かきくけこ#00さしすせそた&ちつてと'
    else:
        words = 'Hello World! #Hello# World! Hello World!'
        expected = 'Hello World! \x05\x00Hello\x05\x00 World! Hello\x01World!'
    result = line_wrap(words, lang)

    if result != expected:
        print('"Honor Control Characters" test failed: Got ' + result + ', wanted ' + expected)
    else:
        print('"Honor Control Characters" test passed!')


def test_honor_player_name(lang) -> None:
    if lang == "jp":
        words = 'あいうえお@さしすせそたちつてと'
        expected = 'あいうえお@さしすせそた&ちつてと'
    else:
        words = 'Hello @! Hello World! Hello World!'
        expected = 'Hello \x0F! Hello World!\x01Hello World!'
    result = line_wrap(words, lang)

    if result != expected:
        print('"Honor Player Name" test failed: Got ' + result + ', wanted ' + expected)
    else:
        print('"Honor Player Name" test passed!')


def test_maintain_multiple_forced_breaks(lang) -> None:
    if lang == "jp":
        words = 'あいうえお&&&かきくけこさしすせそたちつてと'
        expected = 'あいうえお&&^かきくけこさしすせそたちつてと'
    else:
        words = 'Hello World!&&&Hello World!'
        expected = 'Hello World!\x01\x01\x01Hello World!'
    result = line_wrap(words, lang)

    if result != expected:
        print('"Maintain Multiple Forced Breaks" test failed: Got ' + result + ', wanted ' + expected)
    else:
        print('"Maintain Multiple Forced Breaks" test passed!')


def test_trim_whitespace(lang) -> None:
    if lang == "jp":
        words = 'あいうえおかきく　けこさしすせそたちつてと'
        expected = 'あいうえおかきく　けこさしすせそ&たちつてと'
    else:
        words = 'Hello World! & Hello World!'
        expected = 'Hello World!\x01Hello World!'
    result = line_wrap(words, lang)

    if result != expected:
        print('"Trim Whitespace" test failed: Got ' + result + ', wanted ' + expected)
    else:
        print('"Trim Whitespace" test passed!')


def test_support_long_words(lang) -> None:
    if lang == "jp":
        words = 'あいうえおかきくけこさしすせそたちつてと'
        expected = 'あいうえおかきくけこさしすせそた&ちつてと'
    else:
        words = 'Hello World! WWWWWWWWWWWWWWWWWWWW Hello World!'
        expected = 'Hello World!\x01WWWWWWWWWWWWWWWWWWWW\x01Hello World!'
    result = line_wrap(words, lang)

    if result != expected:
        print('"Support Long Words" test failed: Got ' + result + ', wanted ' + expected)
    else:
        print('"Support Long Words" test passed!')
