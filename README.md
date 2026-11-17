# Zero-Knowledge Authentication: Fiat-Shamir and a Sudoku zk-SNARK

Code from my MEng Cyber Security project at the University of Limerick (LK473), supervised by Professor Richard Conway.

With a password, the server has to hold something that can be stolen. Zero-knowledge authentication removes that: the user proves they know a secret and the verifier learns nothing about it. I built two small demonstrations of this idea, using two very different techniques, to see how each one works in practice.

| | Fiat-Shamir identification | Sudoku zk-SNARK |
|---|---|---|
| Secret | A number `s` | A solved Sudoku grid |
| What the verifier holds | `v = s² mod n` | The unsolved puzzle and a verification key |
| Technique | Interactive challenge-response, modular arithmetic | Arithmetic circuit, Groth16 proof |
| Tools | Python | Circom, snarkjs, Python for tests |

These are teaching demonstrations, not production code. The limitations are listed at the end and they matter.

## Files

**Fiat-Shamir**

| File | What it does |
|---|---|
| `Fiat_Shamir.py` | Setup, one challenge-response round, a 20-round honest prover run and a 20-round impersonator run |

**Sudoku circuits**

| File | What it does |
|---|---|
| `multiplier.circom` | One-line circuit I used to check the toolchain worked before writing any Sudoku logic |
| `sudoku4x4.circom` | Warm-up circuit: 2x2 boxes, digits 1-4 |
| `sudoku9x9.circom` | Full 9x9 circuit |

**Inputs and tests**

| File | What it does |
|---|---|
| `make_input.py`, `make_bad_input.py` | Write a valid or an invalid 4x4 `input.json` |
| `make_sudoku9x9_input.py` | Writes a valid `input9x9.json` (public puzzle and private solution) |
| `validate_grid.py` | Checks the grid in `make_sudoku9x9_input.py` is a valid Sudoku before it is used |
| `run_tests.py`, `run_tests_9x9.py` | Six-case regression tests for the 4x4 and 9x9 circuits |
| `independent_check.py` | Checks `input9x9.json` with plain Python loops, no Circom involved |
| `sudoku_auth_demo.py` | Interactive "log in by solving the puzzle" demo |

**Proof artefacts from my run**

| File | What it is |
|---|---|
| `verification_key.json` | Groth16 verification key for the 9x9 circuit |
| `proof.json`, `public.json` | A proof I generated, and its public input (the 81 puzzle cells) |
| `public_tampered.json` | The same public input with one digit changed |

## Verify my proof without building anything

You only need snarkjs (`npm install -g snarkjs`).

```bash
snarkjs groth16 verify verification_key.json public.json proof.json
```

This prints `OK!`. The solved grid is not in any of those three files.

```bash
snarkjs groth16 verify verification_key.json public_tampered.json proof.json
```

This prints `Invalid proof`. The proof is bound to the exact puzzle it was made for, not to any valid Sudoku.

## Part 1: Fiat-Shamir identification protocol

This is the interactive identification protocol, not the Fiat-Shamir heuristic that turns interactive proofs into non-interactive ones.

**Setup.** Two primes `p` and `q` give a public modulus `n = p*q`. The prover picks a secret `s` with `1 < s < n` and `gcd(s, n) = 1`, and registers `v = s² mod n` with the verifier. The verifier never sees `s`.

**One round.**

1. The prover picks a fresh random `r` with `gcd(r, n) = 1` and sends the commitment `x = r² mod n`.
2. The verifier sends a random challenge `e`, either 0 or 1.
3. The prover replies with `y = r` if `e = 0`, or `y = r*s mod n` if `e = 1`.
4. The verifier accepts the round if `y² mod n = x * v^e mod n`.

Someone who does not know `s` has to commit to `x` before seeing `e`. They can prepare an answer for one value of `e` but not both, so they get through a round with probability 1/2. Over 20 rounds that drops to (1/2)^20, about 1 in a million.

**Run it**

```bash
python3 Fiat_Shamir.py
```

The script asks for a secret, runs the honest prover, then asks for the secret again and for an impersonator's guess.

| Scenario | Rounds passed | Outcome |
|---|---|---|
| Honest prover, correct secret | 20/20 | Login successful |
| Impersonator, guessed secret | about 10/20 | Access denied |

Why this is zero-knowledge: the verifier only ever sees `(x, e, y)`. A simulator that does not know `s` can produce transcripts that look the same as real ones, so a real transcript cannot be leaking anything about `s`.

## Part 2: Proving a Sudoku solution without showing it

The puzzle is public. The solved grid is private. The prover produces a Groth16 proof that they know a solution to that exact puzzle, and the verifier checks it without ever seeing the grid.

I built a 4x4 version first. The constraint logic is the same shape as 9x9, and it compiles in seconds, so mistakes were cheap to find. Then I scaled the same pattern up.

### How the rules become constraints

A circuit has no `if` statements. Every Sudoku rule has to become a polynomial equation that is either satisfied or not.

- **Each cell is 1 to 9.** The circuit forces `(x-1)(x-2)...(x-9) = 0`. That product is zero only when `x` is one of the allowed digits.
- **Rows, columns and boxes have no repeats.** For every pair `a`, `b` in a group, the circuit requires that `a - b` has a multiplicative inverse. Zero has no inverse in a field, so two equal values make the constraint impossible to satisfy. Nine cells give 36 pairs per group, and there are 27 groups.
- **The solution matches the given clues.** For each cell, `puzzle * (puzzle - solution) = 0`. A blank cell (0) passes automatically. A clue forces the solution to equal it.

