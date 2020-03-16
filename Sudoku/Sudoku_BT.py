import sys
import copy

# Running script: given code can be run with the command:
# python file.py, ./path/to/init_state.txt ./output/output.txt

class Variable(object):
    def __init__(self, position):
        self.position = position  # position is a tuple (i, j) representing i-j coordinates
        self.domain = set(range(1, 10))  # domain of variable is from 1..9 incl. initially
        self.fixedValue = 0  # 0 indicates value is not fixed yet.

    def __hash__(self):
        return hash(str(self.position))

    def set_value(self, value):
        self.fixedValue = value
        self.domain = self.domain.remove(value)  # initialize set to being empty

    def reset_value(self):
        self.fixedValue = 0  # 0 indicates value is not fixed yet

    # Remove all items in elements_to_remove (a set) from this variable's domain
    def reduce_domain(self, elements_to_remove):
        self.domain = self.domain.difference(elements_to_remove)

class Assignment(object):
    def __init__(self, list_of_cells):
        self.assignment_dict = dict()  # maps tuple (i, j) to a value.
        # Initialise the assignments from list of cells (2D array) given
        num_of_fixed_values = 0  # counting number of unassigned variables left
        for i in range(0, len(list_of_cells)):
            for j in range(0, len(list_of_cells[0])):
                curr_variable = list_of_cells[i][j]

                if curr_variable != 0:  # not 0 means variable has been assigned
                    num_of_fixed_values += 1
                self.assignment_dict[(i, j)] = curr_variable
        self.unassigned_count = 9 * 9 - num_of_fixed_values

    def isComplete(self):
        return self.unassigned_count == 0

class CSP(object):
    def __init__(self, list_of_cells):
        self.unassigned_dict = dict()  # maps tuple (i, j) to a Variable object (of corresponding position)
        for i in range(0, len(list_of_cells)):
            for j in range(0, len(list_of_cells[0])):
                if list_of_cells[i][j] == 0:  # 0 means unassigned initially, is a variable to consider
                    self.unassigned_dict[(i, j)] = Variable((i, j))

    def size(self):
        return len(self.unassigned_dict)

class Sudoku(object):
    def __init__(self, puzzle):
        self.puzzle = puzzle  # self.puzzle is a list of lists
        self.ans = copy.deepcopy(puzzle)  # self.ans is a list of lists
        self.assignment = Assignment(puzzle)  # initialize assignment based on given input
        self.csp = CSP(puzzle)

    def backtrack(self, assignment, csp):
        if assignment.isComplete():
            return assignment
        else:
            return assignment.unassigned_count

    def backtrack_search(self, csp):
        return self.backtrack(self.assignment, csp)

    # Method to initially reduce domains of all variables based on already assigned cells
    def initial_domain_reduction(self):
        # Go through every row
        for r in range(0, 9):
            items = set()
            for c in range(0, 9):
                if self.puzzle[r][c] != 0:
                    items.add(self.puzzle[r][c])
            for x in range(0, 9):
                if (r, x) in self.csp.unassigned_dict:
                    self.csp.unassigned_dict[(r, x)].reduce_domain(items)

        # Go through every column
        for a in range(0, 9):
            items = set()
            for b in range(0, 9):
                if self.puzzle[b][a] != 0:
                    items.add(self.puzzle[b][a])
            for y in range(0, 9):
                if (y, a) in self.csp.unassigned_dict:
                    self.csp.unassigned_dict[(y, a)].reduce_domain(items)

        # Go through 3x3 grid
        for f in range(0, 7, 3):
            for g in range(0, 7, 3):
                items = set()
                for i in range(f, f + 3):
                    for j in range(g, g + 3):
                        if self.puzzle[i][j] != 0:
                            items.add(self.puzzle[i][j])
                for i in range(f, f + 3):
                    for j in range(g, g + 3):
                        if (i, j) in self.csp.unassigned_dict:
                            self.csp.unassigned_dict[(i, j)].reduce_domain(items)

    def solve(self):

        self.initial_domain_reduction()
        print(self.csp.unassigned_dict[(0, 1)].domain)


        # self.ans is a list of lists
        return self.ans

    # you may add more classes/functions if you think is useful
    # However, ensure all the classes/functions are in this file ONLY
    # Note that our evaluation scripts only call the solve method.
    # Any other methods that you write should be used within the solve() method.

if __name__ == "__main__":
    # STRICTLY do NOT modify the code in the main function here
    if len(sys.argv) != 3:
        print ("\nUsage: python CS3243_P2_Sudoku_XX.py input.txt output.txt\n")
        raise ValueError("Wrong number of arguments!")

    try:
        f = open(sys.argv[1], 'r')
    except IOError:
        print ("\nUsage: python CS3243_P2_Sudoku_XX.py input.txt output.txt\n")
        raise IOError("Input file not found!")

    puzzle = [[0 for i in range(9)] for j in range(9)]
    lines = f.readlines()

    i, j = 0, 0
    for line in lines:
        for number in line:
            if '0' <= number <= '9':
                puzzle[i][j] = int(number)
                j += 1
                if j == 9:
                    i += 1
                    j = 0

    sudoku = Sudoku(puzzle)
    ans = sudoku.solve()

    with open(sys.argv[2], 'a') as f:
        for i in range(9):
            for j in range(9):
                f.write(str(ans[i][j]) + " ")
            f.write("\n")
