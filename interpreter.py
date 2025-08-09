import sys
import os
import re
import time
import subprocess
import json
import tempfile

variables = {}
functions = {}
prompt_counter = 1  # for input1, input2, etc.

def evaluate_expression(expr):
    expr = expr.strip()
    if (expr.startswith('"') and expr.endswith('"')) or (expr.startswith("'") and expr.endswith("'")):
        return expr[1:-1]

    tokens = re.findall(r'\w+|[+-]', expr)
    if not tokens:
        raise ValueError("Empty expression")

    def val(token):
        if token.isdigit() or (token.startswith('-') and token[1:].isdigit()):
            return int(token)
        if token in variables:
            return variables[token]
        raise ValueError(f"Undefined variable: {token}")

    total = val(tokens[0])
    i = 1
    while i < len(tokens):
        op = tokens[i]
        right = val(tokens[i + 1])
        if op == '+':
            total += right
        elif op == '-':
            total -= right
        else:
            raise ValueError(f"Unsupported operator: {op}")
        i += 2
    return total

def strip_comments(line):
    while True:
        start = line.find("//")
        if start == -1:
            break
        end = line.find("//", start + 2)
        if end == -1:
            break
        line = line[:start] + line[end + 2:]
    return line.strip()

def interpret_easy_line(line):
    global prompt_counter
    line = strip_comments(line)
    if not line:
        return

    # --- runpyfile with shared vars ---
    if line.startswith("runpyfile(") and line.endswith(")"):
        py_path = line[len("runpyfile("):-1].strip().strip('"').strip("'")
        if not os.path.isfile(py_path):
            print(f"[EasyScript ERROR] Python file not found: {py_path}")
            return
        
        # Save current EasyScript variables to temp file
        temp_json = os.path.join(tempfile.gettempdir(), "easyscript_vars.json")
        with open(temp_json, "w") as f:
            json.dump(variables, f)

        try:
            # Run the Python file with the path to the temp vars file
            subprocess.run(["python", py_path, temp_json], check=True)
        except subprocess.CalledProcessError as e:
            print(f"[EasyScript ERROR] Python script failed with exit code {e.returncode}")
            return

        # Reload variables after Python finishes
        if os.path.exists(temp_json):
            with open(temp_json, "r") as f:
                try:
                    loaded_vars = json.load(f)
                    variables.update(loaded_vars)
                except json.JSONDecodeError:
                    print("[EasyScript ERROR] Could not read variables from Python output.")
        return
    # ----------------------------------

    if line.startswith("delay(") and line.endswith(")"):
        try:
            seconds = float(line[len("delay("):-1].strip())
            time.sleep(seconds)
        except ValueError:
            raise ValueError(f"Invalid delay value: {line}")
        return

    if line == "letterfromsilsyn()()":
        print("""\nDear Easyscript User,

hello, if you're reading this, congrats! I'm probably dead, but my language lives on. 
To those who have helped EasyScript grow, thank you. 
And to you reading this—encourage your kids to be what I was when I was 9: 
a coder, a creator, a dreamer, and most of all, a believer.

Believe in yourself, and you can do anything.

— Silent Syntax (Silsyn)
""")
        return

    if line.startswith("prompt(") and line.endswith(")"):
        inner = line[len("prompt("):-1].strip()
        if (inner.startswith('"') and inner.endswith('"')) or (inner.startswith("'") and inner.endswith("'")):
            prompt_text = inner[1:-1]
        else:
            prompt_text = inner
        response = input(prompt_text)
        variables[f"input{prompt_counter}"] = response
        prompt_counter += 1
        return

    if line.startswith("let "):
        match = re.match(r"let (\w+) = (.+)", line)
        if not match:
            raise ValueError(f"Invalid let syntax: {line}")
        var, val = match.groups()
        val = val.strip()

        if val.isdigit() or (val.startswith('-') and val[1:].isdigit()):
            variables[var] = int(val)
        elif (val.startswith('"') and val.endswith('"')) or (val.startswith("'") and val.endswith("'")):
            variables[var] = val[1:-1]
        elif val in variables:
            variables[var] = variables[val]
        else:
            variables[var] = val
        return

    if line.startswith("print(") and line.endswith(")"):
        expr = line[len("print("):-1].strip()
        result = evaluate_expression(expr)
        print(result)
        return

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
            if not line:
                i += 1
                continue

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

            if line.startswith("loop"):
                match = re.match(r"loop\s*(\d*)\[", line)
                if match is None:
                    raise ValueError(f"Invalid loop syntax: {line}")
                count_str = match.group(1)
                count = int(count_str) if count_str else 100

                i += 1
                loop_body = []
                while i < len(lines):
                    inner = lines[i].strip()
                    if inner == "]":
                        break
                    loop_body.append(inner)
                    i += 1
                for _ in range(count):
                    for loop_line in loop_body:
                        interpret_easy_line(loop_line)
                i += 1
                continue

            if line.startswith("if "):
                cond_match = re.match(r"if (.+)\[", line)
                if not cond_match:
                    raise ValueError(f"Invalid if syntax: {line}")
                cond_str = cond_match.group(1).strip()
                conds = [c.strip() for c in cond_str.split("&&")]

                def check_condition(cond):
                    m = re.match(r"(\w+)\s*=\s*(.+)", cond)
                    if not m:
                        raise ValueError(f"Invalid condition: {cond}")
                    var_name, value = m.groups()
                    var_val = variables.get(var_name)

                    value = value.strip()
                    if value.isdigit() or (value.startswith('-') and value[1:].isdigit()):
                        cmp_val = int(value)
                    elif (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
                        cmp_val = value[1:-1]
                    else:
                        cmp_val = variables.get(value, value)

                    return var_val == cmp_val

                all_true = all(check_condition(c) for c in conds)

                i += 1
                block = []
                while i < len(lines):
                    inner = lines[i].strip()
                    if inner == "]":
                        break
                    block.append(inner)
                    i += 1

                if all_true:
                    for bline in block:
                        interpret_easy_line(bline)
                i += 1
                continue

            interpret_easy_line(line)
            i += 1

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: easyscript <filename.easy>")
    else:
        run_file(sys.argv[1])
