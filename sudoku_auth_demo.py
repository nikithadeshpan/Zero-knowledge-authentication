import json
import subprocess
import sys

def get_grid(prompt_label):
    print(f"\nEnter your {prompt_label} row by row (9 numbers per row, space-separated, 0 for blank):")
    grid = []
    for i in range(9):
        while True:
            row_input = input(f"Row {i+1}: ").strip().split()
            if len(row_input) == 9 and all(x.isdigit() for x in row_input):
                grid.append(row_input)
                break
            print("Invalid row -- enter exactly 9 digits separated by spaces.")
    return grid

def authenticate():
    print("=== Sudoku ZK Authentication Demo ===")
    print("This simulates a login: you must prove you know a valid completed")
    print("Sudoku solution to the registered puzzle, without revealing it.\n")

    with open("input9x9.json") as f:
        registered = json.load(f)
    puzzle = registered["puzzle"]

    print("Registered puzzle (public -- this is what the 'server' already has):")
    for row in puzzle:
        print(" ".join(row))

    solution = get_grid("proposed solution")

    data = {"puzzle": puzzle, "solution": solution}
    with open("input9x9.json", "w") as f:
        json.dump(data, f)

    print("\nGenerating witness from your solution...")
    result = subprocess.run(
        ["node", "sudoku9x9_js/generate_witness.js",
         "sudoku9x9_js/sudoku9x9.wasm", "input9x9.json", "auth_witness.wtns"],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        print("\n*** AUTHENTICATION FAILED ***")
        print("Your solution does not satisfy the puzzle's constraints.")
        return

    print("Generating zero-knowledge proof...")
    subprocess.run(
        ["snarkjs", "groth16", "prove", "sudoku9x9_final.zkey",
         "auth_witness.wtns", "auth_proof.json", "auth_public.json"],
        capture_output=True, text=True
    )

    print("Verifying proof (server-side check, using ONLY the public puzzle)...")
    verify_result = subprocess.run(
        ["snarkjs", "groth16", "verify", "verification_key.json",
         "auth_public.json", "auth_proof.json"],
        capture_output=True, text=True
    )

    if "OK!" in verify_result.stdout:
        print("\n*** AUTHENTICATION SUCCESSFUL ***")
        print("Proof verified. Your solution was never transmitted or stored.")
    else:
        print("\n*** AUTHENTICATION FAILED ***")
        print("Proof did not verify.")

if __name__ == "__main__":
    authenticate()
