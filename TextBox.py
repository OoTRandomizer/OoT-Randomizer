import Messages
import re

# Least common multiple of all possible character widths. A line wrap must occur when the combined widths of all of the
# characters on a line reach this value.
NORMAL_LINE_WIDTH = 1801800

# Attempting to display more lines in a single text box will cause additional lines to bleed past the bottom of the box.
LINES_PER_BOX = 4

# Attempting to display more characters in a single text box will cause buffer overflows. First, visual artifacts will
# appear in lower areas of the text box. Eventually, the text box will become uncloseable.
MAX_CHARACTERS_PER_BOX = 200

CONTROL_CHARS = {
    'LINE_BREAK':   ['&', '\x01'],
    'BOX_BREAK':    ['^', '\x04'],
    'NAME':         ['@', '\x0F'],
    'COLOR':        ['#', '\x05\x00'],
}
TEXT_END = '\x02'

character_table_jp = {
    'a':  6, # LINE_WIDTH /  35
    'b':  6, # LINE_WIDTH /  35
    'c':  6, # LINE_WIDTH /  35
    'd':  6, # LINE_WIDTH /  35
    'e':  6, # LINE_WIDTH /  35
    'f':  9, # LINE_WIDTH /  52
    'g':  6, # LINE_WIDTH /  35
    'h':  6, # LINE_WIDTH /  35
    'i':  12, # LINE_WIDTH /  70
    'j':  9, # LINE_WIDTH /  52
    'k':  6, # LINE_WIDTH /  35
    'l':  12, # LINE_WIDTH /  70
    'm':  0, # LINE_WIDTH /  22
    'n':  6, # LINE_WIDTH /  35
    'o':  6, # LINE_WIDTH /  35
    'p':  6, # LINE_WIDTH /  35
    'q':  6, # LINE_WIDTH /  35
    'r':  8, # LINE_WIDTH /  42
    's':  6, # LINE_WIDTH /  35
    't':  8, # LINE_WIDTH /  42
    'u':  6, # LINE_WIDTH /  35
    'v':  6, # LINE_WIDTH /  35
    'w':  0, # LINE_WIDTH /  22
    'x':  6, # LINE_WIDTH /  35
    'y':  6, # LINE_WIDTH /  35
    'z':  6, # LINE_WIDTH /  35
    'A':  0, # LINE_WIDTH /  22
    'B':  6, # LINE_WIDTH /  35
    'C':  2, # LINE_WIDTH /  25
    'D':  2, # LINE_WIDTH /  25
    'E':  6, # LINE_WIDTH /  35
    'F':  6, # LINE_WIDTH /  35
    'G':  0, # LINE_WIDTH /  22
    'H':  4, # LINE_WIDTH /  30
    'I':  12, # LINE_WIDTH /  70
    'J':  6, # LINE_WIDTH /  35
    'K':  4, # LINE_WIDTH /  30
    'L':  6, # LINE_WIDTH /  35
    'M':  0, # LINE_WIDTH /  22
    'N':  2, # LINE_WIDTH /  25
    'O':  0, # LINE_WIDTH /  22
    'P':  6, # LINE_WIDTH /  35
    'Q':  0, # LINE_WIDTH /  22
    'R':  4, # LINE_WIDTH /  30
    'S':  4, # LINE_WIDTH /  30
    'T':  6, # LINE_WIDTH /  35
    'U':  4, # LINE_WIDTH /  30
    'V':  2, # LINE_WIDTH /  25
    'W': -4, # LINE_WIDTH /  18
    'X':  2, # LINE_WIDTH /  25
    'Y':  4, # LINE_WIDTH /  30
    'Z':  4, # LINE_WIDTH /  30
    ' ':  6, # LINE_WIDTH /  35
    '1':  12, # LINE_WIDTH /  70
    '2':  6, # LINE_WIDTH /  35
    '3':  6, # LINE_WIDTH /  35
    '4':  4, # LINE_WIDTH /  30
    '5':  6, # LINE_WIDTH /  35
    '6':  6, # LINE_WIDTH /  35
    '7':  6, # LINE_WIDTH /  35
    '8':  6, # LINE_WIDTH /  35
    '9':  6, # LINE_WIDTH /  35
    '0':  4, # LINE_WIDTH /  30
    '!':  6, # LINE_WIDTH /  35
    '?':  2, # LINE_WIDTH /  25
    '\'': 14, # LINE_WIDTH / 104
    '"':  10, # LINE_WIDTH /  52
    '.':  12, # LINE_WIDTH /  70
    ',':  12, # LINE_WIDTH /  70
    '/':  6, # LINE_WIDTH /  35
    '-':  10, # LINE_WIDTH /  52
    '_':  6, # LINE_WIDTH /  35
    '(':  8, # LINE_WIDTH /  42
    ')':  8, # LINE_WIDTH /  42
    '$':  6  # LINE_WIDTH /  35
}

CONTROL_PARSE_JP = {
    'LINE_BREAK':   ['&', 0],
    'BOX_BREAK':    ['^', 0],
    'COLOR':        ['#', -1],
    'ENDMARK':      ['|', 0],
    'ICON':         ['~', -1],
    'INSTANTSTART': ['<', 0],
    'INSTANTEND':   ['>', 0],
    'SOUND':        ['$', -2],
    'DELAY_BOX':    ['[', -1],
    'PREVENT':      [']', 0],
    'EVENT':        ['{', 0],
    'PRINT_T':      ['@T', 6],
    'THREE_C':      [':3', 0],
    'TWO_C':        [':2', 0],
    'GO_MESSAGE':   ['}', -2],
    'FADE_OUT':     ['*F', -1],
    'NAME':         ['@N', 8],
    'PRINT_M':      ['@M', 6],
    'PRINT_R':      ['@R', 6],
    'PRINT_G':      ['@G', 3],
    'PRINT_P':      ['@P', 5],
    'PRINT_H':      ['@H', 4],
    'PRINT_L':      ['@L', 3],
    'SETBACK':      ['@B', -3],
    'SETSPEED':     ['+S', -1],
    'SHIFT_TEXT':   ['+T', -1],
    'OCARINA':      [':O', 0],
    'KEEP_OPEN':    ['*O', 0],
}
CONTROL_PARSE_JP_1 = {
    'LINE_BREAK':   ['&&', 0],
    'BOX_BREAK':    ['^^', 0],
    'COLOR':        ['##', -1],
    'ENDMARK':      ['||', 0],
    'ICON':         ['~~', -1],
    'INSTANTSTART': ['<<', 0],
    'INSTANTEND':   ['>>', 0],
    'SOUND':        ['$$', -2],
    'DELAY_BOX':    ['[[', -1],
    'PREVENT':      [']]', 0],
    'EVENT':        ['{', 0],
    'PRINT_T':      ['@T', 6],
    'THREE_C':      [':3', 0],
    'TWO_C':        [':2', 0],
    'GO_MESSAGE':   ['}}', -2],
    'FADE_OUT':     ['*F', -1],
    'NAME':         ['@N', 8],
    'PRINT_M':      ['@M', 6],
    'PRINT_R':      ['@R', 6],
    'PRINT_G':      ['@G', 3],
    'PRINT_P':      ['@P', 5],
    'PRINT_H':      ['@H', 4],
    'PRINT_L':      ['@L', 3],
    'SETBACK':      ['@B', -3],
    'SETSPEED':     ['+S', -1],
    'SHIFT_TEXT':   ['+T', -1],
    'OCARINA':      [':O', 0],
    'KEEP_OPEN':    ['*O', 0],
}

