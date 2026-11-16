pragma circom 2.0.0;

// Checks that all 9 signals in an array are pairwise distinct
template AllDifferent9() {
    signal input in[9];

    signal diff[36];
    signal invDiff[36];

    var idx = 0;
    for (var i = 0; i < 9; i++) {
        for (var j = i+1; j < 9; j++) {
            diff[idx] <== in[i] - in[j];
            idx++;
        }
    }

    for (var k = 0; k < 36; k++) {
        invDiff[k] <-- 1 / diff[k];
        diff[k] * invDiff[k] === 1;
    }
}

// Checks a single cell's value is in range 1..9
template InRange1to9() {
    signal input in;
    signal p[8];

    p[0] <== (in - 1) * (in - 2);
    for (var k = 3; k <= 9; k++) {
        p[k-2] <== p[k-3] * (in - k);
    }
    p[7] === 0;
}

template Sudoku9x9() {
    signal input puzzle[9][9];
    signal input solution[9][9];

    component rangeCheck[9][9];
    component rowCheck[9];
    component colCheck[9];
    component boxCheck[9];

    // 1. Every cell in range 1..9
    for (var i = 0; i < 9; i++) {
        for (var j = 0; j < 9; j++) {
            rangeCheck[i][j] = InRange1to9();
            rangeCheck[i][j].in <== solution[i][j];
        }
    }

    // 2. Every row has 9 distinct values
    for (var i = 0; i < 9; i++) {
        rowCheck[i] = AllDifferent9();
        for (var j = 0; j < 9; j++) {
            rowCheck[i].in[j] <== solution[i][j];
        }
    }

    // 3. Every column has 9 distinct values
    for (var j = 0; j < 9; j++) {
        colCheck[j] = AllDifferent9();
        for (var i = 0; i < 9; i++) {
            colCheck[j].in[i] <== solution[i][j];
        }
    }

    // 4. Every 3x3 box has 9 distinct values
    var boxRow[9] = [0,0,0,3,3,3,6,6,6];
    var boxCol[9] = [0,3,6,0,3,6,0,3,6];
    for (var b = 0; b < 9; b++) {
        boxCheck[b] = AllDifferent9();
        var idx = 0;
        for (var di = 0; di < 3; di++) {
            for (var dj = 0; dj < 3; dj++) {
                boxCheck[b].in[idx] <== solution[boxRow[b]+di][boxCol[b]+dj];
                idx++;
            }
        }
    }

    // 5. Solution must match every given (non-zero) clue
    for (var i = 0; i < 9; i++) {
        for (var j = 0; j < 9; j++) {
            puzzle[i][j] * (puzzle[i][j] - solution[i][j]) === 0;
        }
    }
}

component main {public [puzzle]} = Sudoku9x9();
