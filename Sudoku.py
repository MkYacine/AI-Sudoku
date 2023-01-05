#Work done by Yacine Mkhinini 20170474 and Labidi Mahmoud 20176755

## Solve Every Sudoku Puzzle

## See http://norvig.com/sudoku.html

## Throughout this program we have:
##   r is a row,    e.g. 'A'
##   c is a column, e.g. '3'
##   s is a square, e.g. 'A3'
##   d is a digit,  e.g. '9'
##   u is a unit,   e.g. ['A1','B1','C1','D1','E1','F1','G1','H1','I1']
##   grid is a grid,e.g. 81 non-blank chars, e.g. starting with '.18...7...
##   values is a dict of possible values, e.g. {'A1':'12349', 'A2':'8', ...}

def cross(A, B):
    "Cross product of elements in A and elements in B."
    return [a + b for a in A for b in B]


digits = '123456789'
rows = 'ABCDEFGHI'
cols = digits
squares = cross(rows, cols)
unitlist = ([cross(rows, c) for c in cols] +
            [cross(r, cols) for r in rows] +
            [cross(rs, cs) for rs in ('ABC', 'DEF', 'GHI') for cs in ('123', '456', '789')])
units = dict((s, [u for u in unitlist if s in u])
             for s in squares)
peers = dict((s, set(sum(units[s], [])) - {s})
             for s in squares)

################ Unit Tests ################

def test():
    "A set of tests that must pass."
    assert len(squares) == 81
    assert len(unitlist) == 27
    assert all(len(units[s]) == 3 for s in squares)
    assert all(len(peers[s]) == 20 for s in squares)
    assert units['C2'] == [['A2', 'B2', 'C2', 'D2', 'E2', 'F2', 'G2', 'H2', 'I2'],
                           ['C1', 'C2', 'C3', 'C4', 'C5', 'C6', 'C7', 'C8', 'C9'],
                           ['A1', 'A2', 'A3', 'B1', 'B2', 'B3', 'C1', 'C2', 'C3']]
    assert peers['C2'] == {'A2', 'B2', 'D2', 'E2', 'F2', 'G2', 'H2', 'I2', 'C1', 'C3', 'C4', 'C5', 'C6', 'C7', 'C8',
                           'C9', 'A1', 'A3', 'B1', 'B3'}
    print('All tests pass.')

#counts the number of conflicts in a given grid
def conflict_count(values):
    rowsAndCols=unitlist[:18]
    conflicts=0
    for u in rowsAndCols:
        #list of digits in a given row/column
        uVals= [values[i] for i in u]

        #count of digits in given row/column
        digitCount= [uVals.count(i) for i in set(uVals)]

        #summing number of conflicts (digits appearing more than once in row/column)
        conflicts+= sum(x>1 for x in digitCount)
    return conflicts

#applies the hidden singles heuristic to a single unit as described by the article Sudoku by Angus Johnson
def hidden_singles(unit,values):
    #array containing each square that a digit is a candidate in .e.g digitsCount[0]=sqaures that have 1 as a candidate
    digitsCount = [[] for digit in digits]

    for s in unit:
        if len(values[s]) > 1:
            for v in values[s]:
                digitsCount[int(v) - 1] += [s]
    for i in range(9):
        #if a digit is a candidate in only one square, assign it to that square
        if len(digitsCount[i]) == 1:
            values = assign(values, digitsCount[i][0], str(i + 1))
    return values

#Hill Climbing
def hill_climbing(values):
    blocs=unitlist[18:]
    newVals=values.copy()
    for b in blocs:
        availDig="123456789"
        for s in b:
            #remove preassigned digits from available digits list
            if len(values[s])==1:
                availDig=availDig.replace(newVals[s],'')
        #assign remaining available digits to empty squares randomly
        for s in b:
            if len(values[s])>1:
                newVals[s]=random.choice(availDig)
                availDig=availDig.replace(newVals[s],'')
    #array containing all possible swaps in our grid as tuples (square1, square2)
    #only squares in the same bloc are considered
    possibleSwaps=[]
    for b in blocs:
        #unassigned squares list
        possibleSwapSquares=[]
        for s in b:
            if len(values[s])>1:
                possibleSwapSquares+=[s]
        for x in possibleSwapSquares:
            for y in possibleSwapSquares:
                if (x!=y and (y,x) not in possibleSwaps):
                    possibleSwaps.append((x,y))
    bestScore = conflict_count(newVals)
    initScore=float('+inf')

    #hill climbing loop
    while initScore!=bestScore:
        initScore=bestScore
        bestSwap=None
        #trying all possible steps
        for swap in possibleSwaps:
            possibleVals = newVals.copy()
            possibleVals[swap[0]], possibleVals[swap[1]] = possibleVals[swap[1]], possibleVals[swap[0]]
            #calculating score after taking step
            possibleScore= conflict_count(possibleVals)
            if possibleScore<bestScore:
                bestScore=possibleScore
                bestSwap=swap
        if bestSwap is not None:
            newVals[bestSwap[0]], newVals[bestSwap[1]] = newVals[bestSwap[1]], newVals[bestSwap[0]]
    return newVals