def line_wrap(text, strip_existing_lines=False, strip_existing_boxes=False, replace_control_chars=True):
    # Replace stand-in characters with their actual control code.
    if replace_control_chars:
        def replace_bytes(matchobj):
            return ''.join(chr(x) for x in bytes.fromhex(matchobj[1]))

        for char in CONTROL_CHARS.values():
            text = text.replace(char[0], char[1])

        text = re.sub(r"\$\{((?:[0-9a-f][0-9a-f] ?)+)}", replace_bytes, text, flags=re.IGNORECASE)

    # Parse the text into a list of control codes.
    text_codes = Messages.parse_control_codes(text)

    # Existing line/box break codes to strip.
    strip_codes = []
    if strip_existing_boxes:
        strip_codes.append(0x04)
    if strip_existing_lines:
        strip_codes.append(0x01)

    # Replace stripped codes with a space.
    if strip_codes:
        index = 0
        while index < len(text_codes):
            text_code = text_codes[index]
            if text_code.code in strip_codes:
                # Check for existing whitespace near this control code.
                # If one is found, simply remove this text code.
                if index > 0 and text_codes[index-1].code == 0x20:
                    text_codes.pop(index)
                    continue
                if index + 1 < len(text_codes) and text_codes[index+1].code == 0x20:
                    text_codes.pop(index)
                    continue
                # Replace this text code with a space.
                text_codes[index] = Messages.Text_Code(0x20, 0)
            index += 1

    # Split the text codes by current box breaks.
    boxes = []
    start_index = 0
    end_index = 0
    for text_code in text_codes:
        end_index += 1
        if text_code.code == 0x04:
            boxes.append(text_codes[start_index:end_index])
            start_index = end_index
    boxes.append(text_codes[start_index:end_index])

    # Split the boxes into lines and words.
    processed_boxes = []
    for box_codes in boxes:
        line_width = NORMAL_LINE_WIDTH
        icon_code = None
        words = []

        # Group the text codes into words.
        index = 0
        while index < len(box_codes):
            text_code = box_codes[index]
            index += 1

            # Check for an icon code and lower the width of this box if one is found.
            if text_code.code == 0x13:
                line_width = 1441440
                icon_code = text_code

            # Find us a whole word.
            if text_code.code in [0x01, 0x04, 0x20]:
                if index > 1:
                    words.append(box_codes[0:index-1])
                if text_code.code in [0x01, 0x04]:
                    # If we have ran into a line or box break, add it as a "word" as well.
                    words.append([box_codes[index-1]])
                box_codes = box_codes[index:]
                index = 0
            if index > 0 and index == len(box_codes):
                words.append(box_codes)
                box_codes = []

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
            if words[end_index-1][0].code in [0x01, 0x04]:
                line = words[start_index:end_index-1]
                break_char = True

            # Check the width of the line after adding one more word.
            if end_index == len(words) or break_char or calculate_width(words[start_index:end_index+1]) > line_width:
                if line or lines:
                    lines.append(line)
                start_index = end_index

            # If we've reached the end of the box, finalize it.
            if end_index == len(words) or words[end_index-1][0].code == 0x04 or len(lines) == LINES_PER_BOX:
                # Append the same icon to any wrapped boxes.
                if icon_code and box_count > 1:
                    lines[0][0] = [icon_code] + lines[0][0]
                processed_boxes.append(lines)
                lines = []
                box_count += 1

    # Construct our final string.
    # This is a hideous level of list comprehension. Sorry.
    return '\x04'.join(['\x01'.join([' '.join([''.join([code.get_string() for code in word]) for word in line]) for line in box]) for box in processed_boxes])

def halflen(text, mode=0):
    t = 0
    if mode == 0:
        for char in CONTROL_PARSE_JP.values():
            text = text.replace(char[0],"")
    elif mode == 1:
        for char in CONTROL_PARSE_JP_1.values():
            text = text.replace(char[0],"")
    for char in character_table_jp:
        num = character_table_jp[char]
        charf = str(char[0]).translate(str.maketrans({chr(0x0021 + i): chr(0xFF01 + i) for i in range(94)}))
        if char[0] in text:
            t += text.count(char[0]) * num
        elif charf in text:
            t += text.count(charf) * num
    return t
    
