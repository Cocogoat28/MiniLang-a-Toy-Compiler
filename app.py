from flask import Flask, request, render_template

app = Flask(__name__)

class Value:
    def __init__(self, type_, value):
        self.type = type_
        self.value = value

    def __repr__(self):
        return f"{self.type}({self.value})"

class CustomInterpreter:
    def __init__(self):
        self.variables = {}
        self.output = []
        self.machine_code = []  # To store symbolic machine code
        self.input_buffer = []
        self.pos = 0
        self.current_token = None
        self.TYPE_MAP = {
            'int': int,
            'float': float,
            'str': str,
            'bool': lambda x: x.lower() == 'true'
        }

    # Tokenizer
    def tokenize(self, code):
        tokens = []
        current = ''
        in_string = False
        quote_char = ''
        line = 1

        i = 0
        while i < len(code):
            char = code[i]
            if in_string:
                if char == quote_char:
                    tokens.append(('STRING', current, line))
                    current = ''
                    in_string = False
                else:
                    current += char
                i += 1
                continue
            if char in ('"', "'"):
                in_string = True
                quote_char = char
                i += 1
                continue
            if char in '(){}[],;:=+-*/%!&|<>^':
                if current:
                    tokens.append(self._get_token(current, line))
                    current = ''
                # handle :=
                if char == ':' and i + 1 < len(code) and code[i+1] == '=':
                    tokens.append(('SYMBOL', ':=', line))
                    i += 2
                    continue
                tokens.append(('SYMBOL', char, line))
                i += 1
                continue
            if char.isspace():
                if current:
                    tokens.append(self._get_token(current, line))
                    current = ''
                if char == '\n':
                    line += 1
                i += 1
                continue
            current += char
            i += 1

        if current:
            tokens.append(self._get_token(current, line))
        return tokens

    def _get_token(self, token, line):
        keywords = {'print', 'input', 'if', 'else', 'while', 'do', 'then'}
        if token in keywords:
            return ('KEYWORD', token, line)
        if token in {'true', 'false'}:
            return ('BOOL', token == 'true', line)
        if token in self.TYPE_MAP:
            return ('TYPE', token, line)
        if token.isdigit():
            return ('INT', int(token), line)
        try:
            return ('FLOAT', float(token), line)
        except:
            return ('ID', token, line)

    def _is_at_end(self):
        return self.pos >= len(self.tokens)

    def _peek(self):
        return None if self._is_at_end() else self.tokens[self.pos]

    def _advance(self):
        self.pos += 1
        return self.tokens[self.pos - 1]

    def _previous(self):
        return self.tokens[self.pos - 1]

    def _consume(self, token_type, value=None, optional=False):
        if self._check(token_type, value):
            return self._advance()
        if not optional:
            raise SyntaxError(f"Expected {token_type} {value} but found {self._peek()}")
        return None

    def _check(self, token_type, value=None):
        if self._is_at_end():
            return False
        token = self.tokens[self.pos]
        if token[0] != token_type:
            return False
        if value is not None and token[1] != value:
            return False
        return True

    def _match(self, token_type, value=None):
        if self._check(token_type, value):
            self._advance()
            return True
        return False

    def parse(self, code):
        self.tokens = self.tokenize(code)
        self.pos = 0
        return self._parse_program()

    def _parse_program(self):
        stmts = []
        while not self._is_at_end():
            stmt = self._parse_stmt()
            stmts.append(stmt)
            self._consume('SYMBOL', ';', optional=True)
        return stmts

    def _parse_stmt(self):
        if self._match('TYPE'):
            return self._parse_declaration()
        if self._match('KEYWORD', 'print'):
            return self._parse_print()
        if self._match('KEYWORD', 'input'):
            return self._parse_input()
        return self._parse_expr()

    def _parse_declaration(self):
        dtype = self._previous()[1]
        name = self._consume('ID')[1]
        self._consume('SYMBOL', ':=')
        value = self._parse_expr()
        return ('DECLARE', dtype, name, value)

    def _parse_print(self):
        args = []
        while not self._check('SYMBOL', ';') and not self._is_at_end():
            args.append(self._parse_expr())
            self._consume('SYMBOL', ',', optional=True)
        return ('PRINT', args)

    def _parse_input(self):
        dtype = 'str'
        if self._match('TYPE'):
            dtype = self._previous()[1]
        prompt = []
        if self._match('SYMBOL', ','):
            while not self._check('SYMBOL', ';') and not self._is_at_end():
                prompt.append(self._parse_expr())
                self._consume('SYMBOL', ',', optional=True)
        return ('INPUT', dtype, prompt)

    def _parse_expr(self):
        token = self._advance()
        if token[0] in ['INT', 'FLOAT', 'STRING', 'BOOL']:
            return token
        elif token[0] == 'ID':
            return token
        else:
            raise SyntaxError(f"Unexpected token in expression: {token}")

    def evaluate(self, node):
        if isinstance(node, list):
            for n in node:
                self._evaluate_node(n)
            return
        return self._evaluate_node(node)

    def _evaluate_node(self, node):
        if node[0] == 'DECLARE':
            _, dtype, name, expr = node
            value = self._evaluate_expr(expr)
            self._type_check(value, dtype)
            self.variables[name] = value
            self.machine_code.append(f"DECLARE {dtype} {name}, value = {value.value}")
            return value
        elif node[0] == 'PRINT':
            outputs = [str(self._evaluate_expr(arg).value) for arg in node[1]]
            self.output.append(' '.join(outputs))
            self.machine_code.append(f"PRINT {' '.join([str(self._evaluate_expr(arg).value) for arg in node[1]])}")
        elif node[0] == 'INPUT':
            _, dtype, prompt = node
            prompt_text = ' '.join(str(self._evaluate_expr(p).value) for p in prompt) if prompt else ''
            if self.input_buffer:
                value = self.input_buffer.pop(0)
            else:
                raise ValueError("Input required but input_buffer is empty")
            try:
                val_obj = Value(dtype, self.TYPE_MAP[dtype](value))
                self.variables[prompt_text or 'input_var'] = val_obj  # store input with prompt text or default
                self.machine_code.append(f"INPUT {dtype} {prompt_text} => {val_obj.value}")
                return val_obj
            except:
                raise TypeError(f"Invalid input type for {dtype}")
        else:
            return self._evaluate_expr(node)

    def _evaluate_expr(self, node):
        if node[0] == 'INT':
            return Value('int', node[1])
        elif node[0] == 'FLOAT':
            return Value('float', node[1])
        elif node[0] == 'STRING':
            return Value('str', node[1])
        elif node[0] == 'BOOL':
            return Value('bool', node[1])
        elif node[0] == 'ID':
            name = node[1]
            if name not in self.variables:
                raise NameError(f"Variable '{name}' not defined")
            return self.variables[name]
        else:
            raise ValueError(f"Unknown expression node: {node}")

    def _type_check(self, value, expected_type):
        if value.type != expected_type:
            raise TypeError(f"Expected type {expected_type}, got {value.type}")

@app.route('/', methods=['GET', 'POST'])
def home():
    output = ''
    machine_code = ''
    code = ''
    inputs = ''
    if request.method == 'POST':
        code = request.form['code']
        inputs = request.form.get('inputs', '')
        interpreter = CustomInterpreter()
        interpreter.input_buffer = [x.strip() for x in inputs.split(',') if x.strip()]
        try:
            ast = interpreter.parse(code)
            interpreter.evaluate(ast)
            output = '\n'.join(interpreter.output)
            machine_code = '\n'.join(interpreter.machine_code)
        except Exception as e:
            output = f"Error: {str(e)}"
    return render_template('index.html', code=code, inputs=inputs, output=output, machine_code=machine_code)

if __name__ == '__main__':
    app.run(debug=True)
