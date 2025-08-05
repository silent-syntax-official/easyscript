import sys
import os
import re

variables = {}

def evaluate_expression(expr):
    expr = expr.strip()
    
    # Handle string in quotes
    if (expr.startswith('"') and expr.endswith('"')) or (expr.startswith("'") and expr.endswith("'")):
        return expr[1:-1]

    # Handle arithmetic: x + y
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

    if line.startswith("let "):
        match = re.match(r"let (\w+) = (\w+)", line)
        if not match:
            raise ValueError(f"Invalid let syntax: {line}")
        var, val = match.groups()
        variables[var] = int(val)

    elif line.startswith("print(") and line.endswith(")"):
        expr = line[len("print("):-1].strip()
        result = evaluate_expression(expr)
        print(result)

    else:
        raise ValueError(f"Invalid EasyScript syntax: {line}")

def run_file(filename):
    if not os.path.exists(filename):
        print(f"Error: File '{filename}' not found.")
        return

    try:
        with open(filename, 'r') as file:
            for line in file:
                interpret_easy_line(line)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: easyscript <filename.easy>")
    else:
        run_file(sys.argv[1])
