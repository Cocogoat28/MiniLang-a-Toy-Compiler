
# MiniLang Compiler & Web Interpreter

A minimal educational language with a Flask web UI. Write small programs, run them in the browser, and see both the **program output** and a **symbolic “machine code” log** for each executed statement. fileciteturn0file0

---

## ✨ What’s inside

- **Flask web app** with a single `/` route that accepts code and a comma‑separated list of inputs. fileciteturn0file0  
- **Tokenizer → Parser → Evaluator** pipeline implemented in pure Python. fileciteturn0file0  
- **Primitive types**: `int`, `float`, `str`, `bool`. Declarations use `:=`. fileciteturn0file0  
- **Statements** supported:
  - Variable **declaration**: `TYPE IDENT := EXPR`  
  - **print**: `print EXPR[, EXPR ...]`  
  - **input**: `input [TYPE][, PROMPT ...]` (values read from a web **input buffer**) fileciteturn0file0  
- **Execution log**: every statement appends a line of symbolic “machine code” (e.g., `DECLARE int x, value = 10`). fileciteturn0file0

> ⚠️ This is a learning project: control‑flow keywords (`if/else/while/do/then`) are recognized by the lexer but **not yet implemented by the parser**. Expressions are limited to single literals or identifiers (no operators yet). fileciteturn0file0

---

## 🧩 Language overview

### Lexical elements
- **Literals**: integers, floats, strings in single or double quotes, and booleans `true`/`false`. fileciteturn0file0  
- **Identifiers**: sequences of non‑space characters that are not keywords, types, or numbers. fileciteturn0file0  
- **Symbols** recognized by the tokenizer: `(){}[],;:=+-*/%!&|<>^` (most are reserved for future use). fileciteturn0file0

### Types
`int`, `float`, `str`, `bool` (booleans are parsed from the strings `"true"`/`"false"`). fileciteturn0file0

### Statements
- **Declaration**  
  ```minilang
  int x := 10;
  str name := "MiniLang";
  bool ok := true;
  ```
  Declares a variable with a type and initializes it. Runtime enforces the type (`TypeError` on mismatch). fileciteturn0file0

- **Print**  
  ```minilang
  print "Hello,", name;
  print x, ok;
  ```
  Prints space‑joined values to the output buffer shown in the UI. fileciteturn0file0

- **Input**  
  ```minilang
  input int;           # reads one integer from the input buffer
  print input_var;     # the value is stored as variable 'input_var'
  ```
  The web UI supplies inputs from a **comma‑separated list**; the interpreter consumes them from `input_buffer`.  
  If you pass a prompt (e.g., `input int, "Age?"`), the value is stored under a variable **named exactly as the prompt text**; if no prompt is given, it’s stored as `input_var`. fileciteturn0file0

> **Expressions** are currently only a single literal or identifier. There is no arithmetic or concatenation yet. fileciteturn0file0

---

## 🏃‍♀️ Quick start

### Requirements
- Python 3.10+
- `Flask`

### Install & run
```bash
pip install Flask
python app.py
# open http://127.0.0.1:5000/
```
The app serves a form (template `templates/index.html`) with **Code** and **Inputs** fields. On submit, it parses and evaluates the code, then renders **Output** and **Machine Code** logs. fileciteturn0file0

> The server runs with `debug=True` and is not intended for production use as‑is. fileciteturn0file0

---

## 🧪 Examples

### 1) Hello world
```minilang
print "Hello, world!";
```

### 2) Variables + print
```minilang
int x := 42;
str who := "Alice";
print "Answer:", x, "User:", who;
```

### 3) Reading input
Inputs (comma‑separated in the UI): `25`
```minilang
input int;          # consumes 25
print "age:", input_var;
```

### 4) Using a prompt (advanced)
Inputs: `Goa`
```minilang
input str, "City";  # stores variable with name exactly 'City'
print "done";       # note: current grammar cannot reference 'City' (contains space)
```
Prefer no prompt if you want to read the value later as `input_var`. fileciteturn0file0

---

## 🏗️ Architecture

- **`CustomInterpreter`**: manages `variables`, `output`, `machine_code`, `input_buffer`, and token stream position.  
  - **Tokenizer**: converts source into tokens, handles strings and symbols, tracks line numbers. fileciteturn0file0  
  - **Parser**: builds a simple AST of statements (`DECLARE`, `PRINT`, `INPUT`) and token expressions. fileciteturn0file0  
  - **Evaluator**: executes the AST, enforces types, appends human‑readable machine‑code lines, and accumulates output. fileciteturn0file0

- **Web layer** (`Flask`)  
  - `POST /`: reads `code` and `inputs`, splits inputs on commas into `input_buffer`, runs the interpreter, and renders the results. fileciteturn0file0

---

## ⚠️ Errors you may see

- `SyntaxError`: unexpected token; missing `;` between statements; invalid declaration form. fileciteturn0file0  
- `NameError`: using an identifier that has not been declared. fileciteturn0file0  
- `TypeError`: declared type doesn’t match literal type; or invalid input conversion. fileciteturn0file0  
- `ValueError: Input required but input_buffer is empty`: you used `input` but didn’t supply enough values in the **Inputs** field. fileciteturn0file0

---

## 🚧 Current limitations & roadmap

**Limitations (by design, for now):**
- No arithmetic, boolean, or string operators; expressions are single tokens only. fileciteturn0file0  
- No control flow (`if/else/while/do/then`) despite keyword recognition. fileciteturn0file0  
- No re‑assignment after declaration; no scopes or functions. fileciteturn0file0  
- Prompted `input` stores variable with prompt text; such names (with spaces) aren’t addressable by the current grammar. fileciteturn0file0

**Roadmap ideas:**
- Full expression grammar (precedence, arithmetic/boolean ops, parentheses).
- Assignment statements and mutable variables.
- `if`/`while` statements with blocks and comparison operators.
- Proper AST nodes and pretty‑printer.
- “Real” bytecode representation and a virtual machine.
- CLI mode and unit tests.
- Package as a library + web app (separate modules), add Dockerfile.
- Harden web app for production (remove `debug=True`, CSRF for forms). fileciteturn0file0

---

## 📁 Project layout

```
app.py
templates/
  index.html   # form with 'code' and 'inputs' fields (not included in this snippet)
```
`app.py` contains both the interpreter and the Flask app. fileciteturn0file0

---

## 🤝 Contributing

Issues and PRs are welcome! Suggested areas: parser/grammar, expression evaluation, control flow, test coverage, and UI polish.

---

## 🛡️ License

Add your chosen license here (MIT/BSD-3-Clause/Apache-2.0, etc.).