def charlen(text, leng=0, mode=0):
    i = 0
    n = 1
    e = ""
    a = 0
    q = 0
    get = 0
    if mode == 0:
        if leng <= 0:
            for char in CONTROL_PARSE_JP.values():
                if char[0] in text:
                    i += text.count(char[0]) * char[1]
                    text = text.replace(char[0],"")
            i += len(text)
        elif leng > 0:
            if leng >= charlen(text):
                i = len(text)
            elif leng < charlen(text):
                while n <= len(text):
                    get = charlen(text[:n])
                    if get < leng:
                        pass
                    elif get == leng:
                        e = text[:n + 1]
                        if charlen(e) <= get:
                            pass
                        elif get < charlen(e):
                            for char in CONTROL_PARSE_JP.values():
                                if e.endswith(char[0]):
                                    i = n-1
                                    q = 1
                                    break
                            if q != 0:
                                break
                            elif q == 0:
                                i = n
                                break
                    elif get > leng:
                        for char in CONTROL_PARSE_JP.values():
                            if text[:n].endswith(char[0]):
                                a = len(char[0])
                                i = n - a
                                break
                        if charlen(text[:n-a]) > leng:
                            raise(TypeError("%s" % text))
                        else:
                            break
                    n += 1
    elif mode == 1:
        if leng <= 0:
            for char in CONTROL_PARSE_JP_1.values():
                if char[0] in text:
                    i += text.count(char[0]) * char[1]
                    text = text.replace(char[0],"")
            i += len(text)
        elif leng > 0:
            if leng >= charlen(text):
                i = len(text)
            elif leng < charlen(text):
                while n <= len(text):
                    get = charlen(text[:n])
                    if get < leng:
                        pass
                    elif get == leng:
                        e = text[:n + 1]
                        if charlen(e) <= get:
                            pass
                        elif get < charlen(e):
                            for char in CONTROL_PARSE_JP_1.values():
                                if e.endswith(char[0]):
                                    i = n-1
                                    q = 1
                                    break
                            if q != 0:
                                break
                            elif q == 0:
                                i = n
                                break
                    elif get > leng:
                        for char in CONTROL_PARSE_JP_1.values():
                            if text[:n].endswith(char[0]):
                                a = len(char[0])
                                i = n - a
                                break
                        if charlen(text[:n-a]) > leng:
                            raise(TypeError("%s" % text))
                        else:
                            break
                    n += 1
    return i
    
