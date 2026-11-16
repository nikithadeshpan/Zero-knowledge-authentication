import json

with open("input9x9.json") as f:
     data = json.load(f)

solution = [[int(x) for x in row] for row in data["solution"]]
puzzle = [[int(x) for x in row] for row in data["puzzle"]]

def valid_group(vals):
    return sorted(vals) == list(range(1, 10))

ok = True
for row in solution:
    ok &= valid_group(row)
for c in range(9):
    ok &= valid_group([solution[r][c] for r in range(9)])
for br in range(0, 9, 3):
    for bc in range(0, 9, 3):
        box = [solution[br+i][bc+j] for i in range(3) for j in range(3)]
        ok &= valid_group(box)
for r in range(9):
    for c in range(9):
        if puzzle[r][c] !=0 and puzzle[r][c] != solution[r][c]:
            ok = False

print("Independent check: VALID" if ok else "Independent check: INVALID")
