pragma circom 2.0.0;

// Checks that all 4 signals in an array are pairwise distinct
template AllDifferent4() {
    signal input in[4];

    // For each pair (i, j), (in[i] - in[j]) must be non-zero.
    // We compute the inverse of each difference — this only exists
    // (i.e. only satisfies inv * diff === 1) if diff != 0.
    signal diff[6];
    signal invDiff[6];

    diff[0] <== in[0] - in[1];
    diff[1] <== in[0] - in[2];
    diff[2] <== in[0] - in[3];
    diff[3] <== in[1] - in[2];
    diff[4] <== in[1] - in[3];
    diff[5] <== in[2] - in[3];

    for (var k = 0; k < 6; k++) {
        invDiff[k] <-- 1 / diff[k];
        diff[k] * invDiff[k] === 1;
    }
}

// Checks a single cell's value is in range 1..4
template InRange1to4() {
    signal input in;
    // (in-1)(in-2)(in-3)(in-4) === 0
    signal a <== (in - 1) * (in - 2);
    signal b <== (in - 3) * (in - 4);
    a * b === 0;
}

template Sudoku4x4() {
    // Public: the puzzle clues. 0 means "blank" (not given).
    signal input puzzle[4][4];
    // Private: the prover's full proposed solution.
    signal input solution[4][4];

    component rangeCheck[4][4];
    component rowCheck[4];
    component colCheck[4];
    component boxCheck[4];

    // 1. Every cell in range 1..4
    for (var i = 0; i < 4; i++) {
        for (var j = 0; j < 4; j++) {
            rangeCheck[i][j] = InRange1to4();
            rangeCheck[i][j].in <== solution[i][j];
        }
    }

    // 2. Every row has 4 distinct values
    for (var i = 0; i < 4; i++) {
        rowCheck[i] = AllDifferent4();
        for (var j = 0; j < 4; j++) {
            rowCheck[i].in[j] <== solution[i][j];
        }
    }

    // 3. Every column has 4 distinct values
    for (var j = 0; j < 4; j++) {
        colCheck[j] = AllDifferent4();
        for (var i = 0; i < 4; i++) {
            colCheck[j].in[i] <== solution[i][j];
        }
    }

    // 4. Every 2x2 box has 4 distinct values
    // Box index b in [0,1,2,3]: boxes laid out row-major over the 2x2 grid of boxes
    var boxRow[4] = [0, 0, 2, 2];
    var boxCol[4] = [0, 2, 0, 2];
    for (var b = 0; b < 4; b++) {
        boxCheck[b] = AllDifferent4();
        var idx = 0;
        for (var di = 0; di < 2; di++) {
            for (var dj = 0; dj < 2; dj++) {
                boxCheck[b].in[idx] <== solution[boxRow[b]+di][boxCol[b]+dj];
                idx++;
            }
        }
    }

    // 5. Solution must match every given (non-zero) clue in the public puzzle
    for (var i = 0; i < 4; i++) {
        for (var j = 0; j < 4; j++) {
            // (puzzle[i][j]) * (puzzle[i][j] - solution[i][j]) === 0
            // If puzzle[i][j] == 0 (blank), this is always satisfied.
            // If puzzle[i][j] != 0, it forces solution[i][j] == puzzle[i][j].
            puzzle[i][j] * (puzzle[i][j] - solution[i][j]) === 0;
        }
    }
}

component main {public [puzzle]} = Sudoku4x4();