def linewrapJP(text, mode=0, align="left"):
    LINE = 15
    instant = 0
    alone = align
    if "~" in text:
        LINE = 12
        if align == "center":
            alone = "left"
    if text.startswith("<<"):
        text = text.replace("<<","<",1)
    if text.startswith("<"):
        instant = 1
        text = text.replace("<","",1)
    i = 1
    n = 1
    p = 0
    k = 0
    j = 0
    w = 0
    tex = {}
    box = {}
    shift = ""
    if mode == 0:
        splitbox = text.split("^")
        while n <= text.count("^") + 1:
            if (":2" or ":3" or ":O") in splitbox[n-1]:
                splitbox[n-1] = splitbox[n-1]
            elif "&" in splitbox[n-1] and (":2" or ":3" or ":O" )not in splitbox[n-1]:
                splitline = splitbox[n-1].split("&")
                while i <= splitbox[n-1].count("&") + 1:
                    if charlen(splitline[i-1])-2 <= LINE:
                        if i % 3 == 0:
                            if "~" not in text:
                                if alone == "left":
                                    if "+T" in splitline[i-1]:
                                        splitline[i-1] = splitline[i-1][3:] + "^<"
                                    elif "+T" not in splitline[i-1]:
                                        splitline[i-1] = splitline[i-1] + "^<"
                                elif alone == "center":
                                    w = format((LINE - charlen(splitline[i-1]))*8 + int(halflen(splitline[i-1]) / 2),"02x")
                                    if w != "00" and not "-" in w:
                                        shift = r"+T\x{}".format(w)
                                    elif w == "00" or "-" in w:
                                        shift = ""
                                    if "+T" in splitline[i-1]:
                                        splitline[i-1] = shift + splitline[i-1][3:] + "^<"
                                    elif "+T" not in splitline[i-1]:
                                        splitline[i-1] = shift + splitline[i-1] + "^<"
                                elif alone == "right":
                                    w = format((LINE - charlen(splitline[i-1]))*16 + halflen(splitline[i-1]),"02x")
                                    if w != "00" and not "-" in w:
                                        shift = r"+T\x{}".format(w)
                                    elif w == "00" or "-" in w:
                                        shift = ""
                                    if "+T" in splitline[i-1]:
                                        splitline[i-1] = shift + splitline[i-1][3:] + "^<"
                                    elif "+T" not in splitline[i-1]:
                                        splitline[i-1] = shift + splitline[i-1] + "^<"
                            elif "~" in text:
                                splitline[i-1] = splitline[i-1] + "^<"
                        elif i % 3 != 0:
                            if "~" not in text:
                                if alone == "left":
                                    if "+T" in splitline[i-1]:
                                        splitline[i-1] = splitline[i-1][3:] + "&"
                                    elif "+T" not in splitline[i-1]:
                                        splitline[i-1] = splitline[i-1] + "&"
                                elif alone == "center":
                                    w = format((LINE - charlen(splitline[i-1]))*8 + int(halflen(splitline[i-1]) / 2),"02x")
                                    if w != "00" and not "-" in w:
                                        shift = r"+T\x{}".format(w)
                                    elif w == "00" or "-" in w:
                                        shift = ""
                                    if "+T" in splitline[i-1]:
                                        splitline[i-1] = shift + splitline[i-1][3:] + "&"
                                    elif "+T" not in splitline[i-1]:
                                        splitline[i-1] = shift + splitline[i-1] + "&"
                                elif alone == "right":
                                    w = format((LINE - charlen(splitline[i-1]))*16 + halflen(splitline[i-1]),"02x")
                                    if w != "00" and not "-" in w:
                                        shift = r"+T\x{}".format(w)
                                    elif w == "00" or "-" in w:
                                        shift = ""
                                    if "+T" in splitline[i-1]:
                                        splitline[i-1] = shift + splitline[i-1][3:] + "&"
                                    elif "+T" not in splitline[i-1]:
                                        splitline[i-1] = shift + splitline[i-1] + "&"
                            elif "~" in text:
                                splitline[i-1] = splitline[i-1] + "&"
                    elif charlen(splitline[i-1])-2 > LINE:
                        k = 0
                        j = charlen(splitline[i-1],LINE)
                        p = 0
                        while LINE * (p - 1) <= charlen(splitline[i-1]):
                            if (i + p) % 3 == 0:
                                if "~" not in text:
                                    if alone == "left":
                                        if "+T" in splitline[i-1][k:j]:
                                            tex[p] = splitline[i-1][k+3:j] + "^<"
                                        elif "+T" not in splitline[i-1][k:j]:
                                            tex[p] = splitline[i-1][k:j] + "^<"
                                    elif alone == "center":
                                        w = format((LINE - charlen(splitline[i-1][k:j]))*8 + int(halflen(splitline[i-1][k:j]) / 2),"02x")
                                        if w != "00" and not "-" in w:
                                            shift = r"+T\x{}".format(w)
                                        elif w == "00" or "-" in w:
                                            shift = ""
                                        if "+T" in splitline[i-1][k:j]:
                                            tex[p] = shift + splitline[i-1][k+3:j] + "^<"
                                        elif "+T" not in splitline[i-1][k:j]:
                                            tex[p] = shift + splitline[i-1][k:j] + "^<"
                                    elif alone == "right":
                                        w = format((LINE - charlen(splitline[i-1][k:j]))*16 + halflen(splitline[i-1][k:j]),"02x")
                                        if w != "00" and not "-" in w:
                                            shift = r"+T\x{}".format(w)
                                        elif w == "00" or "-" in w:
                                            shift = ""
                                        if "+T" in splitline[i-1][k:j]:
                                            tex[p] = shift + splitline[i-1][k+3:j] + "^<"
                                        elif "+T" not in splitline[i-1][k:j]:
                                            tex[p] = shift + splitline[i-1][k:j] + "^<"
                                elif "~" in text:
                                    tex[p] = splitline[i-1][k:j] + "^<"
                            elif (i + p) % 3 != 0:
                                if "~" not in text:
                                    if alone == "left":
                                        if "+T" in splitline[i-1][k:j]:
                                            tex[p] = splitline[i-1][k+3:j] + "&"
                                        elif "+T" not in splitline[i-1][k:j]:
                                            tex[p] = splitline[i-1][k:j] + "&"
                                    elif alone == "center":
                                        w = format((LINE - charlen(splitline[i-1][k:j]))*8 + int(halflen(splitline[i-1][k:j]) / 2),"02x")
                                        if w != "00" and not "-" in w:
                                            shift = r"+T\x{}".format(w)
                                        elif w == "00" or "-" in w:
                                            shift = ""
                                        if "+T" in splitline[i-1][k:j]:
                                            tex[p] = shift + splitline[i-1][k+3:j] + "&"
                                        elif "+T" not in splitline[i-1][k:j]:
                                            tex[p] = shift + splitline[i-1][k:j] + "&"
                                    elif alone == "right":
                                        w = format((LINE - charlen(splitline[i-1][k:j]))*16 + halflen(splitline[i-1][k:j]),"02x")
                                        if w != "00" and not "-" in w:
                                            shift = r"+T\x{}".format(w)
                                        elif w == "00" or "-" in w:
                                            shift = ""
                                        if "+T" in splitline[i-1][k:j]:
                                            tex[p] = shift + splitline[i-1][k+3:j] + "&"
                                        elif "+T" not in splitline[i-1][k:j]:
                                            tex[p] = shift + splitline[i-1][k:j] + "&"
                                elif "~" in text:
                                    tex[p] = splitline[i-1][k:j] + "&"
                            k = j
                            j += charlen(splitline[i-1][k:],LINE)
                            p += 1
                        splitline[i-1] = "".join(tex.values())
                    i += 1
                splitbox[n-1] = "".join(splitline)
            elif "&" not in splitbox[n-1] and (":2" or ":3" or ":O" )not in splitbox[n-1]:
                if charlen(splitbox[n-1])-2 <= LINE:
                    if "~" not in text:
                        if alone == "left":
                            if "T+" in splitbox[n-1]:
                                splitbox[n-1] = splitbox[n-1][3:] + "^<"
                            elif "T+" not in splitbox[n-1]:
                                splitbox[n-1] = splitbox[n-1] + "^<"
                        elif alone == "center":
                            w = format((LINE - charlen(splitbox[n-1]))*8 + int(halflen(splitbox[n-1][k:j]) / 2),"02x")
                            if w != "00" and not "-" in w:
                                shift = r"+T\x{}".format(w)
                            elif w == "00" or "-" in w:
                                shift = ""
                            if "T+" in splitbox[n-1]:
                                splitbox[n-1] = shift + splitbox[n-1][3:] + "^<"
                            elif "T+" not in splitbox[n-1]:
                                splitbox[n-1] = shift + splitbox[n-1] + "^<"
                        elif alone == "right":
                            w = format((LINE - charlen(splitbox[n-1]))*16 + halflen(splitbox[n-1][k:j]),"02x")
                            if w != "00" and not "-" in w:
                                shift = r"+T\x{}".format(w)
                            elif w == "00" or "-" in w:
                                shift = ""
                            if "T+" in splitbox[n-1]:
                                splitbox[n-1] = shift + splitbox[n-1][3:] + "^<"
                            elif "T+" not in splitbox[n-1]:
                                splitbox[n-1] = shift + splitbox[n-1] + "^<"
                    elif "~" in text:
                        splitbox[n-1] = splitbox[n-1] + "^<"
                elif charlen(splitbox[n-1])-2 > LINE:
                    j = charlen(splitbox[n-1],LINE)
                    p = 0
                    k = 0
                    while LINE * (p - 1) <= charlen(splitbox[n-1]):
                        if (n + p) % 3 == 0:
                            if "~" not in text:
                                if alone == "left":
                                    if "T+" in splitbox[n-1][k:j]:
                                        box[p] = splitbox[n-1][k+3:j] + "^<"
                                    elif "T+" not in splitbox[n-1][k:j]:
                                        box[p] = splitbox[n-1][k:j] + "^<"
                                elif alone == "center":
                                    w = format((LINE - charlen(splitbox[n-1][k:j]))*8 + int(halflen(splitbox[n-1][k:j]) / 2),"02x")
                                    if w != "00" and not "-" in w:
                                        shift = r"+T\x{}".format(w)
                                    elif w == "00" or "-" in w:
                                        shift = ""
                                    if "+T" in splitbox[n-1][k:j]:
                                        box[p] = shift + splitbox[n-1][k+3:j] + "^<"
                                    elif "+T" not in splitbox[n-1][k:j]:
                                        box[p] = shift + splitbox[n-1][k:j] + "^<"
                                elif alone == "right":
                                    w = format((LINE - charlen(splitbox[n-1][k:j]))*16 + halflen(splitbox[n-1][k:j]),"02x")
                                    if w != "00" and not "-" in w:
                                        shift = r"+T\x{}".format(w)
                                    elif w == "00" or "-" in w:
                                        shift = ""
                                    if "+T" in splitbox[n-1][k:j]:
                                        box[p] = shift + splitbox[n-1][k+3:j] + "^<"
                                    elif "+T" not in splitbox[n-1][k:j]:
                                        box[p] = shift + splitbox[n-1][k:j] + "^<"
                            elif "~" in text:
                                box[p] = splitbox[n-1][k:j] + "^<"
                        elif (n + p) % 3 != 0:
                            if "~" not in text:
                                if alone == "left":
                                    if "T+" in splitbox[n-1][k:j]:
                                        box[p] = splitbox[n-1][k+3:j] + "&"
                                    elif "T+" not in splitbox[n-1][k:j]:
                                        box[p] = splitbox[n-1][k:j] + "&"
                                elif alone == "center":
                                    w = format((LINE - charlen(splitbox[n-1][k:j]))*8 + int(halflen(splitbox[n-1][k:j]) / 2),"02x")
                                    if w != "00" and not "-" in w:
                                        shift = r"+T\x{}".format(w)
                                    elif w == "00" or "-" in w:
                                        shift = ""
                                    if "+T" in splitbox[n-1][k:j]:
                                        box[p] = shift + splitbox[n-1][k+3:j] + "&"
                                    elif "+T" not in splitbox[n-1][k:j]:
                                        box[p] = shift + splitbox[n-1][k:j] + "&"
                                elif alone == "right":
                                    w = format((LINE - charlen(splitbox[n-1][k:j])) * 16 + halflen(splitbox[n-1][k:j]),"02x")
                                    if w != "00" and not "-" in w:
                                        shift = r"+T\x{}".format(w)
                                    elif w == "00" or "-" in w:
                                        shift = ""
                                    if "+T" in splitbox[n-1][k:j]:
                                        box[p] = shift + splitbox[n-1][k+3:j] + "&"
                                    elif "+T" not in splitbox[n-1][k:j]:
                                        box[p] = shift + splitbox[n-1][k:j] + "&"
                            elif "~" in text:
                                box[p] = splitbox[n-1][k:j] + "&"
                        k = j
                        j += charlen(splitbox[n-1][k:], LINE)
                        p += 1
                    splitbox[n-1] = "".join(box.values())
                    if splitbox[n-1].endswith("&"):
                        splitbox[n-1] = splitbox[n-1][:-1] + "^<"
            n += 1
        text = "".join(splitbox)
        text = text.replace("<<","<")
        text = text.replace("^^","^")
        if text.endswith("&"):
            text = text[:-1]
        elif text.endswith("^<"):
            text = text[:-2]
        text = text.replace("^<^<","^<")
        text = text.replace("^<&","^<")
        text = text.replace("&^<","^<")
        text = text.replace("&&","&")
        if text.endswith("&"):
            text = text[:-1]
        elif text.endswith("^<"):
            text = text[:-2]
        if instant == 1:
            text = "<" + text
    elif mode == 1:
        splitbox = text.split("^^")
        while n <= text.count("^^") + 1:
            if (":2" or ":3" or ":O") in splitbox[n-1]:
                splitbox[n-1] = splitbox[n-1]
            elif "&&" in splitbox[n-1] and (":2" or ":3" or ":O") not in splitbox[n-1]:
                splitline = splitbox[n-1].split("&&")
                while i <= splitbox[n-1].count("&&") + 1:
                    print(splitline[i-1])
                    if charlen(splitline[i-1],mode = 1)-2 <= LINE:
                        if i % 3 == 0:
                            if "~" not in text:
                                if alone == "left":
                                    if "+T" in splitline[i-1]:
                                        splitline[i-1] = splitline[i-1][3:] + "^^<<"
                                    elif "+T" not in splitline[i-1]:
                                        splitline[i-1] = splitline[i-1] + "^^<<"
                                elif alone == "center":
                                    w = format((LINE - charlen(splitline[i-1],mode = 1))*8 + int(halflen(splitline[i-1],1) / 2),"02x")
                                    if w != "00" and not "-" in w:
                                        shift = r"+T\x{}".format(w)
                                    elif w == "00" or "-" in w:
                                        shift = ""
                                    if "+T" in splitline[i-1]:
                                        splitline[i-1] = shift + splitline[i-1][3:] + "^^<<"
                                    elif "+T" not in splitline[i-1]:
                                        splitline[i-1] = shift + splitline[i-1] + "^^<<"
                                elif alone == "right":
                                    w = format((LINE - charlen(splitline[i-1],mode = 1))*16 + halflen(splitline[i-1],1),"02x")
                                    if w != "00" and not "-" in w:
                                        shift = r"+T\x{}".format(w)
                                    elif w == "00" or "-" in w:
                                        shift = ""
                                    if "+T" in splitline[i-1]:
                                        splitline[i-1] = shift + splitline[i-1][3:] + "^^<<"
                                    elif "+T" not in splitline[i-1]:
                                        splitline[i-1] = shift + splitline[i-1] + "^^<<"
                            elif "~" in text:
                                splitline[i-1] = splitline[i-1] + "^^<<"
                        elif i % 3 != 0:
                            if "~" not in text:
                                if alone == "left":
                                    if "+T" in splitline[i-1]:
                                        splitline[i-1] = splitline[i-1][3:] + "&&"
                                    elif "+T" not in splitline[i-1]:
                                        splitline[i-1] = splitline[i-1] + "&&"
                                elif alone == "center":
                                    w = format((LINE - charlen(splitline[i-1],mode = 1))*8 + int(halflen(splitline[i-1],1) / 2),"02x")
                                    if w != "00" and not "-" in w:
                                        shift = r"+T\x{}".format(w)
                                    elif w == "00" or "-" in w:
                                        shift = ""
                                    if "+T" in splitline[i-1]:
                                        splitline[i-1] = shift + splitline[i-1][3:] + "&&"
                                    elif "+T" not in splitline[i-1]:
                                        splitline[i-1] = shift + splitline[i-1] + "&&"
                                elif alone == "right":
                                    w = format((LINE - charlen(splitline[i-1],mode = 1))*16 + halflen(splitline[i-1],1),"02x")
                                    if w != "00" and not "-" in w:
                                        shift = r"+T\x{}".format(w)
                                    elif w == "00" or "-" in w:
                                        shift = ""
                                    if "+T" in splitline[i-1]:
                                        splitline[i-1] = shift + splitline[i-1][3:] + "&&"
                                    elif "+T" not in splitline[i-1]:
                                        splitline[i-1] = shift + splitline[i-1] + "&&"
                            elif "~" in text:
                                splitline[i-1] = splitline[i-1] + "&&"
                    elif charlen(splitline[i-1],mode = 1)-2 > LINE:
                        j = charlen(splitline[i-1],LINE,mode = 1)
                        p = 0
                        while LINE * (p - 1) <= charlen(splitline[i-1],mode = 1):
                            if (i + p) % 3 == 0:
                                if "~" not in text:
                                    if alone == "left":
                                        if "+T" in splitline[i-1][k:j]:
                                            tex[p] = splitline[i-1][k+3:j] + "^^<<"
                                        elif "+T" not in splitline[i-1][k:j]:
                                            tex[p] = splitline[i-1][k:j] + "^^<<"
                                    elif alone == "center":
                                        w = format((LINE - charlen(splitline[i-1][k:j],mode = 1))*8 + int(halflen(splitline[i-1][k:j],1) / 2),"02x")
                                        if w != "00" and not "-" in w:
                                            shift = r"+T\x{}".format(w)
                                        elif w == "00" or "-" in w:
                                            shift = ""
                                        if "+T" in splitline[i-1][k:j]:
                                            tex[p] = shift + splitline[i-1][k+3:j] + "^^<<"
                                        elif "+T" not in splitline[i-1][k:j]:
                                            tex[p] = shift + splitline[i-1][k:j] + "^^<<"
                                    elif alone == "right":
                                        w = format((LINE - charlen(splitline[i-1][k:j],mode = 1))*16 + halflen(splitline[i-1][k:j],1),"02x")
                                        if w != "00" and not "-" in w:
                                            shift = r"+T\x{}".format(w)
                                        elif w == "00" or "-" in w:
                                            shift = ""
                                        if "+T" in splitline[i-1][k:j]:
                                            tex[p] = shift + splitline[i-1][k+3:j] + "^^<<"
                                        elif "+T" not in splitline[i-1][k:j]:
                                            tex[p] = shift + splitline[i-1][k:j] + "^^<<"
                                elif "~" in text:
                                    tex[p] = splitline[i-1][k:j] + "^^<<"
                            elif (i + p) % 3 != 0:
                                if "~" not in text:
                                    if alone == "left":
                                        if "+T" in splitline[i-1][k:j]:
                                            tex[p] = splitline[i-1][k+3:j] + "&&"
                                        elif "+T" not in splitline[i-1][k:j]:
                                            tex[p] = splitline[i-1][k:j] + "&&"
                                    elif alone == "center":
                                        w = format((LINE - charlen(splitline[i-1][k:j],mode = 1))*8 + int(halflen(splitline[i-1][k:j],1) / 2),"02x")
                                        if w != "00" and not "-" in w:
                                            shift = r"+T\x{}".format(w)
                                        elif w == "00" or "-" in w:
                                            shift = ""
                                        if "+T" in splitline[i-1][k:j]:
                                            tex[p] = shift + splitline[i-1][k+3:j] + "&&"
                                        elif "+T" not in splitline[i-1][k:j]:
                                            tex[p] = shift + splitline[i-1][k:j] + "&&"
                                    elif alone == "right":
                                        w = format((LINE - charlen(splitline[i-1][k:j],mode = 1))*16 + halflen(splitline[i-1][k:j],1),"02x")
                                        if w != "00" and not "-" in w:
                                            shift = r"+T\x{}".format(w)
                                        elif w == "00" or "-" in w:
                                            shift = ""
                                        if "+T" in splitline[i-1][k:j]:
                                            tex[p] = shift + splitline[i-1][k+3:j] + "&&"
                                        elif "+T" not in splitline[i-1][k:j]:
                                            tex[p] = shift + splitline[i-1][k:j] + "&&"
                                elif "~" in text:
                                    tex[p] = splitline[i-1][k:j] + "&&"
                            k = j
                            j += charlen(splitline[i-1][k:],LINE,mode = 1)
                            p += 1
                        splitline[i-1] = "".join(tex.values())
                    i += 1
                splitbox[n-1] = "".join(splitline)
            elif "&&" not in splitbox[n-1] and (":2" or ":3" or ":O") not in splitbox[n-1]:
                if charlen(splitbox[n-1],mode = 1)-2 <= LINE:
                    if "~" not in text:
                        if alone == "left":
                            if "T+" in splitbox[n-1]:
                                splitbox[n-1] = splitbox[n-1][3:] + "^^<<"
                            elif "T+" not in splitbox[n-1]:
                                splitbox[n-1] = splitbox[n-1] + "^^<<"
                        elif alone == "center":
                            w = format((LINE - charlen(splitbox[n-1],mode = 1))*8 + int(halflen(splitbox[n-1],1) / 2),"02x")
                            if w != "00" and not "-" in w:
                                shift = r"+T\x{}".format(w)
                            elif w == "00" or "-" in w:
                                shift = ""
                            if "T+" in splitbox[n-1]:
                                splitbox[n-1] = shift + splitbox[n-1][3:] + "^^<<"
                            elif "T+" not in splitbox[n-1]:
                                splitbox[n-1] = shift + splitbox[n-1] + "^^<<"
                        elif alone == "right":
                            w = format((LINE - charlen(splitbox[n-1],mode = 1))*16 + halflen(splitbox[n-1],1),"02x")
                            if w != "00" and not "-" in w:
                                shift = r"+T\x{}".format(w)
                            elif w == "00" or "-" in w:
                                shift = ""
                            if "T+" in splitbox[n-1]:
                                splitbox[n-1] = shift + splitbox[n-1][3:] + "^^<<"
                            elif "T+" not in splitbox[n-1]:
                                splitbox[n-1] = shift + splitbox[n-1] + "^^<<"
                    elif "~" in text:
                        splitbox[n-1] = splitbox[n-1] + "^^<<"
                elif charlen(splitbox[n-1],mode = 1)-2 > LINE:
                    j = charlen(splitbox[n-1],LINE,mode = 1)
                    p = 0
                    k = 0
                    while LINE * (p - 1) <= charlen(splitbox[n-1],mode = 1):
                        if (n + p) % 3 == 0:
                            if "~" not in text:
                                if alone == "left":
                                    if "T+" in splitbox[n-1][k:j]:
                                        box[p] = splitbox[n-1][k+3:j] + "^^<<"
                                    elif "T+" not in splitbox[n-1][k:j]:
                                        box[p] = splitbox[n-1][k:j] + "^^<<"
                                elif alone == "center":
                                    w = format((LINE - charlen(splitbox[n-1][k:j],mode = 1))*8 + int(halflen(splitbox[n-1][k:j],1) / 2),"02x")
                                    if w != "00" and not "-" in w:
                                        shift = r"+T\x{}".format(w)
                                    elif w == "00" or "-" in w:
                                        shift = ""
                                    if "+T" in splitbox[n-1][k:j]:
                                        box[p] = shift + splitbox[n-1][k+3:j] + "^^<<"
                                    elif "+T" not in splitbox[n-1][k:j]:
                                        box[p] = shift + splitbox[n-1][k:j] + "^^<<"
                                elif alone == "right":
                                    w = format((LINE - charlen(splitbox[n-1][k:j],mode = 1))*16 + halflen(splitbox[n-1][k:j],1),"02x")
                                    if w != "00" and not "-" in w:
                                        shift = r"+T\x{}".format(w)
                                    elif w == "00" or "-" in w:
                                        shift = ""
                                    if "+T" in splitbox[n-1][k:j]:
                                        box[p] = shift + splitbox[n-1][k+3:j] + "^^<<"
                                    elif "+T" not in splitbox[n-1][k:j]:
                                        box[p] = shift + splitbox[n-1][k:j] + "^^<<"
                            elif "~" in text:
                                box[p] = splitbox[n-1][k:j] + "^^<<"
                        elif (n + p) % 3 != 0:
                            if "~" not in text:
                                if alone == "left":
                                    if "T+" in splitbox[n-1][k:j]:
                                        box[p] = splitbox[n-1][k+3:j] + "&&"
                                    elif "T+" not in splitbox[n-1][k:j]:
                                        box[p] = splitbox[n-1][k:j] + "&&"
                                elif alone == "center":
                                    w = format((LINE - charlen(splitbox[n-1][k:j],mode = 1))*8 + int(halflen(splitbox[n-1][k:j],1) / 2),"02x")
                                    if w != "00" and not "-" in w:
                                        shift = r"+T\x{}".format(w)
                                    elif w == "00" or "-" in w:
                                        shift = ""
                                    if "+T" in splitbox[n-1][k:j]:
                                        box[p] = shift + splitbox[n-1][k+3:j] + "&&"
                                    elif "+T" not in splitbox[n-1][k:j]:
                                        box[p] = shift + splitbox[n-1][k:j] + "&&"
                                elif alone == "right":
                                    w = format((LINE - charlen(splitbox[n-1][k:j],mode = 1))*16 + halflen(splitbox[n-1][k:j],1),"02x")
                                    if w != "00" and not "-" in w:
                                        shift = r"+T\x{}".format(w)
                                    elif w == "00" or "-" in w:
                                        shift = ""
                                    if "+T" in splitbox[n-1][k:j]:
                                        box[p] = shift + splitbox[n-1][k+3:j] + "&&"
                                    elif "+T" not in splitbox[n-1][k:j]:
                                        box[p] = shift + splitbox[n-1][k:j] + "&&"
                            elif "~" in text:
                                box[p] = splitbox[n-1][k:j] + "&&"
                        k = j
                        j += charlen(splitbox[n-1][k:], LINE,mode = 1)
                        p += 1
                    splitbox[n-1] = "".join(box.values())
                    if splitbox[n-1].endswith("&&"):
                        splitbox[n-1] = splitbox[n-1][:-2] + "^^<<"
            n += 1
        text = "".join(splitbox)
        text = text.replace("<<<","<")
        text = text.replace("^^^","^")
        if text.endswith("&&"):
            text = text[:-2]
        elif text.endswith("^^<<"):
            text = text[:-4]
        text = text.replace("^^,<^^<<","^^<<")
        text = text.replace("^^<<&&","^^<<")
        text = text.replace("&&^^<<","^^<<")
        text = text.replace("&&&","&")
        if text.endswith("&&"):
            text = text[:-2]
        elif text.endswith("^^<<"):
            text = text[:-4]
        if instant == 1:
            text = "<<" + text
    return text