I used the inverse trick for "all different" instead of a sorting-based approach because it needs no extra circuitry and rests on one fact that is easy to check by hand.

| Circuit | Non-linear constraints | Linear constraints |
|---|---|---|
| `sudoku4x4.circom` | 136 | 72 |
| `sudoku9x9.circom` | 1701 | 972 |

### Requirements

Built and tested on Ubuntu 24.04.

- Rust (to build Circom)
- [Circom](https://github.com/iden3/circom) 2.x
- Node.js (I installed it with nvm)
- snarkjs 0.7.6: `npm install -g snarkjs`
- Python 3

### Compile and check a witness

```bash
circom sudoku9x9.circom --r1cs --wasm --sym
python3 make_sudoku9x9_input.py
node sudoku9x9_js/generate_witness.js sudoku9x9_js/sudoku9x9.wasm input9x9.json witness9x9.wtns
snarkjs wtns check sudoku9x9.r1cs witness9x9.wtns
```

Run `make_sudoku9x9_input.py` before generating a witness. The test script and the demo both overwrite `input9x9.json`, so it may hold a deliberately wrong solution from the last run.

### Trusted setup (Groth16)

```bash
snarkjs powersoftau new bn128 12 pot12_0000.ptau -v
snarkjs powersoftau contribute pot12_0000.ptau pot12_0001.ptau --name="First contribution" -v
snarkjs powersoftau prepare phase2 pot12_0001.ptau pot12_final.ptau -v
snarkjs groth16 setup sudoku9x9.r1cs pot12_final.ptau sudoku9x9_0000.zkey
snarkjs zkey contribute sudoku9x9_0000.zkey sudoku9x9_final.zkey --name="1st Contributor" -v
snarkjs zkey export verificationkey sudoku9x9_final.zkey verification_key.json
```

Running this produces your own keys, and it overwrites my `verification_key.json`. My `proof.json` will not verify against a new key, so keep a copy if you want both.

I chose Groth16 over PLONK because proofs are small and verification is fast, and verification is the step a server would run on every login. The cost is a setup tied to this one circuit.

### Prove and verify

```bash
snarkjs groth16 prove sudoku9x9_final.zkey witness9x9.wtns proof.json public.json
snarkjs groth16 verify verification_key.json public.json proof.json
```

`public.json` contains only the 81 puzzle cells. Verification uses the verification key, `public.json` and `proof.json`, and nothing else.

### Tests

Compile the circuit first, then:

```bash
python3 run_tests_9x9.py
```

The script takes one valid solved grid and generates six cases:

| Case | Expected | Result |
|---|---|---|
| Valid solution | accepted | accepted |
| Duplicate in a row | rejected | rejected |
| Duplicate in a column | rejected | rejected |
| Duplicate in a 3x3 box | rejected | rejected |
| Value outside 1-9 | rejected | rejected |
| Solution contradicts a clue | rejected | rejected |

The same six cases pass on the 4x4 circuit: compile `sudoku4x4.circom` and run `python3 run_tests.py`.

`independent_check.py` validates the grid in `input9x9.json` with ordinary loops, with no dependency on the circuit. It agrees with the circuit, which rules out a bug shared between the circuit and its test data.

### Authentication demo

This needs the compiled circuit and the `sudoku9x9_final.zkey` from the trusted setup.

```bash
python3 make_sudoku9x9_input.py
python3 sudoku_auth_demo.py
```

The script shows the public puzzle and asks for a solution row by row. It then runs witness generation, proof generation and verification, and prints `AUTHENTICATION SUCCESSFUL` or `AUTHENTICATION FAILED`. A wrong grid fails at witness generation, before a proof is attempted.

## Limitations

**Fiat-Shamir**

- `n = 3233` (61 × 53) is tiny so the numbers stay readable. Anyone can factor it. A real modulus would be at least 2048 bits.
- It uses Python's `random`, which is not cryptographically secure. Real code would use the `secrets` module.
- It is interactive: prover and verifier both have to be online for every round.

**Sudoku**

- The trusted setup had one contributor, me. Groth16 setup is only safe if at least one contributor is honest and discards their randomness, so a real deployment needs a multi-party ceremony.
- The demo reuses the same puzzle, so a captured proof could be replayed. The fix is a fresh verifier nonce bound into the proof as an extra circuit input. I did not implement this.
- The tests cover one representative case per rule, not every possible invalid grid.

## References

- A. Fiat and A. Shamir, "How to Prove Yourself: Practical Solutions to Identification and Signature Problems", CRYPTO 1986.
- R. Gradwohl, M. Naor, B. Pinkas and G. N. Rothblum, "Cryptographic and Physical Zero-Knowledge Proof Systems for Solutions of Sudoku Puzzles", Theory of Computing Systems, 2009.
- M. Bellés-Muñoz et al., "Circom: A Circuit Description Language for Building Zero-Knowledge Applications", IEEE TDSC, 2023.
- J. Groth, "On the Size of Pairing-Based Non-interactive Arguments", EUROCRYPT 2016.

## Author

Nikitha Deshpande, MEng Cyber Security, University of Limerick.
