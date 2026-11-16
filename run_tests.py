import json
import subprocess
import copy

valid_solution = [
    ["1","2","3","4"],
    ["3","4","1","2"],
    ["2","1","4","3"],
    ["4","3","2","1"]
]
puzzle = [
    ["1","0","0","4"],
    ["0","4","1","0"],
    ["0","1","4","0"],
    ["4","0","0","1"]
]

def run_case(name, solution, expect_pass):
    data = {"puzzle": puzzle, "solution": solution}
    with open("input.json", "w") as f:
        json.dump(data, f)

    result = subprocess.run(
        ["node", "sudoku4x4_js/generate_witness.js",
         "sudoku4x4_js/sudoku4x4.wasm", "input.json", "witness_test.wtns"],
        capture_output=True, text=True
    )
    passed = (result.returncode == 0)

    status = "PASS" if passed == expect_pass else "*** UNEXPECTED ***"
    outcome = "accepted" if passed else "rejected"
    expected = "should be accepted" if expect_pass else "should be rejected"
    print(f"[{status}] {name}: witness generation {outcome} ({expected})")
    if passed != expect_pass:
        print("    stderr:", result.stderr.strip()[:200])

run_case("Valid solution", valid_solution, expect_pass=True)

bad = copy.deepcopy(valid_solution)
bad[0][1] = bad[0][0]
run_case("Duplicate in row 0", bad, expect_pass=False)

bad = copy.deepcopy(valid_solution)
bad[1][0] = bad[0][0]
run_case("Duplicate in column 0", bad, expect_pass=False)

bad = copy.deepcopy(valid_solution)
bad[1][1] = bad[0][0]
run_case("Duplicate in top-left box", bad, expect_pass=False)

bad = copy.deepcopy(valid_solution)
bad[2][2] = "5"
run_case("Out-of-range value (5)", bad, expect_pass=False)

bad = copy.deepcopy(valid_solution)
bad[0][0] = "2"
run_case("Solution contradicts given clue", bad, expect_pass=False)

print("\nAll tests complete.")