def calculate_width(words):
    words_width = 0
    for word in words:
        index = 0
        while index < len(word):
            character = word[index]
            index += 1
            if character.code in Messages.CONTROL_CODES:
                if character.code == 0x06:
                    words_width += character.data
            words_width += get_character_width(chr(character.code))
    spaces_width = get_character_width(' ') * (len(words) - 1)

    return words_width + spaces_width


def get_character_width(character):
    try:
        return character_table[character]
    except KeyError:
        if ord(character) < 0x20:
            if character in control_code_width:
                return sum([character_table[c] for c in control_code_width[character]])
            else:
                return 0
        else:
            # A sane default with the most common character width
            return character_table[' ']


control_code_width = {
    '\x0F': '00000000',
    '\x16': '00\'00"',
    '\x17': '00\'00"',
    '\x18': '00000',
    '\x19': '100',
    '\x1D': '00',
    '\x1E': '00000',
    '\x1F': '00\'00"',
}


# Tediously measured by filling a full line of a gossip stone's text box with one character until it is reasonably full
# (with a right margin) and counting how many characters fit. OoT does not appear to use any kerning, but, if it does,
# it will only make the characters more space-efficient, so this is an underestimate of the number of letters per line,
# at worst. This ensures that we will never bleed text out of the text box while line wrapping.
# Larger numbers in the denominator mean more of that character fits on a line; conversely, larger values in this table
# mean the character is wider and can't fit as many on one line.
character_table = {
    '\x0F': 655200,
    '\x16': 292215,
    '\x17': 292215,
    '\x18': 300300,
    '\x19': 145860,
    '\x1D': 85800,
    '\x1E': 300300,
    '\x1F': 265980,
    'a':  51480, # LINE_WIDTH /  35
    'b':  51480, # LINE_WIDTH /  35
    'c':  51480, # LINE_WIDTH /  35
    'd':  51480, # LINE_WIDTH /  35
    'e':  51480, # LINE_WIDTH /  35
    'f':  34650, # LINE_WIDTH /  52
    'g':  51480, # LINE_WIDTH /  35
    'h':  51480, # LINE_WIDTH /  35
    'i':  25740, # LINE_WIDTH /  70
    'j':  34650, # LINE_WIDTH /  52
    'k':  51480, # LINE_WIDTH /  35
    'l':  25740, # LINE_WIDTH /  70
    'm':  81900, # LINE_WIDTH /  22
    'n':  51480, # LINE_WIDTH /  35
    'o':  51480, # LINE_WIDTH /  35
    'p':  51480, # LINE_WIDTH /  35
    'q':  51480, # LINE_WIDTH /  35
    'r':  42900, # LINE_WIDTH /  42
    's':  51480, # LINE_WIDTH /  35
    't':  42900, # LINE_WIDTH /  42
    'u':  51480, # LINE_WIDTH /  35
    'v':  51480, # LINE_WIDTH /  35
    'w':  81900, # LINE_WIDTH /  22
    'x':  51480, # LINE_WIDTH /  35
    'y':  51480, # LINE_WIDTH /  35
    'z':  51480, # LINE_WIDTH /  35
    'A':  81900, # LINE_WIDTH /  22
    'B':  51480, # LINE_WIDTH /  35
    'C':  72072, # LINE_WIDTH /  25
    'D':  72072, # LINE_WIDTH /  25
    'E':  51480, # LINE_WIDTH /  35
    'F':  51480, # LINE_WIDTH /  35
    'G':  81900, # LINE_WIDTH /  22
    'H':  60060, # LINE_WIDTH /  30
    'I':  25740, # LINE_WIDTH /  70
    'J':  51480, # LINE_WIDTH /  35
    'K':  60060, # LINE_WIDTH /  30
    'L':  51480, # LINE_WIDTH /  35
    'M':  81900, # LINE_WIDTH /  22
    'N':  72072, # LINE_WIDTH /  25
    'O':  81900, # LINE_WIDTH /  22
    'P':  51480, # LINE_WIDTH /  35
    'Q':  81900, # LINE_WIDTH /  22
    'R':  60060, # LINE_WIDTH /  30
    'S':  60060, # LINE_WIDTH /  30
    'T':  51480, # LINE_WIDTH /  35
    'U':  60060, # LINE_WIDTH /  30
    'V':  72072, # LINE_WIDTH /  25
    'W': 100100, # LINE_WIDTH /  18
    'X':  72072, # LINE_WIDTH /  25
    'Y':  60060, # LINE_WIDTH /  30
    'Z':  60060, # LINE_WIDTH /  30
    ' ':  51480, # LINE_WIDTH /  35
    '1':  25740, # LINE_WIDTH /  70
    '2':  51480, # LINE_WIDTH /  35
    '3':  51480, # LINE_WIDTH /  35
    '4':  60060, # LINE_WIDTH /  30
    '5':  51480, # LINE_WIDTH /  35
    '6':  51480, # LINE_WIDTH /  35
    '7':  51480, # LINE_WIDTH /  35
    '8':  51480, # LINE_WIDTH /  35
    '9':  51480, # LINE_WIDTH /  35
    '0':  60060, # LINE_WIDTH /  30
    '!':  51480, # LINE_WIDTH /  35
    '?':  72072, # LINE_WIDTH /  25
    '\'': 17325, # LINE_WIDTH / 104
    '"':  34650, # LINE_WIDTH /  52
    '.':  25740, # LINE_WIDTH /  70
    ',':  25740, # LINE_WIDTH /  70
    '/':  51480, # LINE_WIDTH /  35
    '-':  34650, # LINE_WIDTH /  52
    '_':  51480, # LINE_WIDTH /  35
    '(':  42900, # LINE_WIDTH /  42
    ')':  42900, # LINE_WIDTH /  42
    '$':  51480  # LINE_WIDTH /  35
}

