import sys
import os
import re

variables = {}
functions = {}

def evaluate_expression(expr):
    expr = expr.strip()

    if (expr.startswith('"') and expr.endswith('"')) or (expr.startswith("'") and expr.endswith("'")):
        return expr[1:-1]

    tokens = re.findall(r'\w+|[+-]', expr)
    if not tokens:
        raise ValueError("Empty expression")

    total = int(variables.get(tokens[0], tokens[0]))
    i = 1
    while i < len(tokens):
        op = tokens[i]
        right = int(variables.get(tokens[i+1], tokens[i+1]))
        if op == '+':
            total += right
        elif op == '-':
            total -= right
        else:
            raise ValueError(f"Unsupported operator: {op}")
        i += 2
    return total

def interpret_easy_line(line):
    line = line.strip()
    if not line:
        return

    # let a = 1
    if line.startswith("let "):
        match = re.match(r"let (\w+) = (\w+)", line)
        if not match:
            raise ValueError(f"Invalid let syntax: {line}")
        var, val = match.groups()
        variables[var] = int(val)
        return

    # print(...)
    if line.startswith("print(") and line.endswith(")"):
        expr = line[len("print("):-1].strip()
        result = evaluate_expression(expr)
        print(result)
        return

    # function call: name()
    if re.match(r"^[a-zA-Z_]\w*\(\)$", line):
        func_name = line[:-2]
        if func_name not in functions:
            raise ValueError(f"Function '{func_name}' not defined.")
        for func_line in functions[func_name]:
            interpret_easy_line(func_line)
        return

    raise ValueError(f"Invalid EasyScript syntax: {line}")

def run_file(filename):
    if not os.path.exists(filename):
        print(f"Error: File '{filename}' not found.")
        return

    try:
        with open(filename, 'r') as file:
            lines = file.readlines()

        i = 0
        while i < len(lines):
            line = lines[i].strip()

            # Skip blank lines
            if not line:
                i += 1
                continue

            # Function definition
            if line.startswith("function ") and line.endswith("["):
                func_name = line[len("function "):-1].strip()
                i += 1
                body = []
                while i < len(lines):
                    inner = lines[i].strip()
                    if inner == "]":
                        break
                    body.append(inner)
                    i += 1
                functions[func_name] = body
                i += 1
                continue

            # Normal line
            interpret_easy_line(line)
            i += 1

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: easyscript <filename.easy>")
    else:
        run_file(sys.argv[1])
