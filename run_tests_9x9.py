import json
import subprocess
import copy

solution = [
    [5,3,4,6,7,8,9,1,2],
    [6,7,2,1,9,5,3,4,8],
    [1,9,8,3,4,2,5,6,7],
    [8,5,9,7,6,1,4,2,3],
    [4,2,6,8,5,3,7,9,1],
    [7,1,3,9,2,4,8,5,6],
    [9,6,1,5,3,7,2,8,4],
    [2,8,7,4,1,9,6,3,5],
    [3,4,5,2,8,6,1,7,9]
]
puzzle = [
    [5,3,0,0,7,0,0,0,0],
    [6,0,0,1,9,5,0,0,0],
    [0,9,8,0,0,0,0,6,0],
    [8,0,0,0,6,0,0,0,3],
    [4,0,0,8,0,3,0,0,1],
    [7,0,0,0,2,0,0,0,6],
    [0,6,0,0,0,0,2,8,0],
    [0,0,0,4,1,9,0,0,5],
    [0,0,0,0,8,0,0,7,9]
]

def to_str_grid(g):
    return [[str(v) for v in row] for row in g]

def run_case(name, sol, expect_pass):
    data = {"puzzle": to_str_grid(puzzle), "solution": to_str_grid(sol)}
    with open("input9x9.json", "w") as f:
        json.dump(data, f)

    result = subprocess.run(
        ["node", "sudoku9x9_js/generate_witness.js",
         "sudoku9x9_js/sudoku9x9.wasm", "input9x9.json", "witness9x9_test.wtns"],
        capture_output=True, text=True
    )
    passed = (result.returncode == 0)
    status = "PASS" if passed == expect_pass else "*** UNEXPECTED ***"
    outcome = "accepted" if passed else "rejected"
    expected = "should be accepted" if expect_pass else "should be rejected"
    print(f"[{status}] {name}: witness generation {outcome} ({expected})")
    if passed != expect_pass:
        print("    stderr:", result.stderr.strip()[:200])

run_case("Valid solution", solution, expect_pass=True)

bad = copy.deepcopy(solution)
bad[0][1] = bad[0][0]
run_case("Duplicate in row 0", bad, expect_pass=False)

bad = copy.deepcopy(solution)
bad[1][0] = bad[0][0]
run_case("Duplicate in column 0", bad, expect_pass=False)

bad = copy.deepcopy(solution)
bad[1][1] = bad[0][0]
run_case("Duplicate in top-left box", bad, expect_pass=False)

bad = copy.deepcopy(solution)
bad[4][4] = 10
run_case("Out-of-range value (10)", bad, expect_pass=False)

bad = copy.deepcopy(solution)
bad[0][0] = 9
run_case("Solution contradicts given clue", bad, expect_pass=False)

print("\nAll tests complete.")