# To run tests, enter the following into a python3 REPL:
# >>> import Messages
# >>> from TextBox import line_wrap_tests
# >>> line_wrap_tests()
def line_wrap_tests():
    test_wrap_simple_line()
    test_honor_forced_line_wraps()
    test_honor_box_breaks()
    test_honor_control_characters()
    test_honor_player_name()
    test_maintain_multiple_forced_breaks()
    test_trim_whitespace()
    test_support_long_words()


def test_wrap_simple_line():
    words = 'Hello World! Hello World! Hello World!'
    expected = 'Hello World! Hello World! Hello\x01World!'
    result = line_wrap(words)

    if result != expected:
        print('"Wrap Simple Line" test failed: Got ' + result + ', wanted ' + expected)
    else:
        print('"Wrap Simple Line" test passed!')


def test_honor_forced_line_wraps():
    words = 'Hello World! Hello World!&Hello World! Hello World! Hello World!'
    expected = 'Hello World! Hello World!\x01Hello World! Hello World! Hello\x01World!'
    result = line_wrap(words)

    if result != expected:
        print('"Honor Forced Line Wraps" test failed: Got ' + result + ', wanted ' + expected)
    else:
        print('"Honor Forced Line Wraps" test passed!')


def test_honor_box_breaks():
    words = 'Hello World! Hello World!^Hello World! Hello World! Hello World!'
    expected = 'Hello World! Hello World!\x04Hello World! Hello World! Hello\x01World!'
    result = line_wrap(words)

    if result != expected:
        print('"Honor Box Breaks" test failed: Got ' + result + ', wanted ' + expected)
    else:
        print('"Honor Box Breaks" test passed!')


