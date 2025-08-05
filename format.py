import sys
import os

def format_file(filename):
    if not os.path.exists(filename):
        print(f"File '{filename}' not found for formatting.")
        return

    with open(filename, 'r') as f:
        lines = f.readlines()

    changed = True
    while changed:
        changed = False
        new_lines = []
        for line in lines:
            stripped = line.rstrip('\n')
            if len(stripped) <= 30:
                new_lines.append(stripped)
                continue

            break_pos = stripped.rfind(' ', 0, 30)
            if break_pos == -1:
                break_pos = 30

            first_part = stripped[:break_pos].rstrip()
            second_part = stripped[break_pos:].lstrip()

            new_lines.append(first_part)
            new_lines.append(second_part)
            changed = True

        lines = new_lines

    with open(filename, 'w') as f:
        for l in lines:
            f.write(l + '\n')

    print(f"Formatted file '{filename}' successfully.")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python format.py <filename.easy>")
        sys.exit(1)

    format_file(sys.argv[1])
