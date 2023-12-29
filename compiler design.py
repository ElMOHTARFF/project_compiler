from ply import lex, yacc

# Update the tokens list
tokens = ['IDENTIFIER', 'NUMBER', 'PLUSM', 'EQUALSM',
          'PRINTTESTCOMPILERM', 'LPAREN', 'RPAREN', 'SEMICOLON', 'CHARACTER']



# Define regular expressions for tokens
t_PLUSM = r'\+m'
t_EQUALSM = r'=m'
# t_PRINTTESTCOMPILERM = r'printtestcompilerm'
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_SEMICOLON = r';'
t_CHARACTER = r"'.'"

def t_NUMBER(t):
    r'\d+m'
    t.value = int(t.value[:-1])  # Remove 'm' suffix
    return t

def t_IDENTIFIER(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*m?'
    if t.value == 'printtestcompilerm':
        t.type = 'PRINTTESTCOMPILERM'
    return t

t_ignore = ' \t'
# Update the t_PRINTTESTCOMPILERM token definition
def t_PRINTTESTCOMPILERM(t):
    r'printtestcompilerm'
    t.type = 'PRINTTESTCOMPILERM'
    return t
def t_error(t):
    print(f"Illegal character '{t.value[0]}' at line {t.lineno}")
    t.lexer.skip(1)

# Build the lexer
lexer = lex.lex()

# Intermediate Code Generator class
class IntermediateCodeGenerator:
    def __init__(self):
        self.code = []

    def generate_code(self, statement):
        if statement['type'] == 'assignment':
            self.generate_assignment_code(statement)
        elif statement['type'] == 'printtestcompilerm':
            self.generate_printtestcompilerm_code(statement)

    def generate_assignment_code(self, statement):
        variable = statement['variable']
        expression = statement['value']

        if expression['type'] == 'binary_operation':
            self.generate_binary_operation_code(expression, variable)
        elif expression['type'] == 'number':
            self.code.append(f"MOV {variable}, {expression['value']}")
        elif expression['type'] == 'character':
            self.code.append(f"MOV {variable}, '{expression['value']}'")
        elif expression['type'] == 'identifier':
            # Assuming that identifiers represent strings
            self.code.append(f"MOV {variable}, {expression['value']}")
        else:
            print(f"Unsupported expression type: {expression['type']}")

    def generate_binary_operation_code(self, expression, result_variable):
        left_operand = expression['left']
        right_operand = expression['right']
        operator = expression['operator']

        # New variable to hold the result
        result_temp_variable = f"temp_result_{len(self.code)}"

        # Assume x86-64 assembly-style code for simplicity
        self.code.append(f"MOV RAX, {left_operand}")
        if operator == '+m':
            self.code.append(f"ADD RAX, {right_operand}")
        elif operator == '-m':
            self.code.append(f"SUB RAX, {right_operand}")
        # Store the result in the new variable
        self.code.append(f"MOV {result_temp_variable}, RAX")

        # Print the result using printtestcompilerm statement
        print_statement = {'type': 'printtestcompilerm',
                           'expression': {'type': 'identifier', 'value': result_temp_variable}}
        self.generate_printtestcompilerm_code(print_statement)

        # Store the result in the provided result_variable
        self.code.append(f"MOV {result_variable}, {result_temp_variable}")

    def generate_printtestcompilerm_code(self, statement):
        expression = statement['expression']
        if expression['type'] == 'identifier':
            # Assuming that identifiers represent strings
            self.code.append(f"MOV RDI, {expression['value']}")
        elif expression['type'] == 'character':
            self.code.append(f"MOV RDI, '{expression['value']}'")
        elif expression['type'] == 'number':
            # Convert the number to a string before printing
            self.code.append(f"MOV RDI, {expression['value']}")
            self.code.append("CALL int_to_str")  # Assume int_to_str converts RDI to string

        # Assume x86-64 assembly-style code for simplicity
        self.code.append("CALL print_function")


# Build the Intermediate Code Generator
intermediate_code_generator = IntermediateCodeGenerator()

# Define grammar rules
def p_statement_assignment(p):
    'statement : IDENTIFIER EQUALSM expression SEMICOLON'
    variable, expression = p[1], p[3]
    statement = {'type': 'assignment', 'variable': variable, 'value': expression}
    intermediate_code_generator.generate_code(statement)

# Update the p_statement_printtestcompilerm_identifier production
def p_statement_printtestcompilerm_identifier(p):
    'statement : PRINTTESTCOMPILERM LPAREN IDENTIFIER RPAREN SEMICOLON'
    expression = {'type': 'identifier', 'value': p[3]}
    statement = {'type': 'printtestcompilerm', 'expression': expression}
    intermediate_code_generator.generate_code(statement)

# Update the p_statement_printtestcompilerm_literal production
def p_statement_printtestcompilerm_literal(p):
    'statement : PRINTTESTCOMPILERM LPAREN expression RPAREN SEMICOLON'
    expression = p[3]
    statement = {'type': 'printtestcompilerm', 'expression': expression}
    intermediate_code_generator.generate_code(statement)

def p_expression_binary_operation(p):
    'expression : expression PLUSM expression'
    left_operand, right_operand = p[1], p[3]
    operator = '+m'
    p[0] = {'type': 'binary_operation', 'left': left_operand, 'right': right_operand, 'operator': operator}

def p_expression_number(p):
    'expression : NUMBER'
    p[0] = {'type': 'number', 'value': p[1]}

def p_expression_character(p):
    'expression : CHARACTER'
    p[0] = {'type': 'character', 'value': p[1][1:-1]}  # Remove single quotes

def p_expression_identifier(p):
    'expression : IDENTIFIER'
    p[0] = {'type': 'identifier', 'value': p[1]}

def p_error(p):
    if p:
        print(f"{p.value}")
    else:
        print("Syntax error at the end of input")

# Build the parser
parser = yacc.yacc()


if __name__ == '__main__':

    # the code may excute one by one i mean arithmitic only or print only statement by statement in somecases
    # source_code = "x =m 5m +m 3m; printtestcompilerm(x);"
    source_code = "x =m 5m +m 3m; printtestcompilerm(x); y =m 'A';"
    lexer.input(source_code)
    for tok in lexer:
        print(tok)

    result = parser.parse(source_code)

    # Print the intermediate code without sections
    print("\nIntermediate Code (Non-Separated):")
    for line in intermediate_code_generator.code:
        print(line)

    # Print the intermediate code with sections
    print("\nIntermediate Code (Separated):")

    # Section for Arithmetic Operations
    print("\nArithmetic Operations:")
    for line in intermediate_code_generator.code:
        if "MOV" in line or "ADD" in line or "SUB" in line:
            print(line)

    # Section for Print Statements
    print("\nPrint Statements:")
    for line in intermediate_code_generator.code:
        if "CALL print_function" in line:
            print(line)
