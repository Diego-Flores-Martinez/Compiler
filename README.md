# Mini Compiler – Lexing, Parsing, Semantic Analysis & Three-Address Code (TAC)

This repository contains a fully functional mini compiler implemented in Python. It supports a small imperative language with:

- Variable declarations (`int`, `bool`)
- Assignments
- Arithmetic expressions (`+`, `-`, `*`, `/`)
- Boolean expressions (`==`, `!=`, `<`, `>`, `<=`, `>=`, `&&`, `||`)
- Unary operator `!`
- Conditional statements (`if`, `else`)
- Loops (`while`)
- Full semantic analysis (types, declarations, undeclared identifiers, type mismatch)
- TAC (Three-Address Code) generation

The compiler was originally developed in the online IDE **OnlineGDB**, and afterwards uploaded and organized into this GitHub repository as the final deliverable.

---

## Project Structure

Compiler/

├── AST.py # Abstract Syntax Tree node classes

├── Lexer.py # Lexical analyzer

├── Parser.py # Recursive-descent parser

├── Semantic.py # Semantic analyzer

├── CodeGenerator.py # TAC generator

├── Main.py # Main driver that runs the full pipeline


├── programa.txt # Valid program example

└── programa_error.txt # Program containing a semantic error

Compiler pipeline:
source → lexer → parser → semantic analyzer → TAC generator → output code

---

## How to Run

### Option A — Run locally with Python
Requires Python 3.10+.


This will automatically run:
- `programa.txt` (valid program)
- `programa_error.txt` (semantic error)

---

### Option B — Run in GitHub Codespaces

1. Open the repository on GitHub  
2. Click **Code → Codespaces**  
3. Select **Create Codespace on main**  
4. Inside the built-in terminal: python Main.py


---

## Example Program (programa.txt)

```
int x;
int y;
bool ok;

x = 0;
y = 5;
ok = true;

while (x < y && ok) {
    x = x + 1;
    if (x == 3) {
        ok = false;
    } else {
        ok = true;
    }
}
```
===== TOKENS =====

(... token list ...)

AST successfully generated.

Semantic OK. Symbols: {'x': 'int', 'y': 'int', 'ok': 'bool'}

===== TAC =====

x = 0

y = 5
ok = 1

L1:

t1 = x < y

t2 = t1 && ok


if_false t2 goto L2

t3 = x + 1

x = t3

t4 = x == 3

if_false t4 goto L3

ok = 0

goto L4

L3:

ok = 1

L4:

goto L1

L2:

## Example Program (programa.txt)
```
int x;
bool ok;

x = 10;
ok = true;

y = x + 5;   // ERROR: y is not declared
```
Output: SEMANTIC ERROR: Variable 'y' not declared.