################ Parse a Grid ################

def parse_grid(grid):
    """Convert grid to a dict of possible values, {square: digits}, or
    return False if a contradiction is detected."""
    ## To start, every square can be any digit; then assign values from the grid.
    values = dict((s, digits) for s in squares)
    for s, d in grid_values(grid).items():
        if d in digits and not assign(values, s, d):
            return False  ## (Fail if we can't assign d to square s.)
    ## Hidden singles
    for unit in unitlist:
        values = hidden_singles(unit, values)
    return values


def grid_values(grid):
    "Convert grid into a dict of {square: char} with '0' or '.' for empties."
    chars = [c for c in grid if c in digits or c in '0.']
    assert len(chars) == 81

    return dict(zip(squares, chars))


################ Constraint Propagation ################

def assign(values, s, d):
    """Eliminate all the other values (except d) from values[s] and propagate.
    Return values, except return False if a contradiction is detected."""
    other_values = values[s].replace(d,'')
    if all(eliminate(values, s, d2) for d2 in other_values):
        return values
    else:
        return False


def eliminate(values, s, d):
    """Eliminate d from values[s]; propagate when values or places <= 2.
    Return values, except return False if a contradiction is detected."""
    if d not in values[s]:
        return values  ## Already eliminated
    values[s] = values[s].replace(d, '')
    ## (1) If a square s is reduced to one value d2, then eliminate d2 from the peers.
    if len(values[s]) == 0:
        return False  ## Contradiction: removed last value
    elif len(values[s]) == 1:
        d2 = values[s]
        if not all(eliminate(values, s2, d2) for s2 in peers[s]):
            return False
    ## (2) If a unit u is reduced to only one place for a value d, then put it there.
    for u in units[s]:
        dplaces = [s for s in u if d in values[s]]
        if len(dplaces) == 0:
            return False  ## Contradiction: no place for this value
        elif len(dplaces) == 1:\
            # d can only be in one place in unit; assign it there
            if not assign(values, dplaces[0], d):
                return False
    return values


################ Display as 2-D grid ################

def display(values):
    "Display these values as a 2-D grid."
    width = 1 + max(len(values[s]) for s in squares)
    line = '+'.join(['-' * (width * 3)] * 3)
    for r in rows:
        print(''.join(values[r + c].center(width) + ('|' if c in '36' else ''))
              for c in cols)
        if r in 'CF': print(line)


################ Search ################

def solve(grid): return search(parse_grid(grid))

def solveRandom(grid): return searchRandom(parse_grid(grid))

def solveHill(grid): return hill_climbing(parse_grid(grid))


def search(values):
    "Using depth-first search and propagation, try all possible values."
    if values is False:
        return False  ## Failed earlier
    if all(len(values[s]) == 1 for s in squares):
        return values  ## Solved!
    ## Choose the unfilled square s with the fewest possibilities
    n, s = min((len(values[s]), s) for s in squares if len(values[s]) > 1)
    return some(search(assign(values.copy(), s, d))
                for d in values[s])

def searchRandom(values):
    "Using depth-first search and propagation, try all possible values."
    if values is False:
        return False  ## Failed earlier
    if all(len(values[s]) == 1 for s in squares):
        return values  ## Solved!
    ## Choose unfilled square s randomly
    flag=True
    while flag:
        s=random.choice(rows)+random.choice(digits)
        flag = False if (len(values[s]) > 1) else True
    return some(search(assign(values.copy(), s, d))
                for d in values[s])


################ Utilities ################

def some(seq):
    "Return some element of seq that is true."
    for e in seq:
        if e: return e
    return False


def from_file(filename, sep='\n'):
    "Parse a file into a list of strings, separated by sep."
    return open(filename).read().strip().split(sep)


def shuffled(seq):
    "Return a randomly shuffled copy of the input sequence."
    seq = list(seq)
    random.shuffle(seq)
    return seq


################ System test ################

import time, random


