This document contains a list of guidelines for how code in this project should be formatted.

# Overall code style

* Some of our guidelines have automated checks. Run them using `py CI.py --no_unit_tests`.
* If code is commented out, there should be an accompanying explanation of why the code was commented out and a suggestion of when it may be appropriate to uncomment it.
* Use spaces, not tabs, for indentation and alignment. Indentation should be 4 spaces. Exceptions include YAML files, which use 2 spaces for indentation, and the Makefile, which uses tabs.
* Unless requested by other guidelines (such as the next one), Don't use unnecessary parentheses, e.g. write `a + b * c` instead of `a + (b * c)`.
* Do not rely on operator precedence when nesting `and`/`&&` expressions inside `or`/`||` expressions. Always use parentheses.
* For hexadecimal numbers, use a lowercase `x` and uppercase letters as digits.

# C code style

* Include a space between a keyword like `if` or `switch` and the following parenthesis.
* Use braces around single-line `if`, `while`, etc. bodies. The only time omitting braces is acceptable is when the body is a `continue`, `break`, or `return` statement written on the same line as the condition and not followed by `else`.
* The opening brace of a function body, struct/union/enum body, or compound statement goes on the same line as the parameter list, condition, or `do` or `else` keyword.
* The `else` keyword goes on the same line as the preceding closing brace.
* Declare pointer variables with the asterisk aligned to the type (`uint8_t* foo`), not the variable name (`uint8_t *foo`).
* Use spaces around binary operators, with the exception of `.` and `->`.
* When using type casting (`(type) expression`) or shift operators, prefer using explicit parentheses over relying on operator precedence.

# Assembly code style

* Use `;` for comments, not `//`.
* All labels and directives are unindented, and all instructions are indented by 4 spaces.
* The first parameter of an instruction starts at column 13.

# Python code style

* Use f-strings instead of `str.format` or the `%` operator.
* Prefer using parentheses for multiline expressions over using `\` to continue a statement on the next line.
* If a list is written with each element on a separate line, include a comma after the last element.
* Use spaces around binary operators. (This does not include `.`, `,`, `:`, etc.)
* Use tuples rather than lists if both can be used interchangeably.
