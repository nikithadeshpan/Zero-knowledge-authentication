import json

with open("make_sudoku9x9_input.py") as f:
    exec(compile(f.read().split("def to_str_grid")[0], "grid_def", "exec"))

def check_group(vals, label):
    if sorted(vals) != list(range(1, 10)):
        print(f"INVALID {label}: {vals}")
        return False
    return True

ok = True
for i, row in enumerate(solution):
    ok &= check_group(row, f"row {i}")
for j in range(9):
    col = [solution[i][j] for i in range(9)]
    ok &= check_group(col, f"col {j}")
for br in range(0,9,3):
    for bc in range(0,9,3):
        box = [solution[br+i][bc+j] for i in range(3) for j in range(3)]
        ok &= check_group(box, f"box ({br},{bc})")

print("Solution grid is VALID" if ok else "Solution grid is INVALID")
