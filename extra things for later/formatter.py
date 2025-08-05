import sys

def prettify_easy(file_path):
    with open(file_path, 'r') as f:
        lines = f.readlines()

    output = []
    indent_level = 0

    for line in lines:
        stripped = line.strip()

        if stripped.startswith("function ") and stripped.endswith("["):
            output.append("function " + stripped[len("function "):-1].strip() + " [")
            indent_level += 1
        elif stripped == "]":
            indent_level -= 1
            output.append("]")
        elif stripped:
            indented = "    " * indent_level + stripped
            output.append(indented)
        else:
            output.append("")

    with open(file_path, 'w') as f:
        f.write("\n".join(output))

    print(f"Prettified: {file_path}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python formatter.py <file.easy>")
    else:
        prettify_easy(sys.argv[1])