def test_honor_control_characters():
    words = 'Hello World! #Hello# World! Hello World!'
    expected = 'Hello World! \x05\x00Hello\x05\x00 World! Hello\x01World!'
    result = line_wrap(words)

    if result != expected:
        print('"Honor Control Characters" test failed: Got ' + result + ', wanted ' + expected)
    else:
        print('"Honor Control Characters" test passed!')


def test_honor_player_name():
    words = 'Hello @! Hello World! Hello World!'
    expected = 'Hello \x0F! Hello World!\x01Hello World!'
    result = line_wrap(words)

    if result != expected:
        print('"Honor Player Name" test failed: Got ' + result + ', wanted ' + expected)
    else:
        print('"Honor Player Name" test passed!')


def test_maintain_multiple_forced_breaks():
    words = 'Hello World!&&&Hello World!'
    expected = 'Hello World!\x01\x01\x01Hello World!'
    result = line_wrap(words)

    if result != expected:
        print('"Maintain Multiple Forced Breaks" test failed: Got ' + result + ', wanted ' + expected)
    else:
        print('"Maintain Multiple Forced Breaks" test passed!')


def test_trim_whitespace():
    words = 'Hello World! & Hello World!'
    expected = 'Hello World!\x01Hello World!'
    result = line_wrap(words)

    if result != expected:
        print('"Trim Whitespace" test failed: Got ' + result + ', wanted ' + expected)
    else:
        print('"Trim Whitespace" test passed!')


def test_support_long_words():
    words = 'Hello World! WWWWWWWWWWWWWWWWWWWW Hello World!'
    expected = 'Hello World!\x01WWWWWWWWWWWWWWWWWWWW\x01Hello World!'
    result = line_wrap(words)

    if result != expected:
        print('"Support Long Words" test failed: Got ' + result + ', wanted ' + expected)
    else:
        print('"Support Long Words" test passed!')