def solve_all(grids, name='', showif=0.0):
    """Attempt to solve a sequence of grids. Report results.
    When showif is a number of seconds, display puzzles that take longer.
    When showif is None, don't display any puzzles."""

    def time_solve(grid):
        start = time.process_time()
        values = solveHill(grid)
        t = time.process_time() - start
        ## Display puzzles that take long enough
        if showif is not None and t > showif:
            display(grid_values(grid))
            if values: display(values)
            print('(%.2f seconds)\n' % t)
        return (t, solved(values))

    times, results = zip(*[time_solve(grid) for grid in grids])
    N = len(grids)
    if N > 1:
        print("Solved %d of %d %s puzzles (avg %.2f secs (%d Hz), max %.2f secs)." % (
            sum(results), N, name, sum(times) / N, N / sum(times), max(times)))


def solved(values):
    "A puzzle is solved if each unit is a permutation of the digits 1 to 9."

    def unitsolved(unit): return set(values[s] for s in unit) == set(digits)

    return values is not False and all(unitsolved(unit) for unit in unitlist)


def random_puzzle(N=17):
    """Make a random puzzle with N or more assignments. Restart on contradictions.
    Note the resulting puzzle is not guaranteed to be solvable, but empirically
    about 99.8% of them are solvable. Some have multiple solutions."""
    values = dict((s, digits) for s in squares)
    for s in shuffled(squares):
        if not assign(values, s, random.choice(values[s])):
            break
        ds = [values[s] for s in squares if len(values[s]) == 1]
        if len(ds) >= N and len(set(ds)) >= 8:
            return ''.join(values[s] if len(values[s]) == 1 else '.' for s in squares)
    return random_puzzle(N)  ## Give up and make a new puzzle


grid1 = '003020600900305001001806400008102900700000008006708200002609500800203009005010300'
grid2 = '4.....8.5.3..........7......2.....6.....8.4......1.......6.3.7.5..2.....1.4......'
hard1 = '.....6....59.....82....8....45........3........6..3.54...325..6..................'
testgrid={'A1': '5', 'A2': '2', 'A3': '4','A4': '4', 'A5': '3', 'A6': '7','A7': '6', 'A8': '8', 'A9': '9',
 'B1': '6', 'B2': '9', 'B3': '7','B4': '1', 'B5': '5', 'B6': '9','B7': '2', 'B8': '7', 'B9': '3',
 'C1': '8', 'C2': '1', 'C3': '3','C4': '6', 'C5': '', 'C6': '2','C7': '4', 'C8': '1', 'C9': '5',
 'D1': '4', 'D2': '3', 'D3': '1','D4': '1', 'D5': '3', 'D6': '2','D7': '4', 'D8': '8', 'D9': '1',
 'E1': '5', 'E2': '8', 'E3': '6','E4': '5', 'E5': '6', 'E6': '4','E7': '9', 'E8': '3', 'E9': '2',
 'F1': '7', 'F2': '9', 'F3': '2','F4': '7', 'F5': '9', 'F6': '8','F7': '7', 'F8': '6', 'F9': '5',
 'G1': '2', 'G2': '8', 'G3': '9','G4': '7', 'G5': '1', 'G6': '5','G7': '8', 'G8': '4', 'G9': '2',
 'H1': '6', 'H2': '4', 'H3': '5','H4': '2', 'H5': '9', 'H6': '3','H7': '9', 'H8': '1', 'H9': '3',
 'I1': '3', 'I2': '1', 'I3': '7','I4': '8', 'I5': '6', 'I6': '4','I7': '7', 'I8': '5', 'I9': '6'}
if __name__ == '__main__':
    test()
    #print(solve(grid1))
    solve_all(from_file("top95.txt"), "95sudoku", None)
    #solve_all(from_file("easy50.txt", '========'), "easy", None)
    #solve_all(from_file("easy50.txt", '========'), "easy", None)
    solve_all(from_file("100sudoku.txt"), "hard", None)
    solve_all(from_file("1000sudoku.txt"), "hardest", None)
    #solve_all([random_puzzle() for _ in range(99)], "random", 100.0)
    #solve_all(from_file("top95.txt"), "95sudoku", None)
    # solve_all(from_file("easy50.txt", '========'), "easy", None)
    # solve_all(from_file("easy50.txt", '========'), "easy", None)
    # solve_all(from_file("top95.txt"), "hard", None)
    # solve_all(from_file("hardest.txt"), "hardest", None)
    # solve_all([random_puzzle() for _ in range(99)], "random", 100.0)

## References used:
## http://www.scanraid.com/BasicStrategies.htm
## http://www.sudokudragon.com/sudokustrategy.htm
## http://www.krazydad.com/blog/2005/09/29/an-index-of-sudoku-strategies/
## http://www2.warwick.ac.uk/fac/sci/moac/currentstudents/peter_cock/python/sudoku/