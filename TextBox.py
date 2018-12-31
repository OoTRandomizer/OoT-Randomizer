import Messages

# Least common multiple of all possible character widths. A line wrap must occur when the combined widths of all of the
# characters on a line reach this value.
LINE_WIDTH = 1801800

# Attempting to display more lines in a single text box will cause additional lines to bleed past the bottom of the box.
LINES_PER_BOX = 4

# Attempting to display more characters in a single text box will cause buffer overflows. First, visual artifacts will
# appear in lower areas of the text box. Eventually, the text box will become uncloseable.
MAX_CHARACTERS_PER_BOX = 200

LINE_BREAK = '&'
BOX_BREAK = '^'


def lineWrap(text):
    boxes = text.split(BOX_BREAK)
    boxesWithWrappedLines = []

    for box in boxes:
        forcedLines = box.split(LINE_BREAK)
        lines = [line.strip() for forcedLine in forcedLines for line in _wrapLines(forcedLine)]
        wrapped = LINE_BREAK.join(lines)

        if len(lines) > LINES_PER_BOX:
            print('Wrapped text exceeds maximum lines per text box. Original text:\n' + box)

        # Subtracting line count so that line breaks aren't counted as characters
        if len(wrapped) - (len(lines) - 1) > MAX_CHARACTERS_PER_BOX:
            print('Text length exceeds maximum characters per text box. Original text:\n' + box)

        boxesWithWrappedLines.append(wrapped)

    return BOX_BREAK.join(boxesWithWrappedLines)


def _wrapLines(text):
    lines = []
    currentLine = []
    currentWidth = 0

    for word in text.split(' '):
        currentLinePlusWord = currentLine.copy()
        currentLinePlusWord.append(word)
        currentLinePlusWordWidth = _calculateWidth(currentLinePlusWord)

        if (currentLinePlusWordWidth <= LINE_WIDTH):
            currentLine = currentLinePlusWord
            currentWidth = currentLinePlusWordWidth
        else:
            lines.append(' '.join(currentLine))
            currentLine = [word]
            currentWidth = _calculateWidth(currentLine)

    lines.append(' '.join(currentLine))

    return lines


def _calculateWidth(words):
    wordsWidth = 0
    for word in words:
        index = 0
        while index < len(word):
            character = word[index]
            index += 1
            if ord(character) in Messages.CONTROL_CODES:
                index += Messages.CONTROL_CODES[ord(character)][1]
            else:
                wordsWidth += _getCharacterWidth(character)
    spacesWidth = _getCharacterWidth(' ') * (len(words) - 1)

    return wordsWidth + spacesWidth


def _getCharacterWidth(character):
    try:
        return characterTable[character]
    except KeyError:
        # Control character for color settings; does not affect the width
        if character == '#':
            return 0
        # Control character for displaying the player's name; assume greater than average width
        elif character == '@':
            return characterTable['M'] * 8
        # A sane default with the most common character width
        else :
            return characterTable[' ']


# Tediously measured by filling a full line of a gossip stone's text box with one character until it is reasonably full
# (with a right margin) and counting how many characters fit. OoT does not appear to use any kerning, but, if it does,
# it will only make the characters more space-efficient, so this is an underestimate of the number of letters per line,
# at worst. This ensures that we will never bleed text out of the text box while line wrapping.
# Larger numbers in the denominator mean more of that character fits on a line; conversely, larger values in this table
# mean the character is wider and can't fit as many on one line.
characterTable = {
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
# >>> from TextBox import test_lineWrapTests
# >>> test_lineWrapTests()
def test_lineWrapTests():
    test_wrapSimpleLine()
    test_honorForcedLineWraps()
    test_honorBoxBreaks()
    test_honorControlCharacters()
    test_honorPlayerName()
    test_maintainMultipleForcedBreaks()
    test_trimWhitespace()
    test_supportLongWords()


def test_wrapSimpleLine():
    words = 'Hello World! Hello World! Hello World!'
    expected = 'Hello World! Hello World! Hello&World!'
    result = lineWrap(words)

    if result != expected:
        print('"Wrap Simple Line" test failed: Got ' + result + ', wanted ' + expected)
    else:
        print('"Wrap Simple Line" test passed!')


def test_honorForcedLineWraps():
    words = 'Hello World! Hello World!&Hello World! Hello World! Hello World!'
    expected = 'Hello World! Hello World!&Hello World! Hello World! Hello&World!'
    result = lineWrap(words)

    if result != expected:
        print('"Honor Forced Line Wraps" test failed: Got ' + result + ', wanted ' + expected)
    else:
        print('"Honor Forced Line Wraps" test passed!')


def test_honorBoxBreaks():
    words = 'Hello World! Hello World!^Hello World! Hello World! Hello World!'
    expected = 'Hello World! Hello World!^Hello World! Hello World! Hello&World!'
    result = lineWrap(words)

    if result != expected:
        print('"Honor Box Breaks" test failed: Got ' + result + ', wanted ' + expected)
    else:
        print('"Honor Box Breaks" test passed!')


def test_honorControlCharacters():
    words = 'Hello World! #Hello# World! Hello World!'
    expected = 'Hello World! #Hello# World! Hello&World!'
    result = lineWrap(words)

    if result != expected:
        print('"Honor Control Characters" test failed: Got ' + result + ', wanted ' + expected)
    else:
        print('"Honor Control Characters" test passed!')


def test_honorPlayerName():
    words = 'Hello @! Hello World! Hello World!'
    expected = 'Hello @! Hello World!&Hello World!'
    result = lineWrap(words)

    if result != expected:
        print('"Honor Player Name" test failed: Got ' + result + ', wanted ' + expected)
    else:
        print('"Honor Player Name" test passed!')


def test_maintainMultipleForcedBreaks():
    words = 'Hello World!&&&Hello World!'
    expected = 'Hello World!&&&Hello World!'
    result = lineWrap(words)

    if result != expected:
        print('"Maintain Multiple Forced Breaks" test failed: Got ' + result + ', wanted ' + expected)
    else:
        print('"Maintain Multiple Forced Breaks" test passed!')


def test_trimWhitespace():
    words = 'Hello World! & Hello World!'
    expected = 'Hello World!&Hello World!'
    result = lineWrap(words)

    if result != expected:
        print('"Trim Whitespace" test failed: Got ' + result + ', wanted ' + expected)
    else:
        print('"Trim Whitespace" test passed!')


def test_supportLongWords():
    words = 'Hello World! WWWWWWWWWWWWWWWWWWWW Hello World!'
    expected = 'Hello World!&WWWWWWWWWWWWWWWWWWWW&Hello World!'
    result = lineWrap(words)

    if result != expected:
        print('"Support Long Words" test failed: Got ' + result + ', wanted ' + expected)
    else:
        print('"Support Long Words" test passed!')
